"""API routes package."""

from fastapi import APIRouter

from app.api.routes import stories, feedback, analytics, knowledge_base

api_router = APIRouter()

api_router.include_router(stories.router)
api_router.include_router(feedback.router)
api_router.include_router(analytics.router)
api_router.include_router(knowledge_base.router)
