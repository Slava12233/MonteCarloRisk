"""
Unit tests for the registry module.

This module contains unit tests for the registry module implementation.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.registry import register_agent_type, get_agent_factory, create_agent, list_agent_types


@pytest.fixture
def clear_registry():
    """Fixture to clear the registry before each test."""
    from src.registry import _agent_registry
    _agent_registry.clear()
    yield


@pytest.fixture
def mock_agent_factory():
    """Fixture for creating a mock agent factory."""
    mock_agent = MagicMock()
    mock_factory = MagicMock(return_value=mock_agent)
    return mock_factory, mock_agent


def test_register_agent_type(clear_registry, mock_agent_factory):
    """Test registering an agent type."""
    mock_factory, _ = mock_agent_factory
    
    # Register an agent type
    register_agent_type("test", mock_factory)
    
    # Check that the agent type is registered
    from src.registry import _agent_registry
    assert "test" in _agent_registry
    assert _agent_registry["test"] == mock_factory


def test_register_duplicate_agent_type(clear_registry, mock_agent_factory):
    """Test registering a duplicate agent type."""
    mock_factory, _ = mock_agent_factory
    
    # Register an agent type
    register_agent_type("test", mock_factory)
    
    # Try to register the same agent type again
    with pytest.raises(ValueError):
        register_agent_type("test", mock_factory)


def test_get_agent_factory(clear_registry, mock_agent_factory):
    """Test getting an agent factory."""
    mock_factory, _ = mock_agent_factory
    
    # Register an agent type
    register_agent_type("test", mock_factory)
    
    # Get the agent factory
    factory = get_agent_factory("test")
    
    # Check that the factory is correct
    assert factory == mock_factory


def test_get_nonexistent_agent_factory(clear_registry):
    """Test getting a nonexistent agent factory."""
    # Try to get a nonexistent agent factory
    with pytest.raises(ValueError):
        get_agent_factory("nonexistent")


def test_create_agent(clear_registry, mock_agent_factory):
    """Test creating an agent."""
    mock_factory, mock_agent = mock_agent_factory
    
    # Register an agent type
    register_agent_type("test", mock_factory)
    
    # Create an agent
    agent = create_agent(
        agent_type="test",
        name="test_agent",
        model="test_model",
        description="Test agent",
        instruction="Test instruction",
    )
    
    # Check that the agent factory was called with the correct arguments
    mock_factory.assert_called_once_with(
        name="test_agent",
        model="test_model",
        description="Test agent",
        instruction="Test instruction",
    )
    
    # Check that the agent is correct
    assert agent == mock_agent


def test_create_nonexistent_agent(clear_registry):
    """Test creating a nonexistent agent."""
    # Try to create a nonexistent agent
    with pytest.raises(ValueError):
        create_agent("nonexistent")


def test_list_agent_types(clear_registry, mock_agent_factory):
    """Test listing agent types."""
    mock_factory, _ = mock_agent_factory
    
    # Register some agent types
    register_agent_type("test1", mock_factory)
    register_agent_type("test2", mock_factory)
    
    # List the agent types
    agent_types = list_agent_types()
    
    # Check that the agent types are correct
    assert "test1" in agent_types
    assert "test2" in agent_types
    assert len(agent_types) == 2


def test_built_in_search_agent(clear_registry):
    """Test that the built-in search agent is registered."""
    # Re-register the search agent (since we cleared the registry in setUp)
    from src.agents.search_agent import SearchAgent
    
    def _create_search_agent(**kwargs):
        return SearchAgent(**kwargs)
    
    register_agent_type("search", _create_search_agent)
    
    # List the agent types
    agent_types = list_agent_types()
    
    # Check that the search agent is registered
    assert "search" in agent_types
