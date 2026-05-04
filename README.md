# Humans-Are-Not-Just-One-Thing
### Systematic study of intersectional AI harms in workplace settings
**Politecnico di Torino · Engineering AI Systems · 2025/2026**

---

## 🚀 The "MarcChanges" Evolution
We have upgraded the project from a raw dataset to a **causal-driven analytical pipeline**. The current architecture ensures that every identity marker analyzed is not just a correlation, but a direct cause of the AI harm documented, following Kimberlé Crenshaw’s intersectionality principles.

### 🛠 Key Technical Upgrades
* **Causal Filtering (CQ1 & CQ2):** Rigorous double-check system to verify causal links for every identity marker.
* **Causal Outcome Mapping:** Every harm follows the template: `Because of [identity], the subject was [harmful outcome]`.
* **Semantic Cleaning & Deduplication:** Implemented logic to filter redundant overlaps (e.g., *Race: PoC* vs *Skin Tone: Dark*) to ensure high-quality intersectional results.
* **Centralized Logic (`utils.py`):** Refactored the codebase to ensure a single source of truth for causal marker extraction.

---

## 📊 Research Framework & Results
Our pipeline answers four core Research Questions (RQs) by filtering out noise and focusing on intersectional causality.

### [Phase 0] The Causal Gate (CQ1 + CQ2)
Only data where **CQ1=Yes** and **CQ2=No** is retained for analysis.
* *See: `data/figures/graph0_CQ_filter_impact.png`*

### [RQ1] Category Frequency
**Social Class** and **Race** are the leading causal factors in workplace AI incidents.
* *See: `data/figures/graph1_RQ1_frequency.png`*

### [RQ2] Intersectional Overlap & Amplification
Identification of "risk clusters" (e.g., *Disability + Chronic Illness*) where harm is mathematically amplified.
* *See: `data/figures/graph4_amplification.png` & `data/figures/graph2_RQ2_heatmap.png`*

### [RQ3] Media Representation & Power Dynamics
* **52.3%** of harms are **Inferred**, showing how media often obscures victim identities.
* Stark disparity in coverage between *Privileged* and *Oppressed* groups.

---

## 🔍 The Deep-Dive Toolkit (Qualitative Analysis)
Beyond metrics, we developed a specialized toolkit in `src/analysis/` to unpack the human reality behind the numbers.

### 📂 Qualitative Zoom
A full breakdown of all **411 direct-harm markers**.
- **Output:** `data/results/qualitative_zoom_results.txt`.
- **Insight:** Organizes every incident by category, showing the "Real Evidence" used for classification.

### 🏢 Deployer Analysis ("The Hall of Shame")
An analysis of the entities responsible for the harmful AI deployments.
- **Top Offenders:** Amazon, Microsoft, and OpenAI lead the ranking.
- **Corporate vs. State:** Reveals that **Class (74%)** harm is driven by companies, while **Immigration (66%)** harm is driven by the State.

### 📝 Vocabulary of Oppression (Text Mining)
Automated extraction of the lexicon used to describe AI harm.
- **Output:** `data/results/keyword_analysis_results.txt`.
- **Pattern:** Race incidents correlate with *'facial'* and *'arrested'*, while Class incidents correlate with *'income'* and *'workers'*.

### 📄 Case Study Exporter
Interactive tool to generate beautifully formatted Markdown files for individual incidents.
- **Output:** `data/results/case_studies/`.

---

## 📂 Project Structure
```text
src/
├── batch_annotate.py     # LLM engine with causal prompts (CQ1/CQ2)
├── analysis_rq.py        # Computes mathematical scores and metrics
├── quick_analysis.py     # Generates the final research figures (RQ1-RQ4)
└── analysis/             # Deep-Dive Toolkit
    ├── utils.py          # Centralized causal logic & redundancy filters
    ├── deployer_analysis.py # Corporate vs. State harm analysis
    ├── text_mining.py    # Vocabulary & keyword extraction
    ├── case_exporter.py  # Interactive .md case study generator
    └── qualitative_zoom.py # Qualitative evidence packer
data/
├── workplace_reports.csv  # Raw dataset (58k+ entries)
├── annotations.json      # Processed causal dataset
├── results/              # Qualitative reports and text mining results
└── figures/              # Generated research graphs