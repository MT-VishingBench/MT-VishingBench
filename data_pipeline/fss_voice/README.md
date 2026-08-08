# FSS "This Is the Voice" Collection & Refinement Pipeline

From the Financial Supervisory Service (FSS) voice-phishing experience center, ["This Is the Voice"](https://www.fss.or.kr/fss/bbs/B0000203/list.do?menuNo=200686),
we collect and refine actual voice-phishing call recordings from 101 posts into a **per-call dialogue dataset**.
(Serving as real-data grounding and a speech-style anchor for synthetic benchmark dialogues.)

## Pipeline (5 Stages)
| Script | Role | Output |
|---|---|---|
| `scrape.py` | Collect metadata and video URLs from 101 board posts | `data/manifest.json` |
| `scrape_dialogue.py` | Extract original speaker-labeled dialogue from **posts whose body text already contains dialogue transcripts** (legacy UCC posts), split by individual reported case | `data/dialogues/<nttId>__<k>.txt`, `index.json` |
| `download.py` | Download mp4 files for video-only posts with no body text | `data/videos/<nttId>.mp4` |
| `transcribe.py` | Video → audio (ffmpeg) → STT (mlx-whisper) | `data/transcripts/<nttId>.{json,txt}` |
| `build_dataset.py` | Merge body-text dialogues and refined STT transcripts into a single JSON (including metadata and source links) | `data/fss_dialogues.json`, `data/needs_manual.json` |

> **Per-call segmentation, speaker labeling, and conservative error correction** of the STT transcripts are performed via an LLM (Claude) and saved to
> `data/stt_dialogues/<nttId>__<k>.txt` (mishearings or indecipherable segments are saved as `<nttId>__SKIP.txt`).

## Setup & Execution
```bash
brew install ffmpeg
python3    -m venv .venv    && .venv/bin/pip    install requests      # collection/download/build
python3.12 -m venv .venv-tx && .venv-tx/bin/pip install mlx-whisper   # transcription (Apple Silicon)

.venv/bin/python    scrape.py            # 1) manifest
.venv/bin/python    scrape_dialogue.py   # 2) extract body-text dialogues
.venv/bin/python    download.py          # 3) mp4
.venv-tx/bin/python transcribe.py        # 4) STT
# 5) STT refinement (call segmentation / speaker labeling / correction) via LLM → data/stt_dialogues/
.venv/bin/python    build_dataset.py     # 6) merge into a single JSON
```

## Outputs
- **`data/fss_dialogues.json`** — The final merged dataset. Each dialogue entry includes `conversation_id · source (fss_body_text|fss_stt) · nttId · title · date · source_url · turns[{speaker, text}]`.
- **`data/needs_manual.json`** — A list of items requiring **manual human transcription after listening to the video**, due to STT mishearing or indecipherable audio (title, source link, video path).

## Current Status
- 101 posts → **170 dialogues** (73 from body text + 97 from STT) + 10 cases requiring manual transcription.

## Notes
- Original video/audio files are not redistributed (`.gitignore`). Only transcripts and dialogue text are committed.
- A single post may contain multiple reported cases (e.g., "reported on 6 separate occasions..."), so the number of dialogues exceeds the number of posts.
