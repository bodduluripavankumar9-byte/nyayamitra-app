import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="NyayaMitra - AI Legal Counsel",
    page_icon="⚖️",
    layout="wide"
)

# Backend API URL (Local development)
API_URL = "http://127.0.0.1:8000/api/consult"
HISTORY_URL = "http://127.0.0.1:8000/api/history"

# Sidebar for Consultation History
st.sidebar.title("📜 Consultation History")
if st.sidebar.button("Refresh History"):
    pass

try:
    history_response = requests.get(HISTORY_URL)
    if history_response.status_code == 200:
        consultations = history_response.json()
        if consultations:
            for item in consultations:
                # Show truncated query as the sidebar button/label
                with st.sidebar.expander(f"Q: {item['query'][:30]}..."):
                    st.write(f"**Full Query:** {item['query']}")
                    st.write(f"**Date:** {item['created_at']}")
                    if st.button("View Opinion", key=f"hist_{item['id']}"):
                        st.session_state['selected_opinion'] = item['legal_opinion']
        else:
            st.sidebar.info("No past consultations found yet.")
    else:
            st.sidebar.warning("Could not fetch history from server.")
except Exception as e:
    st.sidebar.error("Backend offline.")

# Main Content Area
st.title("⚖️ NyayaMitra")
st.subheader("Your Multilingual AI Legal Counsel (Based on Indian Law)")

# User input text area
user_query = st.text_area(
    "Describe your legal issue or question:",
    placeholder="e.g., What are the tenant rights regarding security deposit refunds in India?"
)

if st.button("Get Legal Counsel", type="primary"):
    if not user_query.strip():
        st.warning("Please enter a legal query before submitting.")
    else:
        with st.spinner("Analyzing legal frameworks and consulting provisions..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"query": user_query}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis Complete")
                    st.session_state['selected_opinion'] = result.get("legal_opinion")
                else:
                    st.error(f"Error from server: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Failed to connect to the backend service: {e}")

# Display Selected or Recent Opinion
if 'selected_opinion' in st.session_state:
    st.markdown("---")
    st.markdown("### Legal Opinion & Guidance")
    st.markdown(st.session_state['selected_opinion'])