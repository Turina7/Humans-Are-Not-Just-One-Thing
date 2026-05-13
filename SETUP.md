# Setup Guide

This guide walks you through installing dependencies, configuring API keys, and running the full pipeline from raw data to published figures.

---

## Requirements

- Python 3.10 or higher
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) (for the annotation step only)
- The raw data files — `workplace_reports.csv` and `workplace_incidents.csv` — placed in `data/`

---

## 1. Clone the repository

```bash
git clone https://github.com/your-username/Humans-Are-Not-Just-One-Thing.git
cd Humans-Are-Not-Just-One-Thing
```

---

## 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The main dependencies are:

| Package | Used by |
|---|---|
| `google-genai` | `batch_annotate.py` — Gemini API client |
| `python-dotenv` | `batch_annotate.py` — loads `.env` API key |
| `pandas` | `data_import.py` — legacy dataset loader |
| `matplotlib` | `quick_analysis.py` — figure generation |
| `numpy` | `quick_analysis.py` — heatmap matrix |

---

## 4. Configure your API key

Create a `.env` file in the project root:

```bash
touch .env
```

Add your Gemini key:

```
GEMINI_API_KEY=your_key_here
```

> The `.env` file is read automatically by `batch_annotate.py` via `python-dotenv`. Never commit this file to version control.

---

## 5. Prepare the data directories

The annotation and analysis scripts expect certain subdirectories to exist. Create them if they are not already present:

```bash
mkdir -p data/annotations data/progress data/figures data/results data/results/case_studies
```

---

## 6. Running the pipeline

### Step 1 — Annotate incidents (LLM extraction)

This step reads `data/workplace_reports.csv` and `data/workplace_incidents.csv`, sends each incident to the Gemini API, and writes results to `data/annotations/annotations.json`. Progress is checkpointed after every incident so the script can be safely interrupted and resumed.

```bash
cd src/rubric
python batch_annotate.py
```

> **Cost & time:** Annotation runs once. With ~285 incidents and a 2-second sleep between calls, expect around 15–20 minutes for a full run. Existing annotations are skipped automatically on resume.

---

### Step 2 — Generate figures

Produces the four publication-ready graphs in `data/figures/`.

```bash
cd src/analysis
python quick_analysis.py
```

Output files:

```
data/figures/
├── graph1_category_prevalence.png
├── graph2_intersection_heatmap.png
├── graph3_top_value_pairs.png
└── graph4_amplification.png
```

---

### Step 3 — Run the RQ analysis report

Prints a consolidated breakdown of all four research questions to the terminal.

```bash
python analysis_rq.py
```

---

### Step 4 — Run optional analysis scripts

These can be run in any order after annotation is complete.

```bash
# Per-category qualitative breakdown → data/results/qualitative_zoom_results.txt
python qualitative_zoom.py

# Corporate vs. state deployer audit → data/results/deployer_analysis_results.txt
python deployer_analysis.py

# Keyword analysis of harm descriptions → data/results/keyword_analysis_results.txt
python text_mining.py

# Interactive case study exporter → data/results/case_studies/Incident_<ID>_Case_Study.md
python case_exporter.py
```

---

## Typical workflow summary

```bash
# One-time setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key_here" > .env
mkdir -p data/annotations data/progress data/figures data/results/case_studies

# Annotate (run once, resumable)
cd src/rubric && python batch_annotate.py

# Analyse
cd ../analysis
python quick_analysis.py       # figures
python analysis_rq.py          # terminal report
python qualitative_zoom.py     # qualitative breakdown
python deployer_analysis.py    # deployer audit
python text_mining.py          # keyword analysis
python case_exporter.py        # interactive case export
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'utils'`**
Run analysis scripts from inside `src/analysis/`, not from the project root. The scripts use relative imports.

**`KeyError` on CSV columns**
The CSV reader in `batch_annotate.py` strips BOM characters and normalises column names automatically. If you are using a custom CSV, ensure column names match `incident_id`, `title`, `description`, `text`, and `source_domain`.

**Gemini API rate limit errors**
The script sleeps 2 seconds between calls and retries up to 3 times with exponential back-off. If you hit persistent quota errors, increase `time.sleep(2)` in `batch_annotate.py`.

**Annotation already complete but you want to re-run**
Delete or clear `data/progress/progress.json` and `data/annotations/annotations.json`, then rerun `batch_annotate.py`.
