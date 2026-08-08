#!/usr/bin/env python3
"""
manifest.json 의 video_url 들을 data/videos/<nttId>.mp4 로 다운로드.
이미 받은 파일(크기 일치)은 건너뜀.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}
ROOT = Path(__file__).parent
DATA = ROOT / "data"
VID = DATA / "videos"; VID.mkdir(parents=True, exist_ok=True)


def download(url: str, dest: Path) -> bool:
    with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        if dest.exists() and total and dest.stat().st_size == total:
            return False  # 이미 완전 다운로드됨
        tmp = dest.with_suffix(".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
        tmp.rename(dest)
        return True


def main():
    items = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(items)
    todo = [it for it in items if it.get("video_url")][:limit]
    print(f"다운로드 대상 {len(todo)}건")
    for i, it in enumerate(todo, 1):
        dest = VID / f"{it['nttId']}.mp4"
        try:
            fresh = download(it["video_url"], dest)
            print(f"  [{i}/{len(todo)}] {it['nttId']}.mp4 "
                  f"{'다운로드' if fresh else '캐시'}  ({dest.stat().st_size//1024} KB)")
        except Exception as e:
            print(f"  ! {it['nttId']} 실패: {e}")
    print(f"완료 → {VID}")


if __name__ == "__main__":
    main()
