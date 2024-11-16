import subprocess
import json

# Constants
MODEL = "llama3.2"
OLLAMA_CMD = f"/usr/local/bin/ollama run {MODEL}"

OLLAMA_PROMPT = """
Given a user query describing an action they want to perform
on the command line, generate up to three possible commands in
JSON format. Each command should be appropriate, non-destructive,
and safe to execute on a typical Unix-like system. If the query
is nonsensical or potentially dangerous, respond with an empty
JSON list. For each command, provide a brief description of what
it does. Return the commands in this format:
{ "commands": [ {"command": "example_command", "description": "Description of the command."} ] }
You are the backend for this program. You receive the query and 
return only the JSON. You only speak JSON. Please take an extra moment
to think and review your suggestions to ensure they are correct.
"""

# Function to generate command suggestions
def generate_command_suggestions(user_query):
    # Prepare the prompt for Ollama
    full_prompt = f"{OLLAMA_PROMPT}\nQuery: '{user_query}'"

    try:
        # Execute Ollama command
        response = subprocess.run(
            [OLLAMA_CMD],
            input=full_prompt,
            text=True,
            capture_output=True,
            shell=True,
        )

        # Check if the model generated a response
        if response.returncode != 0:
            print("Error: Unable to generate command suggestions.")
            return []

        # Parse the response from Ollama
        response_text = response.stdout
        commands_data = json.loads(response_text)

        # Return the JSON list of command suggestions
        return commands_data.get("commands", [])

    except json.JSONDecodeError:
        print("Error: Unable to decode the JSON response.")
        return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

# Main function to run the interactive command prompt
def main():
    # Step 1: Get user input
    user_query = input("Describe what you want to do: ")

    # Step 2: Get command suggestions from the LLM
    commands = generate_command_suggestions(user_query)

    if not commands:
        print("No suitable command suggestions found.")
        return

    # Step 3: Display options to the user
    print("\nCommand suggestions:")
    for index, cmd in enumerate(commands, start=1):
        print(f"{index}) {cmd['description']}")
        print(f"☞ {cmd['command']}")

    # Step 4: Ask the user to select a command
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

    # Step 5: Execute the selected command
    print(f"\nRunning: {selected_command}")
    exec_response = subprocess.run(selected_command, shell=True, capture_output=True, text=True)

    # Display the output of the executed command
    if exec_response.returncode == 0:
        print(exec_response.stdout)
    else:
        print(f"Error executing command: {exec_response.stderr}")

if __name__ == "__main__":
    main()