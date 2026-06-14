# Identity-AI SL HUD Backend

Groq-powered, natural conversational backend for Second Life HUDs.

- Endpoint: `/api/hud`
- Model: `llama-3.1-8b-instant` via Groq
- Per-avatar daily limit: 30 requests
- Designed for Render.com deployment

## Run locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
python app.py
