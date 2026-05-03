"""API routes for story generation."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json

from app.models.story import (
    StoryRequest,
    StoryResponse,
    ComparisonRequest,
    ComparisonResponse,
)
from app.agents.orchestrator import orchestrator
from app.services.cache_service import cache_service
from app.services.database_service import database_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stories", tags=["stories"])


def _get_client_ip(request: Request) -> str:
    """Get client IP address."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _hash_ip(ip: str) -> str:
    """Hash IP for privacy."""
    import hashlib
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


@router.post("/generate", response_model=StoryResponse)
async def generate_story(
    request: StoryRequest,
    http_request: Request,
):
    """Generate a single story based on user idea and preferences."""
    
    # Rate limiting
    ip_hash = _hash_ip(_get_client_ip(http_request))
    if not cache_service.check_rate_limit(ip_hash):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )
    
    try:
        logger.info(f"Generating story for idea: {request.idea[:50]}...")
        response = await orchestrator.generate_story(request)
        return response
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate story: {str(e)}",
        )


@router.post("/generate/stream")
async def generate_story_stream(
    request: StoryRequest,
    http_request: Request,
):
    """Generate a story with streaming output (simulated)."""
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        
        # Send status updates
        stages = [
            ("status", "Extracting themes..."),
            ("status", "Retrieving patterns..."),
            ("status", "Crafting narrative..."),
            ("status", "Evaluating quality..."),
        ]
        
        for stage_type, message in stages:
            yield f"event: {stage_type}\ndata: {json.dumps({'message': message})}\n\n"
            await asyncio.sleep(0.5)  # Simulate processing time
        
        # Generate actual story
        try:
            response = await orchestrator.generate_story(request)
            
            # Send final result
            yield f"event: complete\ndata: {json.dumps(response.model_dump())}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    import asyncio
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/generate-comparison", response_model=ComparisonResponse)
async def generate_comparison(
    request: ComparisonRequest,
    http_request: Request,
):
    """Generate 3 stories with different tones for comparison."""
    
    # Rate limiting (comparison costs more)
    ip_hash = _hash_ip(_get_client_ip(http_request))
    # Allow comparison but note it costs 3x
    
    try:
        logger.info(f"Generating tone comparison for idea: {request.idea[:50]}...")
        response = await orchestrator.generate_comparison(request)
        return response
    except Exception as e:
        logger.error(f"Error generating comparison: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate comparison: {str(e)}",
        )


@router.get("/recent")
async def get_recent_stories(
    limit: int = 10,
    genre: str = None,
    tone: str = None,
):
    """Get recent stories for the history page."""
    
    try:
        stories = await database_service.get_recent_stories(
            limit=limit,
            genre=genre,
            tone=tone,
        )
        return {
            "stories": stories,
            "count": len(stories),
        }
    except Exception as e:
        logger.error(f"Error fetching recent stories: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch stories",
        )
