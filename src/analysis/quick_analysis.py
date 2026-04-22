import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

# ── Load data ────────────────────────────────────────────
DATA_PATH = Path("../../data/annotations/annotations.json")
OUTPUT_DIR = Path("../../data/figures/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

N = len(data)


def normalize_marker(cat, marker):
    marker = marker.lower().strip()
    cat = cat.lower().replace(" ", "_")
    if cat == "class":
        if marker in [
            "working class",
            "low-income",
            "low income",
            "lower class",
            "poor",
            "poverty",
        ]:
            return "lower class"
        if marker in ["upper class", "wealthy", "affluent", "elite"]:
            return "upper class"
        if marker in ["middle class"]:
            return "middle class"
    return marker


def get_cq1_categories(subject, exclude=["geography", "species"]):
    ids = subject.get("identity_markers", {})
    return sorted(
        [
            c.lower().replace(" ", "_")
            for c, v in ids.items()
            if c.lower().replace(" ", "_") not in exclude
            and isinstance(v, dict)
            and str(v.get("DirectScore", "")).strip().lower() == "yes"
            and str(v.get("AlternateScore", "")).strip().lower() == "no"
        ]
    )


def get_cq1_values(subject, exclude=["geography", "species"]):
    ids = subject.get("identity_markers", {})
    result = {}
    for c, v in ids.items():
        cat = c.lower().replace(" ", "_")
        if cat in exclude:
            continue
        if not isinstance(v, dict):
            continue
        if (
            str(v.get("DirectScore", "")).strip().lower() == "yes"
            and str(v.get("AlternateScore", "")).strip().lower() == "no"
        ):
            marker = normalize_marker(cat, str(v.get("marker", "")))
            result[cat] = marker
    return result


# ── Count per INCIDENT ────────────────────────────────────
incident_category_counts = Counter()
incident_value_counts = Counter()
incident_pair_counts = Counter()
incident_value_pair_counts = Counter()

for rec in data:
    cats_in_incident = set()
    values_in_incident = set()

    for subj in rec.get("subjects", []):
        for cat in get_cq1_categories(subj):
            cats_in_incident.add(cat)
        vals = get_cq1_values(subj)
        for cat, marker in vals.items():
            values_in_incident.add((cat, marker))

    for cat in cats_in_incident:
        incident_category_counts[cat] += 1
    for val in values_in_incident:
        incident_value_counts[val] += 1

    cat_list = sorted(cats_in_incident)
    for a, b in combinations(cat_list, 2):
        incident_pair_counts[(a, b)] += 1

    for subj in rec.get("subjects", []):
        subj_vals = get_cq1_values(subj)
        val_list = sorted(subj_vals.items())
        for (c1, v1), (c2, v2) in combinations(val_list, 2):
            if c1 != c2:
                incident_value_pair_counts[((c1, v1), (c2, v2))] += 1

# ── GRAPH 1: Category prevalence per incident ─────────────
print("Building Graph 1 — Category prevalence...")

top_categories = incident_category_counts.most_common(12)
labels = [c[0].replace("_", " ").title() for c in top_categories]
values = [c[1] for c in top_categories]

labels_rev = labels[::-1]
values_rev = values[::-1]
colors_rev = ["#C0392B" if v == max(values) else "#2E86C1" for v in values_rev]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(labels_rev, values_rev, color=colors_rev)
ax.set_xlabel(
    f"Number of incidents where identity caused harm (CQ1=Yes, N={N})", fontsize=11
)
ax.set_title(
    "Most Common Identity Categories in Workplace AI Harm\n(per incident, CQ1=Yes, excluding geography & species)",
    fontsize=13,
    fontweight="bold",
)
ax.axvline(x=0, color="black", linewidth=0.5)

for bar, val in zip(bars, values_rev):
    ax.text(
        bar.get_width() + 0.3,
        bar.get_y() + bar.get_height() / 2,
        str(val),
        va="center",
        fontsize=10,
    )

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph1_category_prevalence.png", dpi=150)
plt.close()
print("  Saved graph1_category_prevalence.png")

# ── GRAPH 2: Heatmap ──────────────────────────────────────
print("Building Graph 2 — Intersection heatmap...")

all_cats = [c for c, _ in incident_category_counts.most_common(8)]
matrix = np.zeros((len(all_cats), len(all_cats)), dtype=int)

for rec in data:
    cats_in_incident = set()
    for subj in rec.get("subjects", []):
        for cat in get_cq1_categories(subj):
            cats_in_incident.add(cat)
    for i, a in enumerate(all_cats):
        for j, b in enumerate(all_cats):
            if i != j and a in cats_in_incident and b in cats_in_incident:
                matrix[i][j] += 1

mask = np.triu(np.ones_like(matrix, dtype=bool), k=0)
matrix_masked = np.where(mask, np.nan, matrix.astype(float))

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(matrix_masked, cmap="Blues")

tick_labels = [c.replace("_", " ").title() for c in all_cats]
ax.set_xticks(range(len(all_cats)))
ax.set_yticks(range(len(all_cats)))
ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
ax.set_yticklabels(tick_labels, fontsize=10)

for i in range(len(all_cats)):
    for j in range(len(all_cats)):
        if not mask[i][j] and matrix[i][j] > 0:
            ax.text(
                j,
                i,
                str(matrix[i][j]),
                ha="center",
                va="center",
                color="white" if matrix[i][j] > matrix.max() * 0.6 else "black",
                fontsize=9,
            )

ax.set_title(
    f"Intersection Heatmap — Workplace AI Harm\n(per incident, CQ1=Yes, N={N})",
    fontsize=13,
    fontweight="bold",
)
plt.colorbar(im, ax=ax, label="Co-occurrence count")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph2_intersection_heatmap.png", dpi=150)
plt.close()
print("  Saved graph2_intersection_heatmap.png")

# ── GRAPH 3: Top value pairs (specific values not categories)
print("Building Graph 3 — Top value pairs...")

top_pairs = incident_value_pair_counts.most_common(10)
pair_labels = [f"{v1.title()}\n+ {v2.title()}" for ((c1, v1), (c2, v2)), _ in top_pairs]
pair_values = [n for _, n in top_pairs]

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar(range(len(pair_labels)), pair_values, color="#2E86C1")
bars[0].set_color("#C0392B")

ax.set_xticks(range(len(pair_labels)))
ax.set_xticklabels(pair_labels, fontsize=8)
ax.set_ylabel("Co-occurrence count", fontsize=11)
ax.set_title(
    f"Top 10 Intersectional Identity Value Pairs in Workplace AI Harm\n(per subject, CQ1=Yes, N={N})",
    fontsize=13,
    fontweight="bold",
)

for bar, val in zip(bars, pair_values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.1,
        str(val),
        ha="center",
        fontsize=10,
    )

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph3_top_value_pairs.png", dpi=150)
plt.close()
print("  Saved graph3_top_value_pairs.png")

# ── GRAPH 4: Amplification scores ────────────────────────
print("Building Graph 4 — Amplification scores...")

amp_results = []
for ((c1, v1), (c2, v2)), observed in incident_value_pair_counts.items():
    n_v1 = incident_value_counts[(c1, v1)]
    n_v2 = incident_value_counts[(c2, v2)]
    expected = (n_v1 * n_v2) / N
    if expected > 0 and observed >= 3:
        amp_score = observed / expected
        amp_results.append(((c1, v1), (c2, v2), observed, expected, amp_score))

amp_results.sort(key=lambda x: x[4], reverse=True)
top_amp = amp_results[:10]

labels_amp = [
    f"{v1.title()} +\n{v2.title()}" for (c1, v1), (c2, v2), obs, exp, amp in top_amp
]
values_amp = [amp for _, _, obs, exp, amp in top_amp]
obs_counts = [obs for _, _, obs, exp, amp in top_amp]

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar(range(len(labels_amp)), values_amp, color="#2E86C1")
bars[0].set_color("#C0392B")

ax.axhline(y=1.0, color="black", linewidth=1, linestyle="--", label="Expected (1.0x)")
ax.set_xticks(range(len(labels_amp)))
ax.set_xticklabels(labels_amp, fontsize=8)
ax.set_ylabel("Amplification Score (observed / expected)", fontsize=11)
ax.set_title(
    f"Top 10 Amplification Scores in Workplace AI Harm\n(minimum 3 observations, per subject, N={N})",
    fontsize=13,
    fontweight="bold",
)
ax.legend()

for bar, amp, obs in zip(bars, values_amp, obs_counts):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.05,
        f"{amp:.2f}x\n(n={obs})",
        ha="center",
        fontsize=8,
    )

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph4_amplification.png", dpi=150)
plt.close()
print("  Saved graph4_amplification.png")

print(f"\n✅ All graphs saved to data/figures/")
