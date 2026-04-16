import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from pathlib import Path
from collections import Counter
from itertools import combinations

# ── Configuration ────────────────────────────────────────────
DATA_PATH = Path("../data/annotations_v2.json")
OUTPUT_DIR = Path("../data/figures")
OUTPUT_DIR.mkdir(exist_ok=True)

with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

def get_cq1_categories(subject):
    ids = subject.get("identity_markers", {})
    return sorted([
        c.lower().replace(" ", "_") for c, v in ids.items()
        if str((v or {}).get("CQ1", "")).strip().lower() == "yes"
        and str((v or {}).get("CQ2", "")).strip().lower() == "no"
    ])

# ── CQ1 & CQ2: DATA RETENTION ────────────────────────────────
print("Processing CQ Filter Stats...")
total_markers = 0
retained_markers = 0

for rec in data:
    for subj in rec.get("subjects", []):
        ids = subj.get("identity_markers", {})
        for cat, v in ids.items():
            total_markers += 1
            if str((v or {}).get("CQ1", "")).strip().lower() == "yes" and \
               str((v or {}).get("CQ2", "")).strip().lower() == "no":
                retained_markers += 1

fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(['Total Raw Markers', 'Causal Markers (CQ1+CQ2)'], [total_markers, retained_markers], color=['#BDC3C7', '#27AE60'])
ax.set_title("Causal Filter Impact (CQ1 & CQ2)\nPrecision-driven data retention", fontweight="bold")
ax.set_ylabel("Number of Identity Markers")
for i, v in enumerate([total_markers, retained_markers]):
    ax.text(i, v + 5, str(v), ha='center', fontweight='bold')
plt.savefig(OUTPUT_DIR / "graph0_CQ_filter_impact.png", dpi=150)
plt.close()

# ── RQ1: Frequency (Top in RED) ──────────────────────────────
print("Processing RQ1...")
category_counts = Counter()
for rec in data:
    for subj in rec.get("subjects", []):
        for cat in get_cq1_categories(subj):
            category_counts[cat] += 1

top_categories = category_counts.most_common(12)
if top_categories:
    labels = [c[0].replace("_", " ").title() for c in top_categories]
    values = [c[1] for c in top_categories]
    colors = ['#C0392B'] + ['#2E86C1'] * (len(values) - 1)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
    ax.set_title("RQ1: Identity Frequency (Causal Filter Applied)", fontsize=13, fontweight="bold")
    for bar in bars:
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, int(bar.get_width()), va="center")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "graph1_RQ1_frequency.png", dpi=150)
    plt.close()

# ── RQ2: Intersection Heatmap (NEW SECTION) ──────────────────
print("Processing RQ2...")
# Extract all pairs of intersectional categories per incident
intersections = []
for rec in data:
    incident_cats = set()
    for subj in rec.get("subjects", []):
        for cat in get_cq1_categories(subj):
            incident_cats.add(cat)
    
    # If an incident has multiple categories, it's intersectional
    if len(incident_cats) >= 2:
        for combo in combinations(sorted(list(incident_cats)), 2):
            intersections.append(combo)

if intersections:
    pair_counts = Counter(intersections)
    unique_cats = sorted(list(set([c for pair in intersections for c in pair])))
    
    # Create a matrix for the heatmap
    matrix = pd.DataFrame(0, index=unique_cats, columns=unique_cats)
    for (c1, c2), count in pair_counts.items():
        matrix.loc[c1, c2] = count
        matrix.loc[c2, c1] = count # Mirror for the heatmap

    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Number of Incidents'})
    plt.title("RQ2: Intersectional Identity Overlaps\n(Causal Co-occurrences)", fontsize=13, fontweight="bold")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "graph2_RQ2_intersections.png", dpi=150)
    plt.close()

# ── RQ3a: Simplification (Numbers in labels) ─────────────────
print("Processing RQ3a...")
explicit, inferred = 0, 0
for rec in data:
    for subj in rec.get("subjects", []):
        ids = subj.get("identity_markers", {})
        for cat, v in ids.items():
            if str((v or {}).get("CQ1", "")).strip().lower() == "yes" and \
               str((v or {}).get("CQ2", "")).strip().lower() == "no":
                mt = str((v or {}).get("marker_type", "")).strip().lower()
                if mt == "explicit": explicit += 1
                elif mt == "inferred": inferred += 1

if explicit + inferred > 0:
    fig, ax = plt.subplots(figsize=(8, 7))
    labels = [f'Explicit ({explicit})', f'Inferred ({inferred})']
    ax.pie([explicit, inferred], labels=labels, autopct='%1.1f%%',
           colors=['#2E86C1', '#F39C12'], explode=(0, 0.1), shadow=True, startangle=140)
    ax.set_title("RQ3a: Media Simplification Score", fontsize=13, fontweight="bold")
    plt.savefig(OUTPUT_DIR / "graph3_RQ3a_simplification.png", dpi=150)
    plt.close()

# ── RQ3b: Representation (Privileged vs Oppressed) ───────────
print("Processing RQ3b...")
power_counts = Counter()
for rec in data:
    for subj in rec.get("subjects", []):
        ids = subj.get("identity_markers", {})
        for cat, v in ids.items():
            if str((v or {}).get("CQ1", "")).strip().lower() == "yes" and \
               str((v or {}).get("CQ2", "")).strip().lower() == "no":
                pp = str((v or {}).get("power_position", "")).strip().title()
                if pp in ["Privileged", "Oppressed"]: power_counts[pp] += 1

fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(power_counts.keys(), power_counts.values(), color=['#E74C3C', '#27AE60'])
ax.set_title("RQ3b: Identity Power Dynamics", fontweight="bold")
plt.savefig(OUTPUT_DIR / "graph4_RQ3b_representation.png", dpi=150)
plt.close()

# ── RQ4: High-Profile ────────────────────────────────────────
print("Processing RQ4...")
high_profile = sorted(data, key=lambda x: len(x.get("sources", [])), reverse=True)[:6]
hp_ids = [f"ID {x.get('incident_id')}" for x in high_profile]
hp_sources = [len(x.get("sources", [])) for x in high_profile]
hp_complexity = [max([len(get_cq1_categories(s)) for s in x.get("subjects", [])] + [0]) for x in high_profile]

fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.bar(hp_ids, hp_sources, color='#AED6F1', alpha=0.7, label='Media Sources')
ax1.set_ylabel('Media Reports', color='#2E86C1', fontweight="bold")
ax2 = ax1.twinx()
ax2.plot(hp_ids, hp_complexity, color='#C0392B', marker='o', linewidth=3, markersize=10)
ax2.set_ylabel('Identity Complexity', color='#C0392B', fontweight="bold")
plt.title("RQ4: High-Profile Cases", fontweight="bold")
plt.savefig(OUTPUT_DIR / "graph5_RQ4_high_profile.png", dpi=150)
plt.close()

print(f"\n✅ All set! Graphs updated in {OUTPUT_DIR}")