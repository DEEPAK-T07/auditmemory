import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HINDSIGHT_API_URL = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
BANK_ID = os.getenv("BANK_ID", "auditmemory-northwind")

# auto: Hindsight if an API key is set, else the local fallback.
# Set MEMORY_BACKEND=hindsight for a self-hosted server (http://localhost:8888, no key).
MEMORY_BACKEND = os.getenv("MEMORY_BACKEND") or ("hindsight" if HINDSIGHT_API_KEY else "local")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gemini-3.1-pro-preview")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-3.1-flash-lite-preview")

TODAY = os.getenv("DEMO_TODAY", "2026-11-07")
AUDIT_START = os.getenv("AUDIT_START", "2026-12-07")
COMPANY = "Northwind Payments (120 employees, SOC 2 Type II)"
