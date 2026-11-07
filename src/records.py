import json, pathlib
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
FILES = ["controls", "audit_findings", "remediation_tickets",
         "policy_changes", "control_tests", "slack_snippets"]

def load_records():
    recs = []
    for f in FILES:
        recs += json.loads((DATA / f"{f}.json").read_text())
    return sorted(recs, key=lambda r: (r["date"], r["id"]))

def to_content(r):
    """Text stored in memory. The record id stays in the text so answers can cite it."""
    return f"[{r['id']}] ({r['type']}, {r['date']}) {r['text']}"
