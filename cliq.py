import subprocess
import json
import argparse
import shutil
from dotenv import load_dotenv
load_dotenv()
import os
from openai import OpenAI

# Constants
MODEL = "llama3.2"
OLLAMA_CMD = f"/usr/local/bin/ollama run {MODEL}"
llm_prompt = """
Given a user query describing an action they want to perform
on the command line, generate up to three possible commands in
JSON format. Each command should be appropriate, non-destructive,
and safe to execute on a typical Unix-like system. If the query
is nonsensical or potentially dangerous, respond with an empty
JSON list. For each command, provide a brief description of what
it does. Return the commands in this exact format:
{
  "commands": [
    {"command": "example_command", "description": "Description of the command."}
  ]
}
You are the backend for this program. You receive the query and 
return only the JSON. You only speak JSON, with no extra text.
Please take an extra moment to think and review your suggestions to ensure they are correct.
"""

# Load environment variables
token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def generate_command_suggestions(user_query, use_remote=False):
    if use_remote:
        # Use OpenAI API to get command suggestions
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": llm_prompt,
                },
                {
                    "role": "user",
                    "content": user_query,
                }
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name
        )
        response_text = response.choices[0].message.content
    else:
        # Prepare the prompt for Ollama
        full_prompt = f"{llm_prompt}\nQuery: '{user_query}'"
        try:
            # Execute Ollama command
            response = subprocess.run(
                [OLLAMA_CMD],
                input=full_prompt,
                text=True,
                capture_output=True,
                shell=True,
            )
            if response.returncode != 0:
                print("Error: Unable to generate command suggestions.")
                return []
            response_text = response.stdout
        except Exception as e:
            print(f"Error: {str(e)}")
            return []

    try:
        # Parse the response
        commands_data = json.loads(response_text)
        return commands_data.get("commands", [])
    except json.JSONDecodeError:
        print("Error: Unable to decode the JSON response.")
        return []

def validate_command(command):
    # Split the command to check the base command (e.g. "ls", "find")
    base_command = command.split()[0]
    return shutil.which(base_command) is not None

def main():
    # Step 1: Parse the command line arguments
    parser = argparse.ArgumentParser(description="Generate command suggestions for a user query.")
    parser.add_argument("user_query", nargs='?', default=None, help="Query describing what you want to do on the command line")
    parser.add_argument("-r", action="store_true", help="Use OpenAI's remote LLM instead of local LLM")
    args = parser.parse_args()

    # Step 2: If no command line arg, prompt the user for input
    user_query = args.user_query
    if user_query is None:
        user_query = input("Describe what you want to do: ")

    # Step 3: Get command suggestions from the LLM
    commands = generate_command_suggestions(user_query, use_remote=args.r)

    if not commands:
        print("No suitable command suggestions found.")
        return

    # Step 4: Validate commands and display options to the user
    validate_commands = []
    for index, cmd in enumerate(commands, start=1):
        validate_commands.append(cmd)
        print(f"{index}) {cmd['description']}")
        print(f"☞ {cmd['command']}")

    if not validate_commands:
        print("No valid command suggestions found.")
        return

    # Step 5: Ask the user to select a command
    while True:
        try:
            choice = int(input("\nPlease select a command number to execute (or press 0 to cancel): "))
            if choice == 0:
                print("Cancelled.")
                return
            if 1 <= choice <= len(commands):
                selected_command = commands[choice - 1]['command']
                break
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Step 6: Execute the selected command
    print(f"\nRunning: {selected_command}")
    exec_response = subprocess.run(selected_command, shell=True, capture_output=True, text=True)

    # Display the output of the executed command
    if exec_response.returncode == 0:
        print(exec_response.stdout)
    else:
        print(f"Error executing command: {exec_response.stderr}")

if __name__ == "__main__":
    main()
