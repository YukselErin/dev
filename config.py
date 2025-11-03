# config.py
import os
import streamlit as st
from dotenv import load_dotenv

# Check if we are running in the Streamlit Cloud environment
def is_running_on_streamlit_cloud():
    """Checks if the app is running on Streamlit Cloud."""
    return "HOSTNAME" in os.environ and os.environ["HOSTNAME"] == "streamlit"

# Load secrets based on the environment
if is_running_on_streamlit_cloud():
    # Fetch secrets from Streamlit Cloud's secret management
    PASSWORD = st.secrets.get("PASSWORD")
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
    GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
    GITHUB_OWNER = st.secrets.get("GITHUB_OWNER")
    GITHUB_REPO = st.secrets.get("GITHUB_REPO")
    GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH")
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
else:
    # Load secrets from the local .env file for development
    load_dotenv()
    PASSWORD = os.getenv("PASSWORD")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    GITHUB_BRANCH = os.getenv("GITHUB_BRANCH")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- MODEL CONFIGURATION ---
AVAILABLE_MODELS = {
    "OpenRouter": [
        "tngtech/deepseek-r1t2-chimera:free",
        "google/gemma-7b-it:free",
        "huggingfaceh4/zephyr-7b-beta:free",
    ],
    "Groq": [
        "llama3-8b-8192",
        "gemma-7b-it",
        "mixtral-8x7b-32768"
    ],
    "Google": [
        "gemini-2.5-flash"
    ]
}