import anthropic
import csv
from dotenv import load_dotenv
import os

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("../data/workplace_reports.csv", encoding="latin-1") as f:
    reader = csv.DictReader(f)
    for report in reader:
        if report['incident_id'] == '335':
            break

print(f"Testing with incident ID: {report['incident_id']}")
print(f"Title: {report['title']}")
print("---")

json_template = """
{
  "incident_id": "INCIDENT_ID",
  "report_id": "REPORT_ID",
  "is_ai_incident": "Yes/No",
  "ai_incident_reasoning": "brief explanation of why this is or is not an AI incident",
  "subjects": [
    {
      "name": "exact name or descriptor of harmed person/group from the text",
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

prompt = (
    "You are an expert AI incident analyst specializing in intersectionality theory.\n\n"
    "Analyze the following AI incident report and return ONLY a valid JSON object.\n\n"
    "Rules:\n"
    "- CQ1 = Yes ONLY if the harm happened BECAUSE of this identity\n"
    "- CQ2 = Yes if the harm would have happened anyway regardless of this identity\n"
    "- Only fill reasoning and harm when CQ1=Yes AND CQ2=No\n"
    "- marker_type must be Explicit, Inferred, or None\n"
    "- Return ONLY the JSON, no other text, no markdown\n\n"
    "Use this exact structure:\n"
    + json_template.replace("INCIDENT_ID", report['incident_id']).replace("REPORT_ID", report['report_id'])
    + "\n\nReport:\n"
    + report['text'][:3000]
)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4000,
    messages=[{"role": "user", "content": prompt}]
)

result = response.content[0].text
print(result)

with open("../data/output_test.json", "w") as f:
    f.write(result)
print("\n---\nLagret til output_test.json")