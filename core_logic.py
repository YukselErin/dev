# core_logic.py
import requests
import json
from jinja2 import Environment, FileSystemLoader, exceptions as jinja2_exceptions
import os
import chroma_handler
import logging
import xml.etree.ElementTree as ET
import robot_analyzer

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))

class PromptFilesError(Exception):
    def __init__(self, message, prefix, example, suffix, simple_robot_template, simple_type_template):
        super().__init__(message)
        self.prefix = prefix
        self.example = example
        self.suffix = suffix
        self.simple_robot_template = simple_robot_template
        self.simple_type_template = simple_type_template

def load_prompt_files():
    """Loads all the static prompt component files."""
    try:
        with open('prefix.txt', 'r') as f:
            prefix = f.read()
        with open('example.json', 'r') as f:
            example = f.read()
        with open('suffix.txt', 'r') as f:
            suffix = f.read()
        with open('simpleRobotTemplate.j2', 'r') as f:
            simple_robot_template = f.read()
        with open('simpleTypeTemplate.j2', 'r') as f:
            simple_type_template = f.read()
        
        if not all([prefix, example, suffix, simple_robot_template, simple_type_template]):
            raise PromptFilesError("One or more prompt component files are empty.", prefix, example, suffix, simple_robot_template, simple_type_template)
            
        return prefix, example, suffix, simple_robot_template, simple_type_template
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error loading prompt files: {e}")

def get_llm_summary(prompt, provider, model, openrouter_api_key, groq_api_key, google_api_key):
    llm_output_content = None
    raw_response_text = None

    try:
        if provider == "Google":
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_api_key)
                model = genai.GenerativeModel(model)
                response = model.generate_content(prompt)
                llm_output_content = response.text
                raw_response_text = llm_output_content
            except Exception as e:
                error_message = f"Google AI API Error: {e}"
                return None, error_message
        else:
            if provider == "Groq":
                api_url = "https://api.groq.com/openai/v1/chat/completions"
                api_key = groq_api_key
            else:  # Default to OpenRouter
                api_url = "https://openrouter.ai/api/v1/chat/completions"
                api_key = openrouter_api_key

            if not api_key:
                error_message = f"API key for {provider} is not configured. Please set it in your environment variables."
                return None, error_message

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": model, "messages": [{"role": "user", "content": prompt}]}

            response = requests.post(api_url, headers=headers, json=data)
            raw_response_text = response.text
            response.raise_for_status()
            response_json = response.json()

            if "choices" in response_json and len(response_json.get("choices", [])) > 0:
                llm_output_content = response_json["choices"][0]["message"]["content"]
            else:
                error_message = response_json.get("error", {}).get("message", "Unknown API error")
                return None, f"API Error: {error_message}"
        return llm_output_content, None

    except requests.exceptions.RequestException as e:
        return None, f"Network or API Error: {e}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

def generate_robot_files(input_text, provider, model, openrouter_api_key, groq_api_key, google_api_key, use_rag=False):
    logging.info("Generating robot files...")
    prefix, example, suffix, simpleRobotTemplate, simpleTypeTemplate = load_prompt_files()
    retrieved_robots = None

    if use_rag:
        logging.info("RAG enabled. Querying ChromaDB...")
        retrieved_robots = chroma_handler.query_robots(input_text, n_results=1)
        if retrieved_robots:
            logging.info(f"Retrieved {len(retrieved_robots)} robots from ChromaDB.")
            # Augment the prompt with the retrieved robots
            robot_content = retrieved_robots[0][0]
            robot_name = robot_analyzer.extract_robot_name(robot_content)
            summary = robot_analyzer.summarize_robot(robot_content, provider, model, openrouter_api_key, groq_api_key, google_api_key)
            if robot_name and summary:
                prefix += f"\n\nHere is an example of a similar robot:\n\nName: {robot_name}\n\nSummary: {summary}\n\n"
        else:
            logging.info("No relevant robots found in ChromaDB.")

    prompt = prefix + example + simpleRobotTemplate + simpleTypeTemplate + "Now, for this description: " + input_text.strip().upper() + suffix
    logging.info("Prompt sent to LLM:")
    logging.info(prompt)
    llm_output_content, error = get_llm_summary(prompt, provider, model, openrouter_api_key, groq_api_key, google_api_key)

    if error:
        logging.error(f"Error from LLM: {error}")
        return (None, None, None, None, error, None, prompt, None)

    logging.info("LLM output received.")

    with open('robot_template.j2', 'r') as f:
        robot_template_content = f.read()
    with open('type_template.j2', 'r') as f:
        type_template_content = f.read()

    templates = {
        "robot_template": robot_template_content,
        "type_template": type_template_content,
        "simple_robot_template": simpleRobotTemplate,
        "simple_type_template": simpleTypeTemplate
    }

    try:
        # Extract JSON from the response
        start_index = llm_output_content.find('[')
        end_index = llm_output_content.rfind(']')
        if start_index != -1 and end_index != -1:
            json_string = llm_output_content[start_index:end_index+1]
            json_list = json.loads(json_string)
        else:
            raise json.JSONDecodeError("Could not find JSON array in the response.", llm_output_content, 0)

        if not json_list[1]: # If the second JSON object is empty
            # Generate a default type definition
            type_ids = json_list[0].get("type_ids", {})
            variables = json_list[0].get("variables", [])
            types = []
            for var in variables:
                type_id = var.get("type_id")
                for type_name, tid in type_ids.items():
                    if tid == type_id:
                        types.append({"name": type_name, "id": type_id})
                        break
            unique_types = [dict(t) for t in {tuple(d.items()) for d in types}]
            json_list[1] = {"types": unique_types}

        template_robot = env.get_template('robot_template.j2')
        xml_robot = template_robot.render(**json_list[0])
        
        template_type = env.get_template('type_template.j2')
        xml_type = template_type.render(**json_list[1])

        logging.info("Robot files generated successfully.")
        return (llm_output_content, xml_robot, xml_type, json_list, None, templates, prompt, retrieved_robots)

    except (json.JSONDecodeError, jinja2_exceptions.TemplateError, IndexError) as e:
        error_message = f"Error processing LLM output: {e}"
        logging.error(error_message)
        return (llm_output_content, None, None, None, error_message, templates, prompt, retrieved_robots)


def generate_robot_snippet(input_text, provider, model, openrouter_api_key, groq_api_key, google_api_key):
    logging.info("Generating robot snippet...")

    prompt = f'''You are an expert in creating robot snippets for a design studio. Based on the user's request, generate a JSON object that defines a list of transitions.
Each transition must have an 'id' (starting from 1), a 'name', and a 'step_action_xml' key. The 'step_action_xml' should be the raw XML for the <property name='stepAction'>...</property> block.

Here is an example for a 'Load File' action:
```json
{{
  "transitions": [
    {{
      "id": 1,
      "name": "Load File",
      "step_action_xml": "<property name=\"stepAction\" class=\"LoadFile\"><property name=\"fileNameExpression\" class=\"kapow.robot.plugin.common.support.expression.multipletype.VariableExpression\" serializationversion=\"2\"><property name=\"variable\" class=\"kapow.robot.plugin.common.support.AttributeName2\"><property name=\"name\" class=\"String\">{{ ExcelFilePath2 }}</property></property></property><property name=\"output\" class=\"kapow.robot.plugin.common.stateprocessor.rest.ToVariableOutputSpecification\" serializationversion=\"1\"><property name=\"variable\" class=\"kapow.robot.plugin.common.support.AttributeName2\"><property name=\"name\" class=\"String\">var_2</property></property></property><property name=\"browserConfigurationSpecification\" class=\"BrowserConfigurationSpecificationWebKit\" serializationversion=\"27\"><property name=\"ancestorProvider\" class=\"BrowserConfigurationSpecificationAncestorProviderForStep\"/></property></property>"
    }}
  ]
}}
```

Now, generate the JSON for the following request: "{input_text}"'''

    logging.info("Prompt sent to LLM for snippet generation:")
    logging.info(prompt)
    llm_output_content, error = get_llm_summary(prompt, provider, model, openrouter_api_key, groq_api_key, google_api_key)

    if error:
        logging.error(f"Error from LLM: {error}")
        return (None, error, prompt)

    logging.info("LLM output received for snippet.")

    try:
        # Extract JSON from the response
        start_index = llm_output_content.find('{')
        end_index = llm_output_content.rfind('}')
        if start_index != -1 and end_index != -1:
            json_string = llm_output_content[start_index:end_index+1]
            json_data = json.loads(json_string)
        else:
            raise json.JSONDecodeError("Could not find JSON object in the response.", llm_output_content, 0)

        template_snippet = env.get_template('snippet_template.j2')
        xml_snippet = template_snippet.render(**json_data)

        logging.info("Robot snippet generated successfully.")
        return (xml_snippet, None, prompt)

    except (json.JSONDecodeError, jinja2_exceptions.TemplateError, IndexError) as e:
        error_message = f"Error processing LLM output for snippet: {e}"
        logging.error(error_message)
        return (None, error_message, prompt)
