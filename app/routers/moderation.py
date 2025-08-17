import hashlib

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import async_session
from ..models import ModerationRequest, ModerationResult, NotificationLog
from ..schemas import (
    ImageModerationRequest,
    ModerationResponse,
    TextModerationRequest,
)
from ..services.moderation import analyze_image, analyze_text
from ..services.notification import send_email_alert, send_slack_alert

router = APIRouter(prefix="/api/v1", tags=["moderation"])


async def get_session():
    async with async_session() as session:
        yield session


@router.post("/moderate/text", response_model=ModerationResponse)
async def moderate_text(
    payload: TextModerationRequest, session: AsyncSession = Depends(get_session)
):
    content_hash = hashlib.sha256(payload.text.encode()).hexdigest()
    req = ModerationRequest(
        user_email=payload.email,
        content_type="text",
        content_hash=content_hash,
        status="pending",
    )
    session.add(req)
    await session.commit()
    await session.refresh(req)

    classification, confidence, reasoning, raw = await analyze_text(payload.text)

    req.status = "completed"
    result = ModerationResult(
        request_id=req.id,
        classification=classification,
        confidence=confidence,
        reasoning=reasoning,
        llm_response=raw,
    )
    session.add(result)
    await session.commit()

    if classification != "safe":
        message = f"Inappropriate content detected: {classification}"
        slack_status = await send_slack_alert(message)
        session.add(
            NotificationLog(
                request_id=req.id,
                channel="slack",
                status="sent" if slack_status else "failed",
            )
        )
        email_status = await send_email_alert(
            payload.email, "Content moderation alert", message
        )
        session.add(
            NotificationLog(
                request_id=req.id,
                channel="email",
                status="sent" if email_status else "failed",
            )
        )
        await session.commit()

    return ModerationResponse(
        request_id=req.id,
        classification=classification,
        confidence=confidence,
        reasoning=reasoning,
        status=req.status,
    )


@router.post("/moderate/image")
async def moderate_image(
    payload: ImageModerationRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    content_hash = hashlib.sha256(payload.image_base64.encode()).hexdigest()
    req = ModerationRequest(
        user_email=payload.email,
        content_type="image",
        content_hash=content_hash,
        status="pending",
    )
    session.add(req)
    await session.commit()
    await session.refresh(req)

    background_tasks.add_task(
        process_image_moderation, req.id, payload.image_base64, payload.email
    )

    return {"request_id": req.id, "status": "processing"}


async def process_image_moderation(request_id: int, image_b64: str, email: str):
    async with async_session() as session:
        classification, confidence, reasoning, raw = await analyze_image(image_b64)
        req = await session.get(ModerationRequest, request_id)
        req.status = "completed"
        result = ModerationResult(
            request_id=request_id,
            classification=classification,
            confidence=confidence,
            reasoning=reasoning,
            llm_response=raw,
        )
        session.add(result)
        await session.commit()

        if classification != "safe":
            message = f"Inappropriate image detected: {classification}"
            slack_status = await send_slack_alert(message)
            session.add(
                NotificationLog(
                    request_id=request_id,
                    channel="slack",
                    status="sent" if slack_status else "failed",
                )
            )
            email_status = await send_email_alert(
                email, "Content moderation alert", message
            )
            session.add(
                NotificationLog(
                    request_id=request_id,
                    channel="email",
                    status="sent" if email_status else "failed",
                )
            )
            await session.commit()
