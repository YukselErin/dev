
# robot_analyzer.py
import xml.etree.ElementTree as ET
import core_logic
import datetime

def extract_robot_name(robot_content):
    try:
        root = ET.fromstring(robot_content)
        return root.get("name")
    except ET.ParseError:
        return None

def log_analysis(log_message):
    with open("analysis_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {log_message}\n")

def summarize_robot(robot_content, provider, model, openrouter_api_key, groq_api_key, google_api_key):
    """
    This function will generate a summary of a robot given its content.
    """
    log_analysis("Summarizing robot...")
    prompt = f"Please provide a concise summary of the following robot:\n\n{robot_content}"
    
    summary, error = core_logic.get_llm_summary(
        prompt=prompt,
        provider=provider,
        model=model,
        openrouter_api_key=openrouter_api_key,
        groq_api_key=groq_api_key,
        google_api_key=google_api_key
    )

    if error:
        log_analysis(f"Error from LLM when summarizing robot: {error}")
        return f"Error from LLM: {error}"
    
    log_analysis("Received summary from LLM.")
    return summary
    
    answer, error = core_logic.get_llm_summary(
        prompt=prompt,
        provider=provider,
        model=model,
        openrouter_api_key=openrouter_api_key,
        groq_api_key=groq_api_key,
        google_api_key=google_api_key
    )

    if error:
        log_analysis(f"Error from LLM when answering question: {error}")
        return f"Error from LLM: {error}"
    
    log_analysis("Received answer from LLM.")
    return answer

def analyze_robot(robot_content, provider, model, openrouter_api_key, groq_api_key, google_api_key):
    """
    This function will analyze the robot content and return a summary.
    """
    log_analysis("Starting robot analysis.")
    try:
        root = ET.fromstring(robot_content)
        transitions = root.findall(".//object[@class='Transition']")
        edges = root.findall(".//object[@class='TransitionEdge']")
        log_analysis(f"Found {len(transitions)} transitions and {len(edges)} edges.")

        chunk_size = 5
        transition_chunks = [transitions[i:i + chunk_size] for i in range(0, len(transitions), chunk_size)]
        log_analysis(f"Divided transitions into {len(transition_chunks)} chunks.")

        summaries = []
        for i, chunk in enumerate(transition_chunks):
            prompt = "Please provide a concise explanation for each of the following transitions and their edges:\n\n"
            for transition in chunk:
                prompt += ET.tostring(transition, encoding='unicode') + "\n"
            
            prompt += "\nEdges:\n"
            for edge in edges:
                prompt += ET.tostring(edge, encoding='unicode') + "\n"

            log_analysis(f"Sending prompt for chunk {i+1} to LLM.")
            summary, error = core_logic.get_llm_summary(
                prompt=prompt,
                provider=provider,
                model=model,
                openrouter_api_key=openrouter_api_key,
                groq_api_key=groq_api_key,
                google_api_key=google_api_key
            )

            if error:
                log_analysis(f"Error from LLM for chunk {i+1}: {error}")
                return f"Error from LLM: {error}"
            
            log_analysis(f"Received summary for chunk {i+1}.")
            summaries.append(summary)

        log_analysis("Combining summaries to get a final summary.")
        final_prompt = "Please provide a final summary of the following robot based on the summaries of its transitions:\n\n" + "\n".join(summaries)
        
        final_summary, error = core_logic.get_llm_summary(
            prompt=final_prompt,
            provider=provider,
            model=model,
            openrouter_api_key=openrouter_api_key,
            groq_api_key=groq_api_key,
            google_api_key=google_api_key
        )

        if error:
            log_analysis(f"Error from LLM for final summary: {error}")
            return f"Error from LLM: {error}"

        log_analysis("Robot analysis complete.")
        return final_summary

    except ET.ParseError as e:
        log_analysis(f"Error parsing XML: {e}")
        return f"Error parsing XML: {e}"
