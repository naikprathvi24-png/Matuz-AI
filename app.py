import streamlit as st
from utils.api import get_ai_response
from utils.text_cleaner import clean_text
from utils.prompts import summary_prompt

# Page Config
st.set_page_config(
    page_title="AI Notes Summarizer",
    page_icon="🧠",
    layout="centered"
)

# Load CSS
with open("styles/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title
st.title("🧠 AI Notes Summarizer")

st.write("Paste your notes below and generate:")
st.write("✅ Summary")
st.write("✅ Important Points")
st.write("✅ Questions & Answers")

# User Input
notes = st.text_area(
    "Paste Notes Here",
    height=300,
    placeholder="Enter long notes..."
)

# Generate Button
if st.button("Generate AI Notes"):

    if notes.strip() == "":
        st.warning("Please enter notes.")
    else:

        cleaned_notes = clean_text(notes)

        prompt = summary_prompt(cleaned_notes)

        with st.spinner("Generating AI Response..."):

            response = get_ai_response(prompt)

            st.success("AI Response Generated")

            st.markdown("## 📄 Output")
            st.write(response)