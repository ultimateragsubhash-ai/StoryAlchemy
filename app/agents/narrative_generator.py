"""Agent 3: Narrative Generator - Generates the actual story."""

from typing import List
from app.services.llm_client import llm_client
from app.models.story import (
    ThemeExtraction,
    RetrievedPattern,
    StoryPreferences,
)
from app.prompts.story_generation import STORY_GENERATION_PROMPT
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class NarrativeGeneratorAgent:
    """Agent 3: Generates the actual story.
    
    Model: GPT-4o (default) or user-selected
    Cost: $0.015 (GPT-4o) or $0.11 (Claude Opus)
    Time: 10-20 seconds with streaming
    """
    
    def __init__(self):
        self.cost_per_generation = {
            "openai/gpt-4o": 0.015,
            "openai/gpt-4o-mini": 0.005,
            "anthropic/claude-opus": 0.11,
            "anthropic/claude-3-haiku": 0.002,
        }
    
    async def process(
        self,
        idea: str,
        themes: ThemeExtraction,
        patterns: List[RetrievedPattern],
        preferences: StoryPreferences,
    ) -> tuple[str, str, float]:
        """Generate the story.
        
        Returns: (story_text, story_title, cost_usd)
        """
        
        # Ensure model has provider prefix
        model = preferences.get_model_with_prefix()
        logger.info(f"Agent 3: Generating story with model: {model}")
        
        # Build patterns text
        patterns_text = "\n\n".join([
            f"Pattern {i+1}: {p.pattern_name}\n{p.text[:300]}..."
            for i, p in enumerate(patterns)
        ])
        
        # Build prompt
        prompt = STORY_GENERATION_PROMPT.format(
            idea=idea,
            themes=", ".join(themes.themes),
            emotional_arc=themes.emotional_arc,
            patterns=patterns_text,
            tone=preferences.tone,
            length=preferences.length,
            style=preferences.style,
            genre=preferences.genre,
            temperature=preferences.temperature,
        )
        
        messages = [
            {"role": "system", "content": "You are a skilled storyteller who writes engaging, original narratives."},
            {"role": "user", "content": prompt},
        ]
        
        # Call LLM
        try:
            result = await llm_client.generate(
                model=model,
                messages=messages,
                temperature=preferences.temperature,
                max_tokens=4000 if preferences.length == "long" else 2500,
            )
            
            story_text = result["choices"][0]["message"]["content"]
            
            # Extract title (first line if it looks like a title, else generate)
            lines = story_text.strip().split("\n")
            story_title = None
            
            if lines and (lines[0].startswith("#") or lines[0].startswith("**")):
                # Remove markdown formatting
                story_title = lines[0].strip("#* ")
                story_text = "\n".join(lines[1:]).strip()
            else:
                # Generate a title based on content
                story_title = self._generate_title(idea, themes)
            
            # Estimate cost
            input_tokens = result.get("usage", {}).get("prompt_tokens", 1500)
            output_tokens = result.get("usage", {}).get("completion_tokens", 1200)
            cost = llm_client.estimate_cost(
                model,
                input_tokens,
                output_tokens,
            )
            
            word_count = len(story_text.split())
            
            logger.info(f"Agent 3: Generated story: {word_count} words, ${cost:.4f}")
            
            return story_text, story_title, cost
            
        except Exception as e:
            logger.error(f"Agent 3 error: {e}")
            # Return fallback on error
            return (
                f"Once upon a time, a story about '{idea}' would have appeared here. "
                f"Unfortunately, an error occurred during generation.",
                "Error: Story Generation Failed",
                0.0,
            )
    
    def _generate_title(self, idea: str, themes: ThemeExtraction) -> str:
        """Generate a title based on idea and themes."""
        # Simple title generation based on themes
        if themes.themes:
            return f"The {themes.themes[0].title()} Story"
        return "Untitled Story"
    
    def estimate_cost(self, model: str) -> float:
        """Return estimated cost for this agent."""
        # Try direct lookup first
        if model in self.cost_per_generation:
            return self.cost_per_generation[model]
        # Try unprefixed version
        if "/" in model:
            unprefixed = model.split("/")[1]
            if unprefixed in self.cost_per_generation:
                return self.cost_per_generation[unprefixed]
        return 0.015  # Default
