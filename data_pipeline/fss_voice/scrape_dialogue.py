#!/usr/bin/env python3
"""
FSS '바로 이 목소리' 게시물 *본문*에서 대화 텍스트를 추출한다.
옛 UCC 게시물은 본문에 `사기범 :` / `피해자 :` 로 라벨된 대화가 들어있고,
한 게시물에 '첫 번째 신고 목소리' … 처럼 여러 신고건(대화)이 묶여 있다.

- 본문 대화가 있으면  → 신고건별로 분리해 data/dialogues/<nttId>__<k>.txt 로 저장
                          (STT보다 정확 → 이걸 우선 사용)
- 본문 대화가 없으면  → video_only 로 분류(STT 전사 사용 대상)

출력:
  data/dialogues/<nttId>__<k>.txt
  data/dialogues/index.json   [{nttId, title, date, source, n_dialogues, files[]}]
"""
from __future__ import annotations
import json, re, html, time
from pathlib import Path
import requests

BASE = "https://www.fss.or.kr/fss/bbs/B0000203"
MENU = "200686"
HEADERS = {"User-Agent": "Mozilla/5.0"}
ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = DATA / "dialogues"; OUT.mkdir(parents=True, exist_ok=True)

# 신고건 구분 헤더:  "첫 번째 신고 목소리", "두 번째 신고 음성", "1차 신고 통화" 등
ORD = "첫|두|세|네|다섯|여섯|일곱|여덟|아홉|열|열한|열두"
SECTION_RE = re.compile(rf"((?:{ORD}|\d+\s*차?)\s*번째?\s*신고\s*(?:목소리|음성|통화))")
SPK_RE = re.compile(r"^(사기범|피해자)\s*[:：]\s*(.*)$")


def get(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def body_lines(h: str) -> list[str]:
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S)  # JS/CSS 제거
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</(p|div|li|tr|td|h[1-6])>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    return [re.sub(r"[ \t]+", " ", l).strip() for l in h.split("\n")]


def parse_dialogues(lines: list[str]) -> list[list[tuple[str, str]]]:
    """본문 라인 → 신고건별 [(speaker, text), ...] 리스트."""
    convos, cur, started = [], [], False
    for l in lines:
        if SECTION_RE.search(l) and len(l) < 30:        # 새 신고건 시작
            if cur:
                convos.append(cur)
            cur, started = [], True
            continue
        m = SPK_RE.match(l)
        if m:
            started = True
            cur.append((m.group(1), m.group(2).strip()))
    if cur:
        convos.append(cur)
    # 헤더 없이 대화만 있는 경우: 통째로 한 건
    if not convos:
        flat = [(m.group(1), m.group(2).strip())
                for l in lines if (m := SPK_RE.match(l))]
        if flat:
            convos = [flat]
    return [c for c in convos if c]


def write_convo(nttid: str, k: int, convo: list[tuple[str, str]], meta: dict) -> str:
    f = OUT / f"{nttid}__{k}.txt"
    head = f"# {nttid}__{k} | {meta['title']} ({meta['date']})\n# 출처: FSS 게시물 본문(원문 화자라벨)\n\n"
    body = "\n".join(f"{spk}: {txt}" for spk, txt in convo if txt)
    f.write_text(head + body + "\n", encoding="utf-8")
    return f.name


def main():
    items = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    index, n_text, n_video = [], 0, 0
    for i, it in enumerate(items, 1):
        ntt = it["nttId"]
        try:
            h = get(f"{BASE}/view.do?nttId={ntt}&menuNo={MENU}")
            convos = parse_dialogues(body_lines(h))
        except Exception as e:
            convos = []
            print(f"  ! {ntt} 실패: {e}")
        rec = {"nttId": ntt, "title": it["title"], "date": it["date"]}
        if convos:
            files = [write_convo(ntt, k + 1, c, it) for k, c in enumerate(convos)]
            rec.update(source="body_text", n_dialogues=len(convos), files=files)
            n_text += 1
        else:
            rec.update(source="video_only(STT 필요)", n_dialogues=0, files=[])
            n_video += 1
        index.append(rec)
        if i % 10 == 0 or i == len(items):
            print(f"[{i}/{len(items)}] 본문대화 {n_text}건 / 영상전용 {n_video}건")
        time.sleep(0.3)

    (OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    total_conv = sum(r["n_dialogues"] for r in index)
    print(f"\n본문대화 보유 게시물 {n_text} / 영상전용 {n_video}")
    print(f"추출된 개별 대화(신고건) 총 {total_conv}건 → {OUT}")


if __name__ == "__main__":
    main()
