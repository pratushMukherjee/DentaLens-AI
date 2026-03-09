"""Chat Assistant page -- conversational AI with multi-agent routing."""

import sys
from pathlib import Path

# Ensure the project src is on the path
_project_root = Path(__file__).resolve().parents[4]
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

import httpx
import streamlit as st

from dentalens.frontend.components.chat_widget import display_message, display_sources
from dentalens.frontend.components.styles import BRAND, brand_header, footer, inject_styles

inject_styles()

brand_header("Chat Assistant", "Ask about dental benefits, claims, or insurance -- powered by multi-agent AI")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# API base URL
api_url = st.session_state.get("api_base_url", "http://localhost:8000")

# Sidebar controls
with st.sidebar:
    if st.button("New Conversation", key="new_convo"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.session_state.pending_query = None
        st.rerun()

    st.divider()
    st.markdown("#### Try an Example")
    examples = [
        ("I got a $1,200 bill for a crown. What should I owe?", "bill"),
        ("I need a root canal. What will my out-of-pocket cost be?", "rootcanal"),
        ("What preventive services are fully covered this year?", "preventive"),
        ("Compare coverage for crowns, orthodontics, and annual maximums", "compare"),
        ("Deep cleaning and two fillings — estimate my cost", "estimate"),
        ("My implant claim was denied. Why and can I appeal?", "denied"),
        ("Are there any billing anomalies in claims data?", "anomaly"),
        ("What's the approval rate for claims?", "approval"),
    ]
    for ex, key in examples:
        if st.button(ex, key=f"ex_{key}"):
            st.session_state.pending_query = ex
            st.rerun()

    st.divider()
    st.markdown(
        '<div style="font-size:0.75rem; opacity:0.7;">'
        "Queries are routed to specialist agents:<br>"
        f'<span style="color:#81C784;">&#9679;</span> Benefits Agent &mdash; plan Q&amp;A<br>'
        f'<span style="color:#41A928;">&#9679;</span> Claims Agent &mdash; data analysis'
        "</div>",
        unsafe_allow_html=True,
    )


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

footer()
