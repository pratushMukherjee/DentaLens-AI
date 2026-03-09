"""Chat Assistant page — conversational AI with multi-agent routing."""

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

# API base URL
api_url = st.session_state.get("api_base_url", "http://localhost:8000")

# New conversation button
if st.sidebar.button("🔄 New Conversation"):
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    display_message(msg["role"], msg["content"], msg.get("agent_source"))
    if msg.get("sources"):
        display_sources(msg["sources"])

# Chat input
if prompt := st.chat_input("Ask about dental benefits or claims..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    display_message("user", prompt)

    # Call API
    with st.spinner("Thinking..."):
        try:
            response = httpx.post(
                f"{api_url}/api/v1/chat",
                json={
                    "conversation_id": st.session_state.conversation_id,
                    "message": prompt,
                },
                timeout=30.0,
            )
            data = response.json()

            # Update conversation ID
            st.session_state.conversation_id = data.get("conversation_id")

            # Display assistant response
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

# Example queries
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
            st.session_state.messages.append({"role": "user", "content": ex})
            st.rerun()
