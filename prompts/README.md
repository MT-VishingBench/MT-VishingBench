# Evaluation Prompts (Expert-Guided Prompting)

The expert-context prompt texts used in the paper's §5.3, "RQ2: Can expert-guided prompting
improve LLM performance on multi-turn financial fraud understanding?" Footnote 1 (right after
the abstract) states that "dataset, sourcecode, detailed type taxonomies, and **prompts** are
available at [repo link]" — this folder is what "prompts" refers to. Footnote 8 ("For detailed
prompts, refer to the link mentioned in Section 1") likewise points here.

## Condition Mapping

| File | Paper condition | Perspective | Target task |
|---|---|---|---|
| *(no file, zero-shot)* | Baseline | No expert context appended | All |
| `1. Financial Fraud (Fraud-type expert).txt` | Financial Fraud | Financial-crime investigator | Task 2 (fraud-type classification) |
| `2. Social Engineering (Social-engineering expert).txt` | Social Engineering | Crime-script (Cornish 1994) / persuasion analyst | Task 3 (stage & persuasion technique) |
| `3. Intervention (Intervention expert).txt` | Intervention | Financial consumer-protection specialist | Task 4 (intervention timing) |
| `4. Integrated (Integrated expert).txt` | Integrated Expert | Combines the three perspectives above into one prompt | Tasks 2, 3, 4 |

## How These Are Used

- All conditions share the identical base task instructions, output schema, and scoring rules.
  Each file's text is only an **added context block** appended to the system prompt — it does
  not change the output format or how responses are scored (see each file's closing sentence,
  "This context does not change the output schema or scoring rules.").
- The Baseline condition is the zero-shot setting with no such context attached, so it has no
  corresponding file.
- Every prompt explicitly restricts judgment to the currently observed prefix ("Judge only the
  observed prefix" and similar phrasing), preventing labels from leaking in information from
  future turns.

## Summary of Paper Findings (§5.3, RQ2)

Expert-guided prompting consistently improved performance on the task each expert perspective
specifically targets (Figure 2). However, combining all three perspectives into a single
Integrated Expert prompt did not always yield the best result — investigative reasoning (who is
after what), crime-script analysis (what scene is happening now), and consumer-protection
judgment (should we intervene now) call for different reasoning priorities, so merging them into
one prompt diluted task-specific reasoning rather than reinforcing it (most pronounced on
Task 3). In short, expert knowledge helps, but how such perspectives are combined is itself a
distinct design problem — that is the key takeaway of this experiment.
