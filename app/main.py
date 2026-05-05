"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.api.routes import api_router
from app.services.database_service import database_service
from app.services.cache_service import cache_service
from app.services.bm25_service import bm25_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="StoryAlchemy API",
    description="AI-powered narrative generation with hybrid RAG",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("=" * 50)
    logger.info("Starting StoryAlchemy API...")
    logger.info("=" * 50)
    
    # Connect to MongoDB - CRITICAL for history feature
    try:
        await database_service.connect()
        if database_service.client is not None:
            logger.info("✅ MongoDB connected successfully")
        else:
            logger.error("❌ MongoDB client is None after connection attempt")
            logger.error("   Stories will be generated but NOT saved to history!")
            logger.error("   Check your MONGODB_URL environment variable")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.error("   Stories will be generated but NOT saved to history!")
        logger.error("   Check your MONGODB_URL environment variable in Railway dashboard")
    
    # Connect to Redis - optional (caching only)
    try:
        cache_service.connect()
        if cache_service.enabled:
            logger.info("✅ Redis connected successfully")
        else:
            logger.warning("⚠️ Redis not connected - caching disabled (stories will still save to MongoDB)")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        logger.warning("   Caching disabled - stories will still save to MongoDB")
    
    # Load seed patterns into BM25 (in-memory) and Qdrant (vector DB)
    try:
        from app.data.seed_patterns import PLOT_STRUCTURES, CHARACTER_ARCHETYPES
        from app.services.vector_service import vector_service
        
        all_patterns = []
        all_metadata = []
        
        for pattern in PLOT_STRUCTURES:
            all_patterns.append(pattern["text"])
            all_metadata.append({
                "id": pattern["id"],
                "pattern_name": pattern["name"],
                "pattern_type": pattern["type"],
                "category": "plot_structure",
                "text": pattern["text"],
            })
        
        for pattern in CHARACTER_ARCHETYPES:
            all_patterns.append(pattern["text"])
            all_metadata.append({
                "id": pattern["id"],
                "pattern_name": pattern["name"],
                "pattern_type": pattern["type"],
                "category": "character",
                "text": pattern["text"],
            })
        
        # Index in BM25 (sparse)
        bm25_service.index_documents(all_patterns, all_metadata)
        logger.info(f"Loaded {len(all_patterns)} patterns into BM25")
        
        # Index in Qdrant (dense vectors)
        if vector_service.available:
            success = await vector_service.upsert_patterns(all_metadata)
            if success:
                logger.info(f"Successfully upserted {len(all_metadata)} patterns into Qdrant")
            else:
                logger.warning("Failed to upsert patterns into Qdrant")
        else:
            logger.warning("Vector service not available - patterns not stored in Qdrant")
    except Exception as e:
        logger.warning(f"Failed to load seed patterns: {e}")
        import traceback
        logger.warning(f"Traceback: {traceback.format_exc()}")
    
    logger.info("StoryAlchemy API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down StoryAlchemy API...")
    
    try:
        await database_service.disconnect()
    except:
        pass
    
    try:
        cache_service.disconnect()
    except:
        pass
    
    logger.info("StoryAlchemy API shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "StoryAlchemy API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "mongodb": database_service.client is not None,
            "redis": cache_service.client is not None and cache_service.enabled,
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.env == "development",
    )
