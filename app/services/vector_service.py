"""Vector database service using Qdrant."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.embedding_service import embedding_service
import logging

logger = logging.getLogger(__name__)


class VectorService:
    """Service for vector database operations."""
    
    def __init__(self):
        self.available = False
        self.client = None
        self.collection_name = settings.qdrant_collection
        
        # Skip if no Qdrant URL configured
        if not settings.qdrant_url:
            logger.warning("No QDRANT_URL configured. Vector search disabled.")
            return
        
        try:
            logger.info(f"Connecting to Qdrant at: {settings.qdrant_url}")
            
            # Check if local (localhost/127.0.0.1) - use no SSL
            is_local = any(x in settings.qdrant_url for x in ['localhost', '127.0.0.1', '0.0.0.0'])
            
            if is_local:
                logger.info("Detected local Qdrant - using HTTP without SSL")
                # Parse host and port from URL
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(settings.qdrant_url)
                    host = parsed.hostname or 'localhost'
                    port = parsed.port or 6333
                except:
                    host = 'localhost'
                    port = 6333
                
                logger.info(f"Connecting to {host}:{port}")
                self.client = QdrantClient(host=host, port=port, https=False)
            else:
                # Cloud Qdrant with SSL
                self.client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                    timeout=10,
                )
            
            self._ensure_collection()
            self.available = True
            logger.info("VectorService initialized successfully")
        except Exception as e:
            logger.warning(f"Qdrant connection failed: {e}")
            logger.warning("Vector search disabled. Using BM25 only.")
            self.available = False
    
    def _ensure_collection(self):
        """Ensure the collection exists."""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_service.dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("Collection created successfully")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
            raise
    
    async def search(
        self,
        query_text: str,
        limit: int = 50,
        filter_conditions: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        
        if not self.available:
            logger.debug("Vector search not available. Returning empty results.")
            return []
        
        try:
            # Embed query
            query_vector = embedding_service.embed_single(query_text)
            
            # Try different Qdrant API versions
            try:
                # Qdrant client 1.x API
                from qdrant_client.models import SearchRequest
                
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    query_filter=filter_conditions,
                    with_payload=True,
                )
            except (AttributeError, TypeError) as api_error:
                # Fallback to older API or different method
                logger.warning(f"Qdrant search API failed: {api_error}, trying query_points...")
                from qdrant_client.models import QueryRequest
                
                # Try using query_points method if available
                if hasattr(self.client, 'query_points'):
                    results = self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        limit=limit,
                        with_payload=True,
                    )
                else:
                    # Last resort - try search with different params
                    results = self.client.search(
                        collection_name=self.collection_name,
                        vector=query_vector,
                        limit=limit,
                        with_payload=True,
                    )
            
            # Handle different result formats (object with .id or tuple)
            parsed_results = []
            for r in results:
                try:
                    if isinstance(r, tuple):
                        # Tuple format: (id, score, payload)
                        parsed_results.append({
                            "id": str(r[0]),
                            "score": r[1] if len(r) > 1 else 0.0,
                            "text": r[2].get("text", "") if len(r) > 2 and isinstance(r[2], dict) else "",
                            "pattern_name": r[2].get("pattern_name", "") if len(r) > 2 and isinstance(r[2], dict) else "",
                            "pattern_type": r[2].get("pattern_type", "") if len(r) > 2 and isinstance(r[2], dict) else "",
                            "genre": r[2].get("genre", "") if len(r) > 2 and isinstance(r[2], dict) else "",
                            "emotional_arc": r[2].get("emotional_arc", "") if len(r) > 2 and isinstance(r[2], dict) else "",
                            "category": r[2].get("category", "") if len(r) > 2 and isinstance(r[2], dict) else "",
                        })
                    else:
                        # Object format with .id, .score, .payload
                        parsed_results.append({
                            "id": str(r.id),
                            "score": r.score,
                            "text": r.payload.get("text", "") if hasattr(r, 'payload') and r.payload else "",
                            "pattern_name": r.payload.get("pattern_name", "") if hasattr(r, 'payload') and r.payload else "",
                            "pattern_type": r.payload.get("pattern_type", "") if hasattr(r, 'payload') and r.payload else "",
                            "genre": r.payload.get("genre", "") if hasattr(r, 'payload') and r.payload else "",
                            "emotional_arc": r.payload.get("emotional_arc", "") if hasattr(r, 'payload') and r.payload else "",
                            "category": r.payload.get("category", "") if hasattr(r, 'payload') and r.payload else "",
                        })
                except Exception as parse_error:
                    logger.warning(f"Failed to parse result item: {parse_error}")
                    continue
            
            return parsed_results
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def upsert_patterns(
        self,
        patterns: List[Dict[str, Any]],
    ) -> bool:
        """Upsert patterns to the vector database."""
        
        if not self.available:
            logger.warning("Vector service not available. Skipping upsert.")
            return False
        
        try:
            import uuid
            
            # Generate embeddings
            texts = [p["text"] for p in patterns]
            embeddings = embedding_service.embed(texts)
            
            # Create points with UUIDs as IDs (Qdrant requirement)
            points = []
            for i, p in enumerate(patterns):
                # Generate UUID from the pattern's string ID, or create a new one
                original_id = p.get("id", "")
                if original_id:
                    # Generate deterministic UUID from string ID
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, original_id))
                else:
                    point_id = str(uuid.uuid4())
                
                points.append(PointStruct(
                    id=point_id,
                    vector=embeddings[i],
                    payload={
                        "text": p["text"],
                        "pattern_name": p.get("pattern_name", ""),
                        "pattern_type": p.get("pattern_type", ""),
                        "genre": p.get("genre", ""),
                        "emotional_arc": p.get("emotional_arc", ""),
                        "category": p.get("category", ""),
                        "source_document_id": p.get("source_document_id", ""),
                        "original_id": original_id,  # Store original ID in payload
                    },
                ))
            
            # Upsert in batches to avoid payload too large errors
            batch_size = 10
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully upserted {len(patterns)} patterns to Qdrant")
            return True
        except Exception as e:
            logger.error(f"Error upserting patterns: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def get_pattern_count(self) -> int:
        """Get total number of patterns in collection."""
        if not self.available:
            return 0
        
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception as e:
            logger.error(f"Error getting pattern count: {e}")
            return 0


# Global service instance
vector_service = VectorService()
