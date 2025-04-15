
import os
import base64
from dotenv import load_dotenv
import streamlit as st
from utils.rag import query_documents

# Must be first
st.set_page_config(page_title="MBA ASSISTANT", page_icon="assets/ai_icon.png")

load_dotenv()

# Load CSS
# st.markdown("<style>" + open("style/chatbot.css").read() + "</style>", unsafe_allow_html=True)

# Function to convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

# Embed AI icon using base64
img_base64 = get_base64_image("assets/ai_icon.png")

# Custom animated title with icon
st.markdown(
    f"""
    <style>
    .title-container {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .title-text {{
        font-size: 2em;
        font-weight: bold;
        background: linear-gradient(90deg, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 3s infinite ease-in-out;
        margin: 0;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.85; transform: scale(1.02); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    </style>
    <div class='title-container'>
        <img src="{img_base64}" width='40'/>
        <div class='title-text'>MBA ASSISTANT</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Ask questions from your uploaded documents, images, or just type queries below.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# File uploader
uploaded_files = st.file_uploader("Upload PDFs, images, or docs", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

# Chat input and response
user_input = st.chat_input("Ask a question about your content...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = query_documents(user_input, st.session_state.get("uploaded_files", []))
            except Exception as e:
                answer = f"❌ Error: {e}"
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# Render full chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])