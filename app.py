import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import requests

# Load environment variables
load_dotenv()

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="ChatPDF Pro", page_icon="📚")

# Get the Groq API key from environment variable
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize session state variables
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Custom CSS for retro-themed UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
    
    body {
        background-color: #000000;
        color: #ff0000;
        font-family: 'VT323', monospace;
    }
    .stApp {
        background-color: #000000;
    }
    .css-1d391kg {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 10px #ff0000;
    }
    .st-bw {
        background-color: #000000;
    }
    h1, h2, h3 {
        color: #8b0000;
        text-shadow: 2px 2px #000000;
        font-family: 'VT323', monospace;
    }
    .stButton>button {
        background-color: #8b0000;
        color: #000000;
        border: 2px solid #ff0000;
        font-family: 'VT323', monospace;
    }
    .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: #ff0000;
        border: 2px solid #ff0000;
        font-family: 'VT323', monospace;
    }
    .stMarkdown, .stText {
        font-family: 'VT323', monospace;
        color: #ff0000;
    }
    .stChat {
        font-family: sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Define the chat_with_pdf function
def chat_with_pdf(pdf_text, prompt, chat_history):
    # Prepare the messages for the API call
    messages = [
        {"role": "system", "content": f"You are an AI assistant that helps with PDF document analysis. The PDF content is: {pdf_text[:10000]}... (truncated for brevity)"},
    ]
    
    # Add chat history
    for message in chat_history:
        messages.append({"role": message["role"], "content": message["content"]})
    
    # Add the user's prompt
    messages.append({"role": "user", "content": prompt})
    
    # Make the API call to Groq
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-70b-versatile",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1000
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Streamlit app layout and functionality
st.title("📚 ChatPDF Pro: LLM powered PDF Analytics")
st.markdown("### Chat with your PDF documents seamlessly!")

# File upload
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None and not st.session_state.file_processed:
    with st.spinner("Processing PDF... This may take a moment."):
        pdf_file = PdfReader(uploaded_file)
        st.session_state.pdf_text = ''.join([page.extract_text() for page in pdf_file.pages])
        st.session_state.file_processed = True
    st.success("PDF processed successfully!")
    st.markdown(f"**PDF Stats:** Approximately {len(st.session_state.pdf_text)} characters.")

# Display PDF icon and file name if processed
if st.session_state.file_processed:
    st.markdown(f"**Current File:** {uploaded_file.name}")

# Chat interface
st.markdown("### 💬 Chat With Your PDF")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your PDF"):
    if not st.session_state.file_processed:
        st.warning("Please upload a PDF file first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_pdf(st.session_state.pdf_text, prompt, st.session_state.messages[:-1])
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with additional information
with st.sidebar:
    st.markdown("## About ChatPDF Pro")
    st.info(
        "ChatPDF Pro allows you to upload PDF documents and chat with their content using advanced language models \n\n"
        "Simply upload a PDF and start asking questions!"
    )
    st.markdown("### How to use:")
    st.markdown(
        "1. Upload a PDF file\n"
        "2. Wait for processing\n"
        "3. Ask questions in the chat\n"
        "4. Get AI-powered responses"
    )
    
    if st.session_state.file_processed:
        st.markdown("### Current PDF Summary")
        st.markdown(f"- **Characters:** {len(st.session_state.pdf_text)}")
        st.markdown(f"- **Est. Words:** {len(st.session_state.pdf_text.split())}")
        
    st.markdown("---")
    st.markdown("Made with ❤️ by Sad_Engineer")

# Reset button
if st.button("Reset Chat"):
    st.session_state.messages = []
    st.session_state.file_processed = False
    st.session_state.pdf_text = ""
    st.rerun()
