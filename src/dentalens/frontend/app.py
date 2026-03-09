"""DentaLens AI — Streamlit entry point."""

import streamlit as st

st.set_page_config(
    page_title="DentaLens AI",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
with st.sidebar:
    st.title("🦷 DentaLens AI")
    st.markdown("Enterprise AI for Dental Insurance")
    st.divider()

    # API configuration
    api_url = st.text_input("API Base URL", value="http://localhost:8000", key="api_url")
    st.session_state["api_base_url"] = api_url

    st.divider()
    st.markdown("### Navigation")
    st.page_link("src/dentalens/frontend/pages/01_chat.py", label="💬 Chat Assistant")
    st.page_link("src/dentalens/frontend/pages/02_claims_dashboard.py", label="📊 Claims Dashboard")
    st.page_link("src/dentalens/frontend/pages/03_evaluation.py", label="🔍 Evaluation")

    st.divider()
    st.caption("Built with LangChain, FastAPI, ChromaDB")
    st.caption("Demonstrating RAG, Multi-Agent AI, Responsible AI")

# Main page
st.title("Welcome to DentaLens AI")
st.markdown("""
### An Enterprise AI Platform for Dental Insurance

DentaLens AI demonstrates cutting-edge AI technologies applied to the dental insurance domain:

---

**💬 Chat Assistant**
Ask questions about dental benefit plans or claims data. The multi-agent system automatically
routes your query to the right specialist:
- **Benefits Agent** — RAG-powered Q&A with source citations
- **Claims Agent** — Data-driven claims analysis and anomaly detection

**📊 Claims Dashboard**
Interactive analytics on dental claims data:
- Summary statistics and approval rates
- Claims by procedure category and status
- Anomaly detection for billing irregularities

**🔍 Evaluation**
Model quality assessment with responsible AI metrics:
- Faithfulness — Are responses grounded in source documents?
- Relevance — Do responses address the user's question?
- Hallucination Detection — Are there unsupported claims?
- Responsible AI — PII protection, medical advice boundaries

---

### Architecture Highlights

| Component | Technology |
|-----------|-----------|
| LLM | OpenAI GPT-4o-mini |
| Embeddings | text-embedding-3-small |
| Vector Store | ChromaDB |
| Orchestration | LangChain |
| API | FastAPI + Pydantic v2 |
| Frontend | Streamlit |

### Design Patterns
Factory • Strategy • Repository • Dependency Injection • Chain of Responsibility
""")
