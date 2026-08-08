#!/usr/bin/env python3
"""생성된 개별 합성 대화(pilot/*.json) → 단일 synth_dialogues.json 통합."""
import json, glob
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).parent
convos = []
for f in sorted(glob.glob(str(ROOT/'pilot'/'C*.json'))):
    try: convos.append(json.load(open(f, encoding='utf-8')))
    except Exception as e: print('ERR', f, e)
# 무결성 체크
bad = [c['conversation_id'] for c in convos for t in c['turns'] if t['speaker'] not in ('사기범','피해자')]
out = {
    "dataset": "MT-PhishingBench-Synthetic",
    "n_conversations": len(convos),
    "by_outcome": dict(Counter(c['outcome'] for c in convos)),
    "by_primary": dict(Counter(c['fraud_type']['primary_code'][:2] for c in convos)),
    "by_channel": dict(Counter(c.get('channel') for c in convos)),
    "avg_turns": round(sum(len(c['turns']) for c in convos)/max(1,len(convos)),1),
    "invalid_speaker_labels": len(bad),
    "conversations": convos,
}
(ROOT/'synth_dialogues.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print({k:out[k] for k in ['n_conversations','by_outcome','by_primary','by_channel','avg_turns','invalid_speaker_labels']})
