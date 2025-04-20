"""
Unit tests for the local deployment module.

This module contains unit tests for the local deployment implementation.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.deployment.local import create_app, run_locally


@pytest.fixture
def mock_agent():
    """Fixture for creating a mock agent."""
    agent = MagicMock()
    agent.name = "test_agent"
    agent.run_and_get_response.return_value = "Mock response"
    return agent


@pytest.fixture
def mock_uvicorn_run():
    """Fixture for mocking uvicorn.run."""
    with patch("src.deployment.local.uvicorn.run") as mock:
        yield mock


@pytest.fixture
def mock_templates():
    """Fixture for mocking Jinja2Templates."""
    with patch("src.deployment.local.Jinja2Templates") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock, mock_instance


@pytest.fixture
def mock_static_files():
    """Fixture for mocking StaticFiles."""
    with patch("src.deployment.local.StaticFiles") as mock:
        yield mock


def test_create_app(mock_agent, mock_templates, mock_static_files):
    """Test creating a FastAPI application."""
    mock_templates_class, _ = mock_templates
    
    # Create the app
    app = create_app(mock_agent)
    
    # Check that the app has the expected routes
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/api/chat" in routes
    assert "/ws/{user_id}/{session_id}" in routes
    
    # Check that the static files are mounted
    mock_static_files.assert_called_once()
    
    # Check that the templates are set up
    mock_templates_class.assert_called_once()


def test_run_locally(mock_agent, mock_uvicorn_run):
    """Test running the agent locally."""
    # Run the agent locally
    run_locally(
        agent=mock_agent,
        host="test_host",
        port=1234,
        log_level="test_level",
        reload=True,
    )
    
    # Check that uvicorn.run was called with the correct arguments
    mock_uvicorn_run.assert_called_once()
    args, kwargs = mock_uvicorn_run.call_args
    assert kwargs["host"] == "test_host"
    assert kwargs["port"] == 1234
    assert kwargs["log_level"] == "test_level"
    assert kwargs["reload"] == True


def test_app_routes(mock_agent, mock_templates, mock_static_files):
    """Test that the app has the expected routes."""
    mock_templates_class, _ = mock_templates
    
    # Create the app
    app = create_app(mock_agent)
    
    # Check that the app has the expected routes
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/api/chat" in routes
    assert "/ws/{user_id}/{session_id}" in routes
    
    # Check that the static files are mounted
    mock_static_files.assert_called_once()
    
    # Check that the templates are set up
    mock_templates_class.assert_called_once()
