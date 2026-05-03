import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from utils import get_causal_markers, is_valid_intersection

DATA_PATH = Path("../../data/annotations/annotations.json")

with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

N = len(data)
incident_category_counts = Counter()
incident_value_counts = Counter()
incident_pair_counts = Counter()
incident_value_pair_counts = Counter()

# --- For RQ3 & RQ4 ---
explicit = 0
inferred = 0
source_power = defaultdict(lambda: {"Privileged": 0, "Oppressed": 0})

# Main processing loop
for rec in data:
    cats_in_incident = set()
    values_in_incident = set()
    sources = rec.get("sources", [])

    for subj in rec.get("subjects", []):
        markers = get_causal_markers(subj)
        
        # RQ1 & RQ2 Logic
        for cat, val in markers.items():
            cats_in_incident.add(cat)
            values_in_incident.add((cat, val))
            incident_value_counts[(cat, val)] += 1
        
        val_list = sorted(markers.items())
        for v1, v2 in combinations(val_list, 2):
            if is_valid_intersection(v1, v2):
                incident_value_pair_counts[(v1, v2)] += 1

        # RQ3 & RQ4 Logic (Media & Bias)
        ids = subj.get("identity_markers", {})
        for cat, v in ids.items():
            if not isinstance(v, dict): continue
            if str(v.get("DirectScore", "")).strip().lower() == "yes":
                # Simplification
                mt = str(v.get("marker_type", "")).strip().lower()
                if mt == "explicit": explicit += 1
                elif mt == "inferred": inferred += 1
                
                # Power Dynamics
                pp = str(v.get("power_position", "")).strip()
                for source in sources:
                    if pp in ["Privileged", "Oppressed"]:
                        source_power[source][pp] += 1

    for cat in cats_in_incident: incident_category_counts[cat] += 1
    for a, b in combinations(sorted(cats_in_incident), 2): incident_pair_counts[(a, b)] += 1

# --- FINAL CONSOLIDATED OUTPUT ---
print("=" * 60)
print(f"RQ1 — CATEGORY PREVALENCE (N={N})")
print("-" * 60)
for cat, count in incident_category_counts.most_common(10):
    print(f"{cat:<25} {count:>6} {count/N*100:>11.1f}%")

print("\n" + "=" * 60)
print("RQ2 — AMPLIFICATION SCORES (Cleaned)")
print("-" * 60)
amp_results = []
for (v1, v2), observed in incident_value_pair_counts.items():
    expected = (incident_value_counts[v1] * incident_value_counts[v2]) / N
    if expected > 0 and observed >= 3:
        amp_results.append(((v1, v2), observed, expected, observed / expected))
amp_results.sort(key=lambda x: x[3], reverse=True)
for (v1, v2), obs, exp, amp in amp_results[:10]:
    print(f"{v1[1]} + {v2[1]:<40} {amp:>7.2f}x")

print("\n" + "=" * 60)
print("RQ3 — MEDIA SIMPLIFICATION")
print("-" * 60)
sim_score = (inferred / (explicit + inferred)) * 100 if (explicit + inferred) > 0 else 0
print(f"Explicit: {explicit} | Inferred: {inferred}")
print(f"Simplification Score: {sim_score:.1f}%")

print("\n" + "=" * 60)
print("RQ4 — SOURCE COVERAGE (Top 5 Oppressed)")
print("-" * 60)
sorted_sources = sorted(source_power.items(), key=lambda x: x[1]["Oppressed"], reverse=True)
for src, counts in sorted_sources[:5]:
    total = counts["Privileged"] + counts["Oppressed"]
    pct = (counts["Oppressed"] / total * 100) if total > 0 else 0
    print(f"{src:<35} {pct:>5.1f}% Oppressed")