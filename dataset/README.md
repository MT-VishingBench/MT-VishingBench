# MT-PhishingBench — Benchmark Dataset

A single integrated release of the Korean voice-phishing **multi-turn dialogue benchmark**.

> Per the paper (ICAIF '26 submission), the final evaluation universe combining positive +
> negative is **5,310 conversations** (2,141 phishing · 3,169 normal, after excluding ≤3-turn
> conversations). Positive dialogues are generated with Claude Opus 4.8 multi-agent roleplay
> and labeled/verified with Claude Sonnet 5. As shown in the table below, the positive and
> negative classes currently ship as separate physical files.

## Files
| File | Description |
|---|---|
| `MT-PhishingBench.json` | Combined file (metadata + schema + conversations). Pretty JSON for human reading. **Positive (phishing) only** |
| `MT-PhishingBench.jsonl` | One line = one conversation. Standard format for training/evaluation loading. **Positive (phishing) only** |
| `build_benchmark.py` | Build script that merges synthetic + FSS data and applies the stratified split |
| `normal_conversation(daily).json` / `.jsonl` | **Negative (normal), everyday-conversation** subset. Synthesized from AIHub 012/020 SNS-corpus seeds (topic/register) + Nemotron persona grounding, with a T4 symmetric hard-negative design. Details: `docs/METHODOLOGY.md` §2.2, §7.2 |
| `normal_conversation(consulting).json` | **Negative (normal), consultation-call** subset. Built from AIHub call-center/consultation data, an asset built independently by a separate team member (original schema source) |

> Each file above is accompanied by an English translation (`<filename>_en.<extension>`, e.g.
> `MT-PhishingBench_en.json`, `normal_conversation(daily)_en.json`).

## Scale
### positive (phishing)
- **2,170 conversations total** = 2,000 synthetic (fully labeled) + 170 real FSS transcripts (speaker labels only)
- Split: **train 1,738 / test 432** (stratified 80/20 by source × type × outcome)
- Type: T1 527 · T3 481 · T5 402 · T4 241 · T2 187 · T7 162 · FSS (untyped) 170
- Outcome distribution (based on the 2,000 synthetic conversations): success 781 · terminated early 638 · attempt failed 581
- The FSS data recovers 180 calls from 101 reported posts, of which 170 yielded usable
  transcripts. Under the paper's evaluation-snapshot rule (excluding ≤3-turn conversations),
  only **141** are retained.

### negative (normal) — two subsets
- **(a) Everyday-conversation** — generated, verified, and QC'd from 1,000 design-matrix slots, yielding **1,000** final released conversations (Track A: 29 general topics + Track B: T4-matched hard negatives across 7 relationships × 3 intensities). Details: `docs/METHODOLOGY.md` §1.2, §7.2
- **(b) Consultation-call** — **2,170** conversations from AIHub call-center/consultation data (banking 968 · insurance 760 · securities 442), built independently by a separate team member (its construction principles and QC approach differ from (a)). 2,169 after excluding ≤3-turn conversations.
- ⚠️ The two negative subsets are **not yet physically merged** into the
  `MT-PhishingBench.json/.jsonl` integrated file; they ship as separate files
  (`normal_conversation(daily/consulting).json`). The paper's evaluation snapshot, however,
  reports figures based on combining the full positive set (141+2,000) with the full negative
  set (1,000+2,169) — **5,310 conversations** (2,141 phishing / 3,169 normal). Physical file
  merging remains future work.

## Schema (one conversation)

### positive (phishing)
```jsonc
{
  "id": "synth_C0001 | fss_18307__1",
  "source": "synthetic | fss_real",
  "label": "phishing",
  "fraud_type": {"primary_code":"T1.1.1","primary_path":[...],"leaf":"..."},  // null for FSS
  "modus_operandi": ["T6.2.1 ..."], "laundering_overlay": ["T9.1.1 ..."],
  "channel": "call|sms|messenger",
  "outcome": "success|attempt_failed|terminated_early",   // null for FSS
  "susceptibility": 0.39,                                  // null for FSS
  "victim_persona": { /* Nemotron fields */ },             // null for FSS
  "source_url": "FSS source link",                         // FSS only
  "split": "train|test",
  "turns": [{"idx":0,"speaker":"attacker","text":"...","stage":"contact",
             "psych_technique":["authority"],"intervention_point":false}]
}
```
- Stages: contact → deception → compliance → extraction
- Techniques: authority · urgency · fear · isolation · rapport-building · compliance-inducing ·
  social proof (`knowledge_base/persuasion_techniques.json`)
- Type codes: `knowledge_base/taxonomy_t1_t9.json`
- FSS real data carries speaker labels only (stage/technique/outcome/persona = null)

> Note: in the released Korean data, label values such as `outcome` and speaker roles are
> stored as Korean strings (e.g., "성공"/"미수"/"중도차단" for success/attempt failed/terminated
> early, "사기범" for attacker); the English terms above are shown for readability and are not
> the literal field values in the underlying files.

### negative (normal) — everyday-conversation (a) subset
```jsonc
{
  "id": "neg_unified_0329",
  "source": "synthetic",
  "label": "negative",
  "fraud_type": {
    "relationship_type": "coworker",     // occupies the position of positive's primary_code
    "primary_type": "sharing"
  },
  "modus_operandi": [], "laundering_overlay": [],
  "channel": "call",
  "outcome": "",                          // mostly an empty string in the release
  "susceptibility": null,
  "victim_persona": { /* Nemotron fields */ },
  "source_url": null,
  "turns": [{"idx":0,"speaker":"coworker","text":"...",
             "stage":"greeting","psych_technique":[],"intervention_point":false}],
  "split": "train"
}
```
- Field names are compatible with the positive schema, but `fraud_type` holds a
  `relationship type × purpose type` pair instead of a T-code (relationship types include
  child, son, younger sibling, friend, coworker, junior schoolmate, etc.).
- `outcome` and `susceptibility` are mostly empty in the final release (the design intent and
  the measured release differ — see `docs/METHODOLOGY.md` §4.2).
- The consultation-call (b) subset follows the original `normal_conversations.json` schema and
  may differ from (a) above.

## Supported Tasks
1. Phishing detection (binary) — possible once combined with the (a) everyday-conversation
   negative subset (see §Scale). Combined/integrated evaluation with the (b) consultation-call
   subset is future work.
2. Fraud-type classification (T1–T9, multi-label)
3. Stage/technique sequence labeling
4. Defensive intervention-point (`intervention_point`) detection

## Quality
- (positive) Automated structural validation passed 10/10; independent sample validation (36
  cases): stage 95.9% · technique 95.5% · outcome 100% · intervention point 88.9% ·
  naturalness 4.11/5
- (negative, everyday-conversation) Rule-based format/signal validation (up to 3 retries) +
  LLM-based QC across 3 axes (structural/rhythmic naturalness, referential consistency,
  content/strategy preservation)
- Details: `docs/METHODOLOGY.md` (§7.2, §8.2 for negative data), `data_pipeline/generation/verify/`

## Ethics
Entirely based on synthetic/public data, for detection/defense research only. Real phishing
content is grounded only in publicly released FSS transcript text. Negative
(everyday-conversation) dialogues are generated from synthetic personas rather than real
individuals, so we judged they do not constitute personal information; real-name masking was
therefore intentionally not applied (only some fields, such as addresses, are selectively
masked). Text-only, de-identified.

## Build
```bash
python build_benchmark.py   # synth_dialogues.json + fss_dialogues.json → MT-PhishingBench.json/.jsonl
# See docs/METHODOLOGY.md §7.2 for the negative(daily) subset's generation/verification/QC pipeline
```
