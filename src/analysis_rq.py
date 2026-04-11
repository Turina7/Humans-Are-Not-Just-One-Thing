import json
import numpy as np
from pathlib import Path
from collections import Counter
from itertools import combinations

DATA_PATH = Path("../data/annotations_v2.json")

with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

def get_cq1_categories(subject, exclude=["geography", "species"]):
    ids = subject.get("identity_markers", {})
    return sorted([
        c.lower().replace(" ", "_") for c, v in ids.items()
        if c.lower().replace(" ", "_") not in exclude
        and str((v or {}).get("DirectScore", "")).strip().lower() == "yes"
        and str((v or {}).get("AlternateScore", "")).strip().lower() == "no"
    ])

def get_markers(subject, exclude=["geography", "species"]):
    ids = subject.get("identity_markers", {})
    return {
        c.lower().replace(" ", "_"): v
        for c, v in ids.items()
        if c.lower().replace(" ", "_") not in exclude
    }

# ── Count incidents (not subjects) per category ──────────
# This matches the reference paper's formula exactly
N = len(data)  # total incidents

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
            marker = get_markers(subj).get(cat, {})
            val = (marker or {}).get("marker", "")
            if val:
                values_in_incident.add((cat, val.lower().strip()))

    # Count each category once per incident
    for cat in cats_in_incident:
        incident_category_counts[cat] += 1

    # Count each value once per incident
    for val in values_in_incident:
        incident_value_counts[val] += 1

    # Count pairs once per incident
    cat_list = sorted(cats_in_incident)
    for a, b in combinations(cat_list, 2):
        incident_pair_counts[(a, b)] += 1

    val_list = sorted(values_in_incident)
    for v1, v2 in combinations(val_list, 2):
        incident_value_pair_counts[(v1, v2)] += 1

print("=" * 60)
print(f"RQ1 — CATEGORY PREVALENCE (N={N} incidents)")
print("=" * 60)
print(f"{'Category':<25} {'Count':>6} {'Prevalence':>12}")
print("-" * 45)
for cat, count in incident_category_counts.most_common(15):
    prevalence = count / N * 100
    print(f"{cat:<25} {count:>6} {prevalence:>11.1f}%")

print()
print("=" * 60)
print("RQ1 — TOP IDENTITY VALUES")
print("=" * 60)
print(f"{'Category + Value':<40} {'Count':>6} {'Prevalence':>12}")
print("-" * 60)
for (cat, val), count in incident_value_counts.most_common(20):
    prevalence = count / N * 100
    print(f"{cat + ' = ' + val:<40} {count:>6} {prevalence:>11.1f}%")

print()
print("=" * 60)
print("RQ2 — INTERSECTIONAL SCORES (top category pairs)")
print("=" * 60)
print(f"{'Pair':<40} {'Count':>6} {'Int. Score':>12}")
print("-" * 60)
for (a, b), count in incident_pair_counts.most_common(15):
    score = count / N * 100
    print(f"{a + ' + ' + b:<40} {count:>6} {score:>11.1f}%")

print()
print("=" * 60)
print("RQ2 — AMPLIFICATION SCORES (top value pairs)")
print("=" * 60)
print(f"{'Value pair':<50} {'Obs':>5} {'Exp':>7} {'Amp':>7}")
print("-" * 70)

amp_results = []
for (v1, v2), observed in incident_value_pair_counts.items():
    n_v1 = incident_value_counts[v1]
    n_v2 = incident_value_counts[v2]
    expected = (n_v1 * n_v2) / N
    if expected > 0 and observed >= 3:
        amp_score = observed / expected
        amp_results.append(((v1, v2), observed, expected, amp_score))

amp_results.sort(key=lambda x: x[3], reverse=True)

for (v1, v2), obs, exp, amp in amp_results[:20]:
    label = f"{v1[0]}={v1[1]} + {v2[0]}={v2[1]}"
    print(f"{label:<50} {obs:>5} {exp:>7.1f} {amp:>7.2f}x")

print()
print("=" * 60)
print("RQ3a — SIMPLIFICATION SCORE (Explicit vs Inferred)")
print("=" * 60)
explicit = 0
inferred = 0
for rec in data:
    for subj in rec.get("subjects", []):
        ids = subj.get("identity_markers", {})
        for cat, v in ids.items():
            if str((v or {}).get("DirectScore", "")).strip().lower() == "yes":
                mt = str((v or {}).get("marker_type", "")).strip().lower()
                if mt == "explicit":
                    explicit += 1
                elif mt == "inferred":
                    inferred += 1

total_markers = explicit + inferred
simplification = inferred / total_markers * 100 if total_markers > 0 else 0
print(f"Explicit markers:  {explicit}")
print(f"Inferred markers:  {inferred}")
print(f"Simplification score: {simplification:.1f}%")
print(f"→ {simplification:.1f}% of harms were hidden in news reports")

print()
print("=" * 60)
print("RQ3b — MEDIA COVERAGE (Privileged vs Oppressed)")
print("=" * 60)
from collections import defaultdict
source_power = defaultdict(lambda: {"Privileged": 0, "Oppressed": 0})

for rec in data:
    sources = rec.get("sources", [])
    for subj in rec.get("subjects", []):
        ids = subj.get("identity_markers", {})
        for cat, v in ids.items():
            if str((v or {}).get("DirectScore", "")).strip().lower() == "yes":
                pp = str((v or {}).get("power_position", "")).strip()
                for source in sources:
                    if pp in ["Privileged", "Oppressed"]:
                        source_power[source][pp] += 1

privileged_total = sum(v["Privileged"] for v in source_power.values())
oppressed_total = sum(v["Oppressed"] for v in source_power.values())
total_power = privileged_total + oppressed_total

print(f"Total Privileged markers in news: {privileged_total} ({privileged_total/total_power*100:.1f}%)")
print(f"Total Oppressed markers in news:  {oppressed_total} ({oppressed_total/total_power*100:.1f}%)")
print()
print("Top sources by Oppressed coverage:")
sorted_sources = sorted(source_power.items(), 
                        key=lambda x: x[1]["Oppressed"], reverse=True)
for source, counts in sorted_sources[:10]:
    total = counts["Privileged"] + counts["Oppressed"]
    if total > 0:
        opp_pct = counts["Oppressed"] / total * 100
        print(f"  {source:<35} Oppressed: {counts['Oppressed']:>4} ({opp_pct:.0f}%)")