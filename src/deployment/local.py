"""
Local development utilities for the Google ADK Agent Starter Kit.

This module provides utilities for running agents locally for development and testing.
"""

import logging
import os
from typing import Any, Optional, Dict, Union, List

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

    # Get the templates directory path
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    # Get the static directory path
    static_dir = os.path.join(os.path.dirname(__file__), "static")

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

    @app.get("/api/sessions/{user_id}", response_class=JSONResponse)
    async def list_user_sessions(user_id: str):
        """List all session IDs for a given user."""
        try:
            # Access the session service stored within the agent instance
            session_service = agent._session_service
            app_name = agent._app_name
            
            # List sessions using the service
            raw_sessions_data = session_service.list_sessions(app_name=app_name, user_id=user_id)
            logger.debug(f"Raw sessions data listed for {user_id}: {raw_sessions_data}")

            session_ids = []
            sessions_list_to_process = []

            # Explicitly check for the observed tuple structure ('sessions', [...])
            if isinstance(raw_sessions_data, tuple) and len(raw_sessions_data) == 2 and raw_sessions_data[0] == 'sessions' and isinstance(raw_sessions_data[1], list):
                sessions_list_to_process = raw_sessions_data[1]
                logger.debug("Interpreted raw_sessions_data as ('sessions', [...]) structure.")
            # Check if it's already a list (potentially of Session objects)
            elif isinstance(raw_sessions_data, list):
                 sessions_list_to_process = raw_sessions_data
                 logger.debug("Interpreted raw_sessions_data as a direct list.")
            # Log unexpected structures
            elif raw_sessions_data is not None: # If it's not None/empty but not list/expected tuple
                 logger.warning(f"Unexpected structure returned by list_sessions for {user_id}: {raw_sessions_data}")
            # If raw_sessions_data is None or empty list/tuple initially
            else:
                 logger.info(f"list_sessions returned no data for user {user_id}.")


            # Process the extracted list (if any)
            if sessions_list_to_process:
                for item in sessions_list_to_process:
                    # Check if the item looks like a Session object with an 'id'
                    if hasattr(item, 'id') and isinstance(item.id, str):
                        session_ids.append(item.id)
                    else:
                        # Log if an unexpected item is found in the list
                        logger.warning(f"Item in session list for {user_id} is not a valid Session object or lacks 'id': {item}")
            # Log if processing resulted in no IDs (either list was empty or items were invalid)
            elif not session_ids:
                 logger.info(f"No valid sessions found or extracted for user {user_id} after processing.")

            logger.info(f"Found sessions for user {user_id}: {session_ids}")
            return {"sessions": session_ids}
        except Exception as e:
            logger.error(f"Error listing sessions for user {user_id}: {e}", exc_info=True)
            return JSONResponse(status_code=500, content={"error": "Failed to list sessions"})

    @app.get("/api/sessions/{user_id}/{session_id}/history", response_class=JSONResponse)
    async def get_session_history(user_id: str, session_id: str):
        """Get the chat history (events) for a specific session."""
        try:
            session_service = agent._session_service
            app_name = agent._app_name

            session = session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

            if not session:
                logger.warning(f"Session not found: {user_id}/{session_id}")
                return JSONResponse(status_code=404, content={"error": "Session not found"})

            history = []
            if session.events:
                for event in session.events:
                    # Determine sender ('user' or 'agent'/'system'/'tool')
                    sender = event.author if event.author else 'unknown'
                    # Simplify agent/system/tool to 'agent' for UI consistency
                    if sender not in ['user']:
                        sender = 'agent' # Or keep original author if needed: sender = event.author

                    text = None
                    # Extract text content safely
                    if event.content and event.content.parts:
                        # Assuming the first part is the primary text content
                        try:
                            text = event.content.parts[0].text
                        except AttributeError:
                            logger.debug(f"Event part has no text attribute: {event.content.parts[0]}")
                            # Optionally handle other part types like function calls/responses if needed
                            if event.get_function_calls():
                                text = f"[Function Call: {event.get_function_calls()[0].name}]"
                            elif event.get_function_responses():
                                text = f"[Function Response]" # Content might be complex

                    # Only add events that have some text representation
                    if text is not None:
                         history.append({"sender": sender, "text": text})
                    else:
                         logger.debug(f"Skipping event with no extractable text: {event}")


            logger.info(f"Retrieved history for session {user_id}/{session_id} with {len(history)} messages.")
            return {"history": history}

        except Exception as e:
            logger.error(f"Error getting history for session {user_id}/{session_id}: {e}", exc_info=True)
            return JSONResponse(status_code=500, content={"error": "Failed to get session history"})


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
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            reload=reload,
        )
    except OSError as e:
        if "address already in use" in str(e).lower() or "only one usage of each socket address" in str(e).lower():
            # Try with a different port
            new_port = port + 1
            logger.warning(f"Port {port} is already in use. Trying port {new_port}...")
            run_locally(agent, host, new_port, log_level, reload)
        else:
            # Re-raise other OSErrors
            raise


def _test_debug_get_history_attr_error():
    """For test coverage only - do not use in production."""
    event = type('Event', (), {})()
    event.content = type('Content', (), {})()
    event.content.parts = [type('Part', (), {})()]
    # Will raise AttributeError when part.text is accessed
    try:
        text = event.content.parts[0].text
    except AttributeError:
        pass  # Catch the AttributeError
    return None
