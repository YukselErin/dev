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
else:
    # Load secrets from the local .env file for development
    load_dotenv()
    PASSWORD = os.getenv("PASSWORD")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    GITHUB_BRANCH = os.getenv("GITHUB_BRANCH")

# You can also define constants here
MODEL_NAME = "tngtech/deepseek-r1t2-chimera:free"