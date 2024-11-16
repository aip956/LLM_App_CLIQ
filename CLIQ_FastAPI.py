from fastapi import FastAPI, HTTPException, Query
import subprocess
import json
import os

app = FastAPI()

# Set up constants 
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
return the only JSON. You only speak JSON. Please take an extra moment
to think and review your suggestions to ensure they are correct.
"""

@app.post("/generate_command")
def generate_command(user_query: str = Query(..., description="Query describing what the user wants to do on the command line")):
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
            raise HTTPException(status_code=500, detail="Error occurred while generating command suggestions.")
        
        # Parse the response from Ollama
        response_text = response.stdout
        commands_data = json.loads(response_text)

        # Return the JSON list of command suggestions
        return commands_data.get("commands", [])
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding the JSON response.")
    except Exception as e:
        raise HTTPException(staus_code=500, detail=str(e))
    
    



