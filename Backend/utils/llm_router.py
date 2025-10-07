import os
import httpx
import json
from datetime import datetime
from Backend.app.config import settings


# ───────────────────────────────────────────────
# 🌐 LLM Provider API Endpoints
# ───────────────────────────────────────────────
OPENAI_CHAT_COMPLETIONS = "https://api.openai.com/v1/chat/completions"
GEMINI_CHAT_COMPLETIONS = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
)


# ───────────────────────────────────────────────
# 🧠 Main Chat Completion Router
# ───────────────────────────────────────────────
def call_chat_completion(
    prompt: str,
    system: str = "You are a helpful assistant.",
    temperature: float = 0.0,
    model: str = "gpt-4o-mini",
):
    """
    Universal LLM router for Lucid Core backend.

    🔹 Priority: Gemini → OpenAI → Mock
    🔹 Normalized output schema: {'text': <string>, 'raw': <dict>}
    🔹 Includes detailed logging for debugging
    """

    # ──────────────── 1️⃣ Load environment keys ────────────────
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = settings.OPENAI_API_KEY
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n🔍 [{timestamp}] Starting LLM request...")
    print(f"   ➤ Model preference → Gemini → OpenAI")
    print(f"   ➤ Prompt preview → {prompt[:120]}{'...' if len(prompt) > 120 else ''}")

    # ──────────────────────────────────────────────────────────────
    # 🟢 GEMINI 2.5 PRO PATH (Primary)
    # ──────────────────────────────────────────────────────────────
    if gemini_key:
        print("⚙️ Using Gemini 2.5 Pro as primary model.")
        try:
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 1024,
                },
            }

            url = f"{GEMINI_CHAT_COMPLETIONS}?key={gemini_key}"
            r = httpx.post(url, json=payload, timeout=30.0)
            r.raise_for_status()
            j = r.json()

            # --- Gemini JSON can vary, handle both shapes safely ---
            text = ""
            try:
                text = j["candidates"][0]["content"]["parts"][0]["text"]
            except KeyError:
                # fallback parsing (sometimes it's under 'output' or 'text')
                text = j.get("output", None) or j.get("text", "[Gemini: No text field found]")

            text = text.strip()
            print("✅ Gemini response received successfully.")
            return {"text": text, "raw": j}

        except httpx.TimeoutException:
            print("⏱️ Gemini request timed out after 30 seconds.")
            return {"text": "[Gemini Timeout] Request took too long."}

        except httpx.HTTPStatusError as e:
            print(f"❌ Gemini HTTP Error → {e.response.status_code} {e.response.text[:200]}")
            return {"text": f"[Gemini HTTP Error] {e.response.text[:200]}"}

        except Exception as e:
            print(f"❌ Gemini Parsing Error: {str(e)}")
            # Continue to fallback

    # ──────────────────────────────────────────────────────────────
    # 🟡 OPENAI GPT PATH (Fallback)
    # ──────────────────────────────────────────────────────────────
    if openai_key:
        print("⚙️ Falling back to OpenAI GPT (gpt-4o-mini).")
        try:
            headers = {"Authorization": f"Bearer {openai_key}"}
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": 800,
            }

            r = httpx.post(
                OPENAI_CHAT_COMPLETIONS, json=payload, headers=headers, timeout=30.0
            )
            r.raise_for_status()
            j = r.json()

            text = j["choices"][0]["message"]["content"].strip()
            print("✅ OpenAI response received successfully.")
            return {"text": text, "raw": j}

        except httpx.TimeoutException:
            print("⏱️ OpenAI request timed out.")
            return {"text": "[OpenAI Timeout] Request took too long."}

        except httpx.HTTPStatusError as e:
            print(f"❌ OpenAI HTTP Error → {e.response.status_code} {e.response.text[:200]}")
            return {"text": f"[OpenAI HTTP Error] {e.response.text[:200]}"}

        except Exception as e:
            print(f"❌ OpenAI Error: {str(e)}")
            return {"text": f"[OpenAI Exception] {str(e)}"}

    # ──────────────────────────────────────────────────────────────
    # 🔴 MOCK MODE (No Keys Available)
    # ──────────────────────────────────────────────────────────────
    print("⚠️ No valid API keys detected — returning mock response.")
    return {
        "text": f"[MOCK RESPONSE] for prompt: {prompt[:200]}",
        "raw": {"provider": "mock"},
    }
