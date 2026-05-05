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
    
    def _extract_db_name(self, url: str) -> str:
        """Extract database name from MongoDB URL or return default."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        # If path exists and is not empty or just '/', use it as db name
        if parsed.path and parsed.path not in ('', '/', '/?'):
            # Remove leading slash if present
            db_name = parsed.path.lstrip('/').split('?')[0]
            if db_name:
                return db_name
        
        # Default database name
        return "storyalchemy"
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive info in MongoDB URL for logging."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.password:
                masked = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
                return masked
            return url
        except:
            return "[invalid-url-format]"
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            logger.info(f"Attempting MongoDB connection...")
            logger.info(f"MongoDB URL (masked): {self._mask_url(settings.mongodb_url)}")
            
            # Extract database name from URL (or use default)
            db_name = self._extract_db_name(settings.mongodb_url)
            logger.info(f"Using database: {db_name}")
            
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
            )
            
            # Verify connection by pinging the server
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB server ping successful")
            
            # Get database - either from URL or use default
            self.db = self.client[db_name]
            
            # Verify access by listing collections
            collections = await self.db.list_collection_names()
            
            logger.info(f"✅ Connected to MongoDB successfully")
            logger.info(f"   Database: {db_name}")
            logger.info(f"   Collections: {collections}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            self.client = None
            self.db = None
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def save_story(self, story_data: Dict[str, Any]) -> str:
        """Save a story to the database."""
        if self.db is None:
            logger.error("Cannot save story: MongoDB not connected")
            raise RuntimeError("Database not connected - story cannot be saved")
        
        story_data["created_at"] = datetime.utcnow()
        
        try:
            result = await self.db.stories.insert_one(story_data)
            story_id = str(result.inserted_id)
            logger.info(f"Saved story: {story_id}")
            return story_id
        except Exception as e:
            logger.error(f"Failed to save story to MongoDB: {e}")
            raise
    
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
        
        if self.db is None:
            logger.error("Cannot get recent stories: MongoDB not connected")
            raise RuntimeError("Database not connected")
        
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
        logger.info(f"Database name: {self.db.name}")
        
        try:
            # First, check how many total stories exist
            total_count = await self.db.stories.count_documents({})
            logger.info(f"Total stories in collection: {total_count}")
            
            cursor = self.db.stories.find(query).sort("created_at", -1).limit(limit)
            stories = await cursor.to_list(length=limit)
            
            logger.info(f"Found {len(stories)} stories matching query")
            
            # Convert ObjectId to string for JSON serialization
            for story in stories:
                if "_id" in story:
                    story["_id"] = str(story["_id"])
                # Also convert any nested ObjectIds
                if "story_id" in story and not isinstance(story["story_id"], str):
                    story["story_id"] = str(story["story_id"])
            
            return stories
        except Exception as e:
            logger.error(f"Error querying stories: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise
    
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
        
        if self.db is None:
            logger.error("Cannot get stats: MongoDB not connected")
            return {
                "stories_generated": 0,
                "average_quality": 0.0,
                "total_cost_usd": 0.0,
                "total_loves": 0,
            }
        
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
