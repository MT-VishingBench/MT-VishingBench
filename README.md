# MT-PhishingBench

A Korean voice-phishing **multi-turn dialogue benchmark dataset**. It synthesizes realistic
conversations between a persistent attacker and a victim who reacts in stages
(resistance → persuasion → compliance/refusal), grounded in the official financial-authority
fraud-type taxonomy (T1–T9) and real-world data (FSS).

> 🎓 For academic benchmarking. All conversations are **synthetic** and intended **solely for
> detection/defense research**.

## Dataset (single-file usage)
- **[`dataset/MT-PhishingBench.jsonl`](dataset/MT-PhishingBench.jsonl)** — one line = one
  conversation (standard loading format)
- **[`dataset/MT-PhishingBench.json`](dataset/MT-PhishingBench.json)** — combined file with
  metadata + schema + full data (human-readable)

| Item | Value |
|---|---|
| Total conversations (positive file) | **2,170** (2,000 synthetic + 170 real FSS transcripts; 141 after excluding conversations of ≤3 turns) |
| Split | train 1,738 / test 432 (stratified 80/20) |
| Fraud type | T1 527 · T3 481 · T5 402 · T4 241 · T2 187 · T7 162 · FSS 170 |
| Average turns | 17.1 (multiple rounds of resistance–rebuttal–compliance; attacker:victim utterance-length ratio ≈7:1) |
| Labels | per-utterance stage, persuasion technique, intervention_point + per-conversation fraud type, outcome, persona |
| Label quality | structural validation 10/10; independent sample (36 cases) stage 95.9% · technique 95.5% · outcome 100% · intervention point 88.9% |
| Outcome distribution | success 781 · terminated early 638 · attempt failed 581 |

⚠️ `MT-PhishingBench.json/.jsonl` are **positive (phishing)-only** files. The **negative
(normal)** class exists as separate files — 1,000 everyday-conversation dialogues + 2,170
consultation-call dialogues — and the paper's evaluation snapshot reports the combined total
of **5,310** conversations (2,141 phishing + 3,169 normal, after excluding ≤3-turn
conversations). Details: [dataset/README_en.md](dataset/README_en.md).

## Methodological Grounding (summary — see [docs/REFERENCES_en.md](docs/REFERENCES_en.md) for detail)
| Axis | Grounding |
|---|---|
| Fraud-type taxonomy T1–T9 | Official classification by the Korean financial authority (FSI contribution) |
| Progression stage (contact→deception→compliance→extraction) | Crime Script Analysis (Cornish 1994) + scam compliance (Whitty 2013) |
| Persuasion techniques (authority, urgency, fear, isolation, rapport-building, compliance-inducing, social proof) | Cialdini / Stajano-Wilson (CACM 2011) / Ferreira et al. (2015) |
| Synthesis methods | Self-Instruct · SODA · CAMEL · Generative Agents · Generator-Critic |
| Generation/labeling models | Dialogue generation: Claude Opus 4.8 (multi-agent roleplay) · Labeling/verification: Claude Sonnet 5 |
| Personas | Nemotron-Personas-Korea (CC BY 4.0) |
| Evaluation/documentation | G-Eval · Datasheets for Datasets |

Compared with prior work (KorCCVi: single-utterance binary classification / TeleAntiFraud-28k:
Chinese, audio / Fraud-R1 · PreScam · ScriptMind: multi-turn but missing some of online-prefix
evaluation, hierarchical typing, or intervention timing / FinBen · FSKU · FinRED:
finance-specific benchmarks that are neither conversational nor fraud-specific),
MT-PhishingBench is the only resource that simultaneously satisfies **Korean + multi-turn +
online-prefix evaluation + T1–T9 multi-label typing + utterance-level dynamics +
intervention-timing evaluation**. Details: [docs/REFERENCES_en.md](docs/REFERENCES_en.md).

> A separate paper describing this dataset exists: "Beyond Detection Task: A Turn-Level
> Benchmark for Fraud Scenario-Aware Understanding and Timely Intervention in Financial Live
> Chat Phishing Conversations" (submitted to ICAIF '26, currently under anonymous review).

## Repository Structure
```
dataset/                      # ★ Integrated benchmark (MT-PhishingBench.json/.jsonl) + datasheet
knowledge_base/               # [A] T1–T9 ontology · persuasion techniques · progression stages
data_pipeline/
  fss_voice/                  # FSS real phishing audio collection/transcription (170 conversations) + real-data statistics
  personas/                   # 750 Nemotron vulnerability-group personas
  generation/                 # design matrix (2,000 cells) · synthesis · label verification · report generation
prompts/                      # Expert-context prompts used for the paper's §5.3 evaluation (RQ2)
docs/                         # METHODOLOGY.md · REFERENCES.md · comprehensive report PDF (1,630p)
```

## Pipeline (reproduction)
```
[A] Knowledge base (T1–T9 · stages · techniques) + real-data grounding (170 FSS transcripts + statistics)
[B] Personas (750 = 5 vulnerability groups × 150) → design matrix (2,000 cells: type × persona × outcome × difficulty × channel)
[C][D] Multi-agent synthesis (Claude Opus 4.8 · domain-knowledge prompting · meta-awareness blocking · outcome control)
[E] Label verification (Claude Sonnet 5; full structural pass + 36-case independent sample)
[F] Merge normal-call classes (1,000 everyday + 2,170 consultation) → 5,310-conversation evaluation snapshot · release
```

## Progress
- ✅ Knowledge base · 170 FSS real-data transcripts (141 reflected in the evaluation snapshot after ≤3-turn exclusion) · 750 personas · 2,000-cell design matrix
- ✅ **2,000** synthetic conversations · label verification (95%+) · positive-class benchmark integrated
- ✅ Negative (normal) subsets built: 1,000 everyday-conversation + 2,170 consultation-call dialogues (the paper's evaluation is based on the combined snapshot of 5,310)
- ⬜ Physical merge of negative data into a single `MT-PhishingBench.json/.jsonl` file · baseline expansion

## Ethics
Entirely based on synthetic/public data, intended solely for detection/defense research. Real
phishing content is grounded only in publicly released FSS transcript text (videos are not
redistributed). Text-only, de-identified. Clearly distinguished from attack-feasibility
research (e.g., ViKing). Details: [docs/METHODOLOGY_en.md](docs/METHODOLOGY_en.md) §Ethics.
