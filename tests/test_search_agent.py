"""
Unit tests for the search agent.

This module contains unit tests for the search agent implementation.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.search_agent import SearchAgent
from src.registry import create_agent, register_agent_type, get_agent_factory, list_agent_types


@pytest.fixture
def mock_google_search():
    """Fixture for mocking the google_search tool."""
    with patch("src.agents.search_agent.google_search") as mock:
        yield mock


@pytest.fixture
def mock_runner():
    """Fixture for mocking the Runner class."""
    with patch("src.agents.base_agent.Runner") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Set up mock events
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = True
        mock_event.content.parts = [MagicMock(text="Mock response")]
        mock_instance.run.return_value = [mock_event]
        
        yield mock_instance


@pytest.fixture
def mock_validate_config():
    """Fixture for mocking the validate_config function."""
    with patch("src.agents.base_agent.validate_config") as mock:
        mock.return_value = None  # No error
        yield mock


@pytest.fixture
def mock_llm_agent():
    """Fixture for mocking the LlmAgent class."""
    with patch("src.agents.base_agent.LlmAgent") as mock:
        yield mock


@pytest.fixture
def search_agent(mock_google_search, mock_runner, mock_validate_config, mock_llm_agent):
    """Fixture for creating a SearchAgent instance."""
    with patch("src.agents.base_agent.DEV_MODE", True):
        agent = SearchAgent(
            name="test_search_agent",
            description="Test search agent",
            instruction="Test instruction",
        )
        yield agent


def test_init(search_agent):
    """Test initialization of the SearchAgent."""
    assert search_agent.name == "test_search_agent"
    assert search_agent.description == "Test search agent"
    assert search_agent._instruction == "Test instruction"
    assert len(search_agent._tools) == 1  # Should have google_search tool


def test_search(search_agent, mock_runner):
    """Test the search method."""
    # Call the search method
    response = search_agent.search("test query")
    
    # Check that the runner.run method was called with the correct arguments
    mock_runner.run.assert_called_once()
    args, kwargs = mock_runner.run.call_args
    assert kwargs["user_id"] == "user"
    assert kwargs["session_id"] == "session"
    
    # Check that the response is correct
    assert response == "Mock response"


def test_search_with_custom_user_and_session(search_agent, mock_runner):
    """Test the search method with custom user and session IDs."""
    # Call the search method with custom user and session IDs
    response = search_agent.search("test query", user_id="custom_user", session_id="custom_session")
    
    # Check that the runner.run method was called with the correct arguments
    mock_runner.run.assert_called_once()
    args, kwargs = mock_runner.run.call_args
    assert kwargs["user_id"] == "custom_user"
    assert kwargs["session_id"] == "custom_session"
    
    # Check that the response is correct
    assert response == "Mock response"


def test_search_no_response(search_agent, mock_runner):
    """Test the search method when there is no response."""
    # Set up mock events with no final response
    mock_event = MagicMock()
    mock_event.is_final_response.return_value = False
    mock_runner.run.return_value = [mock_event]
    
    # Call the search method
    response = search_agent.search("test query")
    
    # Check that the response is the default message
    assert response == "No response from the agent."
