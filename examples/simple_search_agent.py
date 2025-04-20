"""
Simple Search Agent Example for the Google ADK Agent Starter Kit.

This example demonstrates how to create and use a simple search agent.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env file
load_dotenv()

from src.agents.search_agent import SearchAgent
from src.utils.logging import configure_logging

# Configure logging
configure_logging(level="INFO")
logger = logging.getLogger(__name__)


def main():
    """Run the simple search agent example."""
    logger.info("Starting Simple Search Agent Example")

    # Create a search agent
    agent = SearchAgent(
        name="simple_search_agent",
        description="A simple agent that can search the web to answer questions.",
        instruction="I can answer your questions by searching the internet. Just ask me anything!",
    )

    logger.info(f"Created agent: {agent.name}")

    # Define some example queries
    example_queries = [
        "What is the capital of France?",
        "Who won the last World Cup?",
        "What is the tallest mountain in the world?",
        "What is the latest news about artificial intelligence?",
    ]

    # Run the agent with each query
    for query in example_queries:
        logger.info(f"Query: {query}")
        
        # Run the agent
        response = agent.search(query)
        
        # Print the response
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        print("-" * 80)


def interactive_mode():
    """Run the agent in interactive mode."""
    logger.info("Starting Interactive Mode")

    # Create a search agent
    agent = SearchAgent(
        name="interactive_search_agent",
        description="A simple agent that can search the web to answer questions.",
        instruction="I can answer your questions by searching the internet. Just ask me anything!",
    )

    logger.info(f"Created agent: {agent.name}")

    print("\nWelcome to the Interactive Search Agent!")
    print("Type 'exit' or 'quit' to end the session.")
    print("-" * 80)

    # Generate a unique session ID
    import uuid
    session_id = str(uuid.uuid4())

    # Run the agent in a loop
    while True:
        # Get user input
        query = input("\nYou: ")
        
        # Check if the user wants to exit
        if query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        # Run the agent
        response = agent.search(query, session_id=session_id)
        
        # Print the response
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    # Check if the user wants to run in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
