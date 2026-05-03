import json
from pathlib import Path

# Path to your current JSON file
DATA_PATH = Path("../data/annotations_v2.json")

print("Opening the old JSON file...")
try:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"❌ Error: File not found at {DATA_PATH}")
    exit()

changes_made = 0

# Loop through all data to rename the keys
for incident in data:
    for subject in incident.get("subjects", []):
        markers = subject.get("identity_markers", {})
        for cat, details in markers.items():
            # Replace DirectScore with CQ1
            if "DirectScore" in details:
                details["CQ1"] = details.pop("DirectScore")
                changes_made += 1
            # Replace AlternateScore with CQ2
            if "AlternateScore" in details:
                details["CQ2"] = details.pop("AlternateScore")

print(f"Updated {changes_made} identity categories.")
print("Saving the new format...")

# Save the file overwriting it with the new keys
with DATA_PATH.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Migration completed successfully! Keys are now CQ1 and CQ2.")