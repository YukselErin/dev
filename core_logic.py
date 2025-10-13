# core_logic.py
import requests
import json
from jinja2 import Environment, FileSystemLoader
import os

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))

def load_prompt_files():
    """Loads all the static prompt component files."""
    with open('prefix.txt', 'r') as f:
        prefix = f.read()
    with open('example.json', 'r') as f:
        example = f.read()
    with open('suffix.txt', 'r') as f:
        suffix = f.read()
    return prefix, example, suffix

def generate_robot_files(input_text, api_key, model):
    """
    Takes user input and API key, returns generated XML files and raw JSON, or an error message.
    """
    prefix, example, suffix = load_prompt_files()
    
    with open('simpleRobotTemplate.j2', 'r') as f:
        simpleRobotTemplate = f.read()
    with open('simpleTypeTemplate.j2', 'r') as f:
        simpleTypeTemplate = f.read()

    prompt = prefix + example + simpleRobotTemplate + simpleTypeTemplate + "Now, for this description: " + input_text.strip().upper() + suffix

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()

        if response.status_code == 200 and "choices" in response_json and len(response_json["choices"]) > 0:
            llm_output = response_json["choices"][0]["message"]["content"]
            
            # Parse and render
            json_list = json.loads(llm_output)
            
            with open('robot_template.j2', 'r') as f:
                robot_template_content = f.read()
            with open('type_template.j2', 'r') as f:
                type_template_content = f.read()

            template_robot = env.get_template('robot_template.j2')
            xml_robot = template_robot.render(data=json_list[0])
            
            template_type = env.get_template('type_template.j2')
            xml_type = template_type.render(data=json_list[1])
            
            templates = {
                "robot_template": robot_template_content,
                "type_template": type_template_content,
                "simple_robot_template": simpleRobotTemplate,
                "simple_type_template": simpleTypeTemplate
            }

            # Return success tuple
            return (llm_output, xml_robot, xml_type, json_list, None, templates)
        else:
            error_message = response_json.get("error", {}).get("message", "Unknown API error")
            return (json.dumps(response_json), None, None, None, f"API Error: {error_message}", None)

    except requests.exceptions.RequestException as e:
        return (None, None, None, None, f"Network Error: {e}", None)
    except json.JSONDecodeError:
        return (llm_output, None, None, None, "Error: Failed to parse LLM output as JSON.", None)
    except Exception as e:
        return (None, None, None, None, f"An unexpected error occurred: {e}", None)