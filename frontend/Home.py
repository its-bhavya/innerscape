# streamlit_app_name: Home
from tkinter import Image
import streamlit as st
import requests
import io
import os

st.set_page_config(page_title="InnerScape",layout="wide")
st.markdown("""
<style>
@keyframes slideIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

.strategy-card {
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: slideIn 0.4s ease forwards;
}

.strategy-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
        .header {
            display: flex;
            align-items: center;
            background-color: #f3f3f3;
            padding: 1rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        }
        .header img {
            height: 60px;
            margin-right: 20px;
        }
        .header h1 {
            color: #1a1a1a;
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
        }
    </style>

    <div class="header">
        <img src="https://static.thenounproject.com/png/66159-200.png" alt="InnerSpace Logo">
        <h1>InnerScape: AI Wellness Journal</h1>
    </div>
    """,
    unsafe_allow_html=True
)

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
os.environ["STREAMLIT_DISABLE_WATCHDOG_WARNINGS"] = "1"

# Initialize session state variables
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "prompts" not in st.session_state:
    st.session_state.prompts = []
if "resources" not in st.session_state:
    st.session_state.resources = []
if "mindmap_img" not in st.session_state:
    st.session_state.mindmap_img = None
if "central_topic" not in st.session_state:
    st.session_state.central_topic = None

st.markdown("### :material/mic: Share your journal entry")

tab1, tab2, tab3 = st.tabs(["Enter Text", "Record Audio", "Upload Audio"])

uploaded_file = None
input_text = None
recorded_file = None

with tab1:
    input_text = st.text_area(
        "Write about your day, your feelings, or anything on your mind...",
        height=200,
        placeholder="There's no rush, just speak your truth."
    )
    if input_text:
        st.session_state.transcript = input_text
        st.session_state.summary = None
        st.session_state.prompts = []
        st.session_state.resources = []
        st.session_state.mindmap_img = None

with tab2:
    recorded_file = st.audio_input("Record your journal entry...")
    if recorded_file:
        audio_bytes = recorded_file.read()
        st.audio(audio_bytes)
        if st.button("Transcribe Recorded Audio"):
            with st.spinner("Transcribing recorded audio..."):
                try:
                    files = {"file": ("recording.wav", io.BytesIO(audio_bytes), "audio/wav")}
                    res = requests.post(f"{API_BASE}/transcribe", files=files)
                except Exception as e:
                    st.error(f"Transcription request failed: {e}")
                    res = None

                if res and res.status_code == 200:
                    st.session_state.transcript = res.json()["transcript"]
                    st.success("Transcription complete.")
                    st.session_state.summary = None
                    st.session_state.prompts = []
                    st.session_state.resources = []
                    st.session_state.mindmap_img = None
                else:
                    st.error("Transcription failed.")
                    if res:
                        st.json(res.json())

with tab3:
    uploaded_file = st.file_uploader("Upload an MP3/WAV file", type=["mp3", "wav"])
    if uploaded_file:
        if st.button("Transcribe Uploaded Audio"):
            with st.spinner("Listening to your thoughts..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                res = requests.post(f"{API_BASE}/transcribe", files=files)
                
                sum_res = requests.post(f"{API_BASE}/journal/summary", json={"text": st.session_state.transcript})
                if sum_res.status_code == 200:
                    st.session_state.summary = sum_res.json().get("summary", "")
            
            if res.status_code == 200:
                st.session_state.transcript = res.json()["transcript"]
                st.session_state.summary = None
                st.session_state.central_topic = None
                st.session_state.prompts = []
                st.session_state.resources = []
                st.session_state.mindmap_img = None
            else:
                st.error("Transcription failed.")
                st.json(res.json())


# Show transcript preview
if st.session_state.transcript:
    with st.spinner("Understanding your thoughts..."):
        sum_res = requests.post(f"{API_BASE}/journal/summary", json={"text": st.session_state.transcript})
        if sum_res.status_code == 200:
            st.session_state.summary = sum_res.json().get("summary", "")
    
    st.markdown("### :material/speech_to_text: Your Journal Entry")
    with st.expander("Show full journal text", expanded=False):
        st.write(st.session_state.transcript)

col1, col2 = st.columns(2)

# Button to analyze journal
if st.session_state.transcript:
    with col1:
        if st.button("Visualize My Journal"):
            with st.spinner("Reflecting on your words..."):
                res = requests.post(f"{API_BASE}/extract", json={"transcript": st.session_state.transcript})
            
                if res.status_code == 200:
                    
                    central_topic = res.json()["central_topic"]
                    st.session_state.central_topic = central_topic
                else:
                    st.error("Mindmap generation failed.")
                    st.json(res.json())
        
    with col2:
        if st.button("Show me ways to feel better"):
            with st.spinner("Finding ways to ease your mind..."):
                # Call resources agent
                res_res = requests.post(f"{API_BASE}/journal/resources", json={"text": st.session_state.transcript})
                if res_res.status_code == 200:
                    st.session_state.resources = res_res.json().get("resources", [])
                else:
                    st.error("Failed to fetch wellness resources.")

# Display summary, prompts, and resources
if st.session_state.central_topic:
    image_url = f"{API_BASE}/mindmap/{st.session_state.central_topic.replace(' ', '-')}"
    st.image(image_url, caption=f"Mindmap: {st.session_state.central_topic}", use_container_width=True)

if st.session_state.resources:
    st.markdown("### Strategies you might find helpful")

    for i in range(0, len(st.session_state.resources), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(st.session_state.resources):
                strategy = st.session_state.resources[i + j]
                with cols[j]:
                    st.markdown(
                        f"""
                        <div class="strategy-card">
                            <h4 style="margin-bottom: 0.5rem;">{strategy.get("title", f"Strategy {i+j+1}")}</h4>
                            <p style="color: #666; font-size: 0.9rem;">{strategy.get("summary", "")}</p>
                            <ul style="padding-left: 1.2rem; margin-top: 0.5rem;">
                                {''.join(f"<li>{step}</li>" for step in strategy.get("steps", []))}
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
