"""LLM client supporting Google Gemini and Groq with retries and model fallback."""
import json, re, time, urllib.request, urllib.error
from . import config

class LLMError(Exception):
    pass

def available():
    return bool(config.GEMINI_API_KEY or config.GROQ_API_KEY)

def _call_gemini_rest(model: str, system_text: str, user_text: str, api_key: str):
    # Google Gemini REST endpoint with native systemInstruction support and clean model routing
    clean_model = model.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_text}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4096
        }
    }
    if system_text:
        payload["systemInstruction"] = {
            "parts": [{"text": system_text}]
        }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        candidates = res_data.get("candidates", [])
        if not candidates:
            return ""
        candidate = candidates[0]
        finish_reason = candidate.get("finishReason", "")
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        clean = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
        # If finishReason is MAX_TOKENS or truncated unexpectedly, log it
        return clean

def chat(system, user, temperature=0.2, max_tokens=4096):
    if not available():
        raise LLMError("Neither GEMINI_API_KEY nor GROQ_API_KEY is set")

    # Priority 1: Google Gemini API
    if config.GEMINI_API_KEY:
        models = [
            "gemini-3.1-pro-preview",
            "gemini-3.1-flash-lite-preview",
            "gemini-3.1-flash-lite",
            "gemini-flash-latest",
            "gemini-pro-latest"
        ]
        unique_models = list(dict.fromkeys(m for m in models if m))
        last = None
        for model in unique_models:
            for attempt in range(2):
                try:
                    text = _call_gemini_rest(model, system, user, config.GEMINI_API_KEY)
                    if text and len(text.strip()) > 150:
                        return text, f"Gemini ({model})"
                    last = f"model {model} returned short/incomplete response ({len(text)} chars)"
                except urllib.error.HTTPError as e:
                    body = e.read().decode("utf-8", errors="ignore")
                    last = f"HTTP {e.code}: {body}"
                    # If model not found or forbidden, switch model immediately
                    if e.code in (404, 400):
                        break
                except Exception as e:
                    last = str(e)
                time.sleep(1.0)
        raise LLMError(f"Gemini API call failed: {last}")

    # Priority 2: Groq (OpenAI-compatible)
    from openai import OpenAI
    client = OpenAI(api_key=config.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    last = None
    for model in (config.PRIMARY_MODEL, config.FALLBACK_MODEL):
        for attempt in range(2):
            try:
                r = client.chat.completions.create(
                    model=model, temperature=temperature, max_tokens=max_tokens,
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}])
                text = re.sub(r"<think>.*?</think>", "", r.choices[0].message.content or "", flags=re.S).strip()
                if text:
                    return text, model
                last = "empty response"
            except Exception as e:
                last = e
            time.sleep(1.5 * (attempt + 1))
    raise LLMError(f"All models failed: {last}")
