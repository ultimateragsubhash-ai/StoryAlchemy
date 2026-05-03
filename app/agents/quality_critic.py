"""Agent 4: Quality Critic - Evaluates story quality (simplified, no loop)."""

from app.services.llm_client import llm_client
from app.models.story import QualityMetrics, StoryPreferences
from app.prompts.quality_evaluation import QUALITY_EVALUATION_PROMPT
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class QualityCriticAgent:
    """Agent 4: Evaluates story quality.
    
    Model: GPT-4o-mini (cheap for evaluation)
    Cost: ~$0.002 per evaluation
    Time: ~1-2 seconds
    
    SIMPLIFIED: No regeneration loop - just evaluates and logs quality.
    """
    
    def __init__(self):
        self.model = settings.cheap_model
        self.cost_estimate = 0.002
    
    async def process(
        self,
        story: str,
        idea: str,
        preferences: StoryPreferences,
    ) -> QualityMetrics:
        """Evaluate story quality.
        
        SIMPLIFIED: Returns quality metrics without looping back.
        """
        
        logger.info("Agent 4: Evaluating story quality")
        
        # Build prompt
        prompt = QUALITY_EVALUATION_PROMPT.format(
            story=story[:2000],  # Truncate for evaluation
            idea=idea,
            requested_tone=preferences.tone,
            requested_length=preferences.length,
            requested_style=preferences.style,
            requested_genre=preferences.genre,
        )
        
        messages = [
            {"role": "system", "content": "You are a literary critic who evaluates stories objectively."},
            {"role": "user", "content": prompt},
        ]
        
        # Call LLM
        try:
            result = await llm_client.generate_json(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=500,
                default_structure={
                    "narrative_coherence": 0.7,
                    "emotional_impact": 0.7,
                    "overall_quality": 0.7,
                    "length_appropriate": True,
                    "tone_aligned": True,
                    "feedback": "Evaluation unavailable",
                },
            )
            
            # Validate and create QualityMetrics
            coherence = result.get("narrative_coherence", 0.7)
            impact = result.get("emotional_impact", 0.7)
            overall = result.get("overall_quality", (coherence + impact) / 2)
            
            metrics = QualityMetrics(
                overall_quality=round(overall, 2),
                narrative_coherence=round(coherence, 2),
                emotional_impact=round(impact, 2),
                length_appropriate=result.get("length_appropriate", True),
                tone_aligned=result.get("tone_aligned", True),
                feedback=result.get("feedback"),
            )
            
            logger.info(f"Agent 4: Quality score: {metrics.overall_quality}")
            return metrics
            
        except Exception as e:
            logger.error(f"Agent 4 error: {e}")
            # Return default metrics on error
            return QualityMetrics(
                overall_quality=0.7,
                narrative_coherence=0.7,
                emotional_impact=0.7,
                length_appropriate=True,
                tone_aligned=True,
                feedback="Evaluation unavailable",
            )
    
    def estimate_cost(self) -> float:
        """Return estimated cost for this agent."""
        return self.cost_estimate
