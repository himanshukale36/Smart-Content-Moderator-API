from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, EmailStr


class TextModerationRequest(BaseModel):
    email: EmailStr
    text: str


class ImageModerationRequest(BaseModel):
    email: EmailStr
    image_base64: str


class ModerationResponse(BaseModel):
    request_id: int
    classification: str
    confidence: float
    reasoning: Optional[str]
    status: str


class ModerationSummary(BaseModel):
    user: EmailStr
    total_requests: int
    by_classification: Dict[str, int]
    generated_at: datetime
