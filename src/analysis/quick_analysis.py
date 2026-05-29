import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import Counter
from itertools import combinations
from utils import get_causal_markers, is_valid_intersection

# ── Paths ────────────────────────────────────────────────
DATA_PATH = Path("../../data/annotations/annotations.json")
OUTPUT_DIR = Path("../../data/figures/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Style: B&W, minimal, no titles ───────────────────────
# Titles will be added in the report itself, not baked into the figure.
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 15,
    "axes.titlesize": 0,        # titles drawn as empty
    "axes.labelsize": 15,
    "axes.edgecolor": "black",
    "axes.linewidth": 0.8,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

BAR_COLOR = "#1a1a1a"           # near-black, matches reference style
EDGE_COLOR = "black"

# ── Load data ────────────────────────────────────────────
with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

N = len(data)

# ── Aggregate counts ─────────────────────────────────────
# Counts are aggregated PER INCIDENT (not per subject) to match the
# why_harms Formula 4 convention: n_v1, n_v2, and n_v1,v2 all count
# the number of *incidents* in which the value(s) appear, regardless
# of how many subjects within that incident carry them.
incident_category_counts = Counter()
incident_value_counts = Counter()
incident_value_pair_counts = Counter()

for rec in data:
    cats_in_incident = set()
    values_in_incident = set()
    pairs_in_incident = set()

    for subj in rec.get("subjects", []):
        markers = get_causal_markers(subj)
        for cat in markers.keys():
            cats_in_incident.add(cat)
        for cat, val in markers.items():
            values_in_incident.add((cat, val))

        # Collect pairs within a subject; dedup happens at the incident
        # level via the set below so two subjects sharing the same pair
        # don't double-count.
        for v1, v2 in combinations(sorted(markers.items()), 2):
            if is_valid_intersection(v1, v2):
                pairs_in_incident.add((v1, v2))

    for cat in cats_in_incident:
        incident_category_counts[cat] += 1
    for val in values_in_incident:
        incident_value_counts[val] += 1
    for pair in pairs_in_incident:
        incident_value_pair_counts[pair] += 1


# ── GRAPH 1: Category prevalence per incident ────────────
print("Building Graph 1 — Category prevalence...")

top_categories = incident_category_counts.most_common(12)
labels = [c[0].replace("_", " ").title() for c in top_categories]
values = [c[1] for c in top_categories]

# horizontal bars, largest at top
labels_rev = labels[::-1]
values_rev = values[::-1]

fig, ax = plt.subplots(figsize=(12, 6.5))
bars = ax.barh(labels_rev, values_rev, color=BAR_COLOR, edgecolor=EDGE_COLOR)
ax.set_xlabel(f"Number of incidents (CQ1=Yes, N={N})")
ax.axvline(x=0, color="black", linewidth=0.5)

xmax = max(values_rev) if values_rev else 1
# Add a bit more headroom on the right so "64 (22.5%)" labels fit.
ax.set_xlim(0, xmax * 1.18)
for bar, val in zip(bars, values_rev):
    pct = 100 * val / N
    ax.text(
        bar.get_width() + xmax * 0.01,
        bar.get_y() + bar.get_height() / 2,
        f"{val} ({pct:.1f}%)",
        va="center",
        fontsize=14,
    )

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph1_category_prevalence.png", dpi=150)
plt.close()
print("  Saved graph1_category_prevalence.png")


# ── GRAPH 2: Heatmap (kept in colour per request) ────────
print("Building Graph 2 — Intersection heatmap...")

all_cats = [c for c, _ in incident_category_counts.most_common(8)]
matrix = np.zeros((len(all_cats), len(all_cats)), dtype=int)

for rec in data:
    cats_in_incident = set()
    for subj in rec.get("subjects", []):
        markers = get_causal_markers(subj)
        for cat in markers.keys():
            cats_in_incident.add(cat)
    for i, a in enumerate(all_cats):
        for j, b in enumerate(all_cats):
            if i != j and a in cats_in_incident and b in cats_in_incident:
                matrix[i][j] += 1

mask = np.triu(np.ones_like(matrix, dtype=bool), k=0)
matrix_masked = np.where(mask, np.nan, matrix.astype(float))

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(matrix_masked, cmap="Greys")

tick_labels = [c.replace("_", " ").title() for c in all_cats]
ax.set_xticks(range(len(all_cats)))
ax.set_yticks(range(len(all_cats)))
ax.set_xticklabels(tick_labels, rotation=45, ha="right")
ax.set_yticklabels(tick_labels)

for i in range(len(all_cats)):
    for j in range(len(all_cats)):
        if not mask[i][j] and matrix[i][j] > 0:
            ax.text(
                j, i, str(matrix[i][j]),
                ha="center", va="center",
                color="white" if matrix[i][j] > matrix.max() * 0.6 else "black",
                fontsize=14,
            )

cbar = plt.colorbar(im, ax=ax, label="Co-occurrence count")
cbar.ax.tick_params(labelsize=13)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph2_intersection_heatmap.png", dpi=150)
plt.close()
print("  Saved graph2_intersection_heatmap.png")


# ── GRAPH 3: Top intersectional value pairs ──────────────
# Already redundancy-filtered above via is_valid_intersection.
# Horizontal bars so the long pair labels stay legible.
print("Building Graph 3 — Top value pairs...")

top_pairs = incident_value_pair_counts.most_common(8)
pair_labels = [
    f"{v1.title()} + {v2.title()}"
    for ((c1, v1), (c2, v2)), _ in top_pairs
]
pair_values = [n for _, n in top_pairs]

# largest at top
pair_labels_rev = pair_labels[::-1]
pair_values_rev = pair_values[::-1]

fig, ax = plt.subplots(figsize=(11, 6.5))
bars = ax.barh(
    pair_labels_rev, pair_values_rev,
    color=BAR_COLOR, edgecolor=EDGE_COLOR,
)
ax.set_xlabel("Co-occurrence count")
ax.axvline(x=0, color="black", linewidth=0.5)

xmax = max(pair_values_rev) if pair_values_rev else 1
ax.set_xlim(0, xmax * 1.10)
for bar, val in zip(bars, pair_values_rev):
    ax.text(
        bar.get_width() + xmax * 0.01,
        bar.get_y() + bar.get_height() / 2,
        str(val),
        va="center",
        fontsize=14,
    )

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph3_top_value_pairs.png", dpi=150)
plt.close()
print("  Saved graph3_top_value_pairs.png")


# ── GRAPH 4: Amplification scores ────────────────────────
# Methodology follows why_harms Formula 4:
#   amplification = n_v1,v2 / E[n_v1,v2],  where  E = n_v1 * n_v2 / N
# All counts are at the INCIDENT level (set up above).
#
# We exclude pairs containing certain noisy LLM-tagged values that
# inspection showed are over-applied (e.g., "graduate from elite
# university" was tagged on any licensed professional regardless of
# whether the source mentioned a specific elite institution).
print("Building Graph 4 — Amplification scores...")

EXCLUDE_VALUES = {
    ("education", "graduate from elite university"),
}
MIN_OBSERVED = 2  # match the threshold used in earlier runs

amp_results = []
for ((c1, v1), (c2, v2)), observed in incident_value_pair_counts.items():
    if (c1, v1) in EXCLUDE_VALUES or (c2, v2) in EXCLUDE_VALUES:
        continue
    n_v1 = incident_value_counts[(c1, v1)]
    n_v2 = incident_value_counts[(c2, v2)]
    expected = (n_v1 * n_v2) / N
    if expected > 0 and observed >= MIN_OBSERVED:
        amp_score = observed / expected
        amp_results.append(((c1, v1), (c2, v2), observed, expected, amp_score))

amp_results.sort(key=lambda x: x[4], reverse=True)
top_amp = amp_results[:8]

labels_amp = [
    f"{v1.title()} + {v2.title()}"
    for (c1, v1), (c2, v2), obs, exp, amp in top_amp
]
values_amp = [amp for _, _, obs, exp, amp in top_amp]
obs_counts = [obs for _, _, obs, exp, amp in top_amp]

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(
    range(len(labels_amp)), values_amp,
    color=BAR_COLOR, edgecolor=EDGE_COLOR,
)

ax.axhline(y=1.0, color="black", linewidth=1, linestyle="--")
ax.set_xticks(range(len(labels_amp)))
ax.set_xticklabels(labels_amp, fontsize=14, rotation=30, ha="right")
ax.set_ylabel("Amplification (observed / expected)")

ymax = max(values_amp) if values_amp else 1
ax.set_ylim(0, ymax * 1.18)
for bar, amp, obs in zip(bars, values_amp, obs_counts):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + ymax * 0.02,
        f"{amp:.2f}×\n(n={obs})",
        ha="center",
        fontsize=13,
    )

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph4_amplification.png", dpi=150)
plt.close()
print("  Saved graph4_amplification.png")

# ── NOTE: 3-way amplification deliberately not produced ─────
# A 3-way amplification chart (e.g., lower class + female + single
# parent) was considered but the data is too sparse for it. With
# N=285 incidents, every unique triple appears in exactly 1 incident,
# which means no statistically meaningful amplification can be
# computed. The reference paper (why_harms) reports 3-way patterns
# with N=711, where triples can occur multiple times. To enable a
# 3-way chart in this project we'd need either a substantially
# larger incident set or a re-run with a more permissive rubric.
# Discuss in the report's limitations section.

# ── GRAPH 5: Media Erasure — Explicit/Inferred × Oppressed/Privileged ──
# A pie chart (or donut) showing the four segments:
#   • Explicit   + Oppressed
#   • Explicit   + Privileged
#   • Inferred   + Oppressed
#   • Inferred   + Privileged
# Counts operate at the MARKER level (one entry per identity marker per
# subject), not per incident, to match the paper's Table 6 / Table 7
# methodology (828 total markers, E = 48.8%).
print("Building Graph 5 — Media Erasure pie (Explicit/Inferred × Power)...")

seg_counts = {
    ("Explicit",  "Oppressed"):  0,
    ("Explicit",  "Privileged"): 0,
    ("Inferred",  "Oppressed"):  0,
    ("Inferred",  "Privileged"): 0,
}

for rec in data:
    for subj in rec.get("subjects", []):
        for cat, marker_data in subj.get("identity_markers", {}).items():
            # Support both dict-of-dicts and flat-dict schemas.
            if isinstance(marker_data, dict):
                mtype  = marker_data.get("marker_type", "")
                power  = marker_data.get("power_position", "")
                # Retain only markers that passed the causal gate.
                direct = marker_data.get("DirectScore", "No")
                alt    = marker_data.get("AlternateScore", "Yes")
                if direct != "Yes" or alt != "No":
                    continue
                key = (mtype, power)
                if key in seg_counts:
                    seg_counts[key] += 1

# ── Greyscale palette ── four tones from near-black to light grey
GREY_DARK    = "#1a1a1a"   # Inferred  + Oppressed  (most hidden, most harmed)
GREY_MID1    = "#555555"   # Explicit  + Oppressed
GREY_MID2    = "#999999"   # Inferred  + Privileged
GREY_LIGHT   = "#cccccc"   # Explicit  + Privileged

seg_labels = [
    "Inferred\nOppressed",
    "Inferred\nPrivileged",
    "Explicit\nOppressed",
    "Explicit\nPrivileged",
]
seg_keys = [
    ("Inferred",  "Oppressed"),
    ("Inferred",  "Privileged"),
    ("Explicit",  "Oppressed"),
    ("Explicit",  "Privileged"),
]
seg_colors = [GREY_DARK, GREY_MID1, GREY_MID2, GREY_LIGHT]
seg_values = [seg_counts[k] for k in seg_keys]
seg_total   = sum(seg_values)

# Slight explode on the two "Inferred" slices to highlight the erasure gap.
explode = [0.06, 0, 0.06, 0]

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    seg_values,
    labels=seg_labels,
    colors=seg_colors,
    explode=explode,
    autopct=lambda p: f"{p:.1f}%\n(n={int(round(p * seg_total / 100))})",
    pctdistance=0.68,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=2),
    textprops=dict(fontsize=14),
)

# Make percentage labels inside dark wedges white for legibility.
for at, color in zip(autotexts, seg_colors):
    lum = int(color[1:3], 16)  # red channel ≈ luminance for grey tones
    at.set_color("white" if lum < 100 else "black")
    at.set_fontsize(13)

for t in texts:
    t.set_fontsize(14)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "graph5_media_erasure_pie.png", dpi=150)
plt.close()
print("  Saved graph5_media_erasure_pie.png")


print(f"\n✅ All graphs saved to {OUTPUT_DIR}")
