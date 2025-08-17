# Smart Content Moderator API

FastAPI-based service that analyses text or image content for inappropriate material. It stores moderation results in a SQLite database, sends Slack and email alerts for unsafe content, and exposes analytics endpoints.

## Features
- Async FastAPI application
- Asynchronous SQLAlchemy models
- OpenAI integration for content classification (falls back to heuristic if no API key)
- Slack and Brevo (email) notifications
- Background task processing for image moderation
- Basic analytics endpoint

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API
- `POST /api/v1/moderate/text`
- `POST /api/v1/moderate/image`
- `GET /api/v1/analytics/summary?user=user@example.com`

## DOCS
http://127.0.0.1:8000/docs

Set environment variables `OPENAI_API_KEY`, `SLACK_WEBHOOK_URL`, and `BREVO_API_KEY` for full functionality.
