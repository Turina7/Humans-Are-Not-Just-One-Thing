import json
import os
import textwrap

# File paths
FILE_PATH = "../../data/annotations/annotations.json"
OUTPUT_DIR = "../../data/results/case_studies"

def main():
    # Ensure the sub-directory for case studies exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found at {FILE_PATH}")
        return

    # 1. Collect all valid IDs (only those that actually have DirectScore == "Yes")
    valid_ids = set()
    for incident in data:
        for subject in incident.get("subjects", []):
            markers = subject.get("identity_markers", {})
            for cat, details in markers.items():
                if details.get("DirectScore") == "Yes":
                    valid_ids.add(str(incident.get("incident_id")))
    
    # Sort IDs numerically to make them easy to read
    valid_ids = sorted(list(valid_ids), key=lambda x: int(x) if x.isdigit() else x)

    print("============================================================")
    print(" 📄 CASE STUDY EXPORTER (FOR YOUR ANNEX)")
    print("============================================================\n")

    # Display the available IDs neatly wrapped
    print(f"💡 There are {len(valid_ids)} valid incidents involving direct identity-based harm.")
    print("Here are the exact IDs you can choose from:\n")
    
    wrapped_ids = textwrap.fill(", ".join(valid_ids), width=80)
    print(wrapped_ids)
    print("\n" + "-" * 60 + "\n")

    # Ask the user which incident they want to export
    target_id = input("🔍 Enter the Incident ID you want to export: ").strip()

    # Find the specific incident in the JSON data
    incident = next((item for item in data if str(item.get("incident_id")) == target_id), None)

    if not incident:
        print(f"\n❌ Oops! Incident ID {target_id} was not found in the database. Please pick one from the list above.")
        return

    # Prepare the Markdown filename
    md_filename = os.path.join(OUTPUT_DIR, f"Incident_{target_id}_Case_Study.md")

    # Write the beautifully formatted Markdown file
    with open(md_filename, "w", encoding="utf-8") as md:
        md.write(f"# Case Study: Incident {target_id}\n\n")
        md.write(f"## 📌 {incident.get('incident_title', 'Unknown Title')}\n\n")

        # --- Deployer Info ---
        deployer = incident.get("deployer", {})
        md.write("### 🏢 Deployer Information\n")
        md.write(f"- **Name:** {deployer.get('name', 'Unknown')}\n")
        md.write(f"- **Is Company:** {deployer.get('is_company', 'Unknown')}\n\n")

        # --- Subjects & Harms ---
        md.write("### 👥 Impacted Subjects & Identity Markers\n")
        
        subjects = incident.get("subjects", [])
        if not subjects:
            md.write("- No subjects recorded for this incident.\n")
            
        for idx, subject in enumerate(subjects, 1):
            md.write(f"#### Subject {idx}: {subject.get('name', 'Unknown')}\n\n")

            markers = subject.get("identity_markers", {})
            found_harm = False
            
            for cat, details in markers.items():
                if details.get("DirectScore") == "Yes":
                    found_harm = True
                    clean_cat = cat.replace("_", " ").title()
                    md.write(f"**Category:** {clean_cat}\n")
                    md.write(f"- **Reductive Label:** {details.get('marker', 'N/A')}\n")
                    md.write(f"- **Real Evidence (Source):** *\"{details.get('source', 'N/A')}\"*\n")
                    md.write(f"- **Specific Harm:** {details.get('MarkerHarm', 'N/A')}\n\n")
            
            if not found_harm:
                md.write("- *No direct identity-based harm recorded for this specific subject.*\n\n")

        md.write("---\n")
        md.write("*Generated automatically by the Intersectionality Research Toolkit.*\n")

    print(f"\n✅ BOOM! Case study beautifully formatted and saved at:")
    print(f"📄 {md_filename}")
    print("You can copy-paste this Markdown directly into Word, Notion, or your Thesis Annex.")

if __name__ == "__main__":
    main()