"""Chat Assistant page — conversational AI with multi-agent routing."""

import sys
from pathlib import Path

# Ensure the project src is on the path
_project_root = Path(__file__).resolve().parents[4]
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

import httpx
import streamlit as st

from dentalens.frontend.components.chat_widget import display_message, display_sources

st.title("💬 Chat Assistant")
st.caption("Ask about dental benefits, claims, or insurance — powered by multi-agent AI")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# API base URL
api_url = st.session_state.get("api_base_url", "http://localhost:8000")

# New conversation button
if st.sidebar.button("🔄 New Conversation"):
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.session_state.pending_query = None
    st.rerun()

# Example queries in sidebar
with st.sidebar:
    st.markdown("### Example Questions")
    examples = [
        "Does the PPO Gold plan cover root canals?",
        "Compare the PPO and HMO plans",
        "What is the annual maximum?",
        "Are there any billing anomalies?",
        "What's the approval rate for claims?",
        "How do I file a claim?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:20]}"):
            st.session_state.pending_query = ex
            st.rerun()


def send_message(message: str) -> None:
    """Send a message to the API and store the response."""
    st.session_state.messages.append({"role": "user", "content": message})
    display_message("user", message)

    with st.spinner("Thinking..."):
        try:
            response = httpx.post(
                f"{api_url}/api/v1/chat",
                json={
                    "conversation_id": st.session_state.conversation_id,
                    "message": message,
                },
                timeout=30.0,
            )
            data = response.json()

            st.session_state.conversation_id = data.get("conversation_id")

            assistant_msg = {
                "role": "assistant",
                "content": data.get("response", "No response received."),
                "agent_source": data.get("agent_used"),
                "sources": data.get("sources", []),
            }
            st.session_state.messages.append(assistant_msg)
            display_message("assistant", assistant_msg["content"], assistant_msg["agent_source"])
            display_sources(assistant_msg["sources"])

        except httpx.ConnectError:
            st.error("Cannot connect to the API. Make sure the backend is running: `make api`")
        except Exception as e:
            st.error(f"Error: {e}")


# Display chat history
for msg in st.session_state.messages:
    display_message(msg["role"], msg["content"], msg.get("agent_source"))
    if msg.get("sources"):
        display_sources(msg["sources"])

# Handle pending query from example buttons
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
    send_message(query)

# Handle typed input
if prompt := st.chat_input("Ask about dental benefits or claims..."):
    send_message(prompt)
