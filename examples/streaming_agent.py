"""
Streaming Agent Example for the Google ADK Agent Starter Kit.

This example demonstrates how to run an agent with a web interface that supports streaming responses.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env file
load_dotenv()

from src.agents.search_agent import SearchAgent
from src.deployment.local import run_locally
from src.utils.logging import configure_logging

# Configure logging
configure_logging(level="INFO")
logger = logging.getLogger(__name__)


def main(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Run the streaming agent example.
    
    Args:
        host: The host to bind to (default: 127.0.0.1).
        port: The port to bind to (default: 8000).
        reload: Whether to reload the server on code changes (default: False).
    """
    logger.info("Starting Streaming Agent Example")

    # Create a search agent
    agent = SearchAgent(
        name="streaming_search_agent",
        description="A search agent with streaming responses.",
        instruction="""I can answer your questions by searching the internet. 
        
My responses will be streamed in real-time as I generate them.

Just ask me anything!""",
    )

    logger.info(f"Created agent: {agent.name}")
    
    # Run the agent locally with a web interface
    run_locally(
        agent=agent,
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a streaming agent with a web interface.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="The host to bind to.")
    parser.add_argument("--port", type=int, default=8000, help="The port to bind to.")
    parser.add_argument("--reload", action="store_true", help="Reload the server on code changes.")
    
    args = parser.parse_args()
    
    # Run the agent
    main(host=args.host, port=args.port, reload=args.reload)
