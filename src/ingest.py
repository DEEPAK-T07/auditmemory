"""Load the synthetic history into memory.  python -m src.ingest [--bank NAME]"""
import argparse, time
from . import config
from .memory import get_memory, HindsightMemory
from .records import load_records, to_content

def ingest(mem, records, progress=print):
    for i, r in enumerate(records, 1):
        mem.retain(to_content(r), context=r["type"], timestamp=f"{r['date']}T09:00:00Z")
        progress(f"retained {i}/{len(records)}  {r['id']}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default=config.BANK_ID)
    a = ap.parse_args()
    mem = get_memory(a.bank)
    if not isinstance(mem, HindsightMemory):
        raise SystemExit("Backend is 'local': nothing to ingest. Set HINDSIGHT_API_KEY (or MEMORY_BACKEND=hindsight).")
    t = time.time()
    ingest(mem, load_records())
    print(f"Done in {time.time()-t:.0f}s into bank '{a.bank}'. Wait ~1 minute for indexing before recalling.")
