"""Phase-0 check: python scripts/smoke_test.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import config, llm
from src.memory import get_memory

print("memory backend:", config.MEMORY_BACKEND)
m = get_memory(config.BANK_ID + "-smoke")
if config.MEMORY_BACKEND == "hindsight":
    m.retain("Smoke test: Alice works at Northwind Payments.")
    print("retain OK")
print("recall:", m.recall("Where does Alice work?")[:1])
if llm.available():
    print("llm:", llm.chat("Reply with one word.", "Say OK")[0])
else:
    print("GROQ_API_KEY not set: LLM check skipped")
