"""
Example implementation for API Fundamentals module with SSE streaming.
Demonstrates HTTP request/response, REST principles, API security, and Server-Sent Events.
"""

import os
import sys
import json
import requests  # Using requests library for transparency into HTTP mechanics
from typing import List, Dict
from dotenv import load_dotenv

# Load API key from .env file - Security best practice: Never hardcode API keys!
load_dotenv()


class OpenAIChatbot:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        # API URL structure: protocol (https) + domain (api.openai.com) + path (/v1/chat/completions)
        # The 'v1' indicates API version - following REST uniform interface principle
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = model
        # Store conversation history to demonstrate REST statelessness principle
        # Each request must contain complete context
        self.messages: List[Dict[str, str]] = []
        self.system_message = "You are a helpful assistant."
        
    def set_system_message(self, message: str):
        self.system_message = message
        
    def clear_conversation(self):
        self.messages = []
        print("Conversation cleared.")
        
    def chat(self, user_input: str) -> str:
        # Add user message to history for stateless communication
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            # HTTP Request Headers - metadata about the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",  # Bearer token authentication (OpenAI format)
                "Content-Type": "application/json",         # Tells server we're sending JSON data
                "Accept": "text/event-stream"               # Accept SSE format
            }
            
            # HTTP Request Body - the actual data we're sending
            # JSON format as specified by Content-Type header
            # OpenAI format: system message is part of the messages array
            full_messages = [{"role": "system", "content": self.system_message}] + self.messages
            
            payload = {
                "model": self.model,
                "max_tokens": 4096,
                "stream": True,  # Enable SSE streaming
                "messages": full_messages  # Full history including system message = REST statelessness
            }
            
            # HTTP POST method - used for sending data and expecting a response
            # (vs GET which only retrieves data)
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,  # Network timeout for resilience
                stream=True  # Enable streaming in requests library - critical for SSE connections. This keeps the HTTP connection open for continuous data transfer
            )
            
            # Check HTTP Status Code (part of HTTP Response Status Line)
            # 200 = OK/Success, 4xx = Client errors, 5xx = Server errors
            response.raise_for_status()
            
            # SSE Protocol Implementation (Lecture 2: "How SSE Works"):
            # 1. Client sends HTTP request to initialize SSE connection (done above)
            # 2. Server responds with Content-Type: text/event-stream header
            # 3. Server keeps connection open, continuously sending data
            # We'll parse the stream and accumulate the complete response
            assistant_message = ""
            
            # Process Server-Sent Events stream
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    # SSE uses a simple text-based protocol with prefix:value pairs
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        
                        # OpenAI uses '[DONE]' as a sentinel value to signal stream completion
                        # This is API-specific - different providers may use different termination signals
                        if data == '[DONE]':
                            break
                        
                        try:
                            # Parse the JSON event data
                            event_data = json.loads(data)
                            # Streaming uses "delta" updates - incremental chunks of the response
                            # Each delta contains only the new tokens generated since the last update
                            # This enables real-time, token-by-token display as the AI generates text
                            # Note that the data format is specific to each provider
                            if 'choices' in event_data and len(event_data['choices']) > 0:
                                delta = event_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content = delta['content']
                                    print(content, end='', flush=True)  # flush=True ensures immediate display without buffering
                                    assistant_message += content
                        except json.JSONDecodeError:
                            # Skip malformed JSON
                            continue
            
            print()  # New line after streaming completes
            
            # Store response for conversation continuity
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except requests.exceptions.Timeout:
            error_msg = "Request timed out"
            print(f"Error: {error_msg}")
            self.messages.pop()
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"Error: {error_msg}")
            self.messages.pop()
            return error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Error: {error_msg}")
            self.messages.pop()
            return error_msg


def main():
    # Security: Load API key from environment variable, not hardcoded!
    # This follows the Authorization best practices from the course
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key:")
        print("OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    chatbot = OpenAIChatbot(api_key)
    
    print("="*50)
    print("OpenAI Command Line Chatbot (SSE Streaming)")
    print("="*50)
    print("Commands:")
    print("  • Type 'quit' or 'exit' to end")
    print("  • Type 'clear' to reset conversation")
    print("  • Type 'system' to change system message")
    print("="*50)
    
    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
                
            elif user_input.lower() == 'clear':
                chatbot.clear_conversation()
                continue
                
            elif user_input.lower() == 'system':
                new_system = input("Enter new system message: ")
                chatbot.set_system_message(new_system)
                print("System message updated.")
                continue
                
            print("\nGPT: ", end='')
            chatbot.chat(user_input)
            
        except KeyboardInterrupt:
            print("\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
