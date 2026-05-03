"""StoryAlchemy - Clean Light UI with Green Glow Theme."""

import streamlit as st
import requests
import os
import time
import random

st.set_page_config(
    page_title="StoryAlchemy",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/api/v1")

# Clean light theme with green/teal glow - consistent across all pages
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
        font-family: 'Inter', sans-serif;
        color: #134e4a;
    }
    
    #MainMenu, header, footer {visibility: hidden;}
    
    /* Hide empty containers */
    .element-container:empty, .stVerticalBlock:empty {
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Navigation with green glow - consistent theme */
    .nav-bar {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 0.5rem;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.15), 0 0 40px rgba(13, 148, 136, 0.1);
        max-width: 500px;
        margin: 1rem auto 2rem auto;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .nav-link {
        padding: 0.75rem 1.5rem;
        text-decoration: none;
        color: #64748b;
        font-weight: 500;
        font-size: 0.95rem;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .nav-link:hover {
        color: #0d9488;
        background: rgba(13, 148, 136, 0.1);
        box-shadow: 0 0 20px rgba(13, 148, 136, 0.2);
    }
    
    .nav-link.active {
        background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
        color: white;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.4), 0 0 30px rgba(13, 148, 136, 0.3);
    }
    
    /* Title with green glow */
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #134e4a;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(13, 148, 136, 0.3);
    }
    
    .app-subtitle {
        text-align: center;
        color: #0d9488;
        font-size: 1rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #0d9488;
        text-transform: uppercase;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
        text-shadow: 0 0 10px rgba(13, 148, 136, 0.2);
    }
    
    /* Text area with green glow on focus */
    .stTextArea {
        margin-bottom: 0.5rem !important;
    }
    
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #134e4a !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #0d9488 !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15), 0 0 20px rgba(13, 148, 136, 0.2) !important;
    }
    
    /* Select boxes with green glow */
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #0d9488 !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.15) !important;
    }
    
    /* Slider green glow */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #0d9488 0%, #14b8a6 100%) !important;
        box-shadow: 0 0 10px rgba(13, 148, 136, 0.5) !important;
    }
    
    /* Buttons with green glow */
    .stButton > button {
        background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.4), 0 0 20px rgba(13, 148, 136, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(13, 148, 136, 0.5), 0 0 30px rgba(13, 148, 136, 0.3) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        color: #64748b !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: #0d9488 !important;
        color: #0d9488 !important;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.2) !important;
    }
    
    /* Story result with green glow */
    .story-result {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(13, 148, 136, 0.12), 0 0 0 1px rgba(13, 148, 136, 0.1);
        margin-top: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .story-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #134e4a;
        margin-bottom: 1rem;
        text-shadow: 0 0 20px rgba(13, 148, 136, 0.2);
    }
    
    .story-text {
        font-size: 1.05rem;
        line-height: 1.8;
        color: #374151;
        white-space: pre-wrap;
    }
    
    /* Stats with green glow pills */
    .stats-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .stat-pill {
        background: linear-gradient(135deg, #ccfbf1 0%, #99f6e4 100%);
        padding: 0.6rem 1.2rem;
        border-radius: 20px;
        font-size: 0.875rem;
        box-shadow: 0 2px 8px rgba(13, 148, 136, 0.15), 0 0 0 1px rgba(13, 148, 136, 0.1);
        border: 1px solid rgba(13, 148, 136, 0.1);
    }
    
    .stat-value {
        font-weight: 700;
        color: #0d9488;
        text-shadow: 0 0 10px rgba(13, 148, 136, 0.3);
    }
    
    /* Theme tags with green glow */
    .theme-tag {
        display: inline-block;
        background: linear-gradient(135deg, #ccfbf1 0%, #99f6e4 100%);
        color: #0d9488;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.25rem;
        box-shadow: 0 2px 8px rgba(13, 148, 136, 0.15);
        border: 1px solid rgba(13, 148, 136, 0.1);
    }
    
    /* Loading green glow */
    .loading-text {
        text-align: center;
        color: #0d9488;
        font-weight: 600;
        padding: 2rem;
        text-shadow: 0 0 20px rgba(13, 148, 136, 0.5);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; text-shadow: 0 0 20px rgba(13, 148, 136, 0.5); }
        50% { opacity: 0.7; text-shadow: 0 0 30px rgba(13, 148, 136, 0.8); }
    }
    
    /* Footer with green glow */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 2rem;
        color: #5eead4;
        font-size: 0.875rem;
        text-shadow: 0 0 10px rgba(13, 148, 136, 0.2);
    }
</style>
""", unsafe_allow_html=True)


def generate_story(idea, preferences):
    try:
        response = requests.post(
            f"{API_URL}/stories/generate",
            json={"idea": idea, "preferences": preferences},
            timeout=60,
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None


def generate_comparison(idea, preferences, tones):
    try:
        response = requests.post(
            f"{API_URL}/stories/generate-comparison",
            json={"idea": idea, "preferences": preferences, "comparison_tones": tones},
            timeout=120,
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None


# Navigation
st.markdown("""
<div class="nav-bar">
    <a href="/" class="nav-link active">✨ Generate</a>
    <a href="/History" class="nav-link">📖 History</a>
    <a href="/KnowledgeBase" class="nav-link">📚 Knowledge Base</a>
</div>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="app-title">🪄 StoryAlchemy</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">Transform your ideas into compelling stories with AI</p>', unsafe_allow_html=True)

# Story Input
st.markdown("<div class='section-label'>Your Story Idea</div>", unsafe_allow_html=True)
idea = st.text_area(
    "",
    placeholder="A lonely astronaut discovers a mysterious plant on Mars...",
    height=100,
    label_visibility="collapsed",
)

# Story Settings
st.markdown("<div class='section-label'>Story Settings</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    tone = st.selectbox("Tone", ["neutral", "hopeful", "dark", "humorous", "melancholic", "mysterious"])
    genre = st.selectbox("Genre", ["general", "sci-fi", "fantasy", "mystery", "romance", "horror"])

with col2:
    length = st.selectbox("Length", ["short", "medium", "long"])
    style = st.selectbox("Style", ["descriptive", "concise", "poetic", "dramatic"])

with col3:
    model_display_map = {
        "GPT-4o Mini": "openai/gpt-4o-mini",
    }
    model_choice = st.selectbox("AI Model", list(model_display_map.keys()))
    model = model_display_map[model_choice]
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

preferences = {
    "tone": tone,
    "length": length,
    "style": style,
    "genre": genre,
    "model": model,
    "temperature": temperature,
}

# Determine if compare tones should be disabled (only works with neutral tone)
compare_disabled = tone != "neutral" if idea else True

# Show settings preview when idea is entered
if idea:
    st.markdown(f"""
    <div style="background: rgba(13, 148, 136, 0.1); border-radius: 8px; padding: 0.75rem; margin: 0.5rem 0; font-size: 0.85rem; color: #0d9488;">
        <strong>Generate Story will use:</strong> 🎭 {tone} tone · 📖 {genre} · ✍️ {style} · 📏 {length}
    </div>
    """, unsafe_allow_html=True)
    
    if compare_disabled:
        st.markdown("""
        <div style="background: rgba(251, 191, 36, 0.15); border-radius: 8px; padding: 0.75rem; margin: 0.5rem 0; font-size: 0.85rem; color: #b45309;">
            ⚠️ <strong>Compare Tones</strong> requires Tone to be set to "neutral". Current setting will be used for all variations.
        </div>
        """, unsafe_allow_html=True)
    else:
        sample_tones = random.sample(["hopeful", "dark", "humorous", "melancholic", "mysterious"], 3)
        st.markdown(f"""
        <div style="background: rgba(13, 148, 136, 0.1); border-radius: 8px; padding: 0.75rem; margin: 0.5rem 0; font-size: 0.85rem; color: #0d9488;">
            <strong>Compare Tones will use:</strong> 🎭 {', '.join(sample_tones)} (randomly selected) · 📖 {genre} · ✍️ {style} · 📏 {length}
        </div>
        """, unsafe_allow_html=True)

# Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("✨ Generate Story", type="primary", disabled=not idea):
        if idea:
            with st.spinner(""):
                st.markdown('<p class="loading-text">✨ Crafting your story...</p>', unsafe_allow_html=True)
                result = generate_story(idea, preferences)
                if result:
                    st.session_state.story = result
                    st.session_state.comparison = None
                    st.rerun()

with col2:
    if st.button("🎭 Compare Random Tones", type="secondary", disabled=not idea or compare_disabled):
        if idea and not compare_disabled:
            with st.spinner(""):
                st.markdown('<p class="loading-text">🎭 Creating variations...</p>', unsafe_allow_html=True)
                # Let backend randomly select tones
                result = generate_comparison(idea, preferences, None)
                if result:
                    st.session_state.comparison = result
                    st.session_state.story = None
                    st.rerun()

# Display Single Story
if "story" in st.session_state and st.session_state.story:
    story = st.session_state.story
    
    st.markdown('<div class="story-result">', unsafe_allow_html=True)
    
    title = story.get("story_title", "Your Story")
    quality = story.get("quality_metrics", {}).get("overall_quality", 0)
    
    st.markdown(f'<div class="story-title">{title}</div>', unsafe_allow_html=True)
    
    # Stats
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-pill"><span class="stat-value">⭐ {quality:.2f}</span> Quality</div>
        <div class="stat-pill"><span class="stat-value">{story.get('word_count', 0)}</span> Words</div>
        <div class="stat-pill"><span class="stat-value">${story.get('cost_usd', 0):.3f}</span> Cost</div>
        <div class="stat-pill"><span class="stat-value">{story.get('generation_time_ms', 0)//1000}s</span> Time</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Story content
    story_text = story.get("generated_story", "")
    st.markdown(f'<div class="story-text">{story_text}</div>', unsafe_allow_html=True)
    
    # Themes
    themes = story.get("extracted_themes", {}).get("themes", [])
    if themes:
        st.markdown("<br>", unsafe_allow_html=True)
        for t in themes:
            st.markdown(f'<span class="theme-tag">{t}</span>', unsafe_allow_html=True)
    
    # Actions
    story_id = story.get("story_id", "")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👍 Love it", key=f"love_{story_id}"):
            st.success("Thanks!")
    with col2:
        if st.button("😐 It's OK", key=f"ok_{story_id}"):
            st.info("Thanks!")
    with col3:
        if st.button("👎 Regenerate", key=f"bad_{story_id}"):
            st.info("We'll learn from this.")
    
    st.download_button("📥 Download Story", story_text, f"story_{story_id[:8] if story_id else 'unknown'}.txt")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display Comparison
if "comparison" in st.session_state and st.session_state.comparison:
    comp = st.session_state.comparison
    
    st.markdown('<div class="section-label">🎭 Three Perspectives</div>', unsafe_allow_html=True)
    
    idea = comp.get('idea', '')
    st.info(f"**Idea:** {idea[:100]}...")
    
    comparisons = comp.get("comparisons", [])
    
    if comparisons:
        for i, c in enumerate(comparisons):
            tone = c.get("tone", "")
            story = c.get("story", {})
            full_text = story.get("generated_story", "")
            preview = full_text[:350] + "..." if len(full_text) > 350 else full_text
            quality = story.get("quality_metrics", {}).get("overall_quality", 0)
            story_id = story.get("story_id", str(i))
            
            with st.expander(f"{tone.title()} Tone (⭐ {quality:.2f})", expanded=True):
                st.write(full_text)
                st.caption(f"{story.get('word_count', 0)} words · ${story.get('cost_usd', 0):.3f}")
                st.download_button(
                    "📥 Download",
                    full_text,
                    f"story_{tone}_{story_id[:8]}.txt",
                    key=f"download_compare_{story_id}"
                )
