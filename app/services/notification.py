import os
from typing import Optional

import httpx

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


async def send_slack_alert(message: str) -> bool:
    if not SLACK_WEBHOOK_URL:
        print("Slack webhook not configured", message)
        return False
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(SLACK_WEBHOOK_URL, json={"text": message})
            return resp.status_code == 200
        except Exception:
            return False


async def send_email_alert(to_email: str, subject: str, content: str) -> bool:
    if not BREVO_API_KEY:
        print(f"Email alert to {to_email}: {subject} - {content}")
        return False
    headers = {"api-key": BREVO_API_KEY, "Content-Type": "application/json"}
    data = {
        "sender": {"name": "Moderator", "email": "noreply@example.com"},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": content,
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(BREVO_API_URL, json=data, headers=headers)
            return resp.status_code < 300
        except Exception:
            return False
