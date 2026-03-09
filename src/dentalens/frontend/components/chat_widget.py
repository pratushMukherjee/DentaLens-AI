"""Reusable chat UI components for Streamlit."""

import streamlit as st


def display_message(role: str, content: str, agent_source: str | None = None) -> None:
    """Display a chat message with optional agent badge."""
    with st.chat_message(role):
        if agent_source and role == "assistant":
            agent_colors = {
                "benefits": "green",
                "claims": "blue",
                "router": "gray",
            }
            color = agent_colors.get(agent_source, "gray")
            st.caption(f":{color}[Agent: {agent_source}]")
        st.markdown(content)


def display_sources(sources: list[dict]) -> None:
    """Display source citations in an expandable section."""
    if not sources:
        return
    with st.expander(f"📄 Sources ({len(sources)})"):
        for src in sources:
            doc = src.get("document", "Unknown")
            doc_type = src.get("document_type", "")
            score = src.get("relevance_score")
            score_text = f" (score: {score:.3f})" if score is not None else ""
            st.markdown(f"- **{doc}** [{doc_type}]{score_text}")
