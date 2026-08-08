# Victim Persona Pool (Methodology [B])
A victim persona pool constructed via **stratified sampling by voice-phishing vulnerability group** from
[nvidia/Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0).

## Generation
```bash
pip install huggingface_hub pyarrow
python persona_sampler.py [quota_per_group]   # default: 150
```
- Streams rows from the large-scale shards, downloading only a single parquet shard (~220MB) for local sampling.
- Vulnerability groups: older adults (60+) · young working adults (20–39) · middle-aged adults (40–59) · self-employed individuals · homemakers/unemployed (students/job seekers as needed).

## Output
`personas_sample.json` — **750 personas** (5 groups × 150). Each entry contains:
`uuid · age · sex · occupation · province · district · education_level · marital_status · family_type · housing_type · persona · hobbies · vulnerability_group`

## Usage
Serves as the victim conditioning variable in the design matrix (scam-type code × **persona group** × outcome × difficulty).
Susceptibility is assigned at generation time (not fixed as a persona attribute).

## Notes
- The downloaded parquet file resides in the HF cache and is not included in the repository (only `personas_sample.json` is committed).
- Due to Nemotron's independence assumption across attributes, some unrealistic combinations may occur (e.g., older age + unmarried) — when generating, the persona summary field (`persona`) should be prioritized as the primary reference.
