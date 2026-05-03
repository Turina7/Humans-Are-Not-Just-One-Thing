import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import Counter
from itertools import combinations
from utils import get_causal_markers, is_valid_intersection

DATA_PATH = Path("../../data/annotations/annotations.json")
OUTPUT_DIR = Path("../../data/figures/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

N = len(data)

# Data Aggregation
incident_category_counts = Counter()
incident_value_counts = Counter()
incident_value_pair_counts = Counter()

for rec in data:
    cats_in_incident = set()
    for subj in rec.get("subjects", []):
        markers = get_causal_markers(subj)
        for cat in markers.keys(): cats_in_incident.add(cat)
        for cat, val in markers.items(): incident_value_counts[(cat, val)] += 1
        
        # Valid Intersections Only
        for v1, v2 in combinations(sorted(markers.items()), 2):
            if is_valid_intersection(v1, v2):
                incident_value_pair_counts[(v1, v2)] += 1
                
    for cat in cats_in_incident: incident_category_counts[cat] += 1

# --- Generation of Cleaned Graph 4 (Amplification) ---
amp_results = []
for ((c1, v1), (c2, v2)), observed in incident_value_pair_counts.items():
    expected = (incident_value_counts[(c1, v1)] * incident_value_counts[(c2, v2)]) / N
    if expected > 0 and observed >= 3:
        amp_results.append((v1, v2, observed, observed / expected))

amp_results.sort(key=lambda x: x[3], reverse=True)
top_amp = amp_results[:10]

fig, ax = plt.subplots(figsize=(14, 6))
labels = [f"{v1.title()} +\n{v2.title()}" for v1, v2, obs, amp in top_amp]
values = [amp for v1, v2, obs, amp in top_amp]
ax.bar(range(len(labels)), values, color="#2E86C1")
ax.axhline(y=1.0, color="black", linestyle="--", label="Expected baseline")
ax.set_title("RQ2: Top Intersectional Amplification (Filtered Overlaps)", fontweight="bold")
plt.xticks(range(len(labels)), labels, fontsize=8)
plt.savefig(OUTPUT_DIR / "graph4_amplification.png", dpi=150)
plt.close()
print(f"✅ Cleaned graphs saved to {OUTPUT_DIR}")