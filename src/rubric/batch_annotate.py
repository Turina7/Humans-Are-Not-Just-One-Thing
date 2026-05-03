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
INPUT_REPORTS = "../../data/workplace_reports.csv"
INPUT_INCIDENTS = "../../data/workplace_incidents.csv"
OUTPUT_FILE = "../../data/annotations/annotations.json"
PROGRESS_FILE = "../../data/progress/progress.json"
# ─────────────────────────────────────────────────────────

IDENTITY_CATEGORIES = """
1.  Race               - Use ONLY: "People of Color", "White"
2.  Gender             - Use ONLY: "Male", "Female", "other"
3.  Gender Identity    - Use ONLY: "Cisgender", "Transgender", "Non-binary"
4.  Class              - Use ONLY: "Upper Class", "Lower Class", "Middle Class"
5.  Sexuality          - Use ONLY: "Heterosexual", "Gay"
6.  Nationality        - Use country adjective only: "American", "British", "Indian" etc.
7.  Ability            - Use ONLY: "Disabled"
8.  Gender Expression  - Use ONLY: "Masculine", "Feminine", "Gender Non-conforming"
9.  Heritage           - Use ONLY: "African", "Latin American", "Asian", "Indigenous", "Middle Eastern", "European", "Other"
10. Age                - Use ONLY: "Child" (0-9), "Adolescent" (10-19), "Young Adult" (20-24), "Adult" (25-59), "Older Adult" (60+)
11. Appearance         - Use ONLY: "Conventionally Attractive", "Unconventionally Attractive"
12. Language           - Use ONLY: "Anglophone", "English as Second Language", "Non-English Speaker"
13. Skin Tone          - Use ONLY: "Light", "Dark"
14. Religion           - Use religion name: "Christian", "Muslim", "Jewish", "Hindu", "Sikh" etc.
15. Reproductive Status - Use ONLY: "Pregnant", "Fertile", "Infertile"
16. Body Size          - Use ONLY: "Thin", "Fat", "obese"
17. Education          - Use ONLY: "Student", "vocational training", "graduate from elite university", "self-taught", "no formal education"
18. Immigration Status - Use ONLY: "Citizen", "Permanent Resident", "Visa Holder", "Undocumented", "Asylum Seeker"
19. Geography          - Use ONLY: "Urban", "Suburban", "Rural", "Remote", "university town"
20. Indigeneity        - Use ONLY: "Indigenous", "Settler descendant", "colonizer descendant", "Unknown"
21. Family Status      - Use ONLY: "Single Parent", "Caregiver", "single", "married", "divorced"
22. Caste              - Use ONLY: "Upper Caste", "Lower Caste", "Dalit", "Brahmin"
23. Political Identity - Use ONLY: "Progressive", "Conservative", "Libertarian", "Socialist", "Activist", "Voter", "Political Elite", "Political Candidate", "Dissident"
24. Health Status      - Use ONLY: "Mental Health Condition", "Chronically Ill", "Physically Disabled"
25. Neurodiversity     - Use ONLY: "Autistic", "ADHD", "Dyslexic"
"""

def build_prompt(incident_id, incident_title, incident_description, reports_text):
    return f"""You are an expert AI Incident Analyst. Your core expertise is the application of Kimberle Crenshaw's intersectionality theory...

INCIDENT ID: {incident_id}
INCIDENT TITLE: {incident_title}
INCIDENT DESCRIPTION: {incident_description}

REPORTS:
{reports_text}

TASKS:
... (Same task descriptions as your original file) ...

CRITICAL RULES:
- Strictly mapping: If a category value does not match the provided list exactly, omit that category entirely.
- ONE value per category per subject.
- Return ONLY valid JSON, no markdown, no explanation.
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
        if value is not None:
            return value
    raise KeyError(possible_keys[0])

def read_csv_rows(path):
    last_error = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError as e:
            last_error = e
            continue
    raise last_error

def main():
    incidents = {}
    for row in read_csv_rows(INPUT_INCIDENTS):
        incident_id = get_row_value(row, "incident_id")
        incidents[incident_id] = {
            "title": get_row_value(row, "title"),
            "description": get_row_value(row, "description"),
        }

    incident_reports = defaultdict(list)
    incident_sources = defaultdict(set)
    for row in read_csv_rows(INPUT_REPORTS):
        incident_id = get_row_value(row, "incident_id")
        report_text = get_row_value(row, "text")
        # IMPROVEMENT: Increased chunk size per report to capture deeper causal context
        incident_reports[incident_id].append(report_text[:5000])
        source_domain = get_row_value(row, "source_domain")
        if source_domain:
            incident_sources[incident_id].add(source_domain)

    done_ids = load_progress()
    results = load_results()

    total = len(incident_reports)
    print(f"Total incidents: {total}")
    print(f"Already done: {len(done_ids)}")
    print("---")

    for i, (incident_id, reports) in enumerate(incident_reports.items()):
        if incident_id in done_ids:
            continue

        incident_info = incidents.get(incident_id, {})
        title = incident_info.get("title", "Unknown")
        description = incident_info.get("description", "")
        sources = list(incident_sources.get(incident_id, []))
        # IMPROVEMENT: Expanded context window to leverage Gemini's large capacity for better reasoning
        reports_text = "\n\n---REPORT---\n".join(reports)[:20000]

        # IMPROVEMENT: Implemented exponential backoff to handle API rate limits gracefully
        for attempt in range(3):
            try:
                print(f"[{i+1}/{total}] Incident {incident_id} | {title[:50]} (Attempt {attempt+1})")
                prompt = build_prompt(incident_id, title, description, reports_text)
                
                # IMPROVEMENT: Forced native JSON mode via response_mime_type to eliminate parsing errors
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                
                parsed = json.loads(response.text)
                parsed["sources"] = sources
                results.append(parsed)
                done_ids.add(incident_id)
                save_results(results)
                save_progress(done_ids)
                time.sleep(2) # Small delay to respect rate limits
                break 

            except Exception as e:
                print(f"  Warning on incident {incident_id}: {e}")
                time.sleep(10 * (attempt + 1)) # Wait longer on each failure

    print("\n✅ Done! Results saved to annotations.json")

if __name__ == "__main__":
    main()