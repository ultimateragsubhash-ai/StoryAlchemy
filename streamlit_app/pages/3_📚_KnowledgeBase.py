"""Knowledge Base - Clean Light UI with Green Glow Theme."""

import streamlit as st
import requests
import os
import time

API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="StoryAlchemy - Knowledge Base",
    page_icon="📚",
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
    
    .main-container {
        max-width: 700px;
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
    
    /* Upload zone with green glow */
    .upload-box {
        background: rgba(255, 255, 255, 0.95);
        border: 2px dashed #99f6e4;
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.1);
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #0d9488;
        background: #f0fdfa;
        box-shadow: 0 8px 30px rgba(13, 148, 136, 0.2);
    }
    
    /* Input section with green glow */
    .input-section {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.1), 0 0 0 1px rgba(13, 148, 136, 0.1);
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .section-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #134e4a;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 1.5rem 0 0.75rem 0;
    }
    
    .stTextArea > div > div > textarea,
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:hover,
    .stTextInput > div > div > input:hover,
    .stSelectbox > div > div:hover {
        border-color: #0d9488 !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.15) !important;
    }
    
    /* Button with green glow */
    .stButton > button {
        background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.4), 0 0 20px rgba(13, 148, 136, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(13, 148, 136, 0.5), 0 0 30px rgba(13, 148, 136, 0.3) !important;
    }
    
    /* Pattern cards with green glow */
    .pattern-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.1), 0 0 0 1px rgba(13, 148, 136, 0.05);
        margin: 0.5rem 0;
        border-left: 3px solid #99f6e4;
        transition: all 0.3s ease;
    }
    
    .pattern-card:hover {
        box-shadow: 0 8px 25px rgba(13, 148, 136, 0.2);
    }
    
    .pattern-card.user-pattern {
        border-left-color: #059669;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.15);
    }
    
    .stat-pill {
        display: inline-block;
        background: linear-gradient(135deg, #ccfbf1 0%, #99f6e4 100%);
        color: #0d9488;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.25rem;
        box-shadow: 0 2px 8px rgba(13, 148, 136, 0.15);
    }
    
    .info-box {
        background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
        border-left: 3px solid #0d9488;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(13, 148, 136, 0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #86efac;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.15);
    }
    
    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.1);
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
    return {"patterns_indexed": 0, "stories_generated": 0}

def get_user_patterns():
    try:
        response = requests.get(f"{API_URL}/knowledge-base/patterns", timeout=5)
        if response.status_code == 200:
            return response.json().get("patterns", [])
    except:
        pass
    return []

st.markdown("""
<div class="nav-bar">
    <a href="/" class="nav-link">✨ Generate</a>
    <a href="/History" class="nav-link">📖 History</a>
    <a href="/KnowledgeBase" class="nav-link active">📚 Knowledge Base</a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<h1 class="page-title">📚 Knowledge Base</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Upload documents to teach the AI new storytelling patterns</p>', unsafe_allow_html=True)

stats = get_stats()
st.markdown(f"""
<div style="text-align: center; margin-bottom: 2rem;">
    <span class="stat-pill">📚 {stats.get('patterns_indexed', 0)} patterns</span>
    <span class="stat-pill">📝 {stats.get('stories_generated', 0)} stories</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Upload Document</div>', unsafe_allow_html=True)

st.markdown("""
<div class="upload-box">
    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📄</div>
    <p style="color: #0d9488; font-weight: 500; margin: 0;">Drop your file here or click to browse</p>
    <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;">PDF, TXT, MD, DOCX (Max 10MB)</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Select file", type=["pdf", "txt", "md", "docx"], label_visibility="collapsed")

st.markdown('<div class="section-title">Add Pattern Manually</div>', unsafe_allow_html=True)

category = st.selectbox(
    "Category",
    ["plot_structure", "character_archetype", "emotional_arc", "genre_guide", "writing_technique"],
    format_func=lambda x: {
        "plot_structure": "📖 Plot Structure",
        "character_archetype": "👤 Character Archetype",
        "emotional_arc": "💭 Emotional Arc",
        "genre_guide": "🎭 Genre Guide",
        "writing_technique": "✍️ Writing Technique",
    }.get(x, x),
)

title = st.text_input("Title", placeholder="e.g., Hero's Journey Pattern")

text_content = st.text_area(
    "Content",
    placeholder="Paste your narrative pattern here...",
    height=150,
)

if st.button("🚀 Process & Add to Knowledge Base"):
    content = None
    actual_title = title
    
    if uploaded_file:
        content = uploaded_file.read()
        if not actual_title:
            actual_title = uploaded_file.name
    elif text_content:
        content = text_content.encode("utf-8")
    
    if content and actual_title:
        progress = st.progress(0)
        
        for i, step in enumerate(["Reading...", "Chunking...", "Embedding...", "Storing...", "Done!"]):
            progress.progress((i + 1) * 20)
            st.text(step)
            time.sleep(0.4)
        
        try:
            files = {"file": (actual_title, content, "application/octet-stream")} if uploaded_file else None
            data = {"category": category, "title": actual_title}
            if text_content and not uploaded_file:
                data["text_content"] = text_content
            
            response = requests.post(
                f"{API_URL}/knowledge-base/upload",
                files=files,
                data=data,
                timeout=60,
            )
            
            if response.status_code == 200:
                result = response.json()
                st.markdown(f"""
                <div class="success-box">
                    <strong style="color: #059669;">✅ Added {result.get('chunks_added', 0)} pattern(s)!</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        
        progress.empty()
    else:
        st.warning("Please provide content and title.")

st.markdown('<div class="section-title">Your Uploaded Patterns</div>', unsafe_allow_html=True)

user_patterns = get_user_patterns()

if user_patterns:
    st.markdown(f"<p style='color: #64748b;'>You have {len(user_patterns)} uploaded pattern(s):</p>", unsafe_allow_html=True)
    for p in user_patterns[:10]:
        st.markdown(f"""
        <div class="pattern-card user-pattern">
            <strong style="color: #059669;">{p.get('pattern_name', 'Unnamed')}</strong>
            <span style="color: #94a3b8; font-size: 0.8rem; float: right;">{p.get('category', '')}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
        <p>No uploads yet. Add your first document above.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title">Built-in Seed Patterns</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">
        Pre-loaded patterns that provide a foundation of storytelling knowledge.
    </p>
</div>
""", unsafe_allow_html=True)

seed_categories = {
    "Plot Structures": ["Hero's Journey", "Redemption Arc", "Discovery Pattern"],
    "Character Archetypes": ["The Orphan", "The Mentor", "The Trickster"],
    "Emotional Arcs": ["Hope to Despair", "Fear to Courage"],
}

for cat, patterns in seed_categories.items():
    with st.expander(f"🔹 {cat}"):
        for p in patterns:
            st.markdown(f'<div class="pattern-card">{p}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
