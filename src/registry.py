"""
Registry for agent types in the Google ADK Agent Starter Kit.

This module provides a registry for agent types, allowing new agent types to be
registered and used without modifying the CLI code directly.
"""

import logging
from typing import Any, Callable, Dict, Optional, Type

from .utils.logging import get_logger

# Configure logging
logger = get_logger(__name__)

# Type for agent factory functions
AgentFactory = Callable[..., Any]

# Registry of agent types
_agent_registry: Dict[str, AgentFactory] = {}


def register_agent_type(agent_type: str, factory: AgentFactory) -> None:
    """
    Register an agent type with the registry.

    Args:
        agent_type: The type of agent to register (e.g., "search").
        factory: A factory function that creates an agent of the specified type.

    Raises:
        ValueError: If the agent type is already registered.
    """
    if agent_type in _agent_registry:
        raise ValueError(f"Agent type '{agent_type}' is already registered.")
    
    _agent_registry[agent_type] = factory
    logger.info(f"Registered agent type: {agent_type}")


def get_agent_factory(agent_type: str) -> AgentFactory:
    """
    Get the factory function for an agent type.

    Args:
        agent_type: The type of agent to get the factory for.

    Returns:
        The factory function for the agent type.

    Raises:
        ValueError: If the agent type is not registered.
    """
    if agent_type not in _agent_registry:
        raise ValueError(f"Agent type '{agent_type}' is not registered.")
    
    return _agent_registry[agent_type]


def create_agent(
    agent_type: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    description: Optional[str] = None,
    instruction: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Create an agent of the specified type.

    Args:
        agent_type: The type of agent to create (e.g., "search").
        name: The name of the agent (default: None).
        model: The model to use (default: None).
        description: A description of the agent (default: None).
        instruction: Instructions for the agent (default: None).
        **kwargs: Additional keyword arguments to pass to the factory function.

    Returns:
        The created agent.

    Raises:
        ValueError: If the agent type is not registered.
    """
    factory = get_agent_factory(agent_type)
    
    return factory(
        name=name,
        model=model,
        description=description,
        instruction=instruction,
        **kwargs
    )


def list_agent_types() -> list:
    """
    List all registered agent types.

    Returns:
        A list of registered agent types.
    """
    return list(_agent_registry.keys())


# Register built-in agent types
from .agents.base_agent import BaseAgent # Import BaseAgent
# Removed: from .agents.search_agent import SearchAgent
from google.adk.tools import google_search # Import the search tool

def _create_base_agent(
    name: Optional[str] = None,
    model: Optional[str] = None,
    description: Optional[str] = None,
    instruction: Optional[str] = None,
    **kwargs
) -> BaseAgent:
    """Factory function for creating a base agent."""
    # Note: BaseAgent might require specific tools or config depending on usage
    return BaseAgent(
        name=name or "base_agent", # Give it a default name
        model=model, # Pass through model if provided
        description=description or "A generic base agent.", # Default description
        instruction=instruction or "I am a base agent.", # Default instruction
        tools=[google_search], # Add the google_search tool
        **kwargs
    )

# Removed _create_search_agent function

# Register the agent types
register_agent_type("base", _create_base_agent)
# Removed: register_agent_type("search", _create_search_agent)
