from google import genai
import csv
import json
import os
import time
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Settings ─────────────────────────────────────────────
INPUT_REPORTS = "../data/workplace_reports.csv"
INPUT_INCIDENTS = "../data/workplace_incidents.csv"
OUTPUT_FILE = "../data/annotations_v2.json"
PROGRESS_FILE = "../data/progress_v2.json"
# ─────────────────────────────────────────────────────────

IDENTITY_CATEGORIES = """
1.  Race             - e.g., White (Privileged), Black (Oppressed)
2.  Gender           - e.g., Male (P), Female (O)
3.  Gender Identity  - e.g., Cisgender (P), Trans (O)
4.  Class             - e.g., Upper Class (P), Working Class (O)
5.  Sexuality        - e.g., Heterosexual (P), Gay (O)
6.  Nationality      - e.g., German (P), Syrian (O)
7.  Ability          - e.g., Able-bodied (P), Visually Impaired (O)
8.  Gender Expression- e.g., Masculine (P), Gender Deviant (O)
9.  Heritage         - e.g., European (P), Non-European (O)
10. Age              - e.g., Young Adult (P), Child/Old (O)
11. Appearance       - e.g., Attractive (P), Unattractive (O)
12. Language         - e.g., Anglophone (P), English as Second Language (O)
13. Skin Tone        - e.g., Light (P), Dark (O)
14. Religion         - e.g., Christianity (P), Islam (O)
15. Reproductive Status - e.g., Fertile (P), Infertile (O)
16. Body Size        - e.g., Thin (P), Fat (O)
17. Education        - e.g., Highly Educated (P), No Formal Education (O)
18. Immigration Status - e.g., Citizen (P), Undocumented (O)
19. Geography        - e.g., Urban (P), Rural (O)
20. Indigeneity      - e.g., Settler (P), First Nations (O)
21. Family Status    - e.g., Married (P), Single Parent (O)
22. Caste            - e.g., Brahmin (P), Dalit (O)
23. Political Identity - e.g., Mainstream (P), Dissident (O)
24. Health Status    - e.g., Healthy (P), Chronically Ill (O)
25. Neurodiversity   - e.g., Neurotypical (P), Autistic (O)
"""

def build_prompt(incident_id, incident_title, incident_description, reports_text):
    return f"""You are an expert AI Incident Analyst. Your core expertise is the application of Kimberle Crenshaw's intersectionality theory to analyze AI incident reports.
You are precise, context-sensitive, and reason causally and structurally.

INCIDENT ID: {incident_id}
INCIDENT TITLE: {incident_title}
INCIDENT DESCRIPTION: {incident_description}

REPORTS:
{reports_text}

YOUR TASKS:

TASK 1 - Identify harmed subjects:
Extract every living entity (person, group, society) harmed by the AI system.

TASK 2 - For each subject, extract identity markers from these 25 categories:
{IDENTITY_CATEGORIES}

For each marker found, apply exactly these two counterfactual questions:
CQ1: Did this incident happen because the AI Subject was [identity value]?
CQ2: Would this incident still have happened if the AI Subject was not [identity value]?

TASK 3 - Assess deployer:
Identify the organization deploying the AI system.

Return ONLY valid JSON in this exact structure:

{{
  "incident_id": "{incident_id}",
  "incident_title": "{incident_title}",
  "deployer": {{
    "is_company": "Yes or No",
    "name": "company name or Unknown"
  }},
  "sources": [],
  "subjects": [
    {{
      "name": "exact name or descriptor from text",
      "type": "Individual / Group of persons / Society",
      "identity_markers": {{
        "category_name": {{
          "marker": "exact value",
          "marker_type": "Explicit or Inferred",
          "power_position": "Privileged or Oppressed",
          "source": "reasoning or quote",
          "CQ1": "Yes or No",
          "CQ2": "Yes or No",
          "reasoning": "backward reasoning from harm to system design failure",
          "MarkerHarm": "Must follow this template: Because of [this identity], the subject was [harmful outcome]."
        }}
      }}
    }}
  ]
}}

CRITICAL RULES:
- CQ1=Yes means: Did this incident happen because the AI Subject was [identity value]? (Answer: Yes)
- CQ2=No means: Would this incident still have happened if the AI Subject was not [identity value]? (Answer: No)
- MarkerHarm MUST follow the template: "Because of [identity], the subject was [harmful outcome]."
- Example: "Because of being Black, the subject was wrongfully arrested due to facial recognition failure."
- Return ONLY JSON.
"""

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return set(json.load(f))
    return set()

def save_progress(done_ids):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(list(done_ids), f)

def load_results():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_results(results):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def get_row_value(row, *possible_keys):
    normalized = {(k or "").strip().lower().lstrip("\ufeff"): v for k, v in row.items()}
    for key in possible_keys:
        value = normalized.get(key.strip().lower())
        if value is not None: return value
    raise KeyError(possible_keys[0])

def read_csv_rows(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except: continue
    return []

def main():
    incidents = {get_row_value(r, "incident_id"): r for r in read_csv_rows(INPUT_INCIDENTS)}
    incident_reports = defaultdict(list)
    incident_sources = defaultdict(set)
    for row in read_csv_rows(INPUT_REPORTS):
        iid = get_row_value(row, "incident_id")
        incident_reports[iid].append(get_row_value(row, "text")[:1500])
        src = get_row_value(row, "source_domain")
        if src: incident_sources[iid].add(src)

    done_ids = load_progress()
    results = load_results()

    for i, (iid, reports) in enumerate(incident_reports.items()):
        if iid in done_ids: continue
        info = incidents.get(iid, {})
        title = info.get('title', 'Unknown')
        prompt = build_prompt(iid, title, info.get('description',''), "\n\n".join(reports)[:6000])

        try:
            print(f"[{i+1}] Processing Incident {iid}...")
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            raw = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            parsed = json.loads(raw)
            parsed['sources'] = list(incident_sources.get(iid, []))
            results.append(parsed)
            done_ids.add(iid)
            save_results(results)
            save_progress(done_ids)
            time.sleep(3)
        except Exception as e:
            print(f"Error {iid}: {e}")

if __name__ == "__main__":
    main()