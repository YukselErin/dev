
# debug_runner.py
import argparse
import json
import config
import core_logic
import github_handler
from datetime import datetime
import os
import sys

def main():
    # Check if command-line arguments were provided
    if len(sys.argv) > 1:
        # If arguments are provided, parse them
        parser = argparse.ArgumentParser(description="Generate robot files from a text description.")
        parser.add_argument("input_text", type=str, help="The text description of the robot to create.")
        parser.add_argument("--provider", type=str, default="OpenRouter", choices=config.AVAILABLE_MODELS.keys(), help="The provider to use.")
        parser.add_argument("--model", type=str, help="The model to use. Defaults to the first available model for the provider.")
        parser.add_argument("--no-history", action="store_true", help="Do not save the generation to GitHub history.")
        parser.add_argument("--output-dir", type=str, default="output", help="Directory to save the output files.")
        args = parser.parse_args()
        
        input_text = args.input_text
        provider = args.provider
        model = args.model or config.AVAILABLE_MODELS[provider][0]
        no_history = args.no_history
        output_dir = args.output_dir

    else:
        # If no arguments are provided (e.g., running in VSCode debugger), use default values
        print("No command-line arguments detected. Running with default values for debugging.")
        input_text = "THIS ROBOT HAS A SIMPLE VARIABLE A THAT CONTAINS A FILEPATH. OPEN THIS FILEPATH INTO A VARIABLE EXCEL AND OPEN THE EXCEL. GET THE COLUMNS 1 AND 7, AND SAVE THESE TO DATABASE"
        provider = "Groq"
        model = config.AVAILABLE_MODELS[provider][0]
        no_history = False
        output_dir = "output"
        print(f"Using default input text: {input_text}")
        print(f"Using default provider: {provider}")
        print(f"Using default model: {model}")


    print(f"Generating robot files with {provider} - {model}...")

    # Call the core logic function
    llm_output, xml_robot, xml_type, json_list, error, templates, prompt = core_logic.generate_robot_files(
        input_text=input_text,
        provider=provider,
        model=model,
        openrouter_api_key=config.OPENROUTER_API_KEY,
        groq_api_key=config.GROQ_API_KEY
    )

    if error:
        print(f"An error occurred: {error}")
        return

    print("Robot files generated successfully!")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the files
    robot_filename = os.path.join(output_dir, "output.robot")
    type_filename = os.path.join(output_dir, "output.type")
    json_filename = os.path.join(output_dir, "output.json")

    with open(robot_filename, "w") as f:
        f.write(xml_robot)
    print(f"Saved .robot file to {robot_filename}")

    with open(type_filename, "w") as f:
        f.write(xml_type)
    print(f"Saved .type file to {type_filename}")

    with open(json_filename, "w") as f:
        json.dump(json_list, f, indent=4)
    print(f"Saved .json file to {json_filename}")


    # Save to history
    if not no_history:
        print("Saving to GitHub history...")
        history_data = github_handler.load_history(
            owner=config.GITHUB_OWNER,
            repo=config.GITHUB_REPO,
            token=config.GITHUB_TOKEN,
            branch=config.GITHUB_BRANCH
        )
        if history_data is None:
            history_data = []

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
            "templates": templates
        }

        history_data.append(history_entry)
        save_success = github_handler.save_history(
            history_data,
            owner=config.GITHUB_OWNER, repo=config.GITHUB_REPO, token=config.GITHUB_TOKEN, branch=config.GITHUB_BRANCH
        )
        if save_success:
            print("Successfully saved history to GitHub.")
        else:
            print("Failed to save history to GitHub.")

if __name__ == "__main__":
    main()
