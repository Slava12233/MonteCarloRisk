"""
Command-line interface for the Google ADK Agent Starter Kit.

This module provides a command-line interface for running agents.
"""

import os
import sys
import argparse
import logging
from typing import Optional, List, Dict, Any

from .agents.search_agent import SearchAgent
from .deployment.local import run_locally
from .utils.logging import configure_logging, get_logger
from .config import print_config

# Configure logging
configure_logging()
logger = get_logger(__name__)


def create_agent(
    agent_type: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    description: Optional[str] = None,
    instruction: Optional[str] = None,
) -> Any:
    """
    Create an agent of the specified type.

    Args:
        agent_type: The type of agent to create (e.g., "search").
        name: The name of the agent (default: None).
        model: The model to use (default: None).
        description: A description of the agent (default: None).
        instruction: Instructions for the agent (default: None).

    Returns:
        The created agent.

    Raises:
        ValueError: If the agent type is not supported.
    """
    if agent_type == "search":
        # Create a search agent
        agent = SearchAgent(
            name=name or "search_agent",
            model=model,
            description=description or "A search agent that can answer questions using Google Search.",
            instruction=instruction or "I can answer your questions by searching the internet. Just ask me anything!",
        )
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")
    
    return agent


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
) -> None:
    """
    Run an agent.

    Args:
        agent_type: The type of agent to run (e.g., "search").
        query: A query to send to the agent (default: None).
        interactive: Whether to run in interactive mode (default: False).
        web: Whether to run with a web interface (default: False).
        host: The host to bind to for the web interface (default: 127.0.0.1).
        port: The port to bind to for the web interface (default: 8000).
        reload: Whether to reload the server on code changes (default: False).
        name: The name of the agent (default: None).
        model: The model to use (default: None).
        description: A description of the agent (default: None).
        instruction: Instructions for the agent (default: None).
    """
    # Create the agent
    agent = create_agent(
        agent_type=agent_type,
        name=name,
        model=model,
        description=description,
        instruction=instruction,
    )
    
    logger.info(f"Created agent: {agent.name}")
    
    if web:
        # Run with web interface
        logger.info(f"Running agent with web interface at http://{host}:{port}")
        run_locally(
            agent=agent,
            host=host,
            port=port,
            reload=reload,
        )
    elif interactive:
        # Run in interactive mode
        logger.info("Running agent in interactive mode")
        print(f"\nWelcome to the {agent.name} Interactive Mode!")
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
            if agent_type == "search":
                response = agent.search(query, session_id=session_id)
            else:
                response = "Unsupported agent type"
            
            # Print the response
            print(f"\nAgent: {response}")
    elif query:
        # Run with a single query
        logger.info(f"Running agent with query: {query}")
        
        # Run the agent
        if agent_type == "search":
            response = agent.search(query)
        else:
            response = "Unsupported agent type"
        
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
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Add the run command
    run_parser = subparsers.add_parser("run", help="Run an agent")
    run_parser.add_argument("agent_type", choices=["search"], help="Type of agent to run")
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
        parser.print_help()


if __name__ == "__main__":
    main()
