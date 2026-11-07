"""AuditMemory agent: recall -> reason -> cite. Same prompt with and without memory."""
from concurrent.futures import ThreadPoolExecutor
from . import config, llm
from .memory import get_memory, MemoryError_

FACETS = [
    "past audit findings and repeat findings",
    "remediation tickets closed without evidence",
    "policy changes effective date and stale evidence",
    "auditor preferences evidence format rejected",
    "backup restore test last performed",
    "control test not performed overdue",
    "vendor access review",
    "finance database access review",
]
BROAD_WORDS = (
    "worry", "risk", "ready", "readiness", "prepare", "prep", 
    "gaps", "priorit", "focus", "should", "issue", "finding", 
    "problem", "audit", "present", "repeat", "evidence", "fail"
)

SYSTEM_ON = f"""You are AuditMemory, an expert compliance teammate for {config.COMPANY}.
Today is {config.TODAY}. The upcoming SOC 2 audit fieldwork starts on {config.AUDIT_START}.

You have access to the company's historical compliance records provided below.
Rules for answering:
1. Provide a direct, thorough, and complete answer to whatever question the user asks.
2. Ground your claims in the provided records, and cite the record IDs in brackets like [REM-14], [CT-05], [F-03], [POL-01], [SLACK-02].
3. If the user asks generally about "issues", "risks", "gaps", or "what should I prepare", systematically enumerate all known operational risks found in the records (vendor review repeat failures, tickets closed without evidence, overdue backup restores, quarterly review omissions, stale evidence due to policy changes).
4. For every issue you mention, clearly describe:
   - What the issue is and who owns it
   - Why it is an audit risk
   - The concrete action required before audit fieldwork starts
5. Never cut off or stop halfway. Always complete your thoughts and lists fully."""

SYSTEM_OFF = f"""You are a compliance assistant helping a company prepare for a SOC 2 audit.
You have NO access to this company's history, tickets, findings or policies.
Give general SOC 2 readiness advice (max 6 bullets) and do not invent company-specific facts."""

GENERIC_OFFLINE = """Offline mode (no LLM key). Generic SOC 2 readiness checklist:
- Review user access for production systems and databases.
- Confirm backups and test a restore.
- Make sure policies are up to date and approved.
- Collect evidence for every control.
- Check vendor and third-party risk reviews.
- Close out last year's audit findings."""

def _recall_all(mem, question):
    # Always include all core facets plus the user's specific question
    queries = [question] + FACETS
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(lambda q: mem.recall(q, k=5), queries))
    seen, merged = set(), []
    for rank in range(5):  # round-robin so every facet gets represented before the cap
        for res in results:
            if rank < len(res):
                m = res[rank]
                key = m["text"][:80].lower()
                if key not in seen:
                    seen.add(key)
                    merged.append(m)
    return merged[:25]

def answer(question, memory_on=True, memory=None):
    out = {"answer": "", "memories": [], "model": None, "notes": [], "memory_on": memory_on}
    system, user = SYSTEM_OFF, question
    if memory_on:
        mem = memory or get_memory()
        try:
            out["memories"] = _recall_all(mem, question)
        except MemoryError_ as e:
            out["notes"].append(f"Memory unavailable, answered without it: {e}")
        if out["memories"]:
            block = "\n".join(f"- {m['text']}" for m in out["memories"])
            system, user = SYSTEM_ON, f"MEMORY RECORDS:\n{block}\n\nQUESTION: {question}"
        elif "Memory unavailable" not in " ".join(out["notes"]):
            out["notes"].append("No relevant memories found; answering generically.")
    try:
        out["answer"], out["model"] = llm.chat(system, user)
    except llm.LLMError as e:
        out["notes"].append(f"LLM unavailable ({e}). Showing offline output.")
        if out["memories"]:
            lines = "\n".join(f"- {m['text']}" for m in out["memories"])
            out["answer"] = f"Offline mode (no LLM key). Most relevant recalled records:\n{lines}"
        else:
            out["answer"] = GENERIC_OFFLINE
        out["model"] = "offline"
    return out

def give_feedback(text, memory=None):
    mem = memory or get_memory()
    stamp = f"{config.TODAY}T12:00:00Z"
    mem.retain(f"[FB-{config.TODAY}] ({'feedback'}, {config.TODAY}) Compliance lead feedback: {text}",
               context="feedback", timestamp=stamp)
