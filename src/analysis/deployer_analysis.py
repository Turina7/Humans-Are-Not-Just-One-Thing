import json
import os
from collections import defaultdict, Counter

# File paths
FILE_PATH = "../../data/annotations/annotations.json"
OUTPUT_DIR = "../../data/results"
# Combine the directory and filename perfectly regardless of the operating system
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "deployer_analysis_results.txt")

def main():
    # Ensure the output directory exists. If it doesn't, create it automatically.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found at {FILE_PATH}")
        return

    # Trackers for our analysis
    top_deployers = Counter()
    category_vs_deployer_type = defaultdict(lambda: {"Company": 0, "Non-Company": 0})
    total_analyzed = 0

    # Process the dataset
    for incident in data:
        deployer_info = incident.get("deployer", {})
        deployer_name = deployer_info.get("name", "Unknown")
        is_company = deployer_info.get("is_company", "Unknown")
        
        # Categorize the deployer type
        if is_company == "Yes":
            dep_type = "Company"
        else:
            dep_type = "Non-Company" # Usually State, Police, Government, or Universities

        # Check who was harmed in this incident
        for subject in incident.get("subjects", []):
            markers = subject.get("identity_markers", {})
            
            for cat_name, cat_data in markers.items():
                if cat_data.get("DirectScore") == "Yes":
                    total_analyzed += 1
                    clean_cat = cat_name.lower().replace("_", " ").strip()
                    
                    # 1. Add to the Hall of Shame
                    if deployer_name != "Unknown":
                        top_deployers[deployer_name] += 1
                    
                    # 2. Add to the Corporate vs State combat tracker
                    category_vs_deployer_type[clean_cat][dep_type] += 1

    # Write the results to a .txt file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        out_file.write("============================================================\n")
        out_file.write(" 🏢 DEPLOYER ANALYSIS: WHO IS BEHIND THE ALGORITHMS?\n")
        out_file.write("============================================================\n\n")

        # --- Print 1: The Hall of Shame (Top 10) ---
        out_file.write("🚨 TOP 10 OFFENDERS (Entities causing the most identity-based harm):\n")
        out_file.write("-" * 60 + "\n")
        for name, count in top_deployers.most_common(10):
            out_file.write(f"  • {count} cases | {name}\n")
        out_file.write("\n\n")

        # --- Print 2: Corporate vs. State Bias by Category ---
        out_file.write("⚖️ WHO DISCRIMINATES MORE? (Corporate vs. State by Category):\n")
        out_file.write("-" * 60 + "\n")
        
        # Sort categories alphabetically
        for category in sorted(category_vs_deployer_type.keys()):
            counts = category_vs_deployer_type[category]
            total_cat = counts["Company"] + counts["Non-Company"]
            
            if total_cat > 0:
                comp_pct = (counts["Company"] / total_cat) * 100
                gov_pct = (counts["Non-Company"] / total_cat) * 100
                
                # Print only categories with a decent amount of cases to avoid noise (e.g., > 4 cases)
                if total_cat > 4:
                    out_file.write(f" 📂 {category.upper()} ({total_cat} total cases)\n")
                    out_file.write(f"    Private Companies : {comp_pct:.1f}% ({counts['Company']} cases)\n")
                    out_file.write(f"    State/Non-Profit  : {gov_pct:.1f}% ({counts['Non-Company']} cases)\n\n")

        out_file.write(f"✅ Analysis complete! Processed {total_analyzed} direct-harm incidents.\n")

    # Short message in the terminal to notify that it has finished successfully
    print(f"✅ Done! The directory '{OUTPUT_DIR}' is ready (or already existed).")
    print(f"📄 Your report has been saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()