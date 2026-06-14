# Identity-AI SL HUD Backend

Groq-powered conversational backend for Second Life HUDs.

## Features

- Groq Llama 3.1 integration
- Per-avatar daily rate limiting
- Request logging
- Admin dashboard
- Health monitoring endpoints
- Render.com deployment ready

## Endpoints

### HUD Chat

POST `/api/hud`

Example:

```json
{
  "avatar_id": "avatar-uuid",
  "message": "Hello AI"
}
```

Response:

```json
{
  "avatar_id": "avatar-uuid",
  "reply": "Hello there!",
  "remaining": 29
}
```

### Status

- `/status`
- `/status/groq`
- `/status/memory`
- `/health`

### Admin

- `/admin`
- `/api/logs`
- `/api/rate`

## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variable:

```bash
export GROQ_API_KEY=your_api_key_here
```

Run server:

```bash
python server.py
```

Server starts on:

```text
http://localhost:5000
```

## Deployment

Designed for deployment on Render.com using:

```text
web: gunicorn server:app
```