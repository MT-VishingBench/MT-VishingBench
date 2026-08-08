#!/usr/bin/env python3
"""
[E] 라벨 자동 검증 — synth_dialogues.json 전수.
스키마·화자·단계순서(접촉→기망→행동유도→편취)·기법값·intervention_point·outcome 정합성 점검.
출력: label_audit.json (집계 + 위반 사례 id)
"""
import json
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).parent
KB = ROOT.parent.parent / "knowledge_base"

STAGES = ["contact", "deception", "compliance", "extraction"]
SORD = {s: i for i, s in enumerate(STAGES)}
TECHS = {t["name"] for t in json.load(open(KB / "persuasion_techniques.json", encoding="utf-8"))["techniques"]}

d = json.load(open(ROOT / "synth_dialogues.json", encoding="utf-8"))
convos = d["conversations"]

issues = {k: [] for k in [
    "bad_speaker", "bad_stage", "unknown_technique", "empty_text",
    "stage_out_of_order", "success_no_extraction", "blocked_reached_extraction",
    "success_no_intervention", "ip_wrong_stage", "no_attacker_or_victim"]}

for c in convos:
    cid = c["conversation_id"]; outcome = c.get("outcome")
    spk = set(); stages_seen = []; prev = -1; has_ip = False
    for t in c["turns"]:
        spk.add(t.get("speaker"))
        if t.get("speaker") not in ("사기범", "피해자"): issues["bad_speaker"].append(cid)
        if not (t.get("text") or "").strip(): issues["empty_text"].append(cid)
        st = t.get("stage")
        if st not in SORD: issues["bad_stage"].append(cid)
        else:
            stages_seen.append(st)
            if SORD[st] < prev: issues["stage_out_of_order"].append(cid)
            prev = max(prev, SORD[st])
        for tq in t.get("psych_technique", []):
            if tq not in TECHS: issues["unknown_technique"].append(f"{cid}:{tq}")
        if t.get("intervention_point"):
            has_ip = True
            if st not in ("compliance", "extraction"): issues["ip_wrong_stage"].append(cid)
    if not ({"사기범", "피해자"} <= spk): issues["no_attacker_or_victim"].append(cid)
    reached_ext = "extraction" in stages_seen
    if outcome == "성공":
        if not reached_ext: issues["success_no_extraction"].append(cid)
        if not has_ip: issues["success_no_intervention"].append(cid)
    if outcome == "중도차단" and reached_ext:
        issues["blocked_reached_extraction"].append(cid)

# dedup
issues = {k: sorted(set(v)) for k, v in issues.items()}
summary = {k: len(v) for k, v in issues.items()}
audit = {"n": len(convos), "summary": summary,
         "examples": {k: v[:10] for k, v in issues.items() if v}}
(ROOT / "label_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"검증 대상 {len(convos)}건")
for k, n in summary.items():
    flag = "✓" if n == 0 else f"⚠ {n}"
    print(f"  {k:28} {flag}")
