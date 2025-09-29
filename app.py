import streamlit as st
import requests
import json
from jinja2 import Environment, FileSystemLoader
import os

# Load fixed prompt parts (assumes files in same directory)
with open('prefix.txt', 'r') as f:
    prefix = f.read()

with open('suffix.txt', 'r') as f:
    suffix = f.read()

# Your OpenRouter API key (store as secret in Streamlit Cloud)
API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "x-ai/grok-4-fast:free"  # Grok 4 Fast free model

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))

st.title("Robot oluştur.")

# Input text
input_text = st.text_area("Oluşturmak istediğiniz robotu tarif ediniz:")

# Initialize session state if not present
if 'xml_robot' not in st.session_state:
    st.session_state.xml_robot = None
if 'xml_type' not in st.session_state:
    st.session_state.xml_type = None
if 'json_list' not in st.session_state:
    st.session_state.json_list = None

if st.button("Oluştur"):
    if input_text:
        # Your Python text processing logic here (customize)
        processed_text = input_text.strip().upper()  # Placeholder

        # Build the full prompt: fixed prefix + dynamic part + fixed suffix
        # Append instruction to ensure output is ONLY a JSON array of objects (no other text)
        prompt = prefix + processed_text + suffix + "\n\nOutput ONLY a valid JSON array containing the resulting objects (e.g., [{\"key1\": \"value1\"}, {\"key2\": \"value2\"}]). No explanations or extra text. Put the robot JSON first, and the complex type json second."

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
            output = response.json()["choices"][0]["message"]["content"].strip()
            
            try:
                # Parse the output as a list of JSON objects
                json_list = json.loads(output)
                
                if not isinstance(json_list, list) or len(json_list) < 2:
                    st.warning("LLM output parsed, but fewer than 2 JSONs found. Adjust prompt if needed.")
                else:
                    # Render first JSON to template_robot.j2
                    template_robot = env.get_template('robot_template.j2')
                    st.session_state.xml_robot = template_robot.render(data=json_list[0])
                    
                    # Render second JSON to template_type.j2
                    template_type = env.get_template('type_template.j2')
                    st.session_state.xml_type = template_type.render(data=json_list[1])
                    
                    # Store json_list for extras if needed
                    st.session_state.json_list = json_list
            
            except json.JSONDecodeError:
                st.error("Failed to parse LLM output as JSON. Raw output:")
                st.text(output)
        else:
            st.error(f"API error: {response.text}")
    else:
        st.warning("Enter some text.")

# Always display results and buttons if available in session state
if st.session_state.xml_robot and st.session_state.xml_type:
    # Display outputs (optional, for preview)
    st.text_area("First XML (.robot):", value=st.session_state.xml_robot, height=200)
    st.text_area("Second XML (.type):", value=st.session_state.xml_type, height=200)
    
    # Download buttons
    st.download_button("Download First (.robot)", data=st.session_state.xml_robot, file_name="output.robot", mime="text/xml")
    st.download_button("Download Second (.type)", data=st.session_state.xml_type, file_name="output.type", mime="text/xml")
    
    # Handle extras if more than 2
    if st.session_state.json_list and len(st.session_state.json_list) > 2:
        st.info("Additional JSONs found (beyond 2):")
        st.json(st.session_state.json_list[2:])

# Optional: Add a reset button to clear results
if st.button("Reset"):
    st.session_state.xml_robot = None
    st.session_state.xml_type = None
    st.session_state.json_list = None
    st.rerun()