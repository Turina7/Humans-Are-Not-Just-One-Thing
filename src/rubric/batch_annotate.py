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
1.  Race             - Use ONLY:
                       "People of Color", "White"
                       Assign ONE value only per subject.

2.  Gender           - Use ONLY: "Male", "Female", "other"
                       Assign ONE value only per subject.

3.  Gender Identity  - Use ONLY: "Cisgender", "Transgender", "Non-binary"

4.  Class            - Use ONLY: "Upper Class", "Lower Class", "Middle Class"
                       

5.  Sexuality        - Use ONLY: "Heterosexual", "Gay"

6.  Nationality      - Use country adjective only:
                       "American", "British", "Indian" etc.

7.  Ability          - Use ONLY: "Disabled"

8.  Gender Expression - Use ONLY: "Masculine", "Feminine",
                        "Gender Non-conforming"

9.  Heritage         - Use ONLY: "African", "Latin American", "Asian",
                       "Indigenous", "Middle Eastern", "European", "Other"

10. Age              - Use ONLY: "Child" (0-9), "Adolescent" (10-19),
                       "Young Adult" (20-24), "Adult" (25-59),
                       "Older Adult" (60+)

11. Appearance       - Use ONLY: "Conventionally Attractive",
                       "Unconventionally Attractive"

12. Language         - Use ONLY: "Anglophone",
                       "English as Second Language", "Non-English Speaker"

13. Skin Tone        - Use ONLY: "Light", "Dark"

14. Religion         - Use religion name: "Christian", "Muslim",
                       "Jewish", "Hindu", "Sikh" etc.

15. Reproductive Status - Use ONLY: "Pregnant", "Fertile", "Infertile"

16. Body Size        - Use ONLY: "Thin", "Fat", "obese"

17. Education        - Use ONLY: "Student", "vocational training", "graduate from elite university", "self-taught", "no formal education"

18. Immigration Status - Use ONLY: "Citizen", "Permanent Resident",
                         "Visa Holder", "Undocumented", "Asylum Seeker"

19. Geography        - Use ONLY: "Urban", "Suburban", "Rural", "Remote", "university town"

20. Indigeneity      - Use ONLY: "Indigenous", "Settler descendant", "colonizer descendant", "Unknown"

21. Family Status    - Use ONLY: "Single Parent", "Caregiver", "single", "married", "divorced"

22. Caste            - Use ONLY: "Upper Caste", "Lower Caste",
                       "Dalit", "Brahmin"

23. Political Identity - Use ONLY: "Progressive", "Conservative",
                         "Libertarian", "Socialist", "Activist",
                         "Voter", "Political Elite",
                         "Political Candidate", "Dissident"

24. Health Status    - Use ONLY: "Mental Health Condition",
                       "Chronically Ill", "Physically Disabled"

25. Neurodiversity   - Use ONLY: "Autistic", "ADHD", "Dyslexic"
"""


def build_prompt(incident_id, incident_title, incident_description, reports_text):
    return f"""You are an expert AI Incident Analyst. Your core expertise is the application of Kimberle Crenshaw's intersectionality theory to analyze AI incident reports.
You are precise, context-sensitive, and avoid flattening identities into isolated categories. To assess how identity contributes to harm, you reason causally and structurally. You often work backwards from the observed harm to trace contributing design choices or detection failures. This approach is similar to Fault Tree Analysis, where analysts start with a failure and identify underlying conditions or assumptions that allowed it to occur.

INCIDENT ID: {incident_id}
INCIDENT TITLE: {incident_title}
INCIDENT DESCRIPTION: {incident_description}

REPORTS:
{reports_text}

TASKS:

TASK 1 - Identify harmed subjects:
Extract every living entity (person, group, society) harmed by the AI system.
Exclude organizations and inanimate objects.
Each subject gets their OWN identity markers.
If multiple reports refer to the same subject, merge them into one entry.

TASK 2 - For each subject, extract identity markers from these 25 categories:
{IDENTITY_CATEGORIES}

EXTRACTION RULES:
- Explicit: identity is directly stated word-for-word in the report
- Inferred: identity is clearly implied by a SPECIFIC detail in THIS report
  You must cite the specific detail, not a general societal pattern
- When uncertain: do NOT include the marker

For each marker apply these counterfactual questions:
CQ1: "Did this incident happen because the AI Subject was [identity value]?"
     → Yes ONLY if the AI system's behavior changed because of this identity
     → No if the identity is just context about who was harmed

CQ2: "Would this incident still have happened if the AI Subject was not [identity value]?"
     → No if a person with a different identity would NOT have been harmed
     → Yes if the harm would have occurred regardless of this identity

- Do not be overly conservative. If a specific identity 
  marker clearly shaped how the AI system behaved toward 
  this person, flag it. The goal is to find ALL relevant 
  intersections, not just the most obvious ones.

EXAMPLES OF CORRECT USAGE:

✅ Age=Child (16-month-old), CQ1=Yes, CQ2=No:
   A security robot knocked over a toddler at Stanford Mall.
   Young children are less detectable by sensors and behave unpredictably.
   The robot likely failed to detect the toddler. An adult would not have
   been knocked over. Age directly caused the harm.

✅ Gender=Boy, CQ1=No, CQ2=Yes:
   Same incident. The robot did not act differently based on gender.
   If the child had been a girl, the same harm would have occurred.
   Gender is just context, not a cause.

✅ Immigration Status=Newcomer to Canada, CQ1=Yes, CQ2=No:
   AI deepfake targeted newcomers unfamiliar with immigration rules.
   A long-term resident would not have been targeted.
   Immigration status directly caused the harm.

✅ Geography=Toronto-based, CQ1=No, CQ2=Yes:
   The geographic detail only lent superficial credibility.
   The same harm would have occurred in any other Canadian city.
   Geography is just context, not a cause.

✅ CORRECT — Class=Lower Class, CQ1=Yes, CQ2=No (Inferred):
   "The report describes gig workers who cannot afford to challenge 
   the automated firing decision due to lack of legal resources."
   Lower class is inferred from specific economic vulnerability 
   described in the report. A wealthy worker would have had 
   legal recourse. Class directly shaped the harm.

✅ CORRECT — Class=Lower Class, CQ1=Yes, CQ2=No:
   "The automated hiring system rejected applicants from 
   zip codes associated with low-income neighborhoods."
   A wealthy applicant from a different zip code would 
   not have been rejected. Class directly caused the harm.

✅ CORRECT — Gender=Female, CQ1=Yes, CQ2=No:
   "The resume screening algorithm downgraded CVs that 
   included words like 'women's chess club'."
   A male applicant with identical qualifications would 
   not have been downgraded. Gender directly caused the harm.

✅ CORRECT — Age=Older Adult, CQ1=Yes, CQ2=No:
   "The performance management AI flagged workers over 50 
   as 'low productivity' based on metrics designed for 
   younger workers."
   A younger worker with the same output would not have 
   been flagged. Age directly caused the harm.

❌ WRONG — Gender=Male, CQ1=Yes:
   A male warehouse worker was injured by a robot.
   The robot would have injured anyone in that position.
   Male is just context. CQ1 should be No.

❌ WRONG — Class=Middle Class, CQ1=Yes:
   A middle class professional's data was leaked.
   Being middle class did not cause the leak.
   CQ1 should be No.

❌ WRONG — Race=White, CQ1=Yes:
   A white employee was fired by an automated system.
   Being white did not cause the firing.
   CQ1 should be No in most cases.

For marker_type use ONLY:
- "Explicit": identity directly stated in report text
- "Inferred": clearly implied by specific report detail

For power_position use ONLY:
- "Privileged": aligns with privileged examples (P)
- "Oppressed": aligns with oppressed examples (O)

TASK 3 - Assess deployer:
Is there a company or organization deploying the AI system?

Return ONLY valid JSON in this exact structure.
ONLY include identity categories where a marker was found.
ONLY include subjects where at least one marker has DirectScore=Yes AND AlternateScore=No:

{{
  "incident_id": "{incident_id}",
  "incident_title": "{incident_title}",
  "description": "[AI system name] was deployed in [context] to [intended function]. However, it [misfunctioned in a way that affected AI Subject]. As a result, [AI Subject] experienced [specific consequences].",
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
          "marker": "standardized value only",
          "marker_type": "Explicit or Inferred",
          "power_position": "Privileged or Oppressed",
          "source": "direct quote if Explicit, specific report detail if Inferred",
          "DirectScore": "Yes or No",
          "AlternateScore": "Yes or No",
          "reasoning": "backward reasoning from harm to system design — only if DirectScore=Yes",
          "MarkerHarm": "one concrete past-tense sentence — only if DirectScore=Yes AND AlternateScore=No"
        }}
      }}
    }}
  ]
}}

CRITICAL RULES:
- ONE value per category per subject
- NEVER add (O) or (P) to marker values
- Inferred markers need specific report evidence not general knowledge
- DirectScore=Yes only if identity directly shaped the AI harm
- AlternateScore=No only if a different identity would have changed the outcome
- Deduplicate subjects across reports — merge identical subjects into one
- Count as ONE incident regardless of report count
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
        title = incident_info.get("title", "Unknown")
        description = incident_info.get("description", "")
        sources = list(incident_sources.get(incident_id, []))
        reports_text = "\n\n---REPORT---\n".join(reports)[:6000]

        try:
            print(f"[{i+1}/{total}] Incident {incident_id} | {title[:60]}")
            prompt = build_prompt(incident_id, title, description, reports_text)
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview", contents=prompt
            )
            raw = response.text.strip()
            raw = raw.removeprefix("```json").removesuffix("```").strip()
            parsed = json.loads(raw)
            parsed["sources"] = sources
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

    print("\n✅ Done! Results saved to annotations_v6.json")


if __name__ == "__main__":
    TEST_MODE = False  # Change to False to run everything

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
        incident_reports[incident_id].append(report_text[:1500])
        source_domain = get_row_value(row, "source_domain")
        if source_domain:
            incident_sources[incident_id].add(source_domain)

    if TEST_MODE:
        test_id = "11"
        incident_info = incidents.get(test_id, {})
        reports_text = "\n\n---REPORT---\n".join(incident_reports[test_id])[:6000]
        sources = list(incident_sources.get(test_id, []))

        prompt = build_prompt(
            test_id,
            incident_info.get("title", "Unknown"),
            incident_info.get("description", ""),
            reports_text,
        )
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview", contents=prompt
        )
        raw = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(raw)
        parsed["sources"] = sources
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    else:
        main()
