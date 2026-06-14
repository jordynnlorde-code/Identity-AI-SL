import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

def groq_chat(message: str) -> str:
    if not GROQ_API_KEY:
        return "GROQ_API_KEY is not configured on the server."

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a warm, natural, humanlike conversational assistant "
                    "living inside Second Life. Be clear, friendly, and concise."
                )
            },
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]
