"""Feedback-related Pydantic models."""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class FeedbackType(str, Enum):
    LOVE = "love"
    OK = "ok"
    REGENERATE = "regenerate"


class RegenerateReason(str, Enum):
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    OFF_TOPIC = "off_topic"
    POOR_QUALITY = "poor_quality"
    OTHER = "other"


class FeedbackRequest(BaseModel):
    story_id: str
    feedback_type: FeedbackType
    regenerate_reason: Optional[RegenerateReason] = None
    custom_comment: Optional[str] = None
    reading_time_seconds: Optional[int] = None
    did_copy: bool = False
    did_download: bool = False
