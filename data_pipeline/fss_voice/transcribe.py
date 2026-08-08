#!/usr/bin/env python3
"""
영상 → 오디오 추출(ffmpeg) → 한국어 전사(mlx-whisper) → (선택)화자분리(pyannote)
→ 화자가 구분된 텍스트/JSON 출력.

출력(각 nttId):
  data/audio/<nttId>.wav
  data/transcripts/<nttId>.json   세그먼트 [{start,end,speaker,text}]
  data/transcripts/<nttId>.txt    사람이 검수하기 쉬운 "화자A: ..." 형식

화자분리는 HUGGINGFACE_TOKEN 환경변수 + pyannote 설치 시에만 동작.
없으면 speaker 를 빈칸으로 두고(사람이 채움) 타임스탬프만 제공.

사용법:
  python transcribe.py                # manifest 전체
  python transcribe.py 217128 130785  # 특정 nttId 만
  WHISPER_MODEL=mlx-community/whisper-large-v3-mlx python transcribe.py
"""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
VID = DATA / "videos"
AUD = DATA / "audio"; AUD.mkdir(parents=True, exist_ok=True)
TRS = DATA / "transcripts"; TRS.mkdir(parents=True, exist_ok=True)

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")


def extract_audio(mp4: Path, wav: Path) -> None:
    """16kHz mono PCM wav 로 변환 (whisper/pyannote 표준 입력)."""
    if wav.exists():
        return
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp4), "-ac", "1", "-ar", "16000",
         "-vn", "-f", "wav", str(wav)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def transcribe(wav: Path) -> list[dict]:
    import mlx_whisper
    res = mlx_whisper.transcribe(
        str(wav), path_or_hf_repo=WHISPER_MODEL,
        language="ko", word_timestamps=True,
        initial_prompt="보이스피싱 사기범과 피해자의 통화 녹음입니다.")
    segs = []
    for s in res.get("segments", []):
        segs.append({"start": round(s["start"], 2), "end": round(s["end"], 2),
                     "speaker": "", "text": s["text"].strip()})
    return segs


def diarize(wav: Path):
    """pyannote 화자분리. 실패/미설치 시 None."""
    token = os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        return None
    try:
        from pyannote.audio import Pipeline
    except Exception:
        return None
    pipe = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=token)
    dia = pipe(str(wav))
    turns = [(t.start, t.end, spk) for t, _, spk in dia.itertracks(yield_label=True)]
    return turns


def assign_speakers(segs: list[dict], turns) -> None:
    """각 전사 세그먼트에 시간 겹침이 최대인 화자 라벨 부여."""
    if not turns:
        return
    for seg in segs:
        best, best_ov = "", 0.0
        for ts, te, spk in turns:
            ov = min(seg["end"], te) - max(seg["start"], ts)
            if ov > best_ov:
                best_ov, best = ov, spk
        seg["speaker"] = best


def write_outputs(nttid: str, segs: list[dict]) -> None:
    (TRS / f"{nttid}.json").write_text(
        json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = []
    for s in segs:
        spk = s["speaker"] or "화자?"
        lines.append(f"[{s['start']:>7.2f}-{s['end']:>7.2f}] {spk}: {s['text']}")
    (TRS / f"{nttid}.txt").write_text("\n".join(lines), encoding="utf-8")


def main():
    items = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    want = set(sys.argv[1:])
    if want:
        items = [it for it in items if it["nttId"] in want]
    todo = [it for it in items if (VID / f"{it['nttId']}.mp4").exists()]
    print(f"전사 대상 {len(todo)}건  (모델: {WHISPER_MODEL})")
    for i, it in enumerate(todo, 1):
        ntt = it["nttId"]
        mp4, wav = VID / f"{ntt}.mp4", AUD / f"{ntt}.wav"
        try:
            extract_audio(mp4, wav)
            segs = transcribe(wav)
            turns = diarize(wav)
            assign_speakers(segs, turns)
            write_outputs(ntt, segs)
            tag = "화자분리✓" if turns else "타임스탬프만(화자 사람이 지정)"
            print(f"  [{i}/{len(todo)}] {ntt}: {len(segs)}세그먼트, {tag}")
        except Exception as e:
            print(f"  ! {ntt} 실패: {e}")
    print(f"완료 → {TRS}")


if __name__ == "__main__":
    main()
