import json
from collections import defaultdict
import os

# File paths
FILE_PATH = "../../data/annotations/annotations.json"
OUTPUT_DIR = "../../data/results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "qualitative_zoom_results.txt")

def main():
    # Ensure the output directory exists. If it doesn't, create it automatically.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found at {FILE_PATH}")
        return

    grouped_cases = defaultdict(list)
    total_cases = 0

    # 1. Collect, clean, and group the data
    for incident in data:
        for subject in incident.get("subjects", []):
            markers = subject.get("identity_markers", {})
            
            for category_name, category_data in markers.items():
                if category_data.get("DirectScore") == "Yes":
                    total_cases += 1
                    
                    # THE TRICK: Normalize the name (lowercase, replace underscores with spaces)
                    clean_category = category_name.lower().replace("_", " ").strip()
                    
                    grouped_cases[clean_category].append({
                        "id": incident.get("incident_id"),
                        "title": incident.get("incident_title"),
                        "subject": subject.get("name", "Unknown"),
                        "label": category_data.get("marker"),
                        "source": category_data.get("source"),
                        "harm": category_data.get("MarkerHarm")
                    })

    # 2. Write everything to a .txt file instead of printing to the terminal
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        out_file.write("============================================================\n")
        out_file.write(" 🔍 QUALITATIVE ZOOM: UNPACKING ALL IDENTITY CATEGORIES\n")
        out_file.write("============================================================\n")

        for category in sorted(grouped_cases.keys()):
            cases = grouped_cases[category]
            out_file.write(f"\n" + "=" * 60 + "\n")
            out_file.write(f" 📂 CATEGORY: {category.upper()} ({len(cases)} cases found)\n")
            out_file.write("=" * 60 + "\n")
            
            for item in cases:
                out_file.write(f"🔴 Incident ID: {item['id']} | {item['title']}\n")
                out_file.write(f"   Subject: {item['subject']}\n")
                out_file.write(f"   Reductive Label: {item['label']}\n")
                out_file.write(f"   --\n")
                out_file.write(f"   Real Evidence: {item['source']}\n")
                out_file.write(f"   Specific Harm: {item['harm']}\n")
                out_file.write("-" * 60 + "\n")

        out_file.write(f"\n✅ Successfully processed {total_cases} direct-harm identity markers across {len(grouped_cases)} categories.\n")

    # Short message in the terminal to notify that it has finished
    print(f"✅ Done! The directory '{OUTPUT_DIR}' is ready (or already existed).")
    print(f"📄 Your report has been saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()