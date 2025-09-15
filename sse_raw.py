import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

url = "https://api.anthropic.com/v1/messages"

headers = {
    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
    "Content-Type": "application/json",
    "Accept": "text/event-stream",  # Accept SSE format
    "User-Agent": "SomeAIApp/1.0",
    "anthropic-version": "2023-06-01"
}

prompt = input("User: ")

json_body = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 2048,
    "temperature": 0.7,
    "stream": True,  # Enable streaming
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
}

try:
    response = requests.post(
        url, 
        headers=headers, 
        json=json_body,
        timeout=30,
        stream=True  # Enable streaming in requests
    )
    
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            print(line, '\n')
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
