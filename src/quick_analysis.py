import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import Counter

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

# ── CQ1 & CQ2: DATA RETENTION (El que demanaves del CQ2) ──────
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

# ── RQ1: Frequency (Amb el top en VERMELL) ───────────────────
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
    
    # Escala de colors: Vermell pel primer, Blau per la resta
    colors = ['#C0392B'] + ['#2E86C1'] * (len(values) - 1)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
    ax.set_title("RQ1: Identity Frequency (Causal Filter Applied)", fontsize=13, fontweight="bold")
    for bar in bars:
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, int(bar.get_width()), va="center")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "graph1_RQ1_frequency.png", dpi=150)
    plt.close()

# ── RQ3a: Simplification (Amb els NÚMEROS parentitzats) ──────
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
    # Aquí posem els noms amb els números tal com t'agradava
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
# Vermell per Oppressed, Verd per Privileged
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