"""
Multi-Tool Agent Example for the Google ADK Agent Starter Kit.

This example demonstrates how to create and use an agent with multiple tools.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env file
load_dotenv()

from src.agents.search_agent import SearchAgent
from src.tools.custom_tools import create_custom_tool, CustomToolBuilder
from src.utils.logging import configure_logging

# Configure logging
configure_logging(level="INFO")
logger = logging.getLogger(__name__)


# Define a custom tool for getting the current date and time
def get_current_datetime(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get the current date and time.

    Args:
        format_string: The format string for the date and time (default: "%Y-%m-%d %H:%M:%S").

    Returns:
        The current date and time formatted according to the format string.
    """
    now = datetime.now()
    return now.strftime(format_string)


# Create a custom tool using the function
datetime_tool = create_custom_tool(get_current_datetime)


# Create a custom tool using the builder pattern
calculator_tool = (
    CustomToolBuilder("calculate")
    .description("Perform a calculation.")
    .add_parameter("expression", str, "The expression to calculate.")
    .set_handler(lambda params: str(eval(params["expression"])))
    .build()
)


def main():
    """Run the multi-tool agent example."""
    logger.info("Starting Multi-Tool Agent Example")

    # Create a search agent with additional tools
    agent = SearchAgent(
        name="multi_tool_agent",
        description="An agent that can search the web and use custom tools.",
        instruction="""I can answer your questions by searching the internet and using custom tools.
        
I can also:
- Get the current date and time
- Perform calculations
        
Just ask me anything!""",
        additional_tools=[datetime_tool, calculator_tool],
    )

    logger.info(f"Created agent: {agent.name}")

    # Define some example queries
    example_queries = [
        "What is the capital of France?",
        "What is the current date and time?",
        "Calculate 15 * 7 + 22",
        "What is the population of Tokyo and what percentage is that of Japan's total population?",
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

    # Create a search agent with additional tools
    agent = SearchAgent(
        name="interactive_multi_tool_agent",
        description="An agent that can search the web and use custom tools.",
        instruction="""I can answer your questions by searching the internet and using custom tools.
        
I can also:
- Get the current date and time
- Perform calculations
        
Just ask me anything!""",
        additional_tools=[datetime_tool, calculator_tool],
    )

    logger.info(f"Created agent: {agent.name}")

    print("\nWelcome to the Interactive Multi-Tool Agent!")
    print("This agent can search the web, get the current date and time, and perform calculations.")
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
