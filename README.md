# Humans Are Not Just One Thing

**Systematic Study of Intersectional AI Harms in Workplace Settings**

A research pipeline for causally extracting, annotating, and analysing intersectional identity-based harms in AI incident reports. This project produced the dataset and results behind the paper *"Humans Are Not Just One Thing"* (EAI '26, Politecnico di Torino).

---

## What this project does

Most AI fairness audits examine one identity axis at a time — race *or* gender *or* class. This pipeline treats people the way they actually exist: as carriers of multiple, simultaneous identities. It:

1. **Annotates** raw workplace AI incident reports using an LLM-assisted causal extraction pipeline grounded in Kimberlé Crenshaw's intersectionality theory.
2. **Filters** identity markers with a double counterfactual gate (CQ1 + CQ2) so only identities that *caused* the harm are retained.
3. **Quantifies** intersectional amplification — how much riskier a combination of identities is compared to what independent rates would predict.
4. **Audits** media coverage to measure how often causally relevant identities are omitted from press reporting.

---

## Project structure

```
Humans-Are-Not-Just-One-Thing/
├── README.md
├── SETUP.md
├── requirements.txt
├── data/
│   ├── workplace_reports.csv          # 58,000+ raw news articles
│   ├── workplace_incidents.csv        # Pre-aggregated incident summaries
│   ├── fitered_dataset.csv            # Filtered workplace-relevant subset
│   ├── incidents_full_set_27112025_gpt5_1.json  # Legacy GPT-5 annotations
│   ├── migrate_json.py                # Schema migration helper
│   ├── annotations/
│   │   └── annotations.json           # Main output: LLM-annotated incidents
│   ├── progress/                      # Checkpoints for batch annotation runs
│   ├── figures/                       # Generated graphs (PNG)
│   └── results/                       # Generated analysis reports (TXT/MD)
└── src/
    ├── rubric/
    │   └── batch_annotate.py          # LLM annotation pipeline (Gemini API)
    └── analysis/
        ├── utils.py                   # Shared normalisation & validation logic
        ├── analysis_rq.py             # RQ1–RQ4 terminal summary
        ├── quick_analysis.py          # Generates all four paper figures
        ├── qualitative_zoom.py        # Per-category qualitative breakdown
        ├── deployer_analysis.py       # Corporate vs. state deployer audit
        ├── text_mining.py             # Keyword analysis of harm descriptions
        ├── case_exporter.py           # Exports individual incidents as Markdown
        └── data_import.py             # Legacy dataset loader with causal filter
```

---

## Key concepts

| Term | Definition |
|---|---|
| **CQ1** | *"Did this incident happen because the subject was [identity]?"* — Yes only if the AI system's behaviour changed due to that identity. |
| **CQ2** | *"Would this incident still have happened if the subject were not [identity]?"* — No only if a person with a different identity would have been spared. |
| **DirectScore = Yes** | CQ1 passed: identity directly shaped the harm. |
| **AlternateScore = No** | CQ2 passed: harm required that specific identity. |
| **Amplification Score** | `Obs(a ∩ b) / (P(a) · P(b) · N)` — how much more often a pair of identities co-occurs in harm than chance predicts. A score above 1.0× proves intersectional compounding. |
| **Media Erasure Index (E)** | `|Inferred| / (|Explicit| + |Inferred|)` — the fraction of causally relevant identities invisible in press coverage. |

---

## Main findings (EAI '26)

- **285 unique workplace incidents**, yielding **567 causally verified identity-harm links** across **15 identity categories**.
- **Race** (23.1%) and **Class** (22.9%) are the leading causal factors; together they account for nearly half of all verified harms.
- Every statistically reliable identity pair exceeds the 1.0× independent baseline. **Disabled + Older Adult** reaches **5.94×**.
- The **Media Erasure Index is 48.8%**: nearly half of causally relevant identities are never named in the press. Class is the starkest blind-spot — *lower class* appears 104 times as an inferred marker but only 10 times explicitly.

---

## Scripts at a glance

### `src/rubric/batch_annotate.py`
Calls the Gemini API to annotate each incident in `workplace_reports.csv` and `workplace_incidents.csv`. Saves results incrementally to `data/annotations/annotations.json` and checkpoints progress so interrupted runs can resume safely.

### `src/analysis/quick_analysis.py`
Produces the four publication figures saved to `data/figures/`:
- `graph1_category_prevalence.png` — bar chart of top identity categories
- `graph2_intersection_heatmap.png` — co-occurrence heatmap
- `graph3_top_value_pairs.png` — most frequent intersecting value pairs
- `graph4_amplification.png` — amplification scores with 1.0× baseline

### `src/analysis/analysis_rq.py`
Prints a consolidated terminal report covering RQ1 (category prevalence), RQ2 (amplification), RQ3 (media simplification), and RQ4 (source power dynamics).

### `src/analysis/qualitative_zoom.py`
Writes a detailed per-category breakdown of every harm case to `data/results/qualitative_zoom_results.txt`.

### `src/analysis/deployer_analysis.py`
Identifies which organisations caused the most identity-based harms and compares corporate vs. state deployers by category. Output: `data/results/deployer_analysis_results.txt`.

### `src/analysis/text_mining.py`
Extracts the most frequent words in harm descriptions per identity category. Output: `data/results/keyword_analysis_results.txt`.

### `src/analysis/case_exporter.py`
Interactive script: enter an incident ID and it exports a formatted Markdown case study to `data/results/case_studies/`. Useful for thesis annexes.

---


## License

See individual source files. Dataset derived from the [AI Incident Database](https://incidentdatabase.ai/) (AIID) — please respect their terms of use when redistributing annotations.
