#!/usr/bin/env python3
"""
FSS '바로 이 목소리' 대화를 단일 JSON 데이터셋으로 통합한다.

소스 우선순위(중복 방지):
  - 본문 텍스트가 있는 게시물 → data/dialogues/<nttId>__<k>.txt (원문 화자라벨) 사용
  - 본문 없는 영상전용 게시물 → data/transcripts_labeled/<nttId>.txt (STT+화자라벨) 사용

각 대화에 메타데이터(원본 게시물 링크 포함)를 붙여 data/fss_dialogues.json 으로 저장.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
VIEW_URL = "https://www.fss.or.kr/fss/bbs/B0000203/view.do?nttId={ntt}&menuNo=200686"
SPK_RE = re.compile(r"^(사기범|피해자)\s*[:：]\s*(.*)$")


def parse_turns(path: Path) -> list[dict]:
    turns = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = SPK_RE.match(line)
        if m and m.group(2).strip():
            turns.append({"speaker": m.group(1), "text": m.group(2).strip()})
    return turns


def main():
    manifest = {it["nttId"]: it for it in
                json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))}
    index = json.loads((DATA / "dialogues" / "index.json").read_text(encoding="utf-8"))

    convos, needs_manual, pending_tx = [], [], []
    for rec in index:
        ntt = rec["nttId"]
        meta = manifest.get(ntt, {})
        base = {
            "nttId": ntt,
            "title": meta.get("title", "").strip().rstrip("| ").strip(),
            "date": meta.get("date", ""),
            "source_url": VIEW_URL.format(ntt=ntt),
        }
        if rec["source"] == "body_text":
            for fn in rec["files"]:                       # 신고건별 분리본
                turns = parse_turns(DATA / "dialogues" / fn)
                if turns:
                    convos.append({"conversation_id": Path(fn).stem,
                                   "source": "fss_body_text",
                                   **base, "n_turns": len(turns), "turns": turns})
        else:                                             # 영상전용 → STT(통화별 분리본)
            sdir = DATA / "stt_dialogues"
            skip_marker = sdir / f"{ntt}__SKIP.txt"
            files = sorted((p for p in sdir.glob(f"{ntt}__*.txt")
                            if p.stem.split("__")[1].isdigit()),
                           key=lambda p: int(p.stem.split("__")[1]))
            any_turns = False
            for sf in files:
                turns = parse_turns(sf)
                if turns:
                    any_turns = True
                    convos.append({"conversation_id": sf.stem,
                                   "source": "fss_stt",
                                   **base, "n_turns": len(turns), "turns": turns})
            if not any_turns:
                if skip_marker.exists():                  # 처리했으나 환청 = 수기전사 필요
                    needs_manual.append({**base,
                        "reason": "STT 환청/노이즈 — 사람이 영상 청취 후 수기 전사 필요",
                        "video_path": f"data/videos/{ntt}.mp4"})
                else:                                     # 미전사 또는 분리·라벨 대기
                    pending_tx.append(ntt)

    out = {
        "dataset": "MT-PhishingBench-FSS",
        "description": "금융감독원 '바로 이 목소리' 실 보이스피싱 통화 대화. "
                       "본문 원문(화자라벨) 우선, 없으면 STT 전사.",
        "n_conversations": len(convos),
        "by_source": {
            "fss_body_text": sum(c["source"] == "fss_body_text" for c in convos),
            "fss_stt": sum(c["source"] == "fss_stt" for c in convos),
        },
        "n_needs_manual": len(needs_manual),
        "n_pending_transcription": len(pending_tx),
        "conversations": convos,
        "needs_manual": needs_manual,      # 환청 → 사람이 청취 후 수기 전사할 목록
    }
    (DATA / "fss_dialogues.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    # 사람이 보기 쉬운 별도 목록(환청/수기전사 필요)
    (DATA / "needs_manual.json").write_text(
        json.dumps(needs_manual, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"통합 대화 {len(convos)}건 "
          f"(본문 {out['by_source']['fss_body_text']} / STT {out['by_source']['fss_stt']})")
    print(f"환청→수기전사 필요(확정) {len(needs_manual)}건: {[r['nttId'] for r in needs_manual]}")
    print(f"미전사 또는 분리·라벨 대기 {len(pending_tx)}건")
    print(f"저장 → {DATA/'fss_dialogues.json'} , {DATA/'needs_manual.json'}")


if __name__ == "__main__":
    main()
