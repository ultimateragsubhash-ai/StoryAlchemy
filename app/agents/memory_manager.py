"""Agent 5: Memory Manager - Saves stories and caches results."""

from typing import Dict, Any
from datetime import datetime
from app.services.database_service import database_service
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)


class MemoryManagerAgent:
    """Agent 5: Saves stories, caches results, updates metrics.
    
    Tech: MongoDB + Redis (no LLM)
    Cost: $0.00
    Time: ~100ms
    """
    
    def __init__(self):
        pass
    
    async def process(
        self,
        story_data: Dict[str, Any],
    ) -> str:
        """Save story to database and cache.
        
        Returns: story_id
        """
        
        logger.info("Agent 5: Saving story to memory")
        
        try:
            # 1. Save to MongoDB (permanent)
            story_id = await database_service.save_story(story_data)
            
            # 2. Cache in Redis (for quick retrieval)
            cache_key_data = {
                "idea": story_data.get("idea", ""),
                "preferences": story_data.get("preferences", {}),
            }
            
            cache_data = {
                "story_id": story_id,
                "story": story_data.get("generated_story", ""),
                "title": story_data.get("story_title"),
                "quality_score": story_data.get("quality_metrics", {}).get("overall_quality", 0),
                "themes": story_data.get("extracted_themes", {}),
                "model_used": story_data.get("model_used", ""),
            }
            
            cache_service.set(
                cache_key_data["idea"],
                cache_key_data["preferences"],
                cache_data,
            )
            
            logger.info(f"Agent 5: Story saved with ID: {story_id}")
            return story_id
            
        except Exception as e:
            logger.error(f"Agent 5 error: {e}")
            # Return placeholder ID on error
            return "error-saving-story"
    
    async def update_global_stats(self) -> Dict[str, Any]:
        """Update and return global statistics."""
        try:
            stats = await database_service.get_stats()
            logger.info(f"Agent 5: Global stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Agent 5 stats error: {e}")
            return {
                "stories_generated": 0,
                "average_quality": 0.0,
                "total_cost_usd": 0.0,
                "total_loves": 0,
            }
    
    def estimate_cost(self) -> float:
        """Return estimated cost for this agent (always free)."""
        return 0.0
