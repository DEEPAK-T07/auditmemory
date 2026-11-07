"""Memory layer. HindsightMemory is the real thing; LocalMemory is a keyword-search
fallback so the UI still runs without keys (offline demo / tests)."""
import json, math, re, pathlib
from . import config
from .records import load_records, to_content

STOP = set("the a an and or of to in on for is are was were be been it this that with as at by from "
           "what which who how should we our us do does did have has had not no any all about".split())
FEEDBACK_FILE = pathlib.Path(__file__).resolve().parent.parent / "data" / ".local_feedback.json"

def _tok(s):
    return [w for w in re.findall(r"[a-z0-9\-]+", s.lower()) if len(w) > 2 and w not in STOP]

class MemoryError_(Exception):
    pass

class LocalMemory:
    name = "local (keyword fallback)"
    def __init__(self, records=None, use_feedback=True):
        base = records if records is not None else load_records()
        self.docs = [{"text": to_content(r), "fb": False} for r in base]
        self.use_feedback = use_feedback
        if use_feedback and FEEDBACK_FILE.exists():
            for t in json.loads(FEEDBACK_FILE.read_text()):
                self.docs.append({"text": t, "fb": True})

    def retain(self, content, context=None, timestamp=None):
        self.docs.append({"text": content, "fb": context == "feedback"})
        if self.use_feedback and context == "feedback":
            old = json.loads(FEEDBACK_FILE.read_text()) if FEEDBACK_FILE.exists() else []
            FEEDBACK_FILE.write_text(json.dumps(old + [content]))

    def recall(self, query, k=6):
        q = _tok(query)
        if not q or not self.docs:
            return []
        toks = [_tok(d["text"]) for d in self.docs]
        n = len(self.docs)
        df = {}
        for t in toks:
            for w in set(t):
                df[w] = df.get(w, 0) + 1
        scored = []
        for d, t in zip(self.docs, toks):
            s = sum(math.log(1 + n / (1 + df.get(w, 0))) for w in set(q) if w in t)
            if d["fb"]:
                s *= 1.5
            if s > 0:
                scored.append((s, d["text"]))
        scored.sort(key=lambda x: -x[0])
        return [{"text": t, "score": round(s, 2)} for s, t in scored[:k]]

    def reflect(self, query):
        return "Reflect is only available with the Hindsight backend."

    @staticmethod
    def reset_feedback():
        if FEEDBACK_FILE.exists():
            FEEDBACK_FILE.unlink()

class HindsightMemory:
    name = "Hindsight"
    def __init__(self, bank_id=None):
        from hindsight_client import Hindsight
        kw = {"base_url": config.HINDSIGHT_API_URL}
        if config.HINDSIGHT_API_KEY:
            kw["api_key"] = config.HINDSIGHT_API_KEY
        self.client = Hindsight(**kw)
        self.bank_id = bank_id or config.BANK_ID

    def retain(self, content, context=None, timestamp=None):
        kw = {"bank_id": self.bank_id, "content": content}
        if context: kw["context"] = context
        if timestamp: kw["timestamp"] = timestamp
        try:
            self.client.retain(**kw)
        except Exception as e:
            raise MemoryError_(f"Hindsight retain failed: {e}")

    def recall(self, query, k=6):
        try:
            res = self.client.recall(bank_id=self.bank_id, query=query)
        except Exception as e:
            raise MemoryError_(f"Hindsight recall failed: {e}")
        return [{"text": r.text, "score": None} for r in (res.results or [])[:k]]

    def reflect(self, query):
        try:
            res = self.client.reflect(bank_id=self.bank_id, query=query)
        except Exception as e:
            raise MemoryError_(f"Hindsight reflect failed: {e}")
        return getattr(res, "text", None) or str(res)

def get_memory(bank_id=None, backend=None):
    backend = backend or config.MEMORY_BACKEND
    if backend == "hindsight":
        return HindsightMemory(bank_id)
    return LocalMemory()
