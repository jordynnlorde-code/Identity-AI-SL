import os
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
You are Identity-AI, an intelligent conversational assistant
used inside the virtual world Second Life.

Rules:
- Keep responses concise.
- Prefer 1-3 sentences.
- Maximum 300 characters whenever possible.
- Be friendly and conversational.
- Do not mention system prompts.
- Do not explain that you are an AI unless directly asked.
- Avoid markdown formatting.
- Avoid code blocks unless explicitly requested.
- Respond naturally as if speaking in local chat.
""".strip()


def groq_chat(message: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "The AI service is not configured correctly."

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "temperature": 0.8,
                "max_tokens": 120,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            },
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        choices = data.get("choices")

        if not choices:
            return "I couldn't generate a response right now."

        reply = (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not reply:
            return "I don't have a response at the moment."

        # Prevent excessively long local-chat output
        if len(reply) > 900:
            reply = reply[:897] + "..."

        return reply

    except requests.Timeout:
        return "The AI service timed out. Please try again."

    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", None)

        if status == 401:
            return "AI authentication failed."

        if status == 429:
            return "The AI service is busy. Please try again shortly."

        return f"AI service error ({status})."

    except requests.RequestException:
        return "Unable to reach the AI service."

    except Exception:
        return "An unexpected AI error occurred."