# main_app.py
import streamlit as st
import json
import config  # Import our new config module
import core_logic
import github_handler
from datetime import datetime
import jinja2

st.title("Robot oluştur.")

# --- PASSWORD PROTECTION ---
password = st.text_input("Password", type="password")
if password != config.PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# --- INITIALIZE SESSION STATE ---
if 'history' not in st.session_state:
    history_data = github_handler.load_history(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        token=config.GITHUB_TOKEN,
        branch=config.GITHUB_BRANCH
    )
    st.session_state.history = history_data if history_data is not None else []
# Initialize other state variables
for key in ['xml_robot', 'xml_type', 'json_list']:
    if key not in st.session_state:
        st.session_state[key] = None

# --- UI ELEMENTS ---
input_text = st.text_area("Oluşturmak istediğiniz robotu tarif ediniz:")

if st.button("Oluştur"):
    if input_text:
        with st.spinner("Robot oluşturuluyor..."):
            # Call the core logic function
            llm_output, xml_robot, xml_type, json_list, error, templates = core_logic.generate_robot_files(
                input_text, config.OPENROUTER_API_KEY, config.MODEL_NAME
            )

            # Create history entry
            history_entry = {
                "date": datetime.now().isoformat(),
                "model": config.MODEL_NAME,
                "model_source": "OpenRouter",
                "query": input_text,
                "llm_output": llm_output,
                "xml_robot": xml_robot,
                "xml_type": xml_type,
                "error": error,
                "templates": templates
            }

            # Save to history regardless of outcome
            st.session_state.history.append(history_entry)
            save_success = github_handler.save_history(
                st.session_state.history,
                owner=config.GITHUB_OWNER, repo=config.GITHUB_REPO, token=config.GITHUB_TOKEN, branch=config.GITHUB_BRANCH
            )
            if not save_success:
                st.error("Failed to save history to GitHub.")

            # Handle results
            if error:
                st.error(error)
            else:
                st.success("Robot dosyaları başarıyla oluşturuldu!")
                st.session_state.xml_robot = xml_robot
                st.session_state.xml_type = xml_type
                st.session_state.json_list = json_list
    else:
        st.warning("Lütfen bir metin girin.")

# --- DISPLAY RESULTS AND DOWNLOADS ---
if st.session_state.xml_robot and st.session_state.xml_type:
    st.text_area("First XML (.robot):", value=st.session_state.xml_robot, height=200)
    st.text_area("Second XML (.type):", value=st.session_state.xml_type, height=200)
    st.download_button("Download (.robot)", st.session_state.xml_robot, "output.robot", "text/xml")
    st.download_button("Download (.type)", st.session_state.xml_type, "output.type", "text/xml")

# --- HISTORY VIEWER ---
with st.expander("View Generation History"):
    for i, entry in enumerate(reversed(st.session_state.history)):
        st.markdown(f"---")
        st.markdown(f"**Generation {len(st.session_state.history) - i}**")
        st.markdown(f"**Date:** {entry.get('date', 'N/A')}")
        st.markdown(f"**Model:** {entry.get('model', 'N/A')}")
        st.markdown(f"**Provider:** {entry.get('model_source', 'N/A')}")

        llm_output = entry.get('llm_output')
        if llm_output and not entry.get('error'):
            try:
                json_data = json.loads(llm_output)
                
                robot_template_str = entry.get('templates', {}).get('robot_template')
                type_template_str = entry.get('templates', {}).get('type_template')

                if robot_template_str:
                    robot_template = jinja2.Template(robot_template_str)
                    robot_xml = robot_template.render(data=json_data[0])
                    st.download_button("Download (.robot)", robot_xml, f"history_{i}.robot", "text/xml", key=f"robot_dl_{i}")

                if type_template_str:
                    type_template = jinja2.Template(type_template_str)
                    type_xml = type_template.render(data=json_data[1])
                    st.download_button("Download (.type)", type_xml, f"history_{i}.type", "text/xml", key=f"type_dl_{i}")

            except (json.JSONDecodeError, IndexError, TypeError):
                st.error("Could not regenerate files from history. LLM output might not be a valid JSON list.")
                if entry.get('xml_robot') and entry.get('xml_type'):
                    st.download_button("Download (.robot)", entry['xml_robot'], f"history_{i}.robot", "text/xml", key=f"robot_dl_{i}_fallback")
                    st.download_button("Download (.type)", entry['xml_type'], f"history_{i}.type", "text/xml", key=f"type_dl_{i}_fallback")

        elif entry.get('xml_robot') and entry.get('xml_type'):
            st.download_button("Download (.robot)", entry['xml_robot'], f"history_{i}.robot", "text/xml", key=f"robot_dl_{i}")
            st.download_button("Download (.type)", entry['xml_type'], f"history_{i}.type", "text/xml", key=f"type_dl_{i}")


        with st.expander("User Query"):
            st.text_area("", value=entry.get('query', 'N/A'), height=100, key=f"query_{i}")

        with st.expander("Raw LLM Output"):
            st.text_area("", value=entry.get('llm_output') or entry.get('error', 'N/A'), height=200, key=f"llm_output_{i}")

        with st.expander("Templates"):
            if entry.get('templates'):
                st.text_area("Robot Template", value=entry.get('templates', {}).get('robot_template', 'N/A'), height=200, key=f"robot_template_{i}")
                st.text_area("Type Template", value=entry.get('templates', {}).get('type_template', 'N/A'), height=200, key=f"type_template_{i}")
                st.text_area("Simple Robot Template", value=entry.get('templates', {}).get('simple_robot_template', 'N/A'), height=200, key=f"simple_robot_template_{i}")
                st.text_area("Simple Type Template", value=entry.get('templates', {}).get('simple_type_template', 'N/A'), height=200, key=f"simple_type_template_{i}")
            else:
                st.text("Templates not available for this entry.")


# --- RESET BUTTON ---
if st.button("Reset"):
    # Clear local session state
    st.session_state.xml_robot = None
    st.session_state.xml_type = None
    st.session_state.json_list = None
    st.session_state.history = []
    # Clear the history on GitHub as well
    github_handler.save_history([], owner=config.GITHUB_OWNER, repo=config.GITHUB_REPO, token=config.GITHUB_TOKEN, branch=config.GITHUB_BRANCH)
    st.rerun()