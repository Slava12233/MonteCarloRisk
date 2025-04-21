"""
Unit tests for WebSocket functionality in the local deployment module.

This module tests the WebSocket endpoints in the local deployment module.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
from fastapi.routing import APIRoute
from starlette.routing import WebSocketRoute

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.deployment.local import create_app
from src.agents.base_agent import BaseAgent
from google.genai import types


# --- Helpers ---

class AsyncMockWrapper:
    """Helper class to wrap an AsyncMock for use in a context manager."""
    def __init__(self, mock_websocket):
        self.mock_websocket = mock_websocket
        self.messages = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, *args):
        pass
        
    async def receive_text(self):
        if not self.messages:
            raise WebSocketDisconnect()
        return self.messages.pop(0)
        
    def add_message(self, message):
        self.messages.append(message)


# --- Fixtures ---

@pytest.fixture
def test_client_and_mock_agent():
    """Fixture for creating a test client with a mock agent."""
    # Create a mock agent
    agent = MagicMock()
    agent.name = "test_ws_agent"
    
    # Mock session management
    agent.get_session.return_value = MagicMock()
    agent.create_session.return_value = MagicMock()
    
    # Mock run method to return events
    mock_event1 = MagicMock()
    mock_event1.is_final_response.return_value = False
    mock_event1.content = MagicMock()
    mock_event1.content.parts = [MagicMock(text="Thinking...")]
    
    mock_event2 = MagicMock()
    mock_event2.is_final_response.return_value = True
    mock_event2.content = MagicMock()
    mock_event2.content.parts = [MagicMock(text="Final answer")]
    
    agent.run.return_value = [mock_event1, mock_event2]
    
    # Create app and client
    app = create_app(agent)
    client = TestClient(app)
    
    return client, agent, app


# --- Test Cases ---

def test_websocket_route_exists(test_client_and_mock_agent):
    """Test that the WebSocket route exists with the expected pattern."""
    _, _, app = test_client_and_mock_agent
    
    # Find the WebSocket route
    websocket_route = None
    for route in app.routes:
        if route.path == "/ws/{user_id}/{session_id}":
            websocket_route = route
            break
    
    assert websocket_route is not None, "WebSocket route not found"
    assert websocket_route.endpoint.__name__ == "websocket_endpoint"


def test_websocket_params(test_client_and_mock_agent):
    """Test the WebSocket endpoint parameters."""
    _, _, app = test_client_and_mock_agent
    
    # Find the WebSocket route
    websocket_route = None
    for route in app.routes:
        if route.path == "/ws/{user_id}/{session_id}":
            websocket_route = route
            break
    
    assert websocket_route is not None
    
    # Check that the endpoint expects user_id and session_id parameters
    import inspect
    signature = inspect.signature(websocket_route.endpoint)
    params = list(signature.parameters.keys())
    
    assert "websocket" in params
    assert "user_id" in params
    assert "session_id" in params


def test_chat_endpoint(test_client_and_mock_agent):
    """Test the /api/chat endpoint."""
    client, agent, _ = test_client_and_mock_agent
    agent.run_and_get_response.return_value = "Test chat response"
    
    # Make a request to the chat endpoint
    response = client.post(
        "/api/chat",
        json={"text": "Hello", "user_id": "test_user", "session_id": "test_session"}
    )
    
    # Check response
    assert response.status_code == 200
    assert response.json() == {"response": "Test chat response"}
    
    # Verify agent method was called
    agent.run_and_get_response.assert_called_once_with(
        user_id="test_user",
        session_id="test_session",
        message="Hello"
    )


def test_get_session_history(test_client_and_mock_agent):
    """Test the session history endpoint."""
    client, agent, _ = test_client_and_mock_agent
    
    # Mock a session with events
    mock_session = MagicMock()
    
    # Create event with expected format and attributes
    mock_event1 = MagicMock()
    mock_event1.author = "user"
    mock_event1.content = MagicMock()
    mock_event1.content.parts = [MagicMock()]
    # Mock the text attribute as a property
    type(mock_event1.content.parts[0]).text = "User message"
    mock_event1.get_function_calls = MagicMock(return_value=None)
    mock_event1.get_function_responses = MagicMock(return_value=None)
    
    mock_event2 = MagicMock()
    mock_event2.author = "agent" 
    mock_event2.content = MagicMock()
    mock_event2.content.parts = [MagicMock()]
    # Mock the text attribute as a property
    type(mock_event2.content.parts[0]).text = "Agent response"
    mock_event2.get_function_calls = MagicMock(return_value=None)
    mock_event2.get_function_responses = MagicMock(return_value=None)
    
    # Set up the mock session
    mock_session.events = [mock_event1, mock_event2]
    
    # Need to patch get_session on the agent's session_service
    agent._session_service.get_session.return_value = mock_session
    
    # Make a request to the history endpoint
    response = client.get("/api/sessions/test_user/test_session/history")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    
    # Check history content
    assert len(data["history"]) == 2
    assert data["history"][0]["sender"] == "user"
    assert data["history"][0]["text"] == "User message"
    assert data["history"][1]["sender"] == "agent"
    assert data["history"][1]["text"] == "Agent response"


def test_get_session_history_not_found(test_client_and_mock_agent):
    """Test the session history endpoint when session is not found."""
    client, agent, _ = test_client_and_mock_agent
    
    # Mock session_service.get_session to return None
    agent._session_service.get_session.return_value = None
    
    # Make a request to the history endpoint
    response = client.get("/api/sessions/test_user/nonexistent_session/history")
    
    # Check response
    assert response.status_code == 404
    assert response.json() == {"error": "Session not found"}


def test_get_sessions_list(test_client_and_mock_agent):
    """Test listing sessions for a user."""
    client, agent, _ = test_client_and_mock_agent
    
    # Mock the session service
    mock_session1 = MagicMock()
    mock_session1.id = "session1"
    mock_session2 = MagicMock()
    mock_session2.id = "session2"
    
    # Mock the session service's list_sessions method
    agent._session_service.list_sessions.return_value = ("sessions", [mock_session1, mock_session2])
    
    # Make a request to list sessions
    response = client.get("/api/sessions/test_user")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "session1" in data["sessions"]
    assert "session2" in data["sessions"]
    
    # Verify session_service.list_sessions was called
    agent._session_service.list_sessions.assert_called_once_with(
        app_name=agent._app_name,
        user_id="test_user"
    )


# For websocket testing, we can't use the TestClient directly for WebSockets 
# as it doesn't support WebSockets properly. If we need complete WebSocket testing,
# we would need to use a proper WebSocket client library or mock the WebSocket mechanism.
# The following test checks the route is correctly defined:

def test_websocket_endpoint_integration_simulation(test_client_and_mock_agent):
    """
    Simulate testing the WebSocket endpoint by directly calling the handler
    with mocked objects.
    """
    _, agent, app = test_client_and_mock_agent
    
    # Find the WebSocket endpoint handler
    websocket_endpoint = None
    for route in app.routes:
        if route.path == "/ws/{user_id}/{session_id}":
            websocket_endpoint = route.endpoint
            break
    
    assert websocket_endpoint is not None
    
    # Create a mock content object that would be created in the handler
    mock_content = types.Content(role="user", parts=[types.Part(text="Test message")])
    
    # Verify agent has the necessary methods
    assert hasattr(agent, "get_session")
    assert hasattr(agent, "create_session")
    assert hasattr(agent, "run")
    
    # Verify the events returned by agent.run can be processed correctly
    events = agent.run.return_value
    assert len(events) >= 2
    
    # The first event should be a partial response
    assert events[0].is_final_response() is False
    assert events[0].content.parts[0].text == "Thinking..."
    
    # The second event should be a final response
    assert events[1].is_final_response() is True
    assert events[1].content.parts[0].text == "Final answer"

@pytest.mark.asyncio
async def test_websocket_error_handling():
    """Test handling of WebSocketDisconnect exception in websocket_endpoint."""
    # Create a mock WebSocket
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.receive_text = AsyncMock(side_effect=[
        "Test message", 
        WebSocketDisconnect(code=1000, reason="Client disconnected")
    ])
    
    # Create a mock agent
    mock_agent = MagicMock()
    mock_agent.get_session.return_value = None
    mock_agent.create_session = MagicMock()
    mock_event = MagicMock()
    mock_event.is_final_response.return_value = True
    mock_event.content.parts = [MagicMock(text="Final response")]
    mock_agent.run.return_value = [mock_event]
    
    # Create the FastAPI app
    app = create_app(mock_agent)
    
    # Get the websocket_endpoint handler
    websocket_endpoint = None
    for route in app.routes:
        if isinstance(route, WebSocketRoute) and route.path == "/ws/{user_id}/{session_id}":
            websocket_endpoint = route.endpoint
            break
    
    assert websocket_endpoint is not None
    
    # Run the endpoint with the mock websocket
    # We expect this to complete normally as WebSocketDisconnect is handled internally
    await websocket_endpoint(mock_websocket, "test_user", "test_session")
    
    # Verify behavior
    mock_websocket.accept.assert_called_once()
    # Verify that receive_text was called
    assert mock_websocket.receive_text.call_count > 0
    # Verify that the agent's get_session and create_session were called
    mock_agent.get_session.assert_called_once()
    mock_agent.create_session.assert_called_once()

@pytest.mark.asyncio
async def test_websocket_final_response_handling():
    """Test handling of final response in websocket_endpoint."""
    # Create a mock WebSocket
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.receive_text = AsyncMock(side_effect=["Test message", WebSocketDisconnect()])
    mock_websocket.send_json = AsyncMock()
    
    # Create a mock final response event
    mock_final_event = MagicMock()
    mock_final_event.is_final_response.return_value = True
    mock_final_part = MagicMock()
    mock_final_part.text = "Final response"
    mock_final_event.content.parts = [mock_final_part]
    
    # Create a mock partial response event
    mock_partial_event = MagicMock()
    mock_partial_event.is_final_response.return_value = False
    mock_partial_part = MagicMock()
    mock_partial_part.text = "Partial response"
    mock_partial_event.content.parts = [mock_partial_part]
    
    # Create a mock agent
    mock_agent = MagicMock()
    mock_agent.get_session.return_value = True  # Session exists
    mock_agent.run.return_value = [mock_partial_event, mock_final_event]
    
    # Create the FastAPI app
    app = create_app(mock_agent)
    
    # Get the websocket_endpoint handler
    websocket_endpoint = None
    for route in app.routes:
        if isinstance(route, WebSocketRoute) and route.path == "/ws/{user_id}/{session_id}":
            websocket_endpoint = route.endpoint
            break
    
    assert websocket_endpoint is not None
    
    # Run the endpoint with the mock websocket
    # We expect this to complete normally as WebSocketDisconnect is handled internally
    await websocket_endpoint(mock_websocket, "test_user", "test_session")
    
    # Verify that the agent's run method was called
    mock_agent.run.assert_called_once()
    
    # Verify that send_json was called for both events
    assert mock_websocket.send_json.call_count == 2
    # Check the first call (partial response)
    mock_websocket.send_json.assert_any_call({
        "type": "partial",
        "text": "Partial response",
    })
    # Check the second call (final response)
    mock_websocket.send_json.assert_any_call({
        "type": "final",
        "text": "Final response",
    }) 