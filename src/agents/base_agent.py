"""
Base agent template for the Google ADK Agent Starter Kit.

This module provides a standardized base agent with common functionality.
"""

import logging
from typing import List, Optional, Dict, Any, Union, AsyncGenerator
from typing_extensions import override

from google.adk.agents import BaseAgent as ADKBaseAgent
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..config import DEFAULT_MODEL, get_config, validate_config, DEV_MODE

# Configure logging
logger = logging.getLogger(__name__)


class BaseAgent(ADKBaseAgent):
    """
    Base agent template with common functionality.

    This class provides a standardized foundation for building agents with
    Google's Agent Development Kit (ADK). It inherits directly from ADK's BaseAgent
    and implements custom orchestration logic.
    """

    # Define model_config for Pydantic
    model_config = {"arbitrary_types_allowed": True}

    # These are instance attributes, not Pydantic fields
    # They will be set in __init__ but not validated by Pydantic
    def __init__(
        self,
        name: str,
        model: str = DEFAULT_MODEL,
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Any]] = None,
        sub_agents: Optional[List[Any]] = None,
        session_service: Optional[Any] = None,
        app_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize a new BaseAgent.

        Args:
            name: The name of the agent.
            model: The model to use (default: gemini-2.0-flash).
            description: A description of the agent.
            instruction: Instructions for the agent.
            tools: A list of tools for the agent to use.
            sub_agents: A list of sub-agents for this agent to orchestrate.
            session_service: A session service to use (default: InMemorySessionService).
            app_name: The name of the application (default: agent name).
            **kwargs: Additional keyword arguments to pass to the parent class.
        """
        # Validate configuration (skip in development mode)
        if DEV_MODE is not True:  # Use is not True to handle None case
            error = validate_config()
            if error:
                raise ValueError(f"Invalid configuration: {error}")

        # Validate inputs before passing to parent class
        validated_model = self._validate_model(model)
        validated_tools = self._validate_tools(tools)
        validated_app_name = app_name or name

        # Initialize the parent class first
        super().__init__(
            name=name,
            description=description,
            sub_agents=sub_agents or [],
            **kwargs,
        )
        
        # Store parameters as instance attributes with leading underscore
        # to indicate they are "private"
        self._model = validated_model
        self._instruction = instruction
        self._tools = validated_tools
        self._app_name = validated_app_name
        
        # Create the LLM agent that will handle the actual reasoning
        self._llm_agent = LlmAgent(
            name=f"{name}_llm",
            model=self._model,  # Use validated model
            description=description,
            instruction=instruction,
            tools=self._tools,
        )
        
        # Add the LLM agent as a sub-agent if not already added
        if not any(agent.name == self._llm_agent.name for agent in self.sub_agents):
            self.sub_agents.append(self._llm_agent)
        
        # Set up session management
        self._session_service = session_service or InMemorySessionService()
        
        # Create a runner for direct use
        self._runner = Runner(
            agent=self,
            app_name=self._app_name,
            session_service=self._session_service,
        )
        
        logger.info(f"Initialized agent: {name}")
        
    def _validate_model(self, model: Optional[str]) -> str:
        """
        Validate the model parameter.
        
        Args:
            model: The model to validate.
            
        Returns:
            The validated model.
            
        Raises:
            ValueError: If the model is invalid.
        """
        if not model:
            return DEFAULT_MODEL
            
        # Add additional validation logic here
        # For example, check if the model is in a list of supported models
        # or if it matches a specific pattern
        
        return model
        
    def _validate_tools(self, tools: Optional[List[Any]]) -> List[Any]:
        """
        Validate the tools parameter.
        
        Args:
            tools: The tools to validate.
            
        Returns:
            The validated tools.
            
        Raises:
            ValueError: If any tool is invalid.
        """
        if not tools:
            return []
            
        # Add additional validation logic here
        # For example, check if each tool has required attributes
        # or if the tools list contains only supported tool types
        
        return tools

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implement the custom orchestration logic for this agent.
        
        This is the core method that defines how this agent processes requests and
        orchestrates its sub-agents.
        
        Args:
            ctx: The invocation context, which includes session state and other runtime info.
            
        Yields:
            Events produced by this agent or its sub-agents.
        """
        logger.info(f"[{self.name}] Starting agent execution")
        
        # Process the user's message using the LLM agent
        logger.info(f"[{self.name}] Running LLM agent")
        async for event in self._llm_agent.run_async(ctx):
            # You can add custom logic here to process events
            # For example, you could inspect the event, modify it, or take actions based on it
            
            # For now, we'll just pass the event through
            yield event
        
        logger.info(f"[{self.name}] Agent execution completed")

    async def _run_live_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implement the custom orchestration logic for live (audio/video) interactions.
        
        This method is required by the BaseAgent class but may not be used in all cases.
        
        Args:
            ctx: The invocation context, which includes session state and other runtime info.
            
        Yields:
            Events produced by this agent or its sub-agents.
        """
        # For now, we'll just delegate to the LLM agent
        async for event in self._llm_agent.run_live(ctx):
            yield event

    def create_session(self, user_id: str, session_id: str, state: Optional[Dict[str, Any]] = None) -> Any:
        """
        Create a new session for the agent.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.
            state: Initial state for the session.

        Returns:
            The created session.
        """
        session = self._session_service.create_session(
            app_name=self._app_name,
            user_id=user_id,
            session_id=session_id,
            state=state or {},
        )
        logger.info(f"Created session: {session_id} for user: {user_id}")
        return session

    def get_session(self, user_id: str, session_id: str) -> Any:
        """
        Get an existing session.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            The session, or None if it doesn't exist.
        """
        return self._session_service.get_session(
            app_name=self._app_name,
            user_id=user_id,
            session_id=session_id,
        )

    def run(self, user_id: str, session_id: str, message: Union[str, types.Content]) -> List[Any]:
        """
        Run the agent with a message.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.
            message: The message to send to the agent.

        Returns:
            A list of events from the agent.
        """
        # Ensure the session exists
        if not self.get_session(user_id, session_id):
            self.create_session(user_id, session_id)

        # Convert string message to Content if needed
        if isinstance(message, str):
            message = types.Content(role="user", parts=[types.Part(text=message)])

        # Run the agent
        logger.info(f"Running agent: {self.name} for user: {user_id}, session: {session_id}")
        events = list(self._runner.run(user_id=user_id, session_id=session_id, new_message=message))
        return events

    def get_final_response(self, events: List[Any]) -> Optional[str]:
        """
        Extract the final response from a list of events.

        Args:
            events: A list of events from the agent.

        Returns:
            The final response text, or None if there is no final response.
        """
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                return event.content.parts[0].text
        return None

    def run_and_get_response(self, user_id: str, session_id: str, message: Union[str, types.Content]) -> Optional[str]:
        """
        Run the agent and get the final response.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.
            message: The message to send to the agent.

        Returns:
            The final response text, or None if there is no final response.
        """
        events = self.run(user_id, session_id, message)
        return self.get_final_response(events)
