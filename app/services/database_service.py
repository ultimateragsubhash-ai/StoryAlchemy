"""MongoDB database service."""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for MongoDB operations."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            self.db = self.client.get_default_database()
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def save_story(self, story_data: Dict[str, Any]) -> str:
        """Save a story to the database."""
        story_data["created_at"] = datetime.utcnow()
        
        result = await self.db.stories.insert_one(story_data)
        story_id = str(result.inserted_id)
        
        logger.info(f"Saved story: {story_id}")
        return story_id
    
    async def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Get a story by ID."""
        from bson.objectid import ObjectId
        
        try:
            story = await self.db.stories.find_one({"_id": ObjectId(story_id)})
            if story:
                # Convert ObjectId to string for JSON serialization
                story["_id"] = str(story["_id"])
            return story
        except Exception as e:
            logger.error(f"Error getting story: {e}")
            return None
    
    async def get_recent_stories(
        self,
        limit: int = 20,
        genre: Optional[str] = None,
        tone: Optional[str] = None,
        include_errors: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get recent stories with optional filters."""
        
        query = {}
        
        if not include_errors:
            # Filter out error stories
            query["generated_story"] = {"$exists": True, "$ne": ""}
            query["story_title"] = {"$not": {"$regex": "^Error:"}}
        
        if genre:
            query["preferences.genre"] = genre
        if tone:
            query["preferences.tone"] = tone
        
        logger.info(f"Querying stories with filter: {query}")
        
        cursor = self.db.stories.find(query).sort("created_at", -1).limit(limit)
        stories = await cursor.to_list(length=limit)
        
        logger.info(f"Found {len(stories)} stories")
        
        # Convert ObjectId to string for JSON serialization
        for story in stories:
            if "_id" in story:
                story["_id"] = str(story["_id"])
            # Also convert any nested ObjectIds
            if "story_id" in story and not isinstance(story["story_id"], str):
                story["story_id"] = str(story["story_id"])
        
        return stories
    
    async def save_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Save user feedback."""
        feedback_data["created_at"] = datetime.utcnow()
        
        result = await self.db.feedback.insert_one(feedback_data)
        feedback_id = str(result.inserted_id)
        
        # Update story feedback counts
        await self._update_story_feedback_stats(
            feedback_data["story_id"],
            feedback_data["feedback_type"],
        )
        
        logger.info(f"Saved feedback: {feedback_id}")
        return feedback_id
    
    async def _update_story_feedback_stats(self, story_id: str, feedback_type: str):
        """Update story feedback statistics."""
        from bson.objectid import ObjectId
        
        update_field = f"{feedback_type}_count"
        await self.db.stories.update_one(
            {"_id": ObjectId(story_id)},
            {"$inc": {update_field: 1}},
        )
    
    async def get_pattern_weights(self) -> Dict[str, float]:
        """Get pattern weights from feedback."""
        # Aggregate feedback to calculate pattern scores
        pipeline = [
            {
                "$lookup": {
                    "from": "stories",
                    "localField": "story_id",
                    "foreignField": "_id",
                    "as": "story",
                },
            },
            {"$unwind": "$story"},
            {"$unwind": "$story.retrieved_patterns"},
            {
                "$group": {
                    "_id": "$story.retrieved_patterns.pattern_id",
                    "score": {
                        "$sum": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$feedback_type", "love"]}, "then": 1.0},
                                    {"case": {"$eq": ["$feedback_type", "ok"]}, "then": 0.3},
                                    {"case": {"$eq": ["$feedback_type", "regenerate"]}, "then": -0.5},
                                ],
                                "default": 0,
                            },
                        },
                    },
                    "count": {"$sum": 1},
                },
            },
        ]
        
        weights = {}
        async for doc in self.db.feedback.aggregate(pipeline):
            weights[doc["_id"]] = doc["score"]
        
        return weights
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get platform statistics."""
        
        stories_count = await self.db.stories.count_documents({})
        
        avg_quality = await self.db.stories.aggregate([
            {"$group": {"_id": None, "avg": {"$avg": "$quality_metrics.overall_quality"}}},
        ]).to_list(length=1)
        
        total_cost = await self.db.stories.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$cost_usd"}}},
        ]).to_list(length=1)
        
        love_count = await self.db.stories.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$love_count"}}},
        ]).to_list(length=1)
        
        return {
            "stories_generated": stories_count,
            "average_quality": avg_quality[0]["avg"] if avg_quality else 0.0,
            "total_cost_usd": total_cost[0]["total"] if total_cost else 0.0,
            "total_loves": love_count[0]["total"] if love_count else 0,
        }


# Global service instance
database_service = DatabaseService()
