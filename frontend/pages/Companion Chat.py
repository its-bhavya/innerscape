import streamlit as st
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

st.set_page_config(page_title="Companion Chat", layout="wide")
st.title("🧘 Companion Chat")

# Initialize chat state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "context_loaded" not in st.session_state:
    st.session_state.context_loaded = False

# First message
if not st.session_state.context_loaded:
    summary = st.session_state.get("summary", "")
    intro = summary.strip() or "Hey! I'm here for you—how are you feeling today?"
    st.session_state.chat_history.append({"role": "assistant", "content": intro})
    st.session_state.context_loaded = True

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle input
if prompt := st.chat_input("Type your message here…"):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Build context
    transcript = st.session_state.get("transcript", "")
    summary = st.session_state.get("summary", "")
    context_intro = f"""You're a compassionate emotional wellness companion.
You are friendly, empathetic, and conversational.
This is the user's journal entry: {transcript}
Summary of it: {summary}

Now continue the chat, responding to the user's last message in a natural tone.
Ask follow-ups where needed.
"""

    chat_history = [
        {"role": msg["role"], "parts": [msg["content"]]}
        for msg in st.session_state.chat_history
    ]

    try:
        with st.chat_message("assistant"):
            stream = model.start_chat(history=chat_history)
            gemini_stream = stream.send_message(prompt, stream=True)

            collected_chunks = []

            def response_generator():
                for chunk in gemini_stream:
                    collected_chunks.append(chunk.text)
                    yield chunk.text

            # Streaming via write_stream
            final_text = st.write_stream(response_generator)
            st.session_state.chat_history.append({"role": "assistant", "content": final_text})

    except Exception as e:
        st.error(f"Something went wrong: {e}")
