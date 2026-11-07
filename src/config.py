import os

# 1. Load from .env file if running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Helper to look up secrets from os.environ first, then streamlit.secrets if on Streamlit Cloud
def get_secret(key, default=""):
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default

HINDSIGHT_API_URL = get_secret("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
HINDSIGHT_API_KEY = get_secret("HINDSIGHT_API_KEY", "")
BANK_ID = get_secret("BANK_ID", "auditmemory-northwind")

# auto: Hindsight if an API key is set, else the local fallback.
MEMORY_BACKEND = get_secret("MEMORY_BACKEND") or ("hindsight" if HINDSIGHT_API_KEY else "local")

GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
PRIMARY_MODEL = get_secret("PRIMARY_MODEL", "gemini-3.1-pro-preview")
FALLBACK_MODEL = get_secret("FALLBACK_MODEL", "gemini-3.1-flash-lite-preview")

TODAY = get_secret("DEMO_TODAY", "2026-11-07")
AUDIT_START = get_secret("AUDIT_START", "2026-12-07")
COMPANY = "Northwind Payments (120 employees, SOC 2 Type II)"
