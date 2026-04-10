import anthropic
import csv
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Settings ────────────────────────────────────────────
INPUT_FILE = "../data/workplace_reports.csv"
OUTPUT_FILE = "../data/annotations_output.json"
PROGRESS_FILE = "../data/progress.json"  # tracks which reports are done
# ────────────────────────────────────────────────────────

json_template = """
{
  "incident_id": "INCIDENT_ID",
  "report_id": "REPORT_ID",
  "is_ai_incident": "Yes/No",
  "ai_incident_reasoning": "brief explanation",
  "subjects": [
    {
      "name": "exact name or descriptor of harmed person/group",
      "type": "Individual / Group of persons / Society / Organization / Nature",
      "identity_categories": {
        "race": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "gender": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "gender_identity": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "class": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "sexuality": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "nationality": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "ability": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "gender_expression": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "heritage": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "age": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "appearance": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "language": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "skin_tone": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "religion": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "reproductive_status": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "body_size": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "education": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "immigration_status": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "geography": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "indigeneity": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "family_status": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "caste": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "political_identity": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "neurodiversity": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "health_status": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""},
        "species": {"marker": "value or Not mentioned", "marker_type": "Explicit/Inferred/None", "source": "quote or reasoning", "CQ1": "Yes/No", "CQ2": "Yes/No", "reasoning": "", "harm": ""}
      }
    }
  ]
}
"""

def build_prompt(report):
    return (
        "You are an expert AI incident analyst specializing in intersectionality theory.\n\n"
        "Analyze the following AI incident report and return ONLY a valid JSON object.\n\n"
        "Rules:\n"
        "- CQ1 = Yes ONLY if the harm happened BECAUSE of this identity\n"
        "- CQ2 = Yes if the harm would have happened anyway regardless of this identity\n"
        "- Only fill reasoning and harm when CQ1=Yes AND CQ2=No\n"
        "- marker_type must be Explicit, Inferred, or None\n"
        "- Return ONLY the JSON, no other text, no markdown\n\n"
        "Use this exact structure:\n"
        + json_template
        .replace("INCIDENT_ID", report['incident_id'])
        .replace("REPORT_ID", report['report_id'])
        + "\n\nReport:\n"
        + report['text'][:3000]
    )

def annotate_report(report):
    prompt = build_prompt(report)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.removeprefix("```json").removesuffix("```").strip()
    return json.loads(raw)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_progress(done_ids):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(list(done_ids), f)

def load_results():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_results(results):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

# ── Main loop ────────────────────────────────────────────
def main():
    done_ids = load_progress()
    results = load_results()

    with open(INPUT_FILE, encoding="latin-1") as f:
        reports = list(csv.DictReader(f))

    total = len(reports)
    print(f"Total reports: {total}")
    print(f"Already done: {len(done_ids)}")
    print(f"Remaining: {total - len(done_ids)}")
    print("---")

    for i, report in enumerate(reports):
        report_id = report['report_id']

        if report_id in done_ids:
            continue

        try:
            print(f"[{i+1}/{total}] Incident {report['incident_id']} | {report['title'][:60]}")
            result = annotate_report(report)
            results.append(result)
            done_ids.add(report_id)

            # Save after every report
            save_results(results)
            save_progress(done_ids)

            # Wait 1 second to avoid rate limits
            time.sleep(1)

        except json.JSONDecodeError as e:
            print(f"  JSON error on report {report_id}: {e}")
            continue

        except Exception as e:
            print(f"  Error on report {report_id}: {e}")
            time.sleep(5)
            continue

    print("\n✅ Done! Results saved to annotations_output.json")

if __name__ == "__main__":
    main()