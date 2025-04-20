"""
Search agent implementation for the Google ADK Agent Starter Kit.

This module provides an example implementation of a search agent using Google Search.
"""

from typing import Optional, List, Any, Dict, AsyncGenerator
from typing_extensions import override

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import google_search

from .base_agent import BaseAgent


class SearchAgent(BaseAgent):
    """
    Search agent implementation using Google Search.

    This class extends the BaseAgent to provide a specialized agent that can
    search the web using Google Search to answer questions.
    """

    # Define model_config for Pydantic
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str = "search_agent",
        model: str = "gemini-2.0-flash",
        description: str = "Agent to answer questions using Google Search.",
        instruction: str = "I can answer your questions by searching the internet. Just ask me anything!",
        session_service: Optional[Any] = None,
        app_name: Optional[str] = None,
        additional_tools: Optional[List[Any]] = None,
    ):
        """
        Initialize a new SearchAgent.

        Args:
            name: The name of the agent (default: search_agent).
            model: The model to use (default: gemini-2.0-flash).
            description: A description of the agent.
            instruction: Instructions for the agent.
            session_service: A session service to use.
            app_name: The name of the application.
            additional_tools: Additional tools to include besides Google Search.
        """
        # Combine Google Search with any additional tools
        tools = [google_search]
        if additional_tools:
            tools.extend(additional_tools)

        super().__init__(
            name=name,
            model=model,
            description=description,
            instruction=instruction,
            tools=tools,
            session_service=session_service,
            app_name=app_name,
        )

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implement the custom orchestration logic for this search agent.
        
        This method simply delegates to the LLM agent, which has access to the Google Search tool.
        
        Args:
            ctx: The invocation context, which includes session state and other runtime info.
            
        Yields:
            Events produced by this agent or its sub-agents.
        """
        # For a simple search agent, we just delegate to the LLM agent
        async for event in self._llm_agent.run_async(ctx):
            yield event

    def search(self, query: str, user_id: str = "user", session_id: str = "session") -> str:
        """
        Search for information using Google Search.

        This is a convenience method that runs the agent with a query and returns
        the final response.

        Args:
            query: The search query.
            user_id: The ID of the user (default: "user").
            session_id: The ID of the session (default: "session").

        Returns:
            The search result as text.
        """
        response = self.run_and_get_response(user_id, session_id, query)
        return response or "No response from the agent."
