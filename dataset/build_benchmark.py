#!/usr/bin/env python3
"""
MT-PhishingBench 단일 벤치마크 파일 빌드.
합성 대화(synth_dialogues.json) + FSS 실데이터(fss_dialogues.json)를 일관 스키마로 통합,
층화 train/test(80/20) 분할 부여 → dataset/MT-PhishingBench.json (+ .jsonl)
"""
import json, random
from pathlib import Path
from collections import Counter, defaultdict

random.seed(2026)
ROOT = Path(__file__).parent
GEN = ROOT.parent / "data_pipeline" / "generation" / "synth_dialogues.json"
FSS = ROOT.parent / "data_pipeline" / "fss_voice" / "data" / "fss_dialogues.json"

synth = json.load(open(GEN, encoding="utf-8"))["conversations"]
fss = json.load(open(FSS, encoding="utf-8"))["conversations"]


def norm_turns(turns, rich):
    out = []
    for i, t in enumerate(turns):
        nt = {"idx": i, "speaker": t["speaker"], "text": t["text"]}
        if rich:
            nt["stage"] = t.get("stage")
            nt["psych_technique"] = t.get("psych_technique", [])
            nt["intervention_point"] = bool(t.get("intervention_point", False))
        else:
            nt["stage"] = None
            nt["psych_technique"] = []
            nt["intervention_point"] = False
        out.append(nt)
    return out


unified = []
for c in synth:
    unified.append({
        "id": f"synth_{c['conversation_id']}",
        "source": "synthetic",
        "label": "phishing",
        "fraud_type": c["fraud_type"],
        "modus_operandi": c.get("modus_operandi", []),
        "laundering_overlay": c.get("laundering_overlay", []),
        "channel": c.get("channel", "call"),
        "outcome": c.get("outcome"),
        "susceptibility": c.get("susceptibility"),
        "victim_persona": c.get("victim_persona"),
        "source_url": None,
        "turns": norm_turns(c["turns"], rich=True),
    })
for c in fss:
    unified.append({
        "id": f"fss_{c['conversation_id']}",
        "source": "fss_real",
        "label": "phishing",
        "fraud_type": None,            # 실데이터는 T코드 미부여(제목만; 추후 라벨링 가능)
        "modus_operandi": [],
        "laundering_overlay": [],
        "channel": c.get("channel", "call"),
        "outcome": None,
        "susceptibility": None,
        "victim_persona": None,
        "source_url": c.get("source_url"),
        "title": c.get("title"),
        "turns": norm_turns(c["turns"], rich=False),
    })

# 층화 train/test (80/20) — (source, 유형, outcome) 기준
strata = defaultdict(list)
for i, c in enumerate(unified):
    key = (c["source"], (c["fraud_type"] or {}).get("primary_code", "")[:2], c["outcome"] or "na")
    strata[key].append(i)
test_idx = set()
for key, idxs in strata.items():
    random.shuffle(idxs)
    k = max(1, round(len(idxs) * 0.2)) if len(idxs) > 1 else 0
    test_idx.update(idxs[:k])
for i, c in enumerate(unified):
    c["split"] = "test" if i in test_idx else "train"

random.shuffle(unified)

meta = {
    "name": "MT-PhishingBench",
    "version": "0.1",
    "description": "한국어 보이스피싱 멀티턴 대화 벤치마크. 합성(라벨 완비) + FSS 실데이터(화자라벨).",
    "n_total": len(unified),
    "by_source": dict(Counter(c["source"] for c in unified)),
    "by_label": dict(Counter(c["label"] for c in unified)),
    "by_split": dict(Counter(c["split"] for c in unified)),
    "by_primary_type": dict(Counter((c["fraud_type"] or {}).get("primary_code", "")[:2] or "fss(unlabeled)" for c in unified)),
    "note_negatives": "정상통화(negative) 클래스는 미포함(추후 AIHub 실데이터/합성 결합 예정) — 현재 전량 phishing.",
    "schema": {
        "id": "str", "source": "synthetic|fss_real", "label": "phishing",
        "fraud_type": "{primary_code,primary_path,leaf} | null(fss)",
        "modus_operandi": "[T6/T8 태그]", "laundering_overlay": "[T9 태그]",
        "channel": "call|sms|messenger", "outcome": "성공|미수|중도차단 | null(fss)",
        "susceptibility": "0-1 | null", "victim_persona": "{Nemotron 필드} | null",
        "source_url": "FSS 원본링크 | null", "split": "train|test",
        "turns": "[{idx,speaker(사기범/피해자),text,stage,psych_technique[],intervention_point}]",
    },
    "taxonomy_ref": "knowledge_base/taxonomy_t1_t9.json",
    "conversations": unified,
}

(ROOT / "MT-PhishingBench.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
with open(ROOT / "MT-PhishingBench.jsonl", "w", encoding="utf-8") as f:
    for c in unified:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print(f"통합 {len(unified)}건  source={meta['by_source']}  split={meta['by_split']}")
print(f"유형분포={meta['by_primary_type']}")
print(f"저장 → dataset/MT-PhishingBench.json (+ .jsonl)")
