"""Prompts for Agent 3: Narrative Generator."""

STORY_GENERATION_PROMPT = """Write a story based on the following. Use simple, clear English that anyone can understand.

THE IDEA:
{idea}

KEY THEMES TO INCLUDE:
{themes}

EMOTIONAL JOURNEY:
{emotional_arc}

STORY STRUCTURE IDEAS (use as loose guide):
{patterns}

USER REQUESTS:
- Tone: {tone}
- Length: {length} (short ~800 words, medium ~1500 words, long ~2500 words)
- Writing Style: {style}
- Genre: {genre}

RULES:
1. Write in simple, everyday language - avoid complex words or fancy phrases
2. Tell the story naturally - don't try to sound like a textbook
3. Make it easy to read and understand
4. Include the themes in a natural way
5. Match the tone and length requested
6. Start with a title on the first line
7. Just give me the story - no explanations or notes

Write the story now.
"""

FEW_SHOT_EXAMPLES = """
EXAMPLE 1 (Sci-Fi, Hopeful):
Idea: "A lonely astronaut discovers a mysterious plant on Mars"
Story: "Commander Chen hadn't spoken to another human in 87 days..."

EXAMPLE 2 (Mystery, Dark):
Idea: "A detective finds an old photograph that changes everything"
Story: "The envelope was waiting on my desk when I arrived..."
"""
