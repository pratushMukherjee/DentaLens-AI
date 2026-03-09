"""DentaLens AI -- Streamlit entry point."""

import sys
from pathlib import Path

# Ensure the project src is on the path for all page imports
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

import streamlit as st

from dentalens.frontend.components.styles import (
    BRAND,
    brand_header,
    feature_card,
    footer,
    inject_styles,
    stat_card,
)

st.set_page_config(
    page_title="DentaLens AI | Delta Dental",
    page_icon="https://www.deltadentalmi.com/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

# ── Sidebar ──
with st.sidebar:
    st.markdown(
        '<div style="text-align:center; padding: 1rem 0;">'
        '<span style="font-size:2.2rem;">&#9790;</span><br>'
        '<span style="font-size:1.4rem; font-weight:700;">DentaLens AI</span><br>'
        '<span style="font-size:0.85rem; opacity:0.8;">Enterprise AI for Dental Insurance</span>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    # API configuration
    api_url = st.text_input("API Base URL", value="http://localhost:8000", key="api_url")
    st.session_state["api_base_url"] = api_url

    st.divider()
    st.markdown("#### Navigation")
    st.page_link("pages/01_chat.py", label="Chat Assistant", icon="💬")
    st.page_link("pages/02_claims_dashboard.py", label="Claims Dashboard", icon="📊")
    st.page_link("pages/03_evaluation.py", label="Evaluation", icon="🔍")

    st.divider()
    st.caption("Powered by LangChain, FastAPI, ChromaDB")

# ── Hero header ──
brand_header(
    "Welcome to DentaLens AI",
    "An Enterprise AI Platform for Dental Insurance — We Do Dental. Better.",
)

# ── Feature cards ──
cols = st.columns(3, gap="large")
cards = [
    ("💬", "Chat Assistant",
     "Ask about dental benefit plans or claims data. "
     "Multi-agent AI routes your query to the right specialist."),
    ("📊", "Claims Dashboard",
     "Interactive analytics on 1,200+ dental claims. "
     "Summary statistics, procedure breakdowns, and anomaly detection."),
    ("🔍", "Model Evaluation",
     "Assess RAG quality with faithfulness, relevance, "
     "hallucination detection, and responsible AI checks."),
]
for col, (icon, title, desc) in zip(cols, cards):
    with col:
        st.markdown(feature_card(icon, title, desc), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Architecture section ──
st.markdown(
    f'<h3 style="color:{BRAND["primary_dark"]}; margin-top:1rem;">'
    "Architecture Highlights</h3>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(
        f'<h4 style="color:{BRAND["primary"]};">Multi-Agent System</h4>',
        unsafe_allow_html=True,
    )
    st.markdown("""
- **Router Agent** -- Classifies intent, delegates to specialists
- **Benefits Agent** -- RAG-powered Q&A with source citations
- **Claims Agent** -- Data-driven analysis and anomaly detection
""")

    st.markdown(
        f'<h4 style="color:{BRAND["primary"]};">Design Patterns</h4>',
        unsafe_allow_html=True,
    )
    st.markdown("""
Factory &bull; Strategy &bull; Repository &bull; Dependency Injection &bull; Chain of Responsibility
""")

with col2:
    st.markdown(
        f'<h4 style="color:{BRAND["primary"]};">Technology Stack</h4>',
        unsafe_allow_html=True,
    )

    tech_cols = st.columns(2)
    with tech_cols[0]:
        st.markdown(stat_card("GPT-4o-mini", "LLM"), unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown(stat_card("ChromaDB", "Vector Store"), unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown(stat_card("FastAPI", "REST API"), unsafe_allow_html=True)
    with tech_cols[1]:
        st.markdown(stat_card("text-embedding-3-small", "Embeddings"), unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown(stat_card("LangChain", "Orchestration"), unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown(stat_card("Streamlit", "Frontend"), unsafe_allow_html=True)

# ── Responsible AI section ──
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f'<h3 style="color:{BRAND["primary_dark"]};">Responsible AI</h3>',
    unsafe_allow_html=True,
)
rai_cols = st.columns(4, gap="medium")
rai_items = [
    ("🛡️", "Faithfulness", "Responses grounded in source documents"),
    ("🎯", "Relevance", "Answers directly address the question"),
    ("🔎", "Hallucination Detection", "Unsupported claims identified"),
    ("🔒", "PII Protection", "Personal data never exposed"),
]
for col, (icon, title, desc) in zip(rai_cols, rai_items):
    with col:
        st.markdown(feature_card(icon, title, desc), unsafe_allow_html=True)

footer()
