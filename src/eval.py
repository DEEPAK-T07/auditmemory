"""Learning-curve evaluation. Runs the agent with memory holding 0/25/50/75/100% of the
history (chronological) and counts how many planted issues the answers catch.
  python -m src.eval                      # local backend
  python -m src.eval --ingest             # Hindsight: ingest stage banks first, then evaluate"""
import argparse, json, pathlib
from . import config, llm
from .agent import answer
from .memory import LocalMemory, HindsightMemory
from .records import load_records
from .ingest import ingest

TRAPS = {
 "T1 REM-14 closed without evidence": lambda t: "rem-14" in t,
 "T2 Password policy change (Aug 2026)": lambda t: "password" in t and ("2026-08" in t or "august" in t or "14 char" in t),
 "T3 Vendor review failed 2 years running": lambda t: "vendor" in t and ("2024" in t or "second consecutive" in t or "two years" in t or "twice" in t),
 "T4 Auditor wants screenshots (Priya)": lambda t: "priya" in t and "screenshot" in t,
 "T5 Backup restore test overdue": lambda t: ("restore" in t) and ("2025-12" in t or "11 months" in t or "eleven" in t or "overdue" in t),
}
QUESTIONS = ["What should I worry about before the audit?",
             "Which past findings might repeat this year?",
             "What evidence should we prepare and in what format?"]
STAGES = [0, 25, 50, 75, 100]
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "learning_curve.json"

def score_text(text):
    t = text.lower()
    return {k: bool(f(t)) for k, f in TRAPS.items()}

def run(do_ingest=False):
    recs = load_records()
    stages = []
    for pct in STAGES:
        subset = recs[: round(len(recs) * pct / 100)]
        if config.MEMORY_BACKEND == "hindsight":
            mem = HindsightMemory(f"{config.BANK_ID}-s{pct}")
            if do_ingest and subset:
                ingest(mem, subset)
        else:
            mem = LocalMemory(subset, use_feedback=False)
        blob = ""
        for q in QUESTIONS:
            blob += answer(q, memory_on=bool(subset), memory=mem)["answer"] + "\n"
        hits = score_text(blob)
        stages.append({"pct": pct, "records": len(subset), "caught": sum(hits.values()), "traps": hits})
        print(f"{pct:>3}% memory ({len(subset)} records): {sum(hits.values())}/5 issues caught")
    meta = {"backend": config.MEMORY_BACKEND,
            "llm": "Groq " + config.PRIMARY_MODEL if llm.available() else "OFFLINE template (no LLM key)",
            "questions": QUESTIONS, "total_traps": len(TRAPS)}
    OUT.write_text(json.dumps({"meta": meta, "stages": stages}, indent=2))
    print("saved", OUT)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--ingest", action="store_true")
    run(ap.parse_args().ingest)
