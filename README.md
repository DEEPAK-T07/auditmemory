# AuditMemory

A compliance teammate that never forgets an audit finding. Built for **Hack with Hyderabad 3.0** on **Hindsight** memory.

Every year a company is audited (SOC 2) to prove it keeps customer data safe. Between audits, findings are forgotten, tickets get closed without proof and the same problems return. AuditMemory remembers the whole history and tells you exactly what to worry about before the next audit.

## How Hindsight memory is used
| Hindsight op | Where | What for |
|---|---|---|
| `retain` | `src/ingest.py`, `agent.give_feedback` | Store 57 dated records (findings, tickets, policy changes, control tests, Slack) and every piece of feedback from the compliance lead |
| `recall` | `src/agent.py` | Multi-facet recall (findings, evidence gaps, policy changes, auditor habits, overdue tests) merged into one context |
| `reflect` | Memory browser tab | Hindsight's own synthesis over the stored history |

Memory is the product: the **same prompt and model** is run with memory OFF (generic checklist) and ON (specific, cited risks). Feedback ("evidence rejected") is retained and changes the next answer.

## Run it
```bash
git clone https://github.com/DEEPAK-T07/auditmemory.git && cd auditmemory
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add GEMINI_API_KEY (or GROQ_API_KEY / HINDSIGHT_API_KEY)
python scripts/smoke_test.py
streamlit run app.py
```
No keys? The app still runs on a local keyword-memory fallback with an offline template (clearly labelled in the UI), so you can click through the flow.

## Learning curve
`python -m src.eval` (local) or `python -m src.eval --ingest` (Hindsight, one bank per stage) runs 3 questions with 0/25/50/75/100% of the history loaded and counts how many of 5 planted issues the answers catch. Results go to `data/learning_curve.json` and the **Learning curve** tab.

## Planted issues (ground truth for the demo)
1. REM-14 closed as Done with no evidence attached.
2. Password policy v4.0 (2026-08-01) makes older MFA/password evidence stale.
3. Vendor access review failed two audits in a row (and 2026 review was partial).
4. Auditor Priya Nair only accepts timestamped screenshots, not CSV exports.
5. Last backup restore test was 2025-12-10 (about 11 months ago, control needs 6).

## Layout
`app.py` UI | `src/memory.py` Hindsight + local fallback | `src/agent.py` recall and reasoning | `src/llm.py` Groq with retry and model fallback | `src/eval.py` learning curve | `data/` synthetic Northwind Payments dataset

## Known limitations
Synthetic data only; no live Jira/Slack/AWS integrations; single framework (SOC 2); scorecard keywords are tuned to the planted issues.
