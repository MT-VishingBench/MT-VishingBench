#!/usr/bin/env python3
"""
설계행렬(Design Matrix) — 합성할 대화 '셀'을 통제 샘플링.
셀 = 유형(T코드) × 피해자 페르소나(취약군) × outcome × 난이도(susceptibility) × 채널.
유형 가중치는 신고 prevalence, 턴수·기법강조는 FSS 실통계(fss_stats.json) 반영.

출력: design_matrix.json  (생성 파이프라인 [C][D]의 입력)
"""
from __future__ import annotations
import json, random, sys
from pathlib import Path

random.seed(42)
ROOT = Path(__file__).parent
KB = ROOT.parent.parent / "knowledge_base"
PERS = ROOT.parent / "personas" / "personas_sample.json"
STATS = ROOT.parent / "fss_voice" / "data" / "fss_stats.json"
OUT = ROOT / "design_matrix.json"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

# 상위유형 prevalence 가중치(신고 TOP10 반영) + 적합 취약군
TYPE_W = {
    "T1": (0.28, ["고령층(60+)", "중장년(40-59)", "주부/무직", "청년직장인(20-39)", "자영업자"]),
    "T3": (0.22, ["자영업자", "중장년(40-59)", "청년직장인(20-39)", "주부/무직"]),
    "T5": (0.20, ["청년직장인(20-39)", "중장년(40-59)", "자영업자"]),
    "T4": (0.12, ["고령층(60+)", "중장년(40-59)", "주부/무직"]),
    "T2": (0.10, ["고령층(60+)", "중장년(40-59)", "청년직장인(20-39)", "자영업자", "주부/무직"]),
    "T7": (0.08, ["청년직장인(20-39)", "중장년(40-59)", "자영업자"]),
}
OUTCOME_W = {"성공": 0.40, "미수": 0.30, "중도차단": 0.30}
# 채널: 메신저피싱/스미싱은 별도, 그 외 통화
CH_BY_TYPE = {"T4.3": "messenger", "T6.3": "sms"}


def leaves_under(node):
    if not node.get("children"):
        return [node]
    out = []
    for c in node["children"]:
        out += leaves_under(c)
    return out


def main():
    tax = json.load(open(KB / "taxonomy_t1_t9.json", encoding="utf-8"))
    tech = json.load(open(KB / "persuasion_techniques.json", encoding="utf-8"))["techniques"]
    stages = [s["code"] for s in sorted(
        json.load(open(KB / "crime_script_stages.json", encoding="utf-8"))["stages"],
        key=lambda s: s["order"])]
    personas = json.load(open(PERS, encoding="utf-8"))["personas"]
    stats = json.load(open(STATS, encoding="utf-8"))

    by_type = {t["code"]: t for t in tax["taxonomy"]}
    leaves_by_type = {code: leaves_under(by_type[code]) for code in TYPE_W}
    path_of = {}  # leaf code -> (path names, leaf name)

    def build_paths(node, trail):
        nm = node["name"]; t = trail + [nm]
        if not node.get("children"):
            path_of[node["code"]] = (trail, nm)  # 상위경로(리프 제외), 리프명
        for c in node.get("children", []):
            build_paths(c, t)
    for code in TYPE_W:
        build_paths(by_type[code], [])

    pers_by_group = {}
    for p in personas:
        pers_by_group.setdefault(p["vulnerability_group"], []).append(p)

    # 기법 가중치(FSS 신호빈도) — 강조 기법 샘플용
    tfreq = stats["persuasion_technique_signal_freq"]
    tech_names = [t["name"] for t in tech]
    tech_w = [tfreq.get(n, 1) + 1 for n in tech_names]

    tp = stats["turns_per_conversation"]
    types = list(TYPE_W); tw = [TYPE_W[t][0] for t in types]

    cells = []
    for i in range(N):
        prim = random.choices(types, weights=tw)[0]
        leaf = random.choice(leaves_by_type[prim])
        trail, leafname = path_of[leaf["code"]]
        grp = random.choice(TYPE_W[prim][1])
        pool = pers_by_group.get(grp) or personas
        persona = random.choice(pool)
        outcome = random.choices(list(OUTCOME_W), weights=list(OUTCOME_W.values()))[0]

        # 난이도: 고령층/주부무직 취약↑, 성공일수록 의심↓
        base = {"고령층(60+)": .35, "주부/무직": .45, "중장년(40-59)": .5,
                "자영업자": .5, "청년직장인(20-39)": .6}.get(grp, .5)
        if outcome == "성공": base -= .15
        elif outcome == "중도차단": base += .2
        susceptibility = round(min(.95, max(.05, random.gauss(base, .12))), 2)

        # 채널
        channel = "call"
        for pref, ch in CH_BY_TYPE.items():
            if leaf["code"].startswith(pref):
                channel = ch
        # 턴수: FSS 분포에서(차단은 짧게)
        tgt = int(random.triangular(max(4, tp["p25"]), tp["p75"], tp["median"]))
        if outcome == "중도차단":
            tgt = max(4, int(tgt * 0.5))

        # 수법/자금세탁 오버레이
        mo = []
        if prim in ("T1", "T2", "T3") and random.random() < 0.5:
            mo.append(random.choice(["T6.2.1 원격제어앱", "T6.2.2 악성앱", "T6.2.3 오픈뱅킹탈취", "T6.1.2 명의도용"]))
        laundering = []
        if outcome == "성공":
            laundering.append(random.choice(["T9.1.1 다수 개인 수취", "T9.3.1 ATM 인출",
                                             "T9.2.3 타행 재이체", "T9.4.3 가상자산 전환"]))
        techniques = random.choices(tech_names, weights=tech_w, k=3)
        techniques = list(dict.fromkeys(techniques))  # dedup, 순서유지

        cells.append({
            "cell_id": f"C{i+1:04d}",
            "label": "phishing",
            "fraud_type": {"primary_code": leaf["code"],
                           "primary_path": trail, "leaf": leafname},
            "modus_operandi": mo,
            "laundering_overlay": laundering,
            "channel": channel,
            "victim_persona": {k: persona.get(k) for k in
                               ["uuid", "age", "sex", "occupation", "province", "vulnerability_group"]},
            "outcome": outcome,
            "susceptibility": susceptibility,
            "target_turns": tgt,
            "stage_sequence": stages if outcome != "중도차단" else stages[:3],
            "technique_emphasis": techniques,
        })

    # 분포 요약
    from collections import Counter
    summ = {
        "n": len(cells),
        "by_primary": dict(Counter(c["fraud_type"]["primary_code"][:2] for c in cells)),
        "by_group": dict(Counter(c["victim_persona"]["vulnerability_group"] for c in cells)),
        "by_outcome": dict(Counter(c["outcome"] for c in cells)),
        "by_channel": dict(Counter(c["channel"] for c in cells)),
        "target_turns_mean": round(sum(c["target_turns"] for c in cells) / len(cells), 1),
    }
    OUT.write_text(json.dumps({"summary": summ, "cells": cells}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summ, ensure_ascii=False, indent=2))
    print(f"저장 → {OUT}")


if __name__ == "__main__":
    main()
