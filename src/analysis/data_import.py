import pandas as pd

def filter_causal_categories(ai_subjects):
    """Filters subjects using strict counterfactual logic with error handling."""
    if not isinstance(ai_subjects, dict): return {}
    filtered_subjects = {}

    for sub_id, sub_data in ai_subjects.items():
        categories = sub_data.get("Categories", {})
        cleaned_cats = {}
        
        for cat, details in categories.items():
            if not isinstance(details, dict): continue
            
            # Causal validation from data source
            marker = details.get("Marker", "Not mentioned")
            cq1 = str(details.get("CQ1", "")).strip().lower()
            cq2 = str(details.get("CQ2", "")).strip().lower()
            
            if marker != "Not mentioned" and cq1 == "yes" and cq2 == "no":
                cleaned_cats[cat] = details
        
        if cleaned_cats:
            new_sub = sub_data.copy()
            new_sub["Categories"] = cleaned_cats
            filtered_subjects[sub_id] = new_sub
            
    return filtered_subjects

def get_dataset(path="./data/incidents_full_set_27112025_gpt5_1.json"):
    try:
        df = pd.read_json(path)
        if "AI_Subjects" in df.columns:
            df["AI_Subjects"] = df["AI_Subjects"].apply(filter_causal_categories)
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()