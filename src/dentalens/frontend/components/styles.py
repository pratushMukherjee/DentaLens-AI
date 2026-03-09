"""Delta Dental brand styling for Streamlit."""

# Delta Dental brand colors
BRAND = {
    "primary": "#41A928",       # Delta Dental green
    "primary_dark": "#2E7A1C",  # Darker green for hover/headers
    "primary_light": "#EAF7E6", # Light green tint
    "accent": "#4CAF50",        # Green accent (health/wellness)
    "accent_dark": "#2E7D32",
    "white": "#FFFFFF",
    "bg_light": "#F0F4F8",      # Light gray background
    "text_dark": "#1A2B3C",     # Near-black text
    "text_muted": "#5A6B7C",    # Muted text
    "border": "#D0D9E3",        # Subtle borders
    "success": "#2E7D32",
    "warning": "#E65100",
    "error": "#C62828",
}

CUSTOM_CSS = f"""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BRAND["primary_dark"]} 0%, {BRAND["primary"]} 100%);
        color: white;
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption {{
        color: white !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.2);
    }}
    section[data-testid="stSidebar"] .stTextInput input {{
        background: rgba(255,255,255,0.9);
        color: #1A2B3C;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 8px;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: rgba(255,255,255,0.15);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 8px;
        width: 100%;
        text-align: left;
        transition: all 0.2s;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,255,255,0.25);
        border-color: rgba(255,255,255,0.5);
    }}

    /* ── Page links in sidebar ── */
    section[data-testid="stSidebar"] a {{
        color: white !important;
    }}

    /* ── Header area ── */
    .main .block-container {{
        padding-top: 2rem;
        max-width: 1100px;
    }}

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {{
        background: {BRAND["white"]};
        border: 1px solid {BRAND["border"]};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    div[data-testid="stMetric"] label {{
        color: {BRAND["text_muted"]} !important;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {BRAND["primary"]} !important;
        font-weight: 700;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: {BRAND["primary"]};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        background: {BRAND["primary_dark"]};
        color: white;
    }}

    /* ── Chat messages ── */
    div[data-testid="stChatMessage"] {{
        border-radius: 12px;
        border: 1px solid {BRAND["border"]};
        margin-bottom: 0.5rem;
    }}

    /* ── Expander ── */
    .streamlit-expanderHeader {{
        font-weight: 600;
        color: {BRAND["primary"]};
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {{
        color: {BRAND["text_muted"]};
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        color: {BRAND["primary"]};
        border-bottom-color: {BRAND["primary"]};
    }}

    /* ── Dataframes ── */
    .stDataFrame thead th {{
        background: {BRAND["primary"]} !important;
        color: white !important;
        font-weight: 600;
    }}

    /* ── Brand header bar ── */
    .brand-header {{
        background: linear-gradient(135deg, {BRAND["primary_dark"]}, {BRAND["primary"]});
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }}
    .brand-header h1 {{
        color: white;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }}
    .brand-header p {{
        color: rgba(255,255,255,0.85);
        margin: 0.25rem 0 0 0;
        font-size: 1rem;
    }}

    /* ── Feature cards grid ── */
    .feature-card {{
        background: {BRAND["white"]};
        border: 1px solid {BRAND["border"]};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s;
        height: 100%;
    }}
    .feature-card:hover {{
        box-shadow: 0 4px 16px rgba(65,169,40,0.15);
        border-color: {BRAND["primary"]};
    }}
    .feature-card .icon {{
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }}
    .feature-card h3 {{
        color: {BRAND["primary_dark"]};
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }}
    .feature-card p {{
        color: {BRAND["text_muted"]};
        font-size: 0.9rem;
        margin: 0;
    }}

    /* ── Stat card ── */
    .stat-card {{
        background: {BRAND["white"]};
        border: 1px solid {BRAND["border"]};
        border-left: 4px solid {BRAND["primary"]};
        border-radius: 8px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    .stat-card .value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {BRAND["primary"]};
        line-height: 1.2;
    }}
    .stat-card .label {{
        font-size: 0.8rem;
        color: {BRAND["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }}

    /* ── Footer ── */
    .footer {{
        margin-top: 3rem;
        padding: 1.5rem 0;
        border-top: 1px solid {BRAND["border"]};
        text-align: center;
        color: {BRAND["text_muted"]};
        font-size: 0.8rem;
    }}

    /* ── Hide Streamlit default menu/footer ── */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
"""


def inject_styles():
    """Inject Delta Dental brand CSS into the Streamlit page."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def brand_header(title: str, subtitle: str = ""):
    """Render a Delta Dental branded page header."""
    import streamlit as st
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="brand-header"><h1>{title}</h1>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def feature_card(icon: str, title: str, description: str):
    """Return HTML for a feature card."""
    return f"""
    <div class="feature-card">
        <div class="icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """


def stat_card(value: str, label: str):
    """Return HTML for a stat card with left accent border."""
    return f"""
    <div class="stat-card">
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>
    """


def footer():
    """Render the page footer."""
    import streamlit as st
    st.markdown(
        '<div class="footer">'
        "DentaLens AI &mdash; Enterprise AI for Dental Insurance<br>"
        "Built with LangChain, FastAPI, ChromaDB &bull; "
        '<span style="color: #41A928;">We Do Dental. Better.</span>'
        "</div>",
        unsafe_allow_html=True,
    )
