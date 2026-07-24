import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
CHATBOT_DIR = PROJECT_DIR / "FAQ_Chatbot_Updated_CodeAlpha"
if str(CHATBOT_DIR) not in sys.path:
    sys.path.insert(0, str(CHATBOT_DIR))

from chatbot import get_response


st.set_page_config(
    page_title="College FAQ Chatbot",
    page_icon="🎓",
    layout="centered"
)


st.title("🎓 College FAQ Chatbot")
st.write("Ask me anything about the college.")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# User input
user_question = st.chat_input("Type your question here...")


if user_question:

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.write(user_question)

    # Generate AI response
    response = get_response(user_question)

    # Typing animation
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for character in response:
            full_response += character
            time.sleep(0.03)
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    # Save bot response in history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })