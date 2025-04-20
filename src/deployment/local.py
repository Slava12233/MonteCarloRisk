"""
Local development utilities for the Google ADK Agent Starter Kit.

This module provides utilities for running agents locally for development and testing.
"""

import logging
import os
from typing import Any, Optional, Dict, Union

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from google.genai import types

from ..config import WEB_UI_PORT
from ..utils.logging import get_logger

# Configure logging
logger = get_logger(__name__)


class Message(BaseModel):
    """Model for a message sent to the agent."""
    text: str
    user_id: str = "user"
    session_id: str = "session"


def create_app(agent: Any) -> FastAPI:
    """
    Create a FastAPI application for the agent.

    Args:
        agent: The agent to run.

    Returns:
        A FastAPI application.
    """
    app = FastAPI(title=f"{agent.name} API", description=f"API for {agent.name}")

    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(templates_dir, exist_ok=True)

    # Create static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)

    # Create simple HTML template for the UI
    with open(os.path.join(templates_dir, "index.html"), "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ agent_name }} - Chat Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        #chat-container {
            height: 400px;
            border: 1px solid #ccc;
            padding: 10px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 5px;
        }
        .user {
            background-color: #e6f7ff;
            text-align: right;
        }
        .agent {
            background-color: #f2f2f2;
        }
        #message-form {
            display: flex;
        }
        #message-input {
            flex-grow: 1;
            padding: 8px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <h1>{{ agent_name }} - Chat Interface</h1>
    <div id="chat-container"></div>
    <form id="message-form">
        <input type="text" id="message-input" placeholder="Type your message..." autocomplete="off">
        <button type="submit">Send</button>
    </form>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const messageForm = document.getElementById('message-form');
        const messageInput = document.getElementById('message-input');
        
        // Function to add a message to the chat
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(sender);
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Handle form submission
        messageForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            messageInput.value = '';
            
            try {
                // Send message to API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: message,
                        user_id: 'user',
                        session_id: 'session'
                    })
                });
                
                const data = await response.json();
                
                // Add agent response to chat
                addMessage(data.response, 'agent');
            } catch (error) {
                console.error('Error:', error);
                addMessage('Error: Could not get response from agent', 'agent');
            }
        });
    </script>
</body>
</html>
        """)

    # Mount static files
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Set up templates
    templates = Jinja2Templates(directory=templates_dir)

    @app.get("/", response_class=HTMLResponse)
    async def get_index(request: Request):
        """Serve the chat interface."""
        return templates.TemplateResponse(
            "index.html", {"request": request, "agent_name": agent.name}
        )

    @app.post("/api/chat", response_class=JSONResponse)
    async def chat(message: Message):
        """Handle chat messages."""
        logger.info(f"Received message: {message.text}")
        
        # Run the agent
        response = agent.run_and_get_response(
            user_id=message.user_id,
            session_id=message.session_id,
            message=message.text,
        )
        
        return {"response": response or "No response from the agent."}

    @app.websocket("/ws/{user_id}/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str):
        """Handle WebSocket connections for streaming responses."""
        await websocket.accept()
        
        try:
            while True:
                # Receive message from WebSocket
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message: {data}")
                
                # Create content
                content = types.Content(role="user", parts=[types.Part(text=data)])
                
                # Ensure session exists
                if not agent.get_session(user_id, session_id):
                    agent.create_session(user_id, session_id)
                
                # Run the agent
                events = agent.run(user_id, session_id, content)
                
                # Send events to WebSocket
                for event in events:
                    if event.is_final_response() and event.content and event.content.parts:
                        await websocket.send_json({
                            "type": "final",
                            "text": event.content.parts[0].text,
                        })
                    elif event.content and event.content.parts:
                        await websocket.send_json({
                            "type": "partial",
                            "text": event.content.parts[0].text,
                        })
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {user_id}/{session_id}")

    return app


def run_locally(
    agent: Any,
    host: str = "127.0.0.1",
    port: int = WEB_UI_PORT,
    log_level: str = "info",
    reload: bool = False,
) -> None:
    """
    Run the agent locally with a web interface.

    Args:
        agent: The agent to run.
        host: The host to bind to (default: 127.0.0.1).
        port: The port to bind to (default: from config).
        log_level: The log level for the server (default: info).
        reload: Whether to reload the server on code changes (default: False).
    """
    app = create_app(agent)
    
    logger.info(f"Running {agent.name} locally at http://{host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )
