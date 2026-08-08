#!/usr/bin/env python3
"""
FSS 실데이터(fss_dialogues.json) 통계 분석 → 합성 생성 파라미터.
- 턴 길이 분포, 화자별 발화 비중/길이
- 설득기법(knowledge_base/persuasion_techniques.json) 신호어 빈도
- 공격자 도입부(첫 사기범 발화) 패턴
출력: data/fss_stats.json
"""
from __future__ import annotations
import json, re, statistics as st
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
DATA = ROOT / "data"
KB = ROOT.parent.parent / "knowledge_base"


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))]


def main():
    d = json.load(open(DATA / "fss_dialogues.json", encoding="utf-8"))
    convos = d["conversations"]
    tech = json.load(open(KB / "persuasion_techniques.json", encoding="utf-8"))["techniques"]

    # 품질 필터: 2턴 이상만 통계 대상(과분할 1턴 조각 제외)
    usable = [c for c in convos if c["n_turns"] >= 2]

    turns = [c["n_turns"] for c in usable]
    atk_chars, vic_chars, atk_turns, vic_turns = [], [], [], []
    convo_chars = []
    for c in usable:
        a = [t["text"] for t in c["turns"] if t["speaker"] == "사기범"]
        v = [t["text"] for t in c["turns"] if t["speaker"] == "피해자"]
        atk_turns.append(len(a)); vic_turns.append(len(v))
        atk_chars += [len(x) for x in a]; vic_chars += [len(x) for x in v]
        convo_chars.append(sum(len(t["text"]) for t in c["turns"]))

    # 설득기법 신호어 빈도(사기범 발화 대상)
    atk_text_all = " ".join(t["text"] for c in usable for t in c["turns"] if t["speaker"] == "사기범")
    tech_freq = {}
    for tq in tech:
        cnt = 0
        for sig in tq["signals"]:
            core = re.split(r"[ /(]", sig)[0][:4]   # 신호어 핵심 토막
            if core:
                cnt += atk_text_all.count(core)
        tech_freq[tq["name"]] = cnt

    # 공격자 도입부: 각 대화 첫 사기범 발화의 기관/키워드
    openers = Counter()
    org_kw = ["검찰", "지검", "경찰", "금융감독원", "금감원", "법원", "은행", "수사관", "검사", "사무관"]
    for c in usable:
        first = next((t["text"] for t in c["turns"] if t["speaker"] == "사기범"), "")
        for k in org_kw:
            if k in first:
                openers[k] += 1

    stats = {
        "source": "FSS fss_dialogues.json",
        "n_conversations_total": len(convos),
        "n_usable(>=2turns)": len(usable),
        "turns_per_conversation": {
            "min": min(turns), "p25": pct(turns, .25), "median": int(st.median(turns)),
            "mean": round(st.mean(turns), 1), "p75": pct(turns, .75), "max": max(turns)},
        "attacker_turns_per_conv": {"median": int(st.median(atk_turns)), "mean": round(st.mean(atk_turns), 1)},
        "victim_turns_per_conv": {"median": int(st.median(vic_turns)), "mean": round(st.mean(vic_turns), 1)},
        "chars_per_turn": {
            "attacker": {"median": int(st.median(atk_chars)), "mean": round(st.mean(atk_chars), 1)},
            "victim": {"median": int(st.median(vic_chars)), "mean": round(st.mean(vic_chars), 1)}},
        "attacker_vs_victim_char_ratio": round(sum(atk_chars) / max(1, sum(vic_chars)), 2),
        "chars_per_conversation": {"median": int(st.median(convo_chars)), "mean": round(st.mean(convo_chars), 1)},
        "persuasion_technique_signal_freq": dict(sorted(tech_freq.items(), key=lambda x: -x[1])),
        "attacker_opening_org_freq": dict(openers.most_common()),
    }
    (DATA / "fss_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"\n저장 → {DATA/'fss_stats.json'}")


if __name__ == "__main__":
    main()
