# Knowledge Base (Methodology [A])

The **label ontology and generation conditioning variables** for the synthetic dialogues. Composed of three axes.

| File | Axis | Grounding |
|---|---|---|
| `taxonomy_t1_t9.json` | **Type** (what kind of fraud) | Official T1–T9 classification by the Korean financial authority (FSI) |
| `crime_script_stages.json` | **Progression stage** (how it unfolds) | Cornish (1994) Crime Script Analysis |
| `persuasion_techniques.json` | **Persuasion technique** (how it manipulates) | Cialdini / Stajano-Wilson (2011) / Ferreira (2015) |

At generation time: type (T-code), stage, and technique are injected into the attacker agent's prompt (domain knowledge).
At labeling time: (stage, technique[]) is attached per utterance, and (T-code, label) per conversation.
Real-data (FSS) register and turn statistics are combined on top of this to form the synthesis parameters.