import pandas as pd 

#ToDo: We need to discuss if is necessary do a filter
#Ussualy LLM as Claude can deal with 30 MB data, and the raw json has ~= 6MB
#So if the LLM do not loses itself, a filter me be not necessary

#Here an simple ideia where i just drop SubSubColumns where Marker is Not mentioned
def filter_categories(ai_subjects):
    if not isinstance(ai_subjects, dict):
        return {}

    filtered_subjects = {}

    for subject_key, subject_value in ai_subjects.items():
        categories = subject_value.get("Categories", {})
        
        filtered_categories = {
            cat_key: cat_value
            for cat_key, cat_value in categories.items()
            if isinstance(cat_value, dict) and cat_value.get("Marker") != "Not mentioned"
        }

        if filtered_categories:
            new_subject = subject_value.copy()
            new_subject["Categories"] = filtered_categories
            filtered_subjects[subject_key] = new_subject

    return filtered_subjects


def get_dataset():
    df = pd.read_json('./data/incidents_full_set_27112025_gpt5_1.json')
    df["AI_Subjects"] = df["AI_Subjects"].apply(filter_categories)
    return df


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    
    df = get_dataset()
    print(df.head(5))
    #df.to_csv('data/fitered_dataset.csv')
