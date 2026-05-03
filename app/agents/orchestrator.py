"""Orchestrator - Coordinates all 5 agents in the pipeline."""

import time
import asyncio
from typing import Dict, Any, List
from datetime import datetime

from app.models.story import (
    StoryRequest,
    StoryResponse,
    ComparisonRequest,
    ComparisonResponse,
    ToneComparison,
)
from app.agents.theme_extractor import ThemeExtractorAgent
from app.agents.pattern_retriever import PatternRetrieverAgent
from app.agents.narrative_generator import NarrativeGeneratorAgent
from app.agents.quality_critic import QualityCriticAgent
from app.agents.memory_manager import MemoryManagerAgent
from app.services.cache_service import cache_service
from app.services.database_service import database_service
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates the 5-agent pipeline for story generation."""
    
    def __init__(self):
        self.agent1 = ThemeExtractorAgent()
        self.agent2 = PatternRetrieverAgent()
        self.agent3 = NarrativeGeneratorAgent()
        self.agent4 = QualityCriticAgent()
        self.agent5 = MemoryManagerAgent()
    
    async def generate_story(
        self,
        request: StoryRequest,
        cache_check: bool = True,
    ) -> StoryResponse:
        """Run the full 5-agent pipeline to generate a story."""
        
        start_time = time.time()
        total_cost = 0.0
        cache_hit = False
        
        # Check cache first
        if cache_check and cache_service.enabled:
            cached = cache_service.get(
                request.idea,
                request.preferences.model_dump(),
            )
            if cached:
                logger.info("Cache hit - returning cached story")
                cache_hit = True
                # Convert cached data to response
                return StoryResponse(
                    story_id=cached.get("story_id", "cached"),
                    idea=request.idea,
                    preferences=request.preferences,
                    extracted_themes=cached.get("themes", {}),
                    retrieved_patterns=[],
                    generated_story=cached.get("story", ""),
                    story_title=cached.get("title"),
                    word_count=len(cached.get("story", "").split()),
                    quality_metrics=cached.get("quality_score", 0),
                    generation_time_ms=50,
                    cost_usd=0.0,
                    model_used=cached.get("model_used", ""),
                    cache_hit=True,
                )
        
        # AGENT 1: Theme Extractor
        logger.info("=== Agent 1: Theme Extractor ===")
        themes = await self.agent1.process(request.idea)
        total_cost += self.agent1.estimate_cost()
        
        # Use user's genre preference if specified, otherwise use extracted
        genre = request.preferences.genre
        if genre == "general":
            genre = themes.genre_hint
        
        # AGENT 2: Pattern Retriever
        logger.info("=== Agent 2: Pattern Retriever ===")
        patterns = await self.agent2.process(themes, genre)
        total_cost += self.agent2.estimate_cost()
        
        # AGENT 3: Narrative Generator
        logger.info("=== Agent 3: Narrative Generator ===")
        story_text, story_title, gen_cost = await self.agent3.process(
            idea=request.idea,
            themes=themes,
            patterns=patterns,
            preferences=request.preferences,
        )
        total_cost += gen_cost
        
        # AGENT 4: Quality Critic
        logger.info("=== Agent 4: Quality Critic ===")
        quality = await self.agent4.process(
            story=story_text,
            idea=request.idea,
            preferences=request.preferences,
        )
        total_cost += self.agent4.estimate_cost()
        
        # Calculate timing
        generation_time_ms = int((time.time() - start_time) * 1000)
        word_count = len(story_text.split())
        
        # Prepare story data for saving
        story_data = {
            "idea": request.idea,
            "preferences": request.preferences.model_dump(),
            "extracted_themes": themes.model_dump(),
            "retrieved_patterns": [p.model_dump() for p in patterns],
            "generated_story": story_text,
            "story_title": story_title,
            "word_count": word_count,
            "quality_metrics": quality.model_dump(),
            "generation_time_ms": generation_time_ms,
            "cost_usd": total_cost,
            "model_used": request.preferences.model,
        }
        
        # AGENT 5: Memory Manager
        logger.info("=== Agent 5: Memory Manager ===")
        story_id = await self.agent5.process(story_data)
        total_cost += self.agent5.estimate_cost()
        
        # Build response
        response = StoryResponse(
            story_id=story_id,
            idea=request.idea,
            preferences=request.preferences,
            extracted_themes=themes,
            retrieved_patterns=patterns,
            generated_story=story_text,
            story_title=story_title,
            word_count=word_count,
            quality_metrics=quality,
            generation_time_ms=generation_time_ms,
            cost_usd=total_cost,
            model_used=request.preferences.model,
            cache_hit=cache_hit,
        )
        
        logger.info(f"=== Pipeline Complete ===")
        logger.info(f"Time: {generation_time_ms}ms | Cost: ${total_cost:.4f}")
        
        return response
    
    async def generate_comparison(
        self,
        request: ComparisonRequest,
    ) -> ComparisonResponse:
        """Generate 3 stories with different tones for comparison."""
        import random
        
        start_time = time.time()
        total_cost = 0.0
        
        logger.info("=== Starting Tone Comparison ===")
        
        # Available tones for random selection
        available_tones = ["hopeful", "dark", "humorous", "melancholic", "mysterious", "neutral", "suspenseful", "whimsical"]
        
        # If no tones provided, randomly select 3
        comparison_tones = request.comparison_tones
        if not comparison_tones or len(comparison_tones) == 0:
            comparison_tones = random.sample(available_tones, 3)
            logger.info(f"Randomly selected tones: {comparison_tones}")
        
        # Override tones in preferences for each comparison
        comparisons = []
        all_pattern_ids = set()
        
        for tone in comparison_tones:
            logger.info(f"Generating story with tone: {tone}")
            
            # Create modified request with this tone
            from copy import deepcopy
            modified_prefs = deepcopy(request.preferences)
            modified_prefs.tone = tone
            
            single_request = StoryRequest(
                idea=request.idea,
                preferences=modified_prefs,
            )
            
            # Generate story (disable cache for comparison)
            story = await self.generate_story(single_request, cache_check=False)
            total_cost += story.cost_usd
            
            # Track patterns
            for p in story.retrieved_patterns:
                all_pattern_ids.add(p.pattern_id)
            
            comparisons.append(ToneComparison(
                tone=tone,
                story=story,
            ))
        
        total_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"=== Comparison Complete ===")
        logger.info(f"Time: {total_time_ms}ms | Cost: ${total_cost:.4f}")
        
        return ComparisonResponse(
            idea=request.idea,
            comparisons=comparisons,
            patterns_used_across_all=list(all_pattern_ids),
            total_cost_usd=total_cost,
            total_time_ms=total_time_ms,
        )


# Global orchestrator instance
orchestrator = AgentOrchestrator()
