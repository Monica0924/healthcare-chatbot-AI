"""
Streamlit Web App for the Medical Assistant AI (Informational Only)

Run locally:
  pip install streamlit
  streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st
from medical_assistant_agent import generate_otc_advice


st.set_page_config(page_title="Informational Medical Assistant", page_icon="🩺", layout="centered")

st.title("🩺 Informational Medical Assistant")
st.caption(
    "Provides general, educational information about symptom relief using OTC options. "
    "Not a substitute for professional medical advice."
)

with st.form("symptom_form"):
    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="e.g., sore throat, runny nose, mild fever for 2 days",
        height=120,
    )
    submitted = st.form_submit_button("Get Suggestions")

if submitted:
    if not symptoms.strip():
        st.warning("Please enter some symptoms.")
    else:
        result = generate_otc_advice(symptoms)
        st.markdown(result)

with st.expander("About"):
    st.write(
        "This app suggests common over-the-counter options and general wellness tips based on your input. "
        "It always includes safety disclaimers and red flags for when to seek urgent care."
    )


