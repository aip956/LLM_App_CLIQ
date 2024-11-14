#!/bin/sh

MODEL="llama3.2"
#MODEL="qwen2.5:32b"
#MODEL="llama3.1:70b"
OLLAMA_CMD="/usr/local/bin/ollama run $MODEL"

# Ollama prompt
OLLAMA_PROMPT=$(cat <<EOF
Given a user query describing an action they want to perform on the command line,
generate up to three possible commands in JSON format. Each command should be appropriate,
non-destructive, and safe to execute on a typical Unix-like system. If the query is nonsensical
or potentially dangerous, respond with an empty JSON list. For each command, provide a brief
description of what it does. Return the commands in this format:
{ "commands": [ {"command": "example_command", "description": "Description of the command."} ] }
You are the backend for this program. You receive the query and return the only JSON. You only
speak JSON. Please take an extra moment to think and review your suggestions to ensure they are correct.
EOF
)

# Function to get command suggestions
get_command_suggestions() {
    query="$1"
    full_prompt="$OLLAMA_PROMPT Query: '$query'"
    response=$(echo "$full_prompt" | $OLLAMA_CMD)
    echo "$response" | jq .commands 2>/dev/null
}

# Check if a query is provided as an argument
if [ "$#" -eq 0 ]; then
    echo "Usage: cliq \"<your question here>\""
    exit 1
fi

# Debug mode?
if [ "$1" = "-d" ]
then
    IS_DEBUG=1
    shift
else
    IS_DEBUG=0
fi

# Get the user query from the command line arguments
user_query="$1"

# Get command suggestions from the LLM
commands_json=$(get_command_suggestions "$user_query")
if [ $IS_DEBUG -eq 1 ]
then
    echo "$commands_json"
fi

# Check if any commands were suggested
if [ -z "$commands_json" ] || [ "$commands_json" = "[]" ]; then
    echo "No suitable command suggestions found."
    exit 1
fi

# Display options to the user
index=1
echo "$commands_json" | jq -c '.[]' | while read -r cmd; do
    command=$(echo "$cmd" | jq -r '.command')
    description=$(echo "$cmd" | jq -r '.description')
    echo "$index) $description"
    echo "☞ $command"
    index=$((index + 1))
done

# Ask the user to select a command
echo "Please select a command number to execute (or press 0 to cancel):"
printf "> "
read choice

if [ "$choice" -eq 0 ]; then
    echo "Cancelled."
    exit 0
fi

# Execute the selected command
selected_command=$(echo "$commands_json" | jq -r ".[$((choice - 1))].command")
echo "Running: $selected_command"
eval "$selected_command"
