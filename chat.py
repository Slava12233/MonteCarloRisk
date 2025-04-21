import vertexai
from vertexai import agent_engines
import uuid
import sys

# --- Configuration ---
PROJECT_ID = "risk-manager-457219"  # Your Google Cloud project ID
LOCATION = "us-central1"          # The region where the agent is deployed
AGENT_ENGINE_ID = "1578942677951447040" # The ID from the deployment logs
# --- End Configuration ---

# Construct the full resource name
AGENT_ENGINE_NAME = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}"

try:
    # Initialize Vertex AI (if not already initialized in your environment)
    print("Initializing Vertex AI...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    print("Vertex AI initialized.")

    # Get the deployed AgentEngine object
    print(f"Connecting to agent: {AGENT_ENGINE_NAME}")
    agent_engine = agent_engines.get(AGENT_ENGINE_NAME)
    print("Connected successfully.")

    # Create a unique user ID and session ID for the conversation
    user_id = f"user_{uuid.uuid4()}"
    session_id = agent_engine.create_session(user_id=user_id)["id"]
    print(f"Created new session: {session_id} for user: {user_id}")
    print("\n--- Start Chatting (type 'exit' or 'quit' to end) ---")

    # Start chatting
    while True:
        message = input("You: ")
        if message.lower() in ["exit", "quit"]:
            break

        print("Agent: ", end="", flush=True)
        # Send the query and stream the response
        response_stream = agent_engine.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        )

        full_response = ""
        has_output = False
        for event in response_stream:
            # --- DEBUG: Print the raw event ---
            print(f"\nDEBUG Raw Event: {event!r}\n", flush=True) 
            # --- End DEBUG ---

            # Process different event types (e.g., text chunks, tool calls)
            try:
                # Check if it's the expected event object with a 'type' attribute
                if hasattr(event, 'type'):
                    if event.type == agent_engines.StreamQueryEventType.TEXT_CHUNK:
                        print(event.text_chunk, end="", flush=True)
                        full_response += event.text_chunk
                        has_output = True
                    # Add handling for other standard event types if needed
                    # elif event.type == agent_engines.StreamQueryEventType.TOOL_CALL_CHUNK: ...
                    # elif event.type == agent_engines.StreamQueryEventType.TOOL_RESPONSE_CHUNK: ...
                    else:
                        # Handle other known event types if necessary
                        print(f"\n[Other Event Type: {event.type}]", end="", flush=True)
                        has_output = True
                # Check if it's the raw dictionary format observed for the final response
                elif isinstance(event, dict) and 'content' in event and isinstance(event['content'], dict) and 'parts' in event['content'] and isinstance(event['content']['parts'], list) and event['content']['parts']:
                    # Extract text from the first part
                    final_text = event['content']['parts'][0].get('text', '')
                    if final_text:
                        print(final_text, end="", flush=True)
                        full_response += final_text
                        has_output = True
                        # Assume this dict format is the final response and stop processing this stream
                        break
                    else:
                         print("\n[Received dict event with no text content]", end="", flush=True)
                         has_output = True
                else:
                    # Handle other unexpected formats
                    print(f"\n[Unknown Event Format: {type(event)}]", end="", flush=True)
                    has_output = True

            except Exception as e: # Catch broader exceptions during processing
                print(f"\nERROR processing event: {e}. Event data: {event!r}", file=sys.stderr)
                break # Stop processing this response stream on error

        if not has_output:
            print("[No text response received]", end="")

        print() # Newline after agent response

    print("\n--- Chat ended. ---")

except Exception as e:
    print(f"\nAn error occurred: {e}", file=sys.stderr)
    sys.exit(1)
