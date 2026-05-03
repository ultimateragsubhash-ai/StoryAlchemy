"""API routes for feedback."""

from fastapi import APIRouter, HTTPException, Request
import hashlib

from app.models.feedback import FeedbackRequest, FeedbackType, RegenerateReason
from app.services.database_service import database_service
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _get_client_ip(request: Request) -> str:
    """Get client IP address."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _hash_ip(ip: str) -> str:
    """Hash IP for privacy."""
    return hashlib.sha256(ip.encode()).hexdigest()


@router.post("/submit")
async def submit_feedback(
    request: FeedbackRequest,
    http_request: Request,
):
    """Submit feedback for a story."""
    
    try:
        # Get IP hash for pseudo-anonymous tracking
        ip_hash = _hash_ip(_get_client_ip(http_request))
        user_agent = http_request.headers.get("User-Agent", "")
        
        # Prepare feedback data
        feedback_data = {
            "story_id": request.story_id,
            "feedback_type": request.feedback_type.value,
            "regenerate_reason": request.regenerate_reason.value if request.regenerate_reason else None,
            "custom_comment": request.custom_comment,
            "ip_hash": ip_hash,
            "user_agent": user_agent,
            # Implicit signals
            "reading_time_seconds": request.reading_time_seconds,
            "did_copy": request.did_copy,
            "did_download": request.did_download,
        }
        
        # Save to database
        feedback_id = await database_service.save_feedback(feedback_data)
        
        # Update pattern weights based on feedback
        if request.feedback_type == FeedbackType.LOVE:
            await _boost_patterns(request.story_id)
        elif request.feedback_type == FeedbackType.REGENERATE:
            await _penalize_patterns(request.story_id, request.regenerate_reason)
        
        logger.info(f"Feedback saved: {feedback_id} ({request.feedback_type.value})")
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Thank you for your feedback!",
        }
        
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save feedback",
        )


async def _boost_patterns(story_id: str):
    """Boost pattern weights for loved stories."""
    # Implementation: Update pattern weights in database
    logger.info(f"Boosting patterns for story: {story_id}")
    # This would update a pattern_weights collection
    pass


async def _penalize_patterns(
    story_id: str,
    reason: RegenerateReason = None,
):
    """Penalize patterns for regenerated stories."""
    logger.info(f"Penalizing patterns for story: {story_id}, reason: {reason}")
    # This would decrease pattern weights
    pass


@router.get("/stats/{story_id}")
async def get_story_feedback_stats(story_id: str):
    """Get feedback statistics for a specific story."""
    
    try:
        story = await database_service.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return {
            "story_id": story_id,
            "love_count": story.get("love_count", 0),
            "ok_count": story.get("ok_count", 0),
            "regenerate_count": story.get("regenerate_count", 0),
            "quality_score": story.get("quality_metrics", {}).get("overall_quality", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feedback stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch feedback stats",
        )
