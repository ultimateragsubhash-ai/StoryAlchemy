"""Prompts for Agent 4: Quality Critic."""

QUALITY_EVALUATION_PROMPT = """You are a literary critic evaluating a generated story. Assess the following story against the user's preferences.

STORY TO EVALUATE:
{story}

ORIGINAL IDEA:
{idea}

USER PREFERENCES:
- Requested tone: {requested_tone}
- Requested length: {requested_length}
- Requested style: {requested_style}
- Requested genre: {requested_genre}

Evaluate the story on:
1. Narrative coherence (0-1): Does the story flow logically? Are there plot holes?
2. Emotional impact (0-1): Does it evoke emotion? Is it engaging?
3. Length appropriateness: Does the word count match the requested length?
4. Tone alignment: Does the story match the requested tone?

Respond in JSON format:
{{"overall_quality": 0.8, "narrative_coherence": 0.8, "emotional_impact": 0.8, "length_appropriate": true, "tone_aligned": true, "feedback": "brief feedback"}}

Guidelines:
- overall_quality is the average of coherence and impact
- Be honest but constructive in feedback
- Scores above 0.8 indicate high quality
- Scores below 0.6 indicate issues
"""
