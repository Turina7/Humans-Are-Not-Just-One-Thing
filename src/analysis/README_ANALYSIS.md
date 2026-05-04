# 🛠️ Intersectionality Analysis Toolkit

This folder contains the suite of tools developed to analyze the **AI Incident Database** from an intersectional perspective. These scripts process the annotated data in `../../data/annotations/annotations.json` and generate reports in `../../data/results/`.

## 🚀 How to Run
All scripts should be executed from this directory (`src/analysis`) using:
`python3 <script_name>.py`

---

## 📊 Available Tools

### 1. `qualitative_zoom.py`
**What it does:** Unpacks the entire database into a readable format.
- **Output:** `../../data/results/qualitative_zoom_results.txt`
- **Use case:** Use this to read the "Real Evidence" and "Specific Harm" of every case, organized by category (Age, Race, Class, etc.).

### 2. `deployer_analysis.py`
**What it does:** Identifies who is responsible for the harmful AI systems.
- **Output:** `../../data/results/deployer_analysis_results.txt`
- **Use case:** Great for the "Discussion" section of the thesis. It ranks top offenders (Amazon, Microsoft, etc.) and compares if the harm comes from Private Companies or State Institutions.

### 3. `text_mining.py`
**What it does:** Extracts the most frequent keywords used to describe harm in each category.
- **Output:** `../../data/results/keyword_analysis_results.txt`
- **Use case:** Perfect for finding the "vocabulary of oppression." (e.g., discovering that *'arrested'* is a keyword for Race, while *'fired'* is for Class).

### 4. `generate_charts.py`
**What it does:** Creates a high-resolution Heatmap of intersections.
- **Output:** `../../src/analysis/intersectionality_heatmap.png`
- **Use case:** Put this directly in your PowerPoint or Thesis results. It visually shows which identities overlap most frequently in AI harm cases.

### 5. `case_exporter.py`
**What it does:** An interactive tool to export specific case studies.
- **Output:** `../../data/results/case_studies/Incident_XXX_Case_Study.md`
- **How to use:** Run it, pick an ID from the list, and it will generate a beautifully formatted Markdown file for your Annex.

---
*Developed for the "Humans Are Not Just One Thing" Research Project (2026).*