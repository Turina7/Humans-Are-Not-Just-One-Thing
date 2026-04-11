import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from collections import Counter
from itertools import combinations

# ── Load data ────────────────────────────────────────────
DATA_PATH = Path("../data/annotations_v2.json")
OUTPUT_DIR = Path("../data/figures")
OUTPUT_DIR.mkdir(exist_ok=True)

with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

# ── Helper: get CQ1=Yes categories per subject ──────────
def get_cq1_categories(subject, exclude=["geography", "species"]):
    ids = subject.get("identity_markers", {})
    return sorted([
        c.lower().replace(" ", "_") for c, v in ids.items()
        if c.lower().replace(" ", "_") not in exclude
        and str((v or {}).get("DirectScore", "")).strip().lower() == "yes"
        and str((v or {}).get("AlternateScore", "")).strip().lower() == "no"
    ])

# ── GRAPH 1: Category prevalence (CQ1=Yes) ──────────────
print("Building Graph 1 — Category prevalence...")

category_counts = Counter()
for rec in data:
    for subj in rec.get("subjects", []):
        for cat in get_cq1_categories(subj):
            category_counts[cat] += 1

top_categories = category_counts.most_common(12)
labels = [c[0].replace("_", " ").title() for c in top_categories]
values = [c[1] for c in top_categories]

# Reverse both together so they stay in sync
labels_rev = labels[::-1]
values_rev = values[::-1]
colors_rev = ["#C0392B" if v == max(values) else "#2E86C1" for v in values_rev]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(labels_rev, values_rev, color=colors_rev)
ax.set_xlabel("Number of subjects where identity caused harm (CQ1=Yes)", fontsize=11)
ax.set_title("Most Common Identity Categories in Workplace AI Harm\n(filtered: CQ1=Yes, excluding geography & species)", fontsize=13, fontweight="bold")
ax.axvline(x=0, color="black", linewidth=0.5)

for bar, val in zip(bars, values_rev):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            str(val), va="center", fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph1_category_prevalence.png", dpi=150)
plt.close()
print("  Saved graph1_category_prevalence.png")
# ── GRAPH 2: Top intersections heatmap ───────────────────
print("Building Graph 2 — Intersection heatmap...")

all_cats = [c for c, _ in category_counts.most_common(8)]
matrix = np.zeros((len(all_cats), len(all_cats)), dtype=int)

for rec in data:
    for subj in rec.get("subjects", []):
        cats = set(get_cq1_categories(subj))
        for i, a in enumerate(all_cats):
            for j, b in enumerate(all_cats):
                if i != j and a in cats and b in cats:
                    matrix[i][j] += 1

# Mask upper triangle including diagonal
mask = np.triu(np.ones_like(matrix, dtype=bool), k=0)
matrix_masked = np.where(mask, np.nan, matrix.astype(float))

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(matrix_masked, cmap="Blues")  # ← use matrix_masked here

tick_labels = [c.replace("_", " ").title() for c in all_cats]
ax.set_xticks(range(len(all_cats)))
ax.set_yticks(range(len(all_cats)))
ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
ax.set_yticklabels(tick_labels, fontsize=10)

for i in range(len(all_cats)):
    for j in range(len(all_cats)):
        if not mask[i][j] and matrix[i][j] > 0:
            ax.text(j, i, str(matrix[i][j]),
                    ha="center", va="center",
                    color="white" if matrix[i][j] > matrix.max()*0.6 else "black",
                    fontsize=9)

ax.set_title("Intersection Heatmap — Workplace AI Harm\n(CQ1=Yes, top 8 categories, excluding geography & species)",
             fontsize=13, fontweight="bold")
plt.colorbar(im, ax=ax, label="Co-occurrence count")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph2_intersection_heatmap.png", dpi=150)
plt.close()
print("  Saved graph2_intersection_heatmap.png")

# ── GRAPH 3: Top 10 pairs bar chart ─────────────────────
print("Building Graph 3 — Top intersection pairs...")

pair_counts = Counter()
for rec in data:
    for subj in rec.get("subjects", []):
        cats = get_cq1_categories(subj)
        for a, b in combinations(cats, 2):
            pair_counts[(a, b)] += 1

top_pairs = pair_counts.most_common(10)
pair_labels = [f"{a.replace('_',' ').title()}\n+ {b.replace('_',' ').title()}"
               for (a, b), _ in top_pairs]
pair_values = [n for _, n in top_pairs]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(pair_labels)), pair_values, color="#2E86C1")
bars[0].set_color("#C0392B")

ax.set_xticks(range(len(pair_labels)))
ax.set_xticklabels(pair_labels, fontsize=9)
ax.set_ylabel("Co-occurrence count", fontsize=11)
ax.set_title("Top 10 Intersectional Identity Pairs in Workplace AI Harm\n(CQ1=Yes, excluding geography & species)",
             fontsize=13, fontweight="bold")

for bar, val in zip(bars, pair_values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            str(val), ha="center", fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph3_top_pairs.png", dpi=150)
plt.close()
print("  Saved graph3_top_pairs.png")


print("\n✅ All graphs saved to data/figures/")
print("Open the figures folder to view them!")