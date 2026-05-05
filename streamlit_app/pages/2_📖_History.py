"""Story History - Clean Light UI with Glow."""

import streamlit as st
import requests
import os

# API URL configuration
# In production (Railway/Streamlit Cloud), this should be set as an environment variable
# Example: https://your-backend.up.railway.app/api/v1
API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/api/v1")

# Log the API URL for debugging (only visible in browser console or if explicitly shown)
if not os.getenv("FASTAPI_URL"):
    st.warning("⚠️ FASTAPI_URL environment variable not set. Using default: http://localhost:8000/api/v1")

st.set_page_config(
    page_title="StoryAlchemy - History",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
        font-family: 'Inter', sans-serif;
        color: #134e4a;
    }
    
    #MainMenu, header, footer {visibility: hidden;}
    
    /* Navigation with glow - Teal theme */
    .nav-bar {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.8);
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
    
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        color: #134e4a;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(13, 148, 136, 0.3);
    }
    
    .page-subtitle {
        text-align: center;
        color: #0d9488;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Stats with glow */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.15), 0 0 0 1px rgba(13, 148, 136, 0.1);
        text-align: center;
        min-width: 120px;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .stat-num {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0d9488;
        text-shadow: 0 0 15px rgba(13, 148, 136, 0.4);
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
    }
    
    /* Filter bar with glow */
    .filter-bar {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.1), 0 0 0 1px rgba(13, 148, 136, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #0d9488 !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.15) !important;
    }
    
    /* Story cards with glow */
    .story-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.1), 0 0 0 1px rgba(13, 148, 136, 0.05);
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
    }
    
    .story-card:hover {
        box-shadow: 0 8px 30px rgba(13, 148, 136, 0.2), 0 0 0 1px rgba(13, 148, 136, 0.1);
    }
    
    .story-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #134e4a;
        margin-bottom: 0.5rem;
    }
    
    .story-meta {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    
    .quality-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ccfbf1 0%, #99f6e4 100%);
        color: #0d9488;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(13, 148, 136, 0.2);
    }
    
    .tag {
        display: inline-block;
        background: #f0fdfa;
        color: #0d9488;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        box-shadow: 0 2px 6px rgba(13, 148, 136, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.3) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 8px 25px rgba(13, 148, 136, 0.4) !important;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def get_stats():
    try:
        response = requests.get(f"{API_URL}/analytics/stats", timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"stories_generated": 0, "average_quality": 0, "total_cost_usd": 0, "total_loves": 0}

st.markdown("""
<div class="nav-bar">
    <a href="/" class="nav-link">✨ Generate</a>
    <a href="/History" class="nav-link active">📖 History</a>
    <a href="/KnowledgeBase" class="nav-link">📚 Knowledge Base</a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<h1 class="page-title">📖 Story History</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Browse your previously generated narratives</p>', unsafe_allow_html=True)

stats = get_stats()
# Format cost with 3 decimal places if less than 0.01, otherwise 2 decimal places
total_cost = stats.get('total_cost_usd', 0)
cost_display = f"${total_cost:.3f}" if total_cost < 0.01 else f"${total_cost:.2f}"

st.markdown(f"""
<div class="stats-bar">
    <div class="stat-box">
        <div class="stat-num">{stats.get('stories_generated', 0)}</div>
        <div class="stat-label">Stories</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">⭐ {stats.get('average_quality', 0):.2f}</div>
        <div class="stat-label">Avg Quality</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">{cost_display}</div>
        <div class="stat-label">Total Cost</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">👍 {stats.get('total_loves', 0)}</div>
        <div class="stat-label">Loves</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    genre_filter = st.selectbox("Genre", ["All", "sci-fi", "fantasy", "mystery", "romance", "horror", "general"])
with col2:
    tone_filter = st.selectbox("Tone", ["All", "hopeful", "dark", "humorous", "melancholic", "mysterious", "neutral"])
with col3:
    sort_by = st.selectbox("Sort by", ["Newest", "Highest Quality"])

db_error = None
try:
    params = {"limit": 20}
    if genre_filter != "All":
        params["genre"] = genre_filter
    if tone_filter != "All":
        params["tone"] = tone_filter
    
    response = requests.get(f"{API_URL}/stories/recent", params=params, timeout=10)
    if response.status_code == 200:
        stories = response.json().get("stories", [])
    elif response.status_code == 503:
        db_error = "Database not connected. Please check your MONGODB_URL configuration."
        stories = []
    else:
        db_error = f"Error fetching stories: {response.status_code}"
        stories = []
except Exception as e:
    db_error = f"Connection error: {str(e)}"
    stories = []

# Show database error if any
if db_error:
    st.error(f"⚠️ {db_error}")
    # Show debug info
    with st.expander("🔧 Debug Database Connection"):
        try:
            debug_resp = requests.get(f"{API_URL}/stories/debug/db-status", timeout=5)
            if debug_resp.status_code == 200:
                status = debug_resp.json()
                st.json(status)
                
                if not status.get("mongodb_url_set"):
                    st.error("❌ MONGODB_URL environment variable is not set!")
                    st.info("Go to Railway Dashboard → Your Project → Variables → Add MONGODB_URL")
                elif status.get("status") != "connected":
                    st.error("❌ MongoDB connection failed!")
                    if "error" in status:
                        st.code(status["error"])
                    st.info("Check that your MONGODB_URL is correct and the database is accessible")
            else:
                st.error(f"Debug endpoint returned {debug_resp.status_code}")
        except Exception as debug_e:
            st.error(f"Could not reach debug endpoint: {debug_e}")

if stories:
    for i, story in enumerate(stories):
        title = story.get("story_title", "Untitled")
        
        # Handle quality_metrics - might be a dict or object
        quality_metrics = story.get("quality_metrics", {})
        if hasattr(quality_metrics, 'get'):
            quality = quality_metrics.get("overall_quality", 0)
        else:
            quality = getattr(quality_metrics, 'overall_quality', 0) if quality_metrics else 0
        
        idea = story.get("idea", "")[:100]
        
        # Handle preferences - might be a dict or object
        prefs = story.get("preferences", {})
        if prefs and not hasattr(prefs, 'get'):
            # Convert to dict if it's a Pydantic model
            prefs = dict(prefs) if hasattr(prefs, '__dict__') else {}
        
        words = story.get("word_count", 0)
        cost = story.get("cost_usd", 0)
        # Show cost with 3 decimal places for small values
        cost_str = f"${cost:.3f}" if cost < 0.01 else f"${cost:.2f}"
        
        st.markdown(f"""
        <div class="story-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <div class="story-title">{title}</div>
                <span class="quality-badge">⭐ {quality:.2f}</span>
            </div>
            <div class="story-meta">💭 {idea}...</div>
            <div>
                <span class="tag">🎨 {prefs.get('tone', 'neutral') if hasattr(prefs, 'get') else getattr(prefs, 'tone', 'neutral')}</span>
                <span class="tag">🎭 {prefs.get('genre', 'general') if hasattr(prefs, 'get') else getattr(prefs, 'genre', 'general')}</span>
                <span class="tag">📏 {words} words</span>
                <span class="tag">💰 {cost_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Read full story"):
            st.write(story.get("generated_story", ""))
            story_id = story.get("_id", story.get("story_id", str(i)))
            st.download_button(
                "Download",
                story.get("generated_story", ""),
                f"{title[:20]}.txt",
                use_container_width=True,
                key=f"download_{story_id}"
            )
else:
    st.markdown("""
    <div class="empty-state">
        <h3>📭 No stories yet</h3>
        <p>Generate your first story on the main page</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
