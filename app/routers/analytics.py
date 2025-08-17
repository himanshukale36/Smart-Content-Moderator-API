from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import async_session
from ..models import ModerationRequest, ModerationResult
from ..schemas import ModerationSummary

router = APIRouter(prefix="/api/v1", tags=["analytics"])


async def get_session():
    async with async_session() as session:
        yield session


@router.get("/analytics/summary", response_model=ModerationSummary)
async def analytics_summary(user: str, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(ModerationResult.classification, func.count(ModerationResult.id))
        .join(ModerationRequest)
        .where(ModerationRequest.user_email == user)
        .group_by(ModerationResult.classification)
    )
    res = await session.execute(stmt)
    counts = {row[0]: row[1] for row in res.all()}
    total = sum(counts.values())
    return ModerationSummary(
        user=user,
        total_requests=total,
        by_classification=counts,
        generated_at=datetime.utcnow(),
    )
