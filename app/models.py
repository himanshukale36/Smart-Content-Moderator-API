from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .db import Base


class ModerationRequest(Base):
    __tablename__ = "moderation_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    content_type = Column(String)
    content_hash = Column(String, unique=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    result = relationship("ModerationResult", back_populates="request", uselist=False)
    notifications = relationship("NotificationLog", back_populates="request")


class ModerationResult(Base):
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"))
    classification = Column(String)
    confidence = Column(Float)
    reasoning = Column(Text)
    llm_response = Column(Text)

    request = relationship("ModerationRequest", back_populates="result")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"))
    channel = Column(String)
    status = Column(String)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("ModerationRequest", back_populates="notifications")
