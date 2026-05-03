"""API routes for analytics and stats."""

from fastapi import APIRouter
from app.services.database_service import database_service
from app.services.vector_service import vector_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/stats")
async def get_platform_stats():
    """Get platform-wide statistics."""
    
    try:
        # Get database stats
        db_stats = await database_service.get_stats()
        
        # Get vector DB stats
        pattern_count = await vector_service.get_pattern_count()
        
        return {
            "stories_generated": db_stats.get("stories_generated", 0),
            "average_quality": round(db_stats.get("average_quality", 0), 2),
            "total_cost_usd": round(db_stats.get("total_cost_usd", 0), 2),
            "total_loves": db_stats.get("total_loves", 0),
            "patterns_indexed": pattern_count,
            "cache_enabled": True,
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {
            "stories_generated": 0,
            "average_quality": 0,
            "total_cost_usd": 0,
            "total_loves": 0,
            "patterns_indexed": 0,
            "cache_enabled": False,
        }


@router.get("/pattern-weights")
async def get_pattern_weights():
    """Get current pattern weights based on feedback."""
    
    try:
        weights = await database_service.get_pattern_weights()
        return {
            "pattern_count": len(weights),
            "top_patterns": sorted(
                weights.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10],
        }
    except Exception as e:
        logger.error(f"Error fetching pattern weights: {e}")
        return {"pattern_count": 0, "top_patterns": []}
