# main_app.py
import streamlit as st
import json
import config  # Import our new config module
import core_logic
import github_handler
from datetime import datetime
import jinja2
import robot_analyzer
import chroma_handler

st.title("Robot Utilities")

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
        branch=config.GITHUB_BRANCH,
        file_path='history.json'
    )
    if isinstance(history_data, str):
        st.error(f"Failed to load history: {history_data}")
        st.session_state.history = []
    else:
        st.session_state.history = history_data

if 'snippet_history' not in st.session_state:
    snippet_history_data = github_handler.load_history(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        token=config.GITHUB_TOKEN,
        branch=config.GITHUB_BRANCH,
        file_path='snippet_history.json'
    )
    if isinstance(snippet_history_data, str):
        st.error(f"Failed to load snippet history: {snippet_history_data}")
        st.session_state.snippet_history = []
    else:
        st.session_state.snippet_history = snippet_history_data

# Initialize other state variables
for key in ['xml_robot', 'xml_type', 'json_list', 'analysis_result', 'snippet_text']:
    if key not in st.session_state:
        st.session_state[key] = None

# --- UI TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["Robot Generation", "Robot Analysis", "Snippet Generation", "ChromaDB Management"])

with tab1:
    st.header("Generate a New Robot")
    # --- UI ELEMENTS ---
    st.sidebar.title("Model Selection")
    provider = st.sidebar.selectbox("Select Provider", list(config.AVAILABLE_MODELS.keys()))
    model = st.sidebar.selectbox(f"Select Model for {provider}", config.AVAILABLE_MODELS[provider])
    use_rag = st.sidebar.checkbox("Use RAG", value=True)

    input_text = st.text_area("Oluşturmak istediğiniz robotu tarif ediniz:")

    if st.button("Oluştur"):
        if input_text:
            with st.spinner(f"Generating robot with {provider} - {model}..."):
                try:
                    llm_output, xml_robot, xml_type, json_list, error, templates, prompt, retrieved_robots = core_logic.generate_robot_files(
                        input_text=input_text,
                        provider=provider,
                        model=model,
                        openrouter_api_key=config.OPENROUTER_API_KEY,
                        groq_api_key=config.GROQ_API_KEY,
                        google_api_key=config.GOOGLE_API_KEY,
                        use_rag=use_rag
                    )

                    if retrieved_robots:
                        print("Retrieved robots:", retrieved_robots)
                        with st.expander("Retrieved Robots", expanded=True):
                            st.write(retrieved_robots)

                    with st.expander("Full Prompt Sent to LLM", expanded=True):
                        st.text_area("", value=prompt, height=300)

                    st.write(f"Input text being saved to history: {input_text}")

                    # Create history entry
                    history_entry = {
                        "date": datetime.now().isoformat(),
                        "model": model,
                        "model_source": provider,
                        "query": input_text,
                        "prompt": prompt,
                        "llm_output": llm_output,
                        "xml_robot": xml_robot,
                        "xml_type": xml_type,
                        "error": error,
                        "templates": templates,
                        "retrieved_robots": retrieved_robots
                    }

                    # Save to history regardless of outcome
                    st.session_state.history.append(history_entry)
                    save_success = github_handler.save_history(
                        st.session_state.history,
                        owner=config.GITHUB_OWNER, repo=config.GITHUB_REPO, token=config.GITHUB_TOKEN, branch=config.GITHUB_BRANCH
                    )
                    if save_success is not True:
                        st.error(f"Failed to save history to GitHub: {save_success}")

                    # Handle results
                    if error:
                        st.error(error)
                    else:
                        st.success("Robot dosyaları başarıyla oluşturuldu!")
                        st.session_state.xml_robot = xml_robot
                        st.session_state.xml_type = xml_type
                        st.session_state.json_list = json_list

                except core_logic.PromptFilesError as e:
                    st.error(f"Error: {e}")
                    st.text_area("Prefix File Content:", value=e.prefix, height=100)
                    st.text_area("Example File Content:", value=e.example, height=100)
                    st.text_area("Suffix File Content:", value=e.suffix, height=100)
                    st.text_area("Simple Robot Template Content:", value=e.simple_robot_template, height=100)
                    st.text_area("Simple Type Template Content:", value=e.simple_type_template, height=100)
                except FileNotFoundError as e:
                    st.error(f"Error: {e}")

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

            # Display error if it exists
            if entry.get('error'):
                st.error(f"**Error:** {entry.get('error')}")

            llm_output = entry.get('llm_output')
            if llm_output and not entry.get('error'):
                try:
                    json_data = json.loads(llm_output)
                    
                    robot_template_str = entry.get('templates', {}).get('robot_template')
                    type_template_str = entry.get('templates', {}).get('type_template')

                    if robot_template_str:
                        robot_template = jinja2.Template(robot_template_str)
                        robot_xml = robot_template.render(data=json_data[0])
                        st.download_button("Download (.robot)", robot_xml, f"history_{i}.robot", "text/xml", key=f"robot_dl_{entry.get('date')}_{i}")

                    if type_template_str:
                        type_template = jinja2.Template(type_template_str)
                        type_xml = type_template.render(data=json_data[1])
                        st.download_button("Download (.type)", type_xml, f"history_{i}.type", "text/xml", key=f"type_dl_{entry.get('date')}_{i}")

                except (json.JSONDecodeError, IndexError, TypeError):
                    st.error("Could not regenerate files from history. LLM output might not be a valid JSON list.")
                    if entry.get('xml_robot') and entry.get('xml_type'):
                        st.download_button("Download (.robot)", entry['xml_robot'], f"history_{i}.robot", "text/xml", key=f"robot_dl_{entry.get('date')}_{i}_fallback")
                        st.download_button("Download (.type)", entry['xml_type'], f"history_{i}.type", "text/xml", key=f"type_dl_{entry.get('date')}_{i}_fallback")

            elif entry.get('xml_robot') and entry.get('xml_type'):
                st.download_button("Download (.robot)", entry['xml_robot'], f"history_{i}.robot", "text/xml", key=f"robot_dl_{entry.get('date')}_{i}")
                st.download_button("Download (.type)", entry['xml_type'], f"history_{i}.type", "text/xml", key=f"type_dl_{entry.get('date')}_{i}")


            with st.expander("User Query"):
                st.text_area("", value=entry.get('query', 'N/A'), height=100, key=f"query_{entry.get('date')}_{i}")

            with st.expander("Retrieved Robots"):
                st.write(entry.get('retrieved_robots', 'N/A'))

            with st.expander("Full Prompt", expanded=True):
                st.text_area("", value=entry.get('prompt', 'N/A'), height=200, key=f"prompt_{entry.get('date')}_{i}")

            with st.expander("Raw LLM Output"):
                st.text_area("", value=entry.get('llm_output') or entry.get('error', 'N/A'), height=200, key=f"llm_output_{entry.get('date')}_{i}")

            with st.expander("Templates"):
                if entry.get('templates'):
                    st.text_area("Robot Template", value=entry.get('templates', {}).get('robot_template', 'N/A'), height=200, key=f"robot_template_{entry.get('date')}_{i}")
                    st.text_area("Type Template", value=entry.get('templates', {}).get('type_template', 'N/A'), height=200, key=f"type_template_{entry.get('date')}_{i}")
                    st.text_area("Simple Robot Template", value=entry.get('templates', {}).get('simple_robot_template', 'N/A'), height=200, key=f"simple_robot_template_{entry.get('date')}_{i}")
                    st.text_area("Simple Type Template", value=entry.get('templates', {}).get('simple_type_template', 'N/A'), height=200, key=f"simple_type_template_{entry.get('date')}_{i}")
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

with tab2:
    st.header("Analyze an Existing Robot")
    
    uploaded_file = st.file_uploader("Upload a .robot file", type="robot")
    pasted_text = st.text_area("Or paste the robot's XML content here")

    if st.button("Analyze Robot"):
        robot_content = ""
        if uploaded_file is not None:
            robot_content = uploaded_file.getvalue().decode("utf-8")
        elif pasted_text:
            robot_content = pasted_text
        
        if robot_content:
            st.session_state.robot_content = robot_content
            with st.spinner("Analyzing robot..."):
                st.session_state.analysis_result = robot_analyzer.analyze_robot(
                    robot_content=robot_content,
                    provider=provider,
                    model=model,
                    openrouter_api_key=config.OPENROUTER_API_KEY,
                    groq_api_key=config.GROQ_API_KEY,
                    google_api_key=config.GOOGLE_API_KEY
                )
            st.success("Analysis complete!")
        else:
            st.warning("Please upload a file or paste the content of a .robot file.")

    if st.session_state.analysis_result:
        st.text_area("Analysis Result", value=st.session_state.analysis_result, height=300)
        
        st.header("Ask Questions About the Robot")
        question = st.text_input("Your question")
        if st.button("Ask"):
            if question:
                with st.spinner("Thinking..."):
                    answer = robot_analyzer.answer_question(
                        question=question,
                        summary=st.session_state.analysis_result,
                        robot_content=st.session_state.robot_content,
                        provider=provider,
                        model=model,
                        openrouter_api_key=config.OPENROUTER_API_KEY,
                        groq_api_key=config.GROQ_API_KEY,
                        google_api_key=config.GOOGLE_API_KEY
                    )
                    st.markdown(answer)
            else:
                st.warning("Please enter a question.")

with tab3:
    st.header("Snippet Generation")
    st.session_state.snippet_text = ""
    snippet_input_text = st.text_area("Describe the snippet you want to create:")

    if st.button("Generate Snippet"):
        if snippet_input_text:
            with st.spinner(f"Generating snippet with {provider} - {model}..."):
                xml_snippet, error, prompt = core_logic.generate_robot_snippet(
                    input_text=snippet_input_text,
                    provider=provider,
                    model=model,
                    openrouter_api_key=config.OPENROUTER_API_KEY,
                    groq_api_key=config.GROQ_API_KEY,
                    google_api_key=config.GOOGLE_API_KEY
                )

                history_entry = {
                    "date": datetime.now().isoformat(),
                    "model": model,
                    "model_source": provider,
                    "query": snippet_input_text,
                    "prompt": prompt,
                    "xml_snippet": xml_snippet,
                    "error": error,
                }
                st.session_state.snippet_history.append(history_entry)
                save_success = github_handler.save_history(
                    st.session_state.snippet_history,
                    owner=config.GITHUB_OWNER, repo=config.GITHUB_REPO, token=config.GITHUB_TOKEN, branch=config.GITHUB_BRANCH, file_path='snippet_history.json'
                )
                if save_success is not True:
                    st.error(f"Failed to save snippet history to GitHub: {save_success}")

                with st.expander("Full Prompt Sent to LLM for Snippet", expanded=False):
                    st.text_area("", value=prompt, height=300, key="snippet_prompt")

                if error:
                    st.error(error)
                else:
                    st.success("Snippet generated successfully!")
                    st.session_state.snippet_text = xml_snippet
        else:
            st.warning("Please enter a description for the snippet.")

    if st.session_state.snippet_text:
        st.text_area("Generated Snippet:", value=st.session_state.snippet_text, height=300)
        st.download_button("Download Snippet", st.session_state.snippet_text, "snippet.xml", "text/xml")

    with st.expander("View Snippet Generation History"):
        for i, entry in enumerate(reversed(st.session_state.snippet_history)):
            st.markdown(f"---")
            st.markdown(f"**Generation {len(st.session_state.snippet_history) - i}**")
            st.markdown(f"**Date:** {entry.get('date', 'N/A')}")
            st.markdown(f"**Model:** {entry.get('model', 'N/A')}")
            st.markdown(f"**Provider:** {entry.get('model_source', 'N/A')}")

            if entry.get('error'):
                st.error(f"**Error:** {entry.get('error')}")

            if entry.get('xml_snippet'):
                st.download_button("Download Snippet", entry['xml_snippet'], f"snippet_history_{i}.xml", "text/xml", key=f"snippet_dl_{entry.get('date')}_{i}")

            with st.expander("User Query"):
                st.text_area("", value=entry.get('query', 'N/A'), height=100, key=f"snippet_query_{entry.get('date')}_{i}")

            with st.expander("Full Prompt"):
                st.text_area("", value=entry.get('prompt', 'N/A'), height=200, key=f"snippet_prompt_hist_{entry.get('date')}_{i}")


with tab4:
    st.header("ChromaDB Management")
    if st.button("Add all robots from output folder to DB"):
        with st.spinner("Adding robots to ChromaDB..."):
            robot_files = chroma_handler.get_all_robots_from_output_folder()
            for robot_file in robot_files:
                st.write(chroma_handler.add_robot_to_db(robot_file))
        st.success("Finished adding robots to ChromaDB.")
