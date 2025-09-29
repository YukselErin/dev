import streamlit as st
import requests

# Your OpenRouter API key (store as secret in Streamlit Cloud)
API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "x-ai/grok-4-fast:free"  # Grok 4 Fast free model
# Load fixed prompt parts (assumes files are in the same directory as app.py)
with open('prefix.txt', 'r') as f:
    prefix = f.read()

with open('suffix.txt', 'r') as f:
    suffix = f.read()
st.title("Robot Oluşturucu")

# Input text
input_text = st.text_area("Oluşturmak istediğiniz Kofax robotunu tanımlayınız.")

if st.button("İşle ve üret"):
    if input_text:
        # Your Python text processing logic here (e.g., clean, extract, build prompt)
        processed_text = input_text.upper()  # Placeholder example
        prompt = f"Based on this text: {processed_text}. Generate a summary."  # Customize prompts

        # Your Python text processing logic here (e.g., clean, extract, transform)
        processed_text = input_text.strip().upper()  # Placeholder example; customize this

        # Build the full prompt: fixed prefix + dynamic part + fixed suffix
        prompt = prefix + processed_text + suffix

        


        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            output = response.json()["choices"][0]["message"]["content"]
            st.text_area("Output:", value=output, height=200)
            
            # Optional: Download as text file
            st.download_button("Download Output", data=output, file_name="output.txt")
        else:
            st.error("API error: Check your key or model availability.")
    else:
        st.warning("Enter some text.")