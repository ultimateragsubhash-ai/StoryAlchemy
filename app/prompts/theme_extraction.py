"""Prompts for Agent 1: Theme Extractor."""

THEME_EXTRACTION_PROMPT = """You are a literary analysis expert. Analyze the following story idea and extract key themes, emotional arcs, and genre hints.

Story Idea: {idea}

Your task:
1. Identify 3-5 key themes present in this idea (e.g., isolation, discovery, hope, betrayal, redemption)
2. Determine the emotional arc (how the story's emotional tone changes)
3. Suggest the most appropriate genre

Respond in JSON format:
{{"themes": ["theme1", "theme2", "theme3"], "emotional_arc": "brief description", "genre_hint": "suggested genre"}}

Guidelines:
- Themes should be single words or short phrases
- Emotional arc should capture the transformation (e.g., "loneliness_to_wonder", "hope_to_despair_to_hope")
- Genre hint should be one of: sci-fi, fantasy, mystery, romance, horror, literary, adventure, or general
"""
