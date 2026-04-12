import streamlit as st
from agent.graph import AutoStreamAgent

st.set_page_config(page_title="AutoStream AI Agent", page_icon="🤖", layout="centered")

st.title("🤖 AutoStream Conversational AI Agent")
st.write("Ask about pricing, features, policies, or get started with a plan.")

if "agent" not in st.session_state:
    st.session_state.agent = AutoStreamAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    result = st.session_state.agent.chat(user_input)
    reply = result["response"]

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.expander("Debug Info"):
        st.json({
            "intent": result["intent"],
            "lead_name": result["lead_name"],
            "lead_email": result["lead_email"],
            "creator_platform": result["creator_platform"],
            "lead_captured": result["lead_captured"],
        })