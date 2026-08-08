#!/usr/bin/env python3
"""
FSS 보이스피싱 체험관 "바로 이 목소리" 목록/상세 스크래퍼.

게시판: https://www.fss.or.kr/fss/bbs/B0000203/list.do?menuNo=200686
- 목록(list.do)을 pageIndex로 순회하며 nttId/제목/날짜 수집
- 각 상세(view.do)에서 실제 영상 mp4 URL 추출 (공통 템플릿 더미는 제외)
출력: data/manifest.json  [{nttId, title, date, page, view_url, video_url}]
"""
from __future__ import annotations
import json, re, sys, time, html
from pathlib import Path
import requests

BASE = "https://www.fss.or.kr/fss/bbs/B0000203"
MENU = "200686"
VOD_HOST = "https://vod.fss.or.kr"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}

# 모든 상세 페이지에 공통으로 박혀 있는 템플릿/더미 영상(존재하지 않음, 404) — 제외
TEMPLATE_HASHES = {"02ad42f788454cc4ad75cbba9c957d3a"}

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

MP4_RE = re.compile(r"/upload/encoding/video/(\d{4})/(\d{2})/([0-9a-f]+)_media[^\"'<> ]*\.mp4")
ROW_RE = re.compile(r"view\.do\?nttId=(\d+)[^>]*>(.*?)</a>", re.S)
DATE_RE = re.compile(r"(20\d{2})[-.](\d{2})[-.](\d{2})")


def get(url: str, **kw) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30, **kw)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def parse_list_page(page_idx: int) -> list[dict]:
    url = f"{BASE}/list.do?menuNo={MENU}&pageIndex={page_idx}"
    htm = get(url)
    items = []
    for m in ROW_RE.finditer(htm):
        nttid = m.group(1)
        raw = html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
        raw = re.sub(r"\s+", " ", raw).strip()
        dm = DATE_RE.search(raw)
        date = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}" if dm else ""
        title = DATE_RE.sub("", raw).strip(" -")
        title = re.sub(r"\s*[\d,]+\s*회?\s*$", "", title).strip()  # 끝의 조회수(예: '1138 회') 제거
        items.append({"nttId": nttid, "title": title, "date": date, "page": page_idx})
    # 페이지 내 등장 순서 유지, nttId 중복 제거
    seen, uniq = set(), []
    for it in items:
        if it["nttId"] not in seen:
            seen.add(it["nttId"]); uniq.append(it)
    return uniq


def extract_video_url(nttid: str, date: str) -> str | None:
    url = f"{BASE}/view.do?nttId={nttid}&menuNo={MENU}"
    htm = get(url)
    cands = []  # (year, month, hash, path)
    for m in MP4_RE.finditer(htm):
        if m.group(3) in TEMPLATE_HASHES:
            continue
        cands.append((m.group(1), m.group(2), m.group(3), m.group(0)))
    if not cands:
        return None
    # 게시일 연도와 일치하는 폴더 우선 (여러 개일 때)
    if len(cands) > 1 and date:
        yr = date[:4]
        cands.sort(key=lambda c: (c[0] != yr,))
    return VOD_HOST + cands[0][3]


def main():
    max_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    all_items, seen = [], set()
    for p in range(1, max_pages + 1):
        rows = parse_list_page(p)
        new = [r for r in rows if r["nttId"] not in seen]
        if not new:
            print(f"[list] page {p}: 신규 0건 → 종료")
            break
        for r in new:
            seen.add(r["nttId"])
        all_items.extend(new)
        print(f"[list] page {p}: +{len(new)}건 (누적 {len(all_items)})")
        time.sleep(0.4)

    print(f"\n총 {len(all_items)}건. 상세에서 영상 URL 추출 중...")
    ok = 0
    for i, it in enumerate(all_items, 1):
        it["view_url"] = f"{BASE}/view.do?nttId={it['nttId']}&menuNo={MENU}"
        try:
            it["video_url"] = extract_video_url(it["nttId"], it["date"])
        except Exception as e:
            it["video_url"] = None
            print(f"  ! {it['nttId']} 추출 실패: {e}")
        if it["video_url"]:
            ok += 1
        if i % 10 == 0 or i == len(all_items):
            print(f"  [{i}/{len(all_items)}] 영상 확보 {ok}건")
        time.sleep(0.3)

    (OUT / "manifest.json").write_text(
        json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {OUT/'manifest.json'}  (영상 URL 확보 {ok}/{len(all_items)})")


if __name__ == "__main__":
    main()
