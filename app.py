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
        prompt = prefix + input_text + "\n\nOutput ONLY a valid JSON array containing the resulting objects (e.g., [{\"key1\": \"value1\"}, {\"key2\": \"value2\"}]). No explanations or extra text. Put the robot JSON first, and the complex type json second."

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
                    template_robot = env.get_template('template_robot.j2')
                    xml_robot = template_robot.render(data=json_list[0])
                    
                    # Render second JSON to template_type.j2
                    template_type = env.get_template('template_type.j2')
                    xml_type = template_type.render(data=json_list[1])
                    
                    # Display outputs (optional, for preview)
                    st.text_area("First XML (.robot):", value=xml_robot, height=200)
                    st.text_area("Second XML (.type):", value=xml_type, height=200)
                    
                    # Download buttons
                    st.download_button("Download First (.robot)", data=xml_robot, file_name="output.robot", mime="text/xml")
                    st.download_button("Download Second (.type)", data=xml_type, file_name="output.type", mime="text/xml")
                
                # If more than 2, handle extras (e.g., display raw)
                if len(json_list) > 2:
                    st.info("Additional JSONs found (beyond 2):")
                    st.json(json_list[2:])
            
            except json.JSONDecodeError:
                st.error("Failed to parse LLM output as JSON. Raw output:")
                st.text(output)
        else:
            st.error(f"API error: {response.text}")
    else:
        st.warning("Enter some text.")