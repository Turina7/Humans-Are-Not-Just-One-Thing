import pandas as pd


def filter_causal_categories(ai_subjects):
    """
    Filters AI subjects based on strict causal assessment (Why Harms methodology).
    A category is only retained if:
    1. Marker is NOT 'Not mentioned'
    2. CQ1 (Direct Cause) == 'Yes'
    3. CQ2 (Counterfactual) == 'No'
    """
    if not isinstance(ai_subjects, dict):
        return {}

    filtered_subjects = {}

    for subject_key, subject_value in ai_subjects.items():
        categories = subject_value.get("Categories", {})
        filtered_categories = {}

        for cat_key, cat_value in categories.items():
            if not isinstance(cat_value, dict):
                continue

            marker = cat_value.get("Marker", "Not mentioned")
            # Convertim a lowercase i traiem espais per evitar errors de format de l'LLM
            cq1 = str(cat_value.get("CQ1", "")).strip().lower()
            cq2 = str(cat_value.get("CQ2", "")).strip().lower()

            if marker != "Not mentioned" and cq1 == "yes" and cq2 == "no":
                filtered_categories[cat_key] = cat_value

        if filtered_categories:
            new_subject = subject_value.copy()
            new_subject["Categories"] = filtered_categories
            filtered_subjects[subject_key] = new_subject

    return filtered_subjects


def get_dataset():
    df = pd.read_json("./data/incidents_full_set_27112025_gpt5_1.json")
    df["AI_Subjects"] = df["AI_Subjects"].apply(filter_causal_categories)
    return df


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)

    df = get_dataset()
    print(df.head(5))
