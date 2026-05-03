"""Home page - redirects to main app."""

import streamlit as st
from streamlit_app.app import render_main_content

st.set_page_config(
    page_title="StoryAlchemy - Home",
    page_icon="🏠",
    layout="wide",
)

render_main_content()
