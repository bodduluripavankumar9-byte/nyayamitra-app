import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="NyayaMitra - AI Legal Counsel",
    page_icon="⚖️",
    layout="wide"
)

API_URL = "https://nyayamitra-app.onrender.com/api/consult"
HISTORY_URL = "https://nyayamitra-app.onrender.com/api/history"
TRANSCRIBE_URL = "https://nyayamitra-app.onrender.com/api/transcribe"

st.title("⚖️ NyayaMitra")
st.subheader("Your Multilingual AI Legal Counsel (Based on Indian Law)")

# Choose input method
input_method = st.radio("Choose input method:", ["Type Query", "Speak (Microphone)"])

user_query = ""

if input_method == "Type Query":
    user_query = st.text_area("Describe your legal issue or question:", placeholder="e.g., What are the tenant rights regarding security deposit refunds in India?")
else:
    st.write("Record your legal problem below:")
    # Native Streamlit audio recorder (requires no extra pip packages!)
    audio_file = st.audio_input("Record your voice")
    
    if audio_file is not None:
        with st.spinner("Transcribing your voice..."):
            files = {"file": ("audio.wav", audio_file.getvalue(), "audio/wav")}
            response = requests.post(TRANSCRIBE_URL, files=files)
            if response.status_code == 200:
                user_query = response.json().get("text", "")
                st.success(f"Transcribed Text: {user_query}")
            else:
                st.error("Failed to transcribe audio.")

# Button to submit query
if st.button("Get Legal Counsel") and user_query:
    with st.spinner("Analyzing legal query..."):
        payload = {"query": user_query}
        res = requests.post(API_URL, json=payload)
        if res.status_code == 200:
            st.success("Analysis Complete")
            st.markdown("### Legal Opinion & Guidance")
            st.write(res.json().get("opinion"))
        else:
            st.error(f"Error: {res.text}")