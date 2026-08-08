#!/usr/bin/env python3
"""
Nemotron-Personas-Korea(CC BY 4.0)에서 피해자 페르소나를 취약군별 층화 샘플링.
스트리밍이 대용량 샤드에서 행 → parquet 샤드 1개만 받아서 로컬에서 샘플링.

출력: personas_sample.json
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import defaultdict
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq

OUT = Path(__file__).parent / "personas_sample.json"
PER_GROUP = int(sys.argv[1]) if len(sys.argv) > 1 else 150
SHARD = "data/train-00001-of-00009.parquet"      # 가장 작은 샤드(~220MB, ~11만 레코드)

FIELDS = ["uuid", "age", "sex", "occupation", "province", "district",
          "education_level", "marital_status", "family_type", "housing_type", "persona"]


def vuln_group(age, occ):
    occ = occ or ""
    if (age or 0) >= 60: return "고령층(60+)"
    if any(k in occ for k in ["경영자", "판매원", "노점", "상점", "자영", "소상공"]): return "자영업자"
    if any(k in occ for k in ["학생", "취업준비"]): return "학생/취준"
    if "주부" in occ or occ == "무직": return "주부/무직"
    if (age or 0) >= 40: return "중장년(40-59)"
    return "청년직장인(20-39)"


def main():
    print(f"샤드 다운로드: {SHARD} ...", flush=True)
    path = hf_hub_download("nvidia/Nemotron-Personas-Korea", SHARD, repo_type="dataset")
    print(f"다운로드 완료: {path}", flush=True)

    pf = pq.ParquetFile(path)
    cols = [c for c in FIELDS + ["hobbies_and_interests_list"] if c in pf.schema_arrow.names]
    buckets = defaultdict(list)
    scanned = 0
    core = ["고령층(60+)", "청년직장인(20-39)", "중장년(40-59)", "자영업자"]
    for batch in pf.iter_batches(batch_size=4000, columns=cols):
        rows = batch.to_pylist()
        for r in rows:
            scanned += 1
            g = vuln_group(r.get("age"), r.get("occupation"))
            if len(buckets[g]) < PER_GROUP:
                rec = {k: r.get(k) for k in FIELDS}
                rec["hobbies"] = r.get("hobbies_and_interests_list")
                rec["vulnerability_group"] = g
                buckets[g].append(rec)
        if all(len(buckets[k]) >= PER_GROUP for k in core):
            break

    pool = [p for v in buckets.values() for p in v]
    OUT.write_text(json.dumps({
        "source": "nvidia/Nemotron-Personas-Korea (CC BY 4.0)",
        "shard": SHARD, "scanned": scanned, "n": len(pool),
        "by_group": {k: len(v) for k, v in buckets.items()},
        "personas": pool,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"스캔 {scanned} → 샘플 {len(pool)}  { {k: len(v) for k, v in buckets.items()} }", flush=True)
    print(f"저장 → {OUT}", flush=True)


if __name__ == "__main__":
    main()
