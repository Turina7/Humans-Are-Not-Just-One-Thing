# Setup & Execution Guide

This guide explains how to set up the environment and reproduce the research analysis before running any scripts.

---

## 1. Prerequisites

- **Python:** Version 3.8 or higher.
- **Git:** Installed on your local machine.

---

## 2. Step-by-Step Installation

### Step 1: Clone the Repository

Open your terminal and clone the project using HTTPS (recommended for external users):

```bash
git clone https://github.com/Turina7/Humans-Are-Not-Just-One-Thing.git
cd Humans-Are-Not-Just-One-Thing
```

Alternatively, if you use SSH:

```bash
git clone git@github.com:Turina7/Humans-Are-Not-Just-One-Thing.git
```

### Step 2: Create a Virtual Environment

```bash
# Create the environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

### Step 3: Install Required Libraries

Install Pandas, Matplotlib, Seaborn, and other necessary research tools:

```bash
pip install -r requirements.txt
```

---

## 3. Mandatory Project Structure

Before executing scripts, verify that the project structure is intact:

- `data/annotations_v2.json` — The processed dataset with 285 causal entries.
- `data/figures/` — Folder where visualization PNGs are stored.
- `src/` — Folder containing the Python source code.

---

## 4. Configuration (API Keys)

If you wish to use the LLM-based annotation tools in the `src/` folder, you will need an Anthropic API key:

1. Create a file named `.env` in the root directory.
2. Add your key: `ANTHROPIC_API_KEY=your_key_here`

> **Note:** This is **NOT** required to run the current analysis on existing data.

---

## 5. Running the Analysis

Once the setup is complete, navigate to the `src/` directory:

```bash
cd src
```

### A. Quantitative Analysis (RQ1 – RQ4)

This script calculates prevalence, intersectional scores, and media bias. Results are printed to the terminal:

```bash
python3 analysis_rq.py
```

### B. Visualizations

This script generates all charts and the intersectional heatmap in the `data/figures/` folder:

```bash
python3 quick_analysis.py
```

---

## 6. Research Context (CQ Filter)

All analysis in this project is based on a **Causal Filter**:

- **CQ1:** Did this incident happen because the AI Subject was [identity value]? *(Filter: YES)*
- **CQ2:** Would this incident still have happened if the AI Subject was not [identity value]? *(Filter: NO)*