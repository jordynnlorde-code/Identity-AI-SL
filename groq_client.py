import os
import requests


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def groq_chat(message):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "GROQ_API_KEY is not configured on the server."

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "choices" not in data:
            return "Groq returned an unexpected response."

        return data["choices"][0]["message"]["content"]

    except requests.Timeout:
        return "Groq request timed out."

    except requests.HTTPError as e:
        return f"Groq HTTP error: {e}"

    except Exception as e:
        return f"Groq error: {str(e)}"