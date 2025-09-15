# Module 2: Streaming Text with Server-Sent Events (SSE)

This module extends the [Module 1 chatbot](https://github.com/AI-Systems-Infrastructure/module-1) with real-time text streaming using Server-Sent Events (SSE), as covered in Lecture 2.

## What's New

Module 2 adds **token-by-token streaming** - text appears as it's generated, rather than waiting for the complete response.

## Implementation Changes

### 1. Request Configuration

```python
# Enable SSE in headers
headers["Accept"] = "text/event-stream"

# Enable streaming in payload
payload["stream"] = True

# Keep connection open in requests
response = requests.post(url, headers=headers, json=payload, stream=True)
```

### 2. Stream Processing

```python
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = line[6:]  # Remove 'data: ' prefix
            
            if data == '[DONE]':  # Stream end signal
                break
                
            # Parse JSON and extract delta content
            event_data = json.loads(data)
            delta = event_data['choices'][0].get('delta', {})
            if 'content' in delta:
                print(delta['content'], end='', flush=True)  # Real-time display
```

The key difference: `delta` contains only the new tokens since the last update, not the full message.

**Note:** The parsing logic above is specific to OpenAI's API. Different providers structure their SSE data differently - for example, Anthropic uses a different JSON structure and termination signal. Always check your provider's documentation for their specific streaming format.

## Programs

- **`sse_raw.py`**: Minimal example showing raw SSE stream from Anthropic's API
- **`sse_chatbot.py`**: Full chatbot with SSE streaming for OpenAI's API

## Usage

```bash
python sse_chatbot.py
```

You'll see text appearing word-by-word as the AI generates it, instead of waiting for the complete response.
