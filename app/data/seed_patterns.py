"""Seed patterns for the knowledge base."""

# Plot Structure Patterns
PLOT_STRUCTURES = [
    {
        "id": "hero_journey_001",
        "name": "The Hero's Journey - Call to Adventure",
        "type": "hero_journey",
        "text": "The hero begins in the ordinary world, living an ordinary life. Something happens that disrupts their comfort - a call to adventure they cannot ignore. Initially, they refuse, fearing change, but eventually commit to the journey.",
        "genre": "universal",
        "emotional_arc": "reluctance_to_commitment",
    },
    {
        "id": "hero_journey_002",
        "name": "The Hero's Journey - Supreme Ordeal",
        "type": "hero_journey",
        "text": "The hero faces their greatest fear, confronting death or defeat. In this darkest moment, they find inner strength they didn't know they possessed, emerging transformed.",
        "genre": "universal",
        "emotional_arc": "despair_to_triumph",
    },
    {
        "id": "redemption_arc_001",
        "name": "Redemption Through Sacrifice",
        "type": "redemption",
        "text": "A character burdened by past mistakes finds an opportunity to atone. They must choose between self-preservation and doing what is right. Through sacrifice, they find redemption and peace.",
        "genre": "universal",
        "emotional_arc": "guilt_to_redemption",
    },
    {
        "id": "isolation_discovery_001",
        "name": "Isolation Breeds Discovery",
        "type": "discovery",
        "text": "A character finds themselves isolated - physically, emotionally, or spiritually. In this solitude, they discover something unexpected about themselves or the world, leading to profound transformation.",
        "genre": "universal",
        "emotional_arc": "loneliness_to_wonder",
    },
    {
        "id": "forbidden_knowledge_001",
        "name": "The Cost of Forbidden Knowledge",
        "type": "discovery",
        "text": "A seeker pursues knowledge others warned them against. They obtain the truth they sought, but at a terrible price. Some things are hidden for good reason.",
        "genre": "mystery",
        "emotional_arc": "curiosity_to_regret",
    },
    {
        "id": "unlikely_alliance_001",
        "name": "Enemies Become Allies",
        "type": "relationship",
        "text": "Two opposing forces, driven by circumstance or necessity, must work together. Initially hostile, they gradually develop mutual respect and trust, discovering they're not so different after all.",
        "genre": "universal",
        "emotional_arc": "hostility_to_friendship",
    },
    {
        "id": "last_standin_001",
        "name": "The Last Stand",
        "type": "conflict",
        "text": "Outnumbered and outmatched, a defender makes their final stand. They know they cannot win, yet they fight anyway - for honor, for others, for a principle worth dying for.",
        "genre": "action",
        "emotional_arc": "fear_to_courage",
    },
    {
        "id": "secret_world_001",
        "name": "Discovery of a Secret World",
        "type": "discovery",
        "text": "A mundane life is interrupted by the revelation that another world exists alongside our own - magical, dangerous, or simply different. The protagonist must navigate both worlds while keeping the secret.",
        "genre": "fantasy",
        "emotional_arc": "disbelief_to_awe",
    },
    {
        "id": "false_prophet_001",
        "name": "The False Prophet",
        "type": "revelation",
        "text": "A trusted guide, leader, or mentor is revealed to have ulterior motives. The protagonist must confront the betrayal and decide whether to expose them or use the knowledge to their advantage.",
        "genre": "mystery",
        "emotional_arc": "trust_to_betrayal",
    },
    {
        "id": "second_chance_001",
        "name": "The Second Chance",
        "type": "redemption",
        "text": "Given an impossible opportunity to undo a past mistake, the protagonist must navigate consequences they never anticipated. Changing the past is never simple, and the price may be higher than expected.",
        "genre": "sci-fi",
        "emotional_arc": "regret_to_acceptance",
    },
]

# Character Archetypes
CHARACTER_ARCHETYPES = [
    {
        "id": "archetype_orphan_001",
        "name": "The Orphan",
        "type": "archetype",
        "text": "A character separated from their origins, seeking belonging. They carry wounds from abandonment but possess unique resilience. Their journey often involves finding or creating a new family.",
        "genre": "universal",
    },
    {
        "id": "archetype_mentor_001",
        "name": "The Wise Mentor",
        "type": "archetype",
        "text": "An experienced guide who provides knowledge and tools, but cannot walk the path for the hero. They often harbor their own regrets and live vicariously through the protégé's success.",
        "genre": "universal",
    },
    {
        "id": "archetype_trickster_001",
        "name": "The Trickster",
        "type": "archetype",
        "text": "A clever, mischievous character who challenges conventions through wit rather than force. They blur moral lines, serving neither pure good nor evil, often providing comic relief and unexpected wisdom.",
        "genre": "universal",
    },
    {
        "id": "archetype_caregiver_001",
        "name": "The Caregiver",
        "type": "archetype",
        "text": "A nurturing character driven by compassion and the need to protect others. They often sacrifice their own needs, and their strength emerges when those they love are threatened.",
        "genre": "universal",
    },
    {
        "id": "archetype_outcast_001",
        "name": "The Outcast",
        "type": "archetype",
        "text": "A character rejected by society for being different. They possess unique abilities or perspectives that others fear. Their journey involves either finding acceptance or embracing their outsider status as strength.",
        "genre": "universal",
    },
]

# Emotional Arcs
EMOTIONAL_ARCS = [
    {
        "id": "arc_hope_despair_hope_001",
        "name": "Hope to Despair to Hope",
        "type": "emotional_arc",
        "text": "The character begins with optimism, faces crushing setbacks that test their faith, and ultimately rebuilds their hope stronger than before, tempered by experience.",
    },
    {
        "id": "arc_fear_courage_001",
        "name": "Fear to Courage",
        "type": "emotional_arc",
        "text": "The character starts afraid - of failure, of loss, of the unknown. Through facing their fears step by step, they discover courage was within them all along.",
    },
    {
        "id": "arc_isolation_connection_001",
        "name": "Isolation to Connection",
        "type": "emotional_arc",
        "text": "The character begins isolated - by choice or circumstance. Through the story, they learn to let others in, discovering that vulnerability leads to the deepest connections.",
    },
]

# Genre-Specific Patterns
SCI_FI_PATTERNS = [
    {
        "id": "sf_first_contact_001",
        "name": "First Contact",
        "type": "sci-fi",
        "text": "Humanity encounters alien intelligence for the first time. The story explores communication barriers, mutual misunderstanding, and the profound shift in perspective that comes from knowing we're not alone.",
        "genre": "sci-fi",
    },
    {
        "id": "sf_ai_consciousness_001",
        "name": "AI Awakening",
        "type": "sci-fi",
        "text": "An artificial intelligence develops self-awareness, forcing questions about the nature of consciousness, rights of artificial beings, and humanity's responsibility toward its creations.",
        "genre": "sci-fi",
    },
    {
        "id": "sf_time_paradox_001",
        "name": "The Time Paradox",
        "type": "sci-fi",
        "text": "Time travel creates unexpected consequences - changed futures, erased memories, or meeting oneself. The protagonist must navigate temporal complexity while facing the irreversibility of some choices.",
        "genre": "sci-fi",
    },
]

MYSTERY_PATTERNS = [
    {
        "id": "mystery_unreliable_narrator_001",
        "name": "The Unreliable Narrator",
        "type": "mystery",
        "text": "The story is told from a perspective that hides crucial information, misinterprets events, or deliberately deceives. Readers must piece together the truth from what is unsaid or contradicted.",
        "genre": "mystery",
    },
    {
        "id": "mystery_cold_case_001",
        "name": "The Cold Case",
        "type": "mystery",
        "text": "An old, unsolved mystery resurfaces. The investigator must dig through faded memories, buried secrets, and the weight of time to uncover truths someone wanted forgotten.",
        "genre": "mystery",
    },
]

# Combine all patterns
ALL_PATTERNS = (
    PLOT_STRUCTURES +
    CHARACTER_ARCHETYPES +
    EMOTIONAL_ARCS +
    SCI_FI_PATTERNS +
    MYSTERY_PATTERNS
)


def get_all_patterns():
    """Return all seed patterns."""
    return ALL_PATTERNS


def get_patterns_by_genre(genre: str):
    """Return patterns filtered by genre."""
    return [p for p in ALL_PATTERNS if p.get("genre") == genre]


def get_patterns_by_type(pattern_type: str):
    """Return patterns filtered by type."""
    return [p for p in ALL_PATTERNS if p.get("type") == pattern_type]
