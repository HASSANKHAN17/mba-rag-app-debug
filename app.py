import os
import base64
import streamlit as st
from dotenv import load_dotenv
from utils.rag import query_documents, analyze_file

# Must be first
st.set_page_config(page_title="MBA ASSISTANT", page_icon="assets/ai_icon.png")

load_dotenv()

# Load custom CSS
try:
    with open("style/chatbot.css", "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ chatbot.css not found. Using default styles.")

# Function to convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

# Custom title
try:
    img_base64 = get_base64_image("assets/ai_icon.png")
except FileNotFoundError:
    st.warning("⚠️ AI icon not found.")
    img_base64 = ""

st.markdown(
    f"""
    <style>
    .title-container {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .gradient-text {{
        font-size: 2.2em;
        font-weight: bold;
        background: linear-gradient(90deg, #7b2ff7, #0a84ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }}
    </style>
    <div class='title-container'>
        <img src="{img_base64}" width='70'/>
        <div class='gradient-text'>MBA ASSISTANT</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Ask questions from your uploaded documents, spreadsheets, or images below.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# Upload files
uploaded_files = st.file_uploader(
    "Upload PDFs, images, CSV, or Excel files",
    type=["pdf", "png", "jpg", "jpeg", "csv", "xls", "xlsx"],
    accept_multiple_files=True
)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

# Chat input
user_input = st.chat_input("Ask a question about your content...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = analyze_file(user_input, st.session_state.uploaded_files)
                if result:
                    st.markdown(result.get("summary", ""))
                    if "visuals" in result:
                        for plot in result["visuals"]:
                            st.pyplot(plot)
                else:
                    answer = query_documents(user_input, st.session_state.uploaded_files)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"❌ Error: {e}")
