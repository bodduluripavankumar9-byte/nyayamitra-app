import streamlit as st
import requests
from streamlit_mic_recorder import mic_recorder

# Page configuration
st.set_page_config(
    page_title="NyayaMitra - AI Legal Counsel",
    page_icon="⚖️",
    layout="wide"
)

API_URL = "https://nyayamitra-app.onrender.com/api/consult"
HISTORY_URL = "https://nyayamitra-app.onrender.com/api/history"

st.title("⚖️ NyayaMitra")
st.subheader("Your Multilingual AI Legal Counsel (Based on Indian Law)")

# Option to choose input method
input_method = st.radio("Choose input method:", ["Type Query", "Speak (Microphone)"])

user_query = ""

if input_method == "Type Query":
    user_query = st.text_area("Describe your legal issue or question:", placeholder="e.g., What are the tenant rights regarding security deposit refunds in India?")

else:
    st.write("Click the microphone to start recording your legal problem:")
    # Renders a mic button
    audio_data = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", key='legal_mic')
    
    if audio_data:
        # Save audio bytes temporarily or send directly to backend/Whisper
        st.audio(audio_data['bytes'])
        
        # We can send the audio file to backend for Whisper transcription, 
        # or handle transcription directly using OpenAI API!
        with st.spinner("Transcribing your speech..."):
            files = {"file": ("audio.wav", audio_data['bytes'], "audio/wav")}
            # Optional: Call a backend endpoint that handles Whisper STT
            # For simplicity, we can process it if you build a /api/transcribe endpoint, 
            # or handle it directly. Let's see your backend setup!