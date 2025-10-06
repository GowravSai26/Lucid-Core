import os
import httpx
from Backend.app.config import settings

OPENAI_CHAT_COMPLETIONS = "https://api.openai.com/v1/chat/completions"
# For other providers expand router

def call_chat_completion(prompt: str, system: str = "You are a helpful assistant.", temperature: float = 0.0, model: str = "gpt-4o-mini"):
    """
    Minimal wrapper for OpenAI Chat Completions (resp format adapted).
    Returns dict {'text': <string>}
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        # For dev/test, return an echo or a mock.
        return {"text": f"[MOCK RESPONSE] for prompt: {prompt[:200]}"}

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 800
    }
    r = httpx.post(OPENAI_CHAT_COMPLETIONS, json=payload, headers=headers, timeout=30.0)
    r.raise_for_status()
    j = r.json()
    # OpenAI normal shape: choices[0].message.content
    text = ""
    try:
        text = j["choices"][0]["message"]["content"]
    except Exception:
        text = j.get("choices", [{}])[0].get("text", "")
    return {"text": text, "raw": j}
