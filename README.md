# Humans-Are-Not-Just-One-Thing
### Systematic study of intersectional AI harms in workplace settings
**Politecnico di Torino · Engineering AI Systems · 2025/2026**

---

## 🚀 The "MarcChanges" Evolution
We have upgraded the project from a raw dataset to a **causal-driven analytical pipeline**. The current architecture ensures that every identity marker analyzed is not just a correlation, but a direct cause of the AI harm documented, following Kimberlé Crenshaw’s intersectionality principles.

### 🛠 Key Technical Upgrades
* **Causal Filtering (CQ1 & CQ2):** Implemented a rigorous double-check system using LLM-assisted coding to verify the causal link for every identity marker:
    * **CQ1:** Did this incident happen because the AI Subject was [identity value]?
    * **CQ2:** Would this incident still have happened if the AI Subject was not [identity value]?
* **Causal Outcome Mapping:** Every identified harm is now formatted following a strict causal template to ensure logical consistency:
    * *Template:* `Because of [identity], the subject was [harmful outcome].`
* **Massive Data Processing:** Mapped over **58,000 reports** to **285 unique workplace incidents**, ensuring high-quality deduplication and domain relevance.
* **Automated Visualization:** A custom suite (`quick_analysis.py`) that generates 6 distinct research graphs following our scientific framework.

---

## 📊 Research Framework & Results
Our pipeline answers four core Research Questions (RQs) by filtering out noise and focusing on intersectional causality.

### [Phase 0] The Causal Gate (CQ1 + CQ2)
Before any analysis, we filter raw markers using the strict counterfactual questions mentioned above.
* **Impact:** Only if **CQ1=Yes** and **CQ2=No**, the data is retained for analysis.
* *See: `data/figures/graph0_CQ_filter_impact.png`*

### [RQ1] Category Frequency
**Which identities are most frequently harmed?**
* **Key Finding:** **Social Class** and **Race** are the leading causal factors in workplace AI incidents.
* *See: `data/figures/graph1_RQ1_frequency.png`*

### [RQ2] Intersectional Overlap
**How do identities amplify harm?**
* **Key Finding:** We identified specific "risk clusters" (e.g., *Disability + Chronic Illness*) where harm is mathematically amplified through intersectional overlap.
* *See: `data/figures/graph2_RQ2_heatmap.png`*

### [RQ3] Media Representation Bias
**Does the press accurately report these harms?**
* **RQ3a (Accuracy):** **52.3%** of harms are **Inferred**, meaning the media often obscures the specific identity of the victims.
* **RQ3b (Power Dynamics):** There is a stark disparity in coverage between *Privileged* and *Oppressed* groups.
* *See: `graph3_RQ3a_simplification.png` & `graph4_RQ3b_representation.png`*

### [RQ4] High-Profile Impact
**Do famous AI failures follow these patterns?**
* **Key Finding:** High media reach (e.g., Amazon, ChatGPT cases) often correlates with high identity complexity, even if headlines only mention one factor.
* *See: `data/figures/graph5_RQ4_high_profile.png`*

---

## 📂 Project Structure
```text
src/
├── batch_annotate.py   # LLM engine with causal prompts (CQ1/CQ2)
├── analysis_rq.py      # Computes mathematical scores and metrics
└── quick_analysis.py   # Generates the final research figures (RQ1-RQ4)
data/
├── workplace_reports.csv   # Raw dataset (58k+ entries)
├── annotations_v2.json     # Processed causal dataset with "Because of..." mapping
└── figures/                # Generated research graphs