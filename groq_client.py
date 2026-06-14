import os
import requests

def groq_chat(message):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY is not configured on the server."

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": message}]
            },
            timeout=10
        )
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Groq error: {str(e)}"
