"""
Command-line interface for the Google ADK Agent Starter Kit.

This module provides a command-line interface for running agents.
"""

import os
import sys
import uuid
import argparse
import logging
from typing import Optional, List, Dict, Any

from .registry import create_agent, list_agent_types
from .deployment.local import run_locally
# Removed: from .deployment.vertex import deploy_to_vertex
from .utils.logging import configure_logging, get_logger
from .config import print_config

# Configure logging
configure_logging()
logger = get_logger(__name__)


# Note: We're using the create_agent function from the registry module


def run_agent(
    agent_type: str,
    query: Optional[str] = None,
    interactive: bool = False,
    web: bool = False,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    name: Optional[str] = None,
    model: Optional[str] = None,
    description: Optional[str] = None,
    instruction: Optional[str] = None,
    **kwargs
) -> None:
    """
    Run an agent with the specified parameters.

    Args:
        agent_type: The type of agent to run.
        query: The query to send to the agent.
        interactive: Whether to run in interactive mode.
        web: Whether to run with a web interface.
        host: The host to bind to for the web interface.
        port: The port to bind to for the web interface.
        reload: Whether to reload the server on code changes.
        name: The name of the agent.
        model: The model to use.
        description: The description of the agent.
        instruction: The instructions for the agent.
        **kwargs: Additional arguments to pass to the agent.
    """
    logger.info(f"Running agent of type: {agent_type}")
    
    # Create the agent
    agent = create_agent(
        agent_type=agent_type,
        name=name,
        model=model,
        description=description,
        instruction=instruction,
        **kwargs
    )
    
    if web:
        # Run with web interface
        logger.info("Running with web interface")
        run_locally(
            agent=agent,
            host=host,
            port=port,
            reload=reload,
        )
    elif interactive:
        # Run in interactive mode
        logger.info("Running in interactive mode")
        print(f"\nWelcome to the Interactive Mode with {agent.name}")
        print("Type 'exit' or 'quit' to end the session.")
        
        # Use a consistent session ID for the interactive session
        # Reason: Using a consistent session ID allows the agent to maintain
        # context across multiple messages in the same interactive session
        session_id = str(uuid.uuid4())
        
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit", "bye", "goodbye"]:
                print("\nGoodbye!")
                break
            
            # Run the agent
            try:
                # Try to use the search method if available
                # Reason: The search method is specifically designed for query processing
                # and may have optimizations or additional features compared to run_and_get_response
                if hasattr(agent, 'search'):
                    response = agent.search(query, session_id=session_id)
                else:
                    # Fall back to run_and_get_response
                    # Reason: Not all agents implement the search method, so we need a fallback
                    response = agent.run_and_get_response(user_id="user", session_id=session_id, message=query)
            except Exception as e:
                logger.error(f"Error running agent: {e}")
                response = f"Error: {str(e)}"
            
            # Print the response
            print(f"\nAgent: {response}")
    elif query:
        # Run with a single query
        logger.info(f"Running agent with query: {query}")
        
        # Run the agent
        try:
            # Try to use the search method if available
            # Reason: Same as above, the search method is preferred if available
            if hasattr(agent, 'search'):
                response = agent.search(query)
            else:
                # Fall back to run_and_get_response
                # Reason: For one-off queries, we don't need to explicitly manage the session
                # as it's a single interaction
                response = agent.run_and_get_response(user_id="user", session_id="session", message=query)
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            response = f"Error: {str(e)}"
        
        # Print the response
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
    else:
        # No query or interactive mode specified
        logger.error("No query or interactive mode specified")
        print("Please specify a query with --query or run in interactive mode with --interactive")


def main():
    """Run the command-line interface."""
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Google ADK Agent Starter Kit CLI")
    
    # Add subparsers for different commands
    # Reason: Using subparsers provides a cleaner CLI structure and helps organize
    # different commands (run, config, etc.) with their own arguments
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Add the run command
    run_parser = subparsers.add_parser("run", help="Run an agent")
    # Reason: We dynamically fetch available agent types from the registry to ensure
    # the CLI always shows the current set of registered agents
    run_parser.add_argument("agent_type", choices=list_agent_types(), help="Type of agent to run")
    run_parser.add_argument("--query", help="Query to send to the agent")
    run_parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    run_parser.add_argument("--web", action="store_true", help="Run with a web interface")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to for the web interface")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to bind to for the web interface")
    run_parser.add_argument("--reload", action="store_true", help="Reload the server on code changes")
    run_parser.add_argument("--name", help="Name of the agent")
    run_parser.add_argument("--model", help="Model to use")
    run_parser.add_argument("--description", help="Description of the agent")
    run_parser.add_argument("--instruction", help="Instructions for the agent")
    
    # Add the config command
    config_parser = subparsers.add_parser("config", help="Print the current configuration")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "run":
        run_agent(
            agent_type=args.agent_type,
            query=args.query,
            interactive=args.interactive,
            web=args.web,
            host=args.host,
            port=args.port,
            reload=args.reload,
            name=args.name,
            model=args.model,
            description=args.description,
            instruction=args.instruction,
        )
    elif args.command == "config":
        print_config()
    else:
        # Reason: If no command is specified, show the help text to guide the user
        parser.print_help()


# For test coverage only - do not use in production code
def _test_main_block():
    """Helper function for testing the __name__ == '__main__' block."""
    main()

if __name__ == "__main__":
    main()
