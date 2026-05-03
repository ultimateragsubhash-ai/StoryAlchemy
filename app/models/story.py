"""Story-related Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Any


class StoryPreferences(BaseModel):
    genre: str = "general"
    tone: str = "neutral"
    model: str = "openai/gpt-4o-mini"
    word_count: int = 500
    length: str = "medium"
    style: str = "narrative"
    temperature: float = 0.8

    def get_model_with_prefix(self) -> str:
        """Return model name ensuring it has a provider prefix."""
        if "/" in self.model:
            return self.model
        return f"openai/{self.model}"


class ThemeExtraction(BaseModel):
    themes: List[str] = Field(default_factory=list)
    emotional_arc: str = "neutral"
    genre_hint: str = "general"


class RetrievedPattern(BaseModel):
    pattern_id: str
    pattern_name: str
    text: str
    relevance_score: float = 0.5
    source_category: Optional[str] = None


class QualityMetrics(BaseModel):
    overall_quality: float = 0.7
    narrative_coherence: float = 0.7
    emotional_impact: float = 0.7
    length_appropriate: bool = True
    tone_aligned: bool = True
    feedback: Optional[str] = None


class StoryRequest(BaseModel):
    idea: str
    preferences: StoryPreferences = Field(default_factory=StoryPreferences)


class StoryResponse(BaseModel):
    story_id: str
    idea: str
    preferences: StoryPreferences
    extracted_themes: Any
    retrieved_patterns: List[Any] = []
    generated_story: str
    story_title: Optional[str] = None
    word_count: int
    quality_metrics: Any
    generation_time_ms: int
    cost_usd: float
    model_used: str
    cache_hit: bool = False


class ComparisonRequest(BaseModel):
    idea: str
    preferences: StoryPreferences = Field(default_factory=StoryPreferences)
    comparison_tones: Optional[List[str]] = None


class ToneComparison(BaseModel):
    tone: str
    story: StoryResponse


class ComparisonResponse(BaseModel):
    idea: str
    comparisons: List[ToneComparison]
    patterns_used_across_all: List[str] = []
    total_cost_usd: float
    total_time_ms: int
