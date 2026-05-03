"""Agent 1: Theme Extractor - Extracts themes from user ideas."""

from app.services.llm_client import llm_client
from app.models.story import ThemeExtraction
from app.prompts.theme_extraction import THEME_EXTRACTION_PROMPT
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ThemeExtractorAgent:
    """Agent 1: Extracts themes, emotional arcs, and genre hints from story ideas.
    
    Model: GPT-4o-mini (cheap, fast)
    Cost: ~$0.002 per request
    Time: ~1-2 seconds
    """
    
    def __init__(self):
        self.model = settings.cheap_model
        self.cost_estimate = 0.002
    
    async def process(self, idea: str) -> ThemeExtraction:
        """Extract themes from the user's story idea."""
        
        logger.info(f"Agent 1: Extracting themes from idea: {idea[:50]}...")
        
        try:
            # Build prompt
            prompt = THEME_EXTRACTION_PROMPT.format(idea=idea)
            
            messages = [
                {"role": "system", "content": "You are a literary analysis expert."},
                {"role": "user", "content": prompt},
            ]
            
            # Log the messages for debugging
            logger.info(f"Agent 1: Messages prepared: {len(messages)} messages")
            for i, m in enumerate(messages):
                content_preview = m.get('content', '')[:100].replace('\n', '\\n')
                logger.info(f"Agent 1: Message {i}: role={m.get('role')}, content={content_preview}...")
            
            logger.info(f"Agent 1: Calling LLM with model={self.model}")
            
            # Call LLM
            result = await llm_client.generate_json(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                default_structure={
                    "themes": ["general"],
                    "emotional_arc": "neutral",
                    "genre_hint": "general",
                },
            )
            
            logger.info(f"Agent 1: Got result from LLM: {type(result)}")
            
            # Validate response - use safe .get() access
            if not isinstance(result, dict):
                logger.error(f"Agent 1: result is not dict, it's {type(result)}")
                result = {}
            
            themes = result.get("themes", [])
            emotional_arc = result.get("emotional_arc", "neutral")
            genre_hint = result.get("genre_hint", "general")
            
            # Ensure themes is a list
            if not isinstance(themes, list):
                themes = [str(themes)] if themes else ["general"]
            
            extraction = ThemeExtraction(
                themes=themes[:5],  # Max 5 themes
                emotional_arc=emotional_arc,
                genre_hint=genre_hint,
            )
            
            logger.info(f"Agent 1: Extracted {len(extraction.themes)} themes: {extraction.themes}")
            return extraction
            
        except Exception as e:
            logger.error(f"Agent 1 error: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Agent 1 traceback: {traceback.format_exc()}")
            # Return default extraction on error
            return ThemeExtraction(
                themes=["general"],
                emotional_arc="neutral",
                genre_hint="general",
            )
    
    def estimate_cost(self) -> float:
        """Return estimated cost for this agent."""
        return self.cost_estimate
