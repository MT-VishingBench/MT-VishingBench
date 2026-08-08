# Paper Grounding Summary (References & Grounding)

Summarizes **which literature grounds each design decision** in MT-PhishingBench.
Citations prioritize internationally recognized venues (domestic sources only when no
substitute exists). For arXiv preprints, checking the final published version is recommended
(marked with ✱).

Categories: **A** theoretical foundations · **B** synthetic-data methodology · **C** Korean
voice-phishing detection precedents (comparators) · **D** AI-based attack research
(motivation/ethics comparators) · **E** evaluation & documentation · **F** domain
datasets/resources · **G** related benchmarks/defense systems

---

## Grounding Map at a Glance (design decision → grounding)

| Design decision | Grounding literature | Category |
|---|---|---|
| Fraud-type label system (T1–T9) | Official classification by the Korean financial authority (provided by FSI) — *a research-team contribution, not a citation* | — |
| Call progression stage (contact→deception→compliance→extraction) | Cornish (1994) Crime Script Analysis | A |
| Victim compliance/resistance dynamics | Whitty (2013) scam compliance model | A |
| Utterance persuasion-technique labels (authority, urgency, fear, isolation, rapport-building, compliance-inducing, social proof) | Cialdini; Stajano & Wilson (2011); Ferreira et al. (2015) | A |
| LLM seed bootstrapping (official taxonomy/real training materials as seeds) | Wang et al. (2023) Self-Instruct | B |
| Knowledge-grounded large-scale dialogue distillation | Kim et al. (2023) SODA | B |
| Attacker↔victim roleplay (controlled generation) | Li et al. (2023) CAMEL | B |
| Persona-based behavior simulation | Park et al. (2023) Generative Agents | B |
| Generation–verification separation / iterative refinement | Jandaghi et al. (2024) Generator–Critic | B |
| Victim persona (demographic representativeness) | NVIDIA Nemotron-Personas-Korea | F |
| Quality evaluation (LLM-as-judge) | Liu et al. (2023) G-Eval | E |
| Difficulty/ambiguity quantification | Park et al. (2025) CCDV metric | C |
| Dataset documentation | Gebru et al. (2021) Datasheets | E |
| "Synthetic ≠ real distribution" concern → need for real-data grounding | "Talking Like a Phisher" (2025) | C |
| negative (normal, everyday-conversation) call-opening structure | Schegloff (1968, 1986) | A |
| negative (normal, everyday-conversation) speech-act/function classification | Sacks, Schegloff & Jefferson (1974); Goldsmith (1996); Jumanto (2017); Brown & Yule (1983) | A |
| negative (normal, everyday-conversation) decision to regenerate topic seeds (not substitute the original text) | Daft & Lengel (1986) Media Richness Theory | A |
| negative (normal, everyday-conversation) persona grounding | NVIDIA Nemotron-Personas-Korea | F |
| negative (normal, consultation-call) real-data grounding | AIHub call-center/consultation data | F |
| Domain-knowledge prompting > generic CoT | Sim & Kim (2025) | C |
| Direct comparator (Korean single-utterance classification vs. our multi-turn approach) | KorCCVi family | C/F |
| Ethics distinction (defensive use vs. attack-feasibility research) | ViKing; Heiding & Lermen (2025) | D |
| Differentiation from finance-specific benchmarks (lacking conversational/turn-level modeling) | FinBen; FSKU; FinRED; ConvFinQA | G |
| Differentiation from multi-turn scam/safety benchmarks (lacking online prefix, hierarchical typing, intervention timing) | Fraud-R1; PreScam; Script-Mind | G |
| Differentiation from defensive simulation systems (lacking a standardized prefix protocol) | SE-VSim/SE-OmniGuard; scambaiting systems (Puppeteer, etc.) | G |
| positive dialogue generation model | Anthropic Claude Opus 4.8 | F |

---

## A. Theoretical Foundations — Criminology · Persuasion Psychology
- **Cornish, D. B. (1994).** *The Procedural Analysis of Offending and Its Relevance for Situational Prevention.* Crime Prevention Studies, 3.
  → The **crime script** skeleton for decomposing a call into scenes. Grounds our four stages (contact→deception→compliance→extraction).
- **Whitty, M. T. (2013).** *The Anatomy of the Online Dating Romance Scam.* Security Journal.
  → The **scam compliance** dynamic by which victims are persuaded/comply in stages. Grounds outcome (success/attempt-failed/terminated) and the resistance-loop design.
- **Cialdini, R. B.** *Influence: The Psychology of Persuasion.*
  → The six principles of persuasion (authority, scarcity, reciprocity, consistency, social proof, liking) — the primary basis for the technique labels.
- **Stajano, F. & Wilson, P. (2011).** *Understanding Scam Victims: Seven Principles for Systems Security.* Communications of the ACM, 54(3).
  → Seven scam-specific principles (time, distraction, social compliance, etc.) — the basis for extending "urgency" and "isolation."
- **Ferreira, A., Coventry, L., Lenzini, G. (2015).** *Principles of Persuasion in Social Engineering and Their Use in Phishing.* HAS 2015 (Springer LNCS).
  → An integration of the above three into five principles — the base for our utterance label scheme. Korea-specific tactics (isolation, fear) are added as extension tags.

**negative (normal, everyday-conversation) theoretical foundation — conversation analysis and speech acts**
- **Sacks, H., Schegloff, E. A., & Jefferson, G. (1974).** *A Simplest Systematics for the Organization of Turn-Taking for Conversation.* Language.
  → Turn-taking, adjacency pairs, repair — the basis for the structural criteria (filler phrases, backchannel questions, reaction-token frequency) distinguishing natural conversation from script-like dialogue.
- **Schegloff, E. A. (1968).** *Sequencing in Conversational Openings.* American Anthropologist.
- **Schegloff, E. A. (1986).** *The Routine as Achievement.* Human Studies.
  → These two works establish that telephone calls follow a formalized opening sequence of `identification/recognition→greeting→small talk→topic transition→closing`. The core foundation for the negative (a) CA call-opening design (§2.2).
- **Goldsmith, D. (1996).** *Managing Relational Boundaries: A Taxonomy of Speech Events.* Human Communication Research.
  → A taxonomy of 29 speech events occurring in everyday relationship formation — grounds the request/sharing/relationship-maintenance three-way classification.
- **Jumanto, J. (2017).** *Phatic Communication: Its Functions in Everyday Talk.*
  → A 12-function classification of phatic communication — used to identify topical diversity in the text (SNS) seed corpus.
- **Brown, G. & Yule, G. (1983).** *Discourse Analysis.* Cambridge University Press.
  → The interactional vs. transactional distinction in language function — grounds the reflection of channel characteristics (calls vs. text).
- **Daft, R. L. & Lengel, R. H. (1986).** *Organizational Information Requirements, Media Richness and Structural Design.* Management Science.
  → Media Richness Theory — the theoretical basis for the decision to regenerate topic seeds into call structure rather than substituting the original text verbatim.

## B. Synthetic Dialogue Data Methodology
- **Wang, Y. et al. (2023).** *Self-Instruct: Aligning LMs with Self-Generated Instructions.* ACL 2023.
- **Kim, H. et al. (2023).** *SODA: Million-scale Dialogue Distillation with Social Commonsense Contextualization.* EMNLP 2023.
- **Li, G. et al. (2023).** *CAMEL: Communicative Agents for "Mind" Exploration of LLM Society.* NeurIPS 2023.
- **Park, J. S. et al. (2023).** *Generative Agents: Interactive Simulacra of Human Behavior.* UIST 2023.
- **Jandaghi, P. et al. (2024).** *Faithful Persona-based Conversational Dataset Generation with LLMs* (Generator–Critic; Synthetic-Persona-Chat). NLP4ConvAI @ ACL 2024. ✱arXiv:2312.10007.

## C. Korean Voice-Phishing Detection Precedents (Direct Comparators)
- **Lee, M. & Park, E. (2023).** *Real-time Korean voice phishing detection based on machine learning approaches.* Journal of Ambient Intelligence and Humanized Computing (Springer). — **KorCCVi v1** (Doc2Vec).
- **Boussougou, M. K. M. & Park, D.-J. (2022).** *Exploiting Korean Language Model to Improve Korean Voice Phishing Detection.* KIPS Trans. Software and Data Engineering. — KoBERT.
- **Boussougou, M. K. M. & Park, D.-J. (2023).** *Attention-Based 1D CNN-BiLSTM with FastText for Korean VP Detection.* Mathematics (MDPI).
- **Yu, S. et al. (2024).** *Korean Voice Phishing Detection Applying NER with Key Tags and Sentence-Level N-Gram.* IEEE Access, 12: 52951–52962.
- **Boussougou & Park (2024).** *Enhancing VP Detection Using Multilingual Back-Translation and SMOTE.* IEEE DataPort. — **KorCCVi v2**.
- **Park, H., Lee, Han, Byun (2025).** *Enhanced Voice Phishing Detection Using an LLM-Based Framework for Data Augmentation and Classification.* IEEE Access. — GPT-4o augmentation · **CCDV** metric.
- **(2025).** *A Multimodal Voice Phishing Detection System Integrating Text and Audio Analysis.* Applied Sciences (MDPI).
- **Sim & Kim (2025).** *Detecting Voice Phishing with Precision: Fine-Tuning Small Language Models.* ✱arXiv:2506.06180. — **domain-knowledge prompting > CoT**.
- **(2025).** *Talking Like a Phisher: LLM-Based Attacks on Voice Phishing Classifiers.* ✱arXiv:2507.16291. — synthetic evasion → basis for **the need for external validation**.

> Differentiation: the KorCCVi family centers on **real transcripts, single utterances, and
> binary classification**. This benchmark is **multi-turn + T1–T9 multi-label + stage/technique
> utterance labels + personas + defense evaluation**.

## D. AI-Based Voice-Phishing Attack Research (Motivation/Ethics Comparators)
- **Figueiredo et al. (2024).** *On the Feasibility of Fully AI-automated Vishing Attacks* (ViKing). ✱arXiv:2409.13793.
- **Figueiredo et al. (2025).** *Sounds Vishy: Automating Vishing Attacks with AI-Powered Systems.* ACM AsiaCCS 2025.
- **Toapanta, Rivadeneira, Tipantuña, Guamán (2024).** *AI-Driven Vishing Attacks: A Practical Approach.* MDPI Engineering Proceedings, 77(1):15.
- **Heiding & Lermen (2025).** *Can AI Models be Jailbroken to Phish Elderly Victims? An End-to-End Evaluation.* ✱arXiv:2511.11759 (AAAI AI Governance Workshop).

> Distinction: these are studies of *attack feasibility against real human targets using
> voice (TTS)*. Our work is **defense-side, text-only, entirely synthetic, with no real
> targets** — intended use is restricted to detection/defense (§Ethics).

## E. Evaluation and Documentation
- **Liu, Y. et al. (2023).** *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment.* EMNLP 2023.
- **Gebru, T. et al. (2021).** *Datasheets for Datasets.* Communications of the ACM, 64(12).

## F. Domain Datasets and Resources
- **TeleAntiFraud-28k (2025).** *An Audio-Text Slow-Thinking Dataset for Telecom Fraud Detection.* ✱arXiv:2503.24115. — Chinese, audio. A precedent for `<think>` reasoning labels (contrasted with our reasoning/stage labels).
- **NVIDIA (2026).** *Nemotron-Personas-Korea* (CC BY 4.0). — Victim persona pool; the same pool is also used for the negative (normal, everyday-conversation) subset's persona grounding.
- **Financial Supervisory Service Voice-Phishing Experience Center, "This is the Voice."** — Real phishing audio (public), used for grounding and register anchoring.
- **AIHub call-center/consultation data.** — Source of the negative (normal, consultation-call) class (built independently by a separate team member, `normal_conversations.json`).
- **AIHub Korean SNS multi-turn dialogue data (012), everyday text dialogue data by topic (020).** — Source of the negative (normal, everyday-conversation) subset's topic/register seeds.
- **Anthropic. Claude Opus 4.8.** — positive (phishing) dialogue generation model (multi-agent roleplay).
- **Anthropic. Claude Sonnet 5 API** (docs.claude.com). — positive labeling/verification model and the negative (normal, everyday-conversation) subset's generation/QC model.

### Supplementary (Domestic/Secondary Citations)
- Choi, K. & Kim, M. (2015). *A Study on the Progression Process of Korean Voice-Phishing Crime.* Korean Police Studies Review. — a supplementary Korean application case of Cornish's crime script.

## G. Related Benchmarks and Defense Systems (Related-Work Supplement)
> Summarizes the paper's §2.1 (finance-specific benchmarks), §2.3 (multi-turn scam
> benchmarks), and §2.4 (defensive simulation systems). See METHODOLOGY_en.md §1.1b for how
> this benchmark differs from these three lines of work.
- **Xie, Q. et al. (2024).** *FinBen: A Holistic Financial Benchmark for Large Language Models.* NeurIPS Datasets and Benchmarks Track.
- **Lee, J. et al. (2026).** *FSKU: A Practical Question-Answering Benchmark for Real-world Financial Security Knowledge Understanding in LLMs.* ACM Web Conference.
- **Kim, C. et al. (2026).** *FinRED: An Expert-guided Red-teaming Benchmark for Financial LLM Safety.* Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining.
- **Chen, Z. et al. (2022).** *ConvFinQA: Exploring the Chain of Numerical Reasoning in Conversational Finance Question Answering.* EMNLP 2022.
- **Yang, S. et al. (2025).** *Fraud-R1: A Multi-Round Benchmark for Assessing the Robustness of LLM Against Augmented Fraud and Phishing Inducements.* ACL 2025.
- **Sun, W. et al. (2023).** *PreScam: A Benchmark for Predicting Scam Progression from Early Conversations.* COLM.
- **Kim, H. et al. (2026).** *Script-Mind: A Korean-Centric LLM-based Framework for Smishing Detection and Explanation Generation.* EACL Industry Track.
- **Lee, Y. & Han, D. (2026).** *An Explainable Agentic System for Detection of Conversational Scams with Summary-Based Memory.* arXiv:2607.11707. — SE-VSim/SE-OmniGuard.
- **Siadati, H. et al. (2025).** *Evaluation of an LLM-assisted Scambaiting System.* APWG Symposium on Electronic Crime Research (eCrime).
- **Hossain, I. et al. (2025).** *AI-in-the-Loop: Privacy Preserving Real-Time Scam Detection and Conversational Scambaiting by Leveraging LLMs and Federated Learning.* arXiv:2509.05362.
- **Charnsethikul, P. et al. (2025).** *Puppeteer: Leveraging a Large Language Model for Scambaiting.* HICSS.
- **Kim, H., Kim, M. et al. (2026).** *An LLM-based Chain-of-Response Counter-Scam System.* arXiv:2606.01475.

---

✱ = arXiv preprint. Verify final published bibliographic details before submission.
