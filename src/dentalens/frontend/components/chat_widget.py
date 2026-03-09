"""Reusable chat UI components for Streamlit."""

import streamlit as st


def display_message(role: str, content: str, agent_source: str | None = None) -> None:
    """Display a chat message with optional agent badge."""
    with st.chat_message(role):
        if agent_source and role == "assistant":
            agent_badges = {
                "benefits": ("🛡️", "#2E7D32", "Benefits Agent"),
                "claims": ("📊", "#0054A4", "Claims Agent"),
                "router": ("🔀", "#5A6B7C", "Router"),
            }
            icon, color, label = agent_badges.get(agent_source, ("🤖", "#5A6B7C", agent_source))
            st.markdown(
                f'<span style="background:{color}; color:white; padding:2px 10px; '
                f'border-radius:12px; font-size:0.75rem; font-weight:600;">'
                f'{icon} {label}</span>',
                unsafe_allow_html=True,
            )
        st.markdown(content)


def display_sources(sources: list[dict]) -> None:
    """Display source citations in an expandable section."""
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})"):
        for src in sources:
            doc = src.get("document", "Unknown")
            doc_type = src.get("document_type", "")
            score = src.get("relevance_score")
            score_text = f" — relevance: {score:.3f}" if score is not None else ""
            st.markdown(
                f'<div style="padding:4px 0; border-bottom:1px solid #E8F1FA;">'
                f'<strong>{doc}</strong> '
                f'<span style="color:#5A6B7C; font-size:0.8rem;">[{doc_type}]{score_text}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
