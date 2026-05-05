"""Redis cache service for semantic caching."""

import redis
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import timedelta
from app.config import settings
from app.services.embedding_service import embedding_service
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Service for Redis caching."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.enabled = settings.enable_semantic_cache
        self.ttl = settings.cache_ttl_seconds
    
    def connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            # Test connection
            self.client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
    
    def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from Redis")
    
    def _generate_cache_key(self, idea: str, preferences: Dict[str, Any]) -> str:
        """Generate cache key from idea and preferences.
        
        Uses simple text hash for exact matching (not semantic similarity).
        This ensures identical inputs produce identical cache keys.
        """
        # Normalize the idea text (lowercase, strip whitespace)
        normalized_idea = idea.strip().lower()
        
        # Create a deterministic string representation of preferences
        # Sort keys to ensure consistent ordering
        prefs_str = json.dumps(preferences, sort_keys=True, separators=(',', ':'))
        
        # Combine and hash
        combined = f"{normalized_idea}:{prefs_str}"
        hash_key = hashlib.md5(combined.encode('utf-8')).hexdigest()
        
        logger.debug(f"Cache key for idea '{idea[:30]}...': {hash_key[:16]}")
        
        return f"cache:story:{hash_key}"
    
    def get(self, idea: str, preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached story if available."""
        if not self.enabled or not self.client:
            logger.debug(f"Cache disabled or client not available. enabled={self.enabled}, client={self.client}")
            return None
        
        try:
            key = self._generate_cache_key(idea, preferences)
            cached = self.client.get(key)
            
            if cached:
                logger.info(f"✅ Cache HIT for idea: '{idea[:50]}...' (key: {key[:20]}...)")
                return json.loads(cached)
            else:
                logger.info(f"❌ Cache MISS for idea: '{idea[:50]}...' (key: {key[:20]}...)")
            
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(
        self,
        idea: str,
        preferences: Dict[str, Any],
        story_data: Dict[str, Any],
    ) -> bool:
        """Cache a story."""
        if not self.enabled or not self.client:
            logger.debug(f"Cache set skipped - disabled or no client")
            return False
        
        try:
            key = self._generate_cache_key(idea, preferences)
            
            # Add metadata
            story_data["cache_hit"] = True
            
            self.client.setex(
                key,
                timedelta(seconds=self.ttl),
                json.dumps(story_data),
            )
            
            logger.info(f"💾 Cached story with key: {key[:20]}... (TTL: {self.ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def check_rate_limit(self, ip_hash: str) -> bool:
        """Check if request is within rate limit."""
        if not self.enabled or not self.client:
            return True
        
        try:
            key = f"ratelimit:{ip_hash}"
            current = self.client.get(key)
            
            if current is None:
                # First request
                self.client.setex(key, timedelta(hours=1), 1)
                return True
            
            count = int(current)
            if count >= settings.max_requests_per_hour:
                return False
            
            # Increment
            self.client.incr(key)
            return True
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True


# Global service instance
cache_service = CacheService()
