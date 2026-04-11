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
4.  Class            - e.g., Upper Class (P), Working Class (O)
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
You are precise, context-sensitive, and avoid flattening identities into isolated categories. You reason causally and structurally, working backwards from the observed harm to trace contributing design choices or detection failures.

INCIDENT ID: {incident_id}
INCIDENT TITLE: {incident_title}
INCIDENT DESCRIPTION: {incident_description}

REPORTS:
{reports_text}

YOUR TASKS:

TASK 1 - Identify harmed subjects:
Extract every living entity (person, group, society) harmed by the AI system.
Exclude organizations and inanimate objects.

TASK 2 - For each subject, extract identity markers from these 25 categories ONLY if explicitly stated or clearly inferable:
{IDENTITY_CATEGORIES}

For each marker found, apply exactly these two counterfactual questions:
CQ1: "Did this incident happen because the AI Subject was [identity value]?"
CQ2: "Would this incident still have happened if the AI Subject was not [identity value]?"

For marker_type, use ONLY:
- "Explicit": the identity is directly stated word-for-word in the report text
- "Inferred": the identity is not stated but is clearly and logically implied by specific context
- Never include a marker if you are uncertain or guessing

For power_position, use ONLY:
- "Privileged": the marker aligns with the privileged examples above (P)
- "Oppressed": the marker aligns with the oppressed examples above (O)
- If ambiguous (e.g. middle class), use your best judgment and explain in source

TASK 3 - Assess deployer:
Is there a company/organization deploying the AI system? If yes, what is its name?

Return ONLY valid JSON in this exact structure.
ONLY include identity categories where a marker was found.
ONLY include subjects where at least one marker has DirectScore=Yes AND AlternateScore=No:

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
        "race": {{
          "marker": "exact value e.g. Black",
          "marker_type": "Explicit or Inferred",
          "power_position": "Privileged or Oppressed",
          "source": "direct quote if Explicit, or one sentence logical reasoning if Inferred",
          "DirectScore": "Yes or No",
          "AlternateScore": "Yes or No",
          "reasoning": "backward reasoning from harm to system design failure - only fill if DirectScore=Yes",
          "MarkerHarm": "one concrete past-tense sentence about the exact harm - only fill if DirectScore=Yes AND AlternateScore=No"
        }}
      }}
    }}
  ]
}}

CRITICAL RULES:
- Only include identity categories where you found actual evidence
- DirectScore=Yes means the identity caused or shaped the AI harm
- AlternateScore=No means changing the identity would have changed the outcome
- MarkerHarm must be a concrete past-tense sentence about the actual harm
- marker_type must be Explicit or Inferred only
- power_position must be Privileged or Oppressed only
- Count this as ONE incident regardless of how many reports cover it
- Return ONLY JSON, no markdown, no explanation
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
    """Fetch CSV value with tolerant header matching (BOM/case/space safe)."""
    normalized = {
        (k or "").strip().lower().lstrip("\ufeff"): v
        for k, v in row.items()
    }
    for key in possible_keys:
        value = normalized.get(key.strip().lower())
        if value is not None:
            return value
    raise KeyError(possible_keys[0])

def read_csv_rows(path):
    """Read CSV with encoding fallback for mixed legacy data."""
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
    # Load incidents
    incidents = {}
    for row in read_csv_rows(INPUT_INCIDENTS):
        incident_id = get_row_value(row, "incident_id")
        incidents[incident_id] = {
            'title': get_row_value(row, "title"),
            'description': get_row_value(row, "description")
        }

    # Group reports by incident — collect text AND source domains
    incident_reports = defaultdict(list)
    incident_sources = defaultdict(set)
    for row in read_csv_rows(INPUT_REPORTS):
        incident_id = get_row_value(row, "incident_id")
        report_text = get_row_value(row, "text")
        incident_reports[incident_id].append(report_text[:1500])
        source_domain = get_row_value(row, "source_domain")
        if source_domain:
            incident_sources[incident_id].add(source_domain)

    done_ids = load_progress()
    results = load_results()

    total = len(incident_reports)
    print(f"Total incidents: {total}")
    print(f"Already done: {len(done_ids)}")
    print(f"Remaining: {total - len(done_ids)}")
    print("---")

    for i, (incident_id, reports) in enumerate(incident_reports.items()):
        if incident_id in done_ids:
            continue

        incident_info = incidents.get(incident_id, {})
        title = incident_info.get('title', 'Unknown')
        description = incident_info.get('description', '')
        sources = list(incident_sources.get(incident_id, []))

        # Combine reports, limit total length
        reports_text = "\n\n---REPORT---\n".join(reports)[:6000]

        try:
            print(f"[{i+1}/{total}] Incident {incident_id} | {title[:60]}")

            prompt = build_prompt(incident_id, title, description, reports_text)
            response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt
            )
            raw = response.text.strip()
            raw = raw.removeprefix("```json").removesuffix("```").strip()

            parsed = json.loads(raw)

            # Always use sources from CSV, not from LLM
            parsed['sources'] = sources

            results.append(parsed)
            done_ids.add(incident_id)

            save_results(results)
            save_progress(done_ids)

            time.sleep(4)

        except json.JSONDecodeError as e:
            print(f"  JSON error on incident {incident_id}: {e}")
            continue

        except Exception as e:
            print(f"  Error on incident {incident_id}: {e}")
            time.sleep(5)
            continue

    print("\n✅ Done! Results saved to annotations_v2.json")

if __name__ == "__main__":
    main()