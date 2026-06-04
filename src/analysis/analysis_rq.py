import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from utils import get_causal_markers, is_valid_intersection, normalize_marker

DATA_PATH = Path("../../data/annotations/annotations.json")

with DATA_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

N = len(data)

# ── Counters ──────────────────────────────────────────────────────────────────
incident_category_counts   = Counter()
incident_value_counts      = Counter()
incident_pair_counts       = Counter()
incident_value_pair_counts = Counter()

# RQ3 — marker type tallies, per-category breakdowns
explicit_markers   = Counter()   # (cat, val) → n explicit
inferred_markers   = Counter()   # (cat, val) → n inferred
explicit = inferred = 0

# RQ4 — source power dynamics
source_power = defaultdict(lambda: {"Privileged": 0, "Oppressed": 0})

# ── Main loop ─────────────────────────────────────────────────────────────────
for rec in data:
    cats_in_incident   = set()
    values_in_incident = set()
    sources = rec.get("sources", [])

    for subj in rec.get("subjects", []):
        markers = get_causal_markers(subj)

        # RQ1 & RQ2 — category / value prevalence
        for cat, val in markers.items():
            cats_in_incident.add(cat)
            values_in_incident.add((cat, val))
            incident_value_counts[(cat, val)] += 1

        val_list = sorted(markers.items())
        for v1, v2 in combinations(val_list, 2):
            if is_valid_intersection(v1, v2):
                incident_value_pair_counts[(v1, v2)] += 1

        # RQ3 — explicit vs inferred breakdown
        ids = subj.get("identity_markers", {})
        for cat, v in ids.items():
            if not isinstance(v, dict):
                continue
            if str(v.get("DirectScore", "")).strip().lower() != "yes":
                continue

            val = normalize_marker(cat, str(v.get("marker", cat)).strip())
            mt  = str(v.get("marker_type", "")).strip().lower()
            if mt == "explicit":
                explicit += 1
                explicit_markers[(cat, val)] += 1
            elif mt == "inferred":
                inferred += 1
                inferred_markers[(cat, val)] += 1

            # RQ4 — power dynamics per source
            pp = str(v.get("power_position", "")).strip()
            if pp in ("Privileged", "Oppressed"):
                for source in sources:
                    source_power[source][pp] += 1

    for cat in cats_in_incident:
        incident_category_counts[cat] += 1
    for a, b in combinations(sorted(cats_in_incident), 2):
        incident_pair_counts[(a, b)] += 1

# ── Helpers ───────────────────────────────────────────────────────────────────
W1, W2, W3, W4 = 28, 8, 8, 10   # column widths for pretty-printing

def rule(char="─", width=64):
    return char * width

def col_header(*args):
    return "  ".join(str(a) for a in args)

# ── RQ1 — Category prevalence (all categories) ────────────────────────────────
print(rule("═"))
print(f"RQ1 TABLE A — ALL IDENTITY CATEGORIES  (N={N})")
print(rule())
print(f"{'Category':<{W1}} {'N':>{W2}} {'%':>{W3}}")
print(rule("-"))
for cat, count in incident_category_counts.most_common():
    print(f"{cat:<{W1}} {count:>{W2}} {count/N*100:>{W3}.1f}%")

# ── RQ1 — Top-20 specific identity values ────────────────────────────────────
print()
print(rule("═"))
print(f"RQ1 TABLE B — TOP-20 SPECIFIC IDENTITY VALUES  (N={N})")
print(rule())
print(f"{'Category = Value':<{W1}} {'N':>{W2}} {'%':>{W3}}")
print(rule("-"))
for (cat, val), count in incident_value_counts.most_common(20):
    label = f"{cat} = {val}"
    print(f"{label:<{W1}} {count:>{W2}} {count/N*100:>{W3}.1f}%")

# ── RQ2 — Top-15 category co-occurrence pairs ─────────────────────────────────
print()
print(rule("═"))
print(f"RQ2 TABLE A — TOP-15 CATEGORY CO-OCCURRENCE PAIRS  (N={N})")
print(rule())
print(f"{'Pair':<{W1}} {'N':>{W2}} {'%':>{W3}}")
print(rule("-"))
for (a, b), count in incident_pair_counts.most_common(15):
    label = f"{a} + {b}"
    print(f"{label:<{W1}} {count:>{W2}} {count/N*100:>{W3}.1f}%")

# ── RQ2 — Value-pair amplification scores (top 10 + bottom 10) ──────────────
print()
print(rule("═"))
print("RQ2 TABLE B — VALUE-PAIR AMPLIFICATION SCORES")
print("Top 10 and Bottom 10")
print(rule())
print(f"{'Value Pair':<{W1}} {'O':>{W2}} {'E':>{W2}} {'Amp':>{W4}}")
print(rule("-"))

amp_results = []
for (v1, v2), observed in incident_value_pair_counts.items():
    expected = (incident_value_counts[v1] * incident_value_counts[v2]) / N
    if expected > 0 and observed > 1:
        amp_results.append(((v1, v2), observed, expected, observed / expected))

# Sort by amplification score
amp_results.sort(key=lambda x: x[3], reverse=True)

top_10 = amp_results[:10]
bottom_10 = amp_results[-10:]

print("TOP 10")
print(rule("-"))
for (v1, v2), obs, exp, amp in top_10:
    label = f"{v1[1]} + {v2[1]}"
    dagger = "†" if obs < 3 else " "
    print(f"{label:<{W1}} {obs:>{W2}} {exp:>{W2}.2f} {amp:>{W4}.1f}×{dagger}")

print()
print("BOTTOM 10")
print(rule("-"))
for (v1, v2), obs, exp, amp in bottom_10:
    label = f"{v1[1]} + {v2[1]}"
    dagger = "†" if obs < 3 else " "
    print(f"{label:<{W1}} {obs:>{W2}} {exp:>{W2}.2f} {amp:>{W4}.1f}×{dagger}")

print("  † n<3 — statistically unstable")

# ── RQ3 — Explicit vs Inferred summary ───────────────────────────────────────
total_markers = explicit + inferred
sim_score     = (inferred / total_markers * 100) if total_markers > 0 else 0

print()
print(rule("═"))
print("RQ3 — MEDIA REPRESENTATION SUMMARY")
print(rule())
print(f"  Total markers : {total_markers}")
print(f"  Explicit      : {explicit}  ({explicit/total_markers*100:.1f}%)" if total_markers else "  Explicit: 0")
print(f"  Inferred      : {inferred}  ({inferred/total_markers*100:.1f}%)" if total_markers else "  Inferred: 0")
print(f"  Simplification score (% inferred): {sim_score:.1f}%")

# ── RQ3 TABLE A — Top-15 explicit markers ────────────────────────────────────
print()
print(rule("═"))
print("RQ3 TABLE A — TOP-15 EXPLICIT MARKERS  (directly named in press)")
print(rule())
print(f"{'Marker':<{W1}} {'N':>{W2}}")
print(rule("-"))
for (cat, val), n in explicit_markers.most_common(15):
    print(f"{cat} = {val:<{W1 - len(cat) - 3}} {n:>{W2}}")

# ── RQ3 TABLE B — Top-15 inferred markers ────────────────────────────────────
print()
print(rule("═"))
print("RQ3 TABLE B — TOP-15 INFERRED MARKERS  (causally present, not reported)")
print(rule())
print(f"{'Marker':<{W1}} {'N':>{W2}}")
print(rule("-"))
for (cat, val), n in inferred_markers.most_common(15):
    print(f"{cat} = {val:<{W1 - len(cat) - 3}} {n:>{W2}}")

# ── RQ3 TABLE C — Outlet oppressed-group coverage ────────────────────────────
print()
print(rule("═"))
print("RQ3 TABLE C — OPPRESSED-GROUP COVERAGE PER OUTLET")
print(rule())
print(f"{'Outlet':<35} {'Oppressed':>{W2}} {'%':>{W3}}")
print(rule("-"))

total_opp = sum(v["Oppressed"] for v in source_power.values())
total_all = sum(v["Privileged"] + v["Oppressed"] for v in source_power.values())
overall_pct = (total_opp / total_all * 100) if total_all else 0

sorted_sources = sorted(
    source_power.items(),
    key=lambda x: x[1]["Oppressed"],
    reverse=True,
)
for src, counts in sorted_sources:
    total = counts["Privileged"] + counts["Oppressed"]
    pct   = (counts["Oppressed"] / total * 100) if total else 0
    print(f"{src:<35} {counts['Oppressed']:>{W2}} {pct:>{W3}.0f}%")

print(rule("-"))
print(f"{'OVERALL':<35} {total_opp:>{W2}} {overall_pct:>{W3}.1f}%")

# ── RQ4 — Top-5 sources by oppressed coverage ────────────────────────────────
print()
print(rule("═"))
print("RQ4 — TOP-5 SOURCES BY OPPRESSED COVERAGE (% of total markers)")
print(rule())
print(f"{'Source':<35} {'Opp%':>{W3}}")
print(rule("-"))
for src, counts in sorted_sources[:5]:
    total = counts["Privileged"] + counts["Oppressed"]
    pct   = (counts["Oppressed"] / total * 100) if total else 0
    print(f"{src:<35} {pct:>{W3}.1f}% Oppressed")
