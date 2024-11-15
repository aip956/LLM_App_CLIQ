from fastapi import FastAPI, HTTPException, Query
import subprocess
import json
import os

app = FastAPI()

# Set up constants 
MODEL = "llama3.2"
OLLAMA_CMD = f"/usr/local/bin/ollama run {MODEL}"

OLLAMA_PROMPT = """
Given a user query describing an 

"""




# thetone Tony's github
