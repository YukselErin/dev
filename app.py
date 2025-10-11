import streamlit as st
import requests
import json
from jinja2 import Environment, FileSystemLoader
import os
import base64

# GitHub API functions for persistent history
def load_history():
    url = f"https://api.github.com/repos/{st.secrets['GITHUB_OWNER']}/{st.secrets['GITHUB_REPO']}/contents/history.json"
    if 'GITHUB_BRANCH' in st.secrets:
        url += f"?ref={st.secrets['GITHUB_BRANCH']}"
    headers = {
        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        content = base64.b64decode(resp.json()['content']).decode('utf-8')
        return json.loads(content)
    else:
        st.error(f"Load history failed: Status {resp.status_code}, Response: {resp.text}")
        return []  # File doesn't exist or other error

def save_history(history):
    url = f"https://api.github.com/repos/{st.secrets['GITHUB_OWNER']}/{st.secrets['GITHUB_REPO']}/contents/history.json"
    if 'GITHUB_BRANCH' in st.secrets:
        url += f"?ref={st.secrets['GITHUB_BRANCH']}"
    headers = {
        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # Get current SHA if file exists
    resp_get = requests.get(url, headers=headers)
    sha = None
    if resp_get.status_code == 200:
        sha = resp_get.json()['sha']
    elif resp_get.status_code != 404:
        st.error(f"Get SHA failed: Status {resp_get.status_code}, Response: {resp_get.text}")
        return
    
    new_content = base64.b64encode(json.dumps(history, indent=4).encode('utf-8')).decode('utf-8')
    data = {
        "message": "Update LLM history",
        "content": new_content
    }
    if sha:
        data["sha"] = sha
    
    resp = requests.put(url, headers=headers, json=data)
    if resp.status_code not in (200, 201):
        st.error(f"Save history failed: Status {resp.status_code}, Response: {resp.text}")
    else:
        st.success("History saved successfully!")

        
# Password protection for privacy
password = st.text_input("Password", type="password")
if password != st.secrets["PASSWORD"]:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# Load fixed prompt parts (assumes files in same directory)
with open('prefix.txt', 'r') as f:
    prefix = f.read()

with open('example.json', 'r') as f:
    example = f.read()

with open('suffix.txt', 'r') as f:
    suffix = f.read()

with open('simpleRobotTemplate.j2', 'r') as f:
    simpleRobotTemplate = f.read()

with open('simpleTypeTemplate.j2', 'r') as f:
    simpleTypeTemplate = f.read()

# Your OpenRouter API key (store as secret in Streamlit Cloud)
API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "deepseek/deepseek-chat-v3.1:free"  # Grok 4 Fast free model

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
if 'history' not in st.session_state:
    st.session_state.history = load_history()

if st.button("Oluştur"):
    if input_text:
        # Your Python text processing logic here (customize)
        processed_text = input_text.strip().upper()  # Placeholder

        # Build the full prompt: fixed prefix + dynamic part + fixed suffix
        # Append instruction to ensure output is ONLY a JSON array of objects (no other text)
        prompt = prefix +example+ simpleRobotTemplate+simpleTypeTemplate+"Now, for this description: "+processed_text + suffix   

        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": MODEL,
            "reasoning": {"enabled":True},
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            output = response.json()["choices"][0]["message"]["content"].strip()
            
            # Save query-answer pair to history
            st.session_state.history.append({'query': prompt, 'answer': output})
            save_history(st.session_state.history)
            
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

# Display history in an expander
with st.expander("View LLM Query-Answer History"):
    for idx, item in enumerate(st.session_state.history):
        st.subheader(f"Pair {idx + 1}")
        st.text_area("Query:", value=item['query'], height=100)
        st.text_area("Answer:", value=item['answer'], height=100)

# Download history as JSON
if st.session_state.history:
    history_json = json.dumps(st.session_state.history, indent=4)
    st.download_button("Download History (JSON)", data=history_json, file_name="llm_history.json", mime="application/json")

# Optional: Add a reset button to clear results and history
if st.button("Reset"):
    st.session_state.xml_robot = None
    st.session_state.xml_type = None
    st.session_state.json_list = None
    st.session_state.history = []
    save_history(st.session_state.history)

    st.rerun()


