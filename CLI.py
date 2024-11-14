import subprocess
import requests
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import json
import re



def generate_command_from_llama(user_input):
    api_url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3.2:latest",
        "prompt": (
            "You are an assistant that generates Linux terminal commands based on descriptions.\n"
            "Description: list all files in the current directory\n"
            "Command: ls\n"
            "Description: show hidden files in the current directory\n"
            "Command: ls -a\n"
            "Description: " + user_input + "\nCommand:"
        ),
        "max_tokens": 50
    }
    response = requests.post(api_url, headers=headers, json=data, stream=True) 
    print("20Raw response: ", response.text)  
    if response.status_code != 200:
        return "Error: Unable to generate command"
    # try:
    #     response.json().get("output", "No command suggestions")
    # except requests.exceptions.JSONDecodeError:
    #     return "Error: Unable to parse JSON response"
    generated_text = ""
    for line in response.iter_lines(decode_unicode=True):
        if line:
            try:
                json_data = json.loads(line)
                generated_text += json_data.get("response", "")
            except json.JSONDecodeError:
                # Ignore malformed JSON parts if any
                continue
    # Post-process the generated text to extract commands
    generated_text = generated_text.strip()
    command_lines = generated_text.splitlines()
    commands = []

    for line in command_lines:
        #Check to see if a line looks like a shell command
        if re.match(r'^[a-zA-Z]', line):
            commands.append(line.strip())

    return "\n".join(commands) if commands else "No command suggestions"

# A dictionary mapping intents to commands  
commands = {
    "find a file": "find . -name '*.txt'",
    "list files": "ls -la",
    "show disk usage": "du -sh *",
}


def safe_command_check(command):
    """Basic check to ensure that the command is safe"""
    dangerous_commands = ["rm -rf", "dd if=", "del", ":(){ :|:& };:", "format"]    
    for danger in dangerous_commands:
        if danger in command:
            return False
    return True

def main():
    while True:
        # Step 1: Get user input
        user_input = prompt("Describe what you want to do: ")

        # Step 2: Generate a command from the user input
        suggested_command = generate_command_from_llama(user_input)

        # Step 3: Provide shadow typing with confirmation; check if safe
        if safe_command_check(suggested_command):
            completer = WordCompleter([suggested_command], ignore_case=True)
            selected_command = prompt("Suggested Command: ", completer=completer, complete_while_typing = True)


            # Execute the selected command or let user modify
            if selected_command == suggested_command:
                output = subprocess.run(selected_command, shell=True, capture_output=True, text=True)
                print(output.stdout)
            else:
                print(f"Modified command: {selected_command}")
        else:
            print("Command is not safe. Please review before executing.")

if __name__ == "__main__":
    main()


# thetone Tony's github
