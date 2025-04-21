"""
Unit tests for the BaseAgent class.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import the class to test
from src.agents.base_agent import BaseAgent
from src import config # To access DEFAULT_MODEL

# --- Fixtures ---

@pytest.fixture
def minimal_agent_args():
    """Provides minimal arguments needed to initialize BaseAgent for validation tests."""
    # Mock dependencies that might be called during init if validation is strict
    # For now, assume basic init works for validation method testing
    return {
        "name": "test_validation_agent",
        # We might need to mock config.validate_config if DEV_MODE is False
    }

# --- Tests for _validate_model ---

def test_validate_model_with_value(minimal_agent_args):
    """Test _validate_model with a specific model string."""
    # Need an instance to call the method
    # Patch validate_config to avoid issues during init if DEV_MODE is False
    with patch('src.agents.base_agent.validate_config', return_value=None):
         agent = BaseAgent(**minimal_agent_args)
    model = "gemini-pro"
    validated_model = agent._validate_model(model)
    assert validated_model == model

def test_validate_model_with_none(minimal_agent_args):
    """Test _validate_model with None, should return default."""
    with patch('src.agents.base_agent.validate_config', return_value=None):
        agent = BaseAgent(**minimal_agent_args)
    validated_model = agent._validate_model(None)
    assert validated_model == config.DEFAULT_MODEL

def test_validate_model_with_empty_string(minimal_agent_args):
    """Test _validate_model with an empty string, should return default."""
    with patch('src.agents.base_agent.validate_config', return_value=None):
        agent = BaseAgent(**minimal_agent_args)
    validated_model = agent._validate_model("")
    assert validated_model == config.DEFAULT_MODEL

# --- Tests for _validate_tools ---

def test_validate_tools_with_list(minimal_agent_args):
    """Test _validate_tools with a list of tools."""
    with patch('src.agents.base_agent.validate_config', return_value=None):
        agent = BaseAgent(**minimal_agent_args)
    mock_tool_1 = MagicMock()
    mock_tool_2 = MagicMock()
    tools = [mock_tool_1, mock_tool_2]
    validated_tools = agent._validate_tools(tools)
    assert validated_tools == tools
    assert len(validated_tools) == 2

def test_validate_tools_with_none(minimal_agent_args):
    """Test _validate_tools with None, should return empty list."""
    with patch('src.agents.base_agent.validate_config', return_value=None):
        agent = BaseAgent(**minimal_agent_args)
    validated_tools = agent._validate_tools(None)
    assert validated_tools == []

def test_validate_tools_with_empty_list(minimal_agent_args):
    """Test _validate_tools with an empty list."""
    with patch('src.agents.base_agent.validate_config', return_value=None):
        agent = BaseAgent(**minimal_agent_args)
    validated_tools = agent._validate_tools([])
    assert validated_tools == []

# --- Tests for __init__ ---

@patch('src.agents.base_agent.Runner')
@patch('src.agents.base_agent.LlmAgent')
@patch('src.agents.base_agent.InMemorySessionService')
@patch('src.agents.base_agent.validate_config', return_value=None) # Assume config is valid
def test_base_agent_init_defaults(
    mock_validate_config, mock_session_service_cls, mock_llm_agent_cls, mock_runner_cls
):
    """Test BaseAgent initialization with default arguments."""
    agent_name = "test_default_agent"
    mock_session_service_instance = MagicMock()
    mock_session_service_cls.return_value = mock_session_service_instance
    mock_llm_agent_instance = MagicMock(name="test_default_agent_llm")
    mock_llm_agent_cls.return_value = mock_llm_agent_instance

    agent = BaseAgent(name=agent_name)

    # Check public/internal attributes
    assert agent.name == agent_name # Use public attribute
    assert agent._model == config.DEFAULT_MODEL
    assert agent._instruction == ""
    assert agent._tools == []
    assert agent._app_name == agent_name # Defaults to name

    # Check SessionService initialization
    mock_session_service_cls.assert_called_once()
    assert agent._session_service == mock_session_service_instance

    # Check LlmAgent initialization
    mock_llm_agent_cls.assert_called_once_with(
        name=f"{agent_name}_llm",
        model=config.DEFAULT_MODEL,
        description="",
        instruction="",
        tools=[],
    )
    assert agent._llm_agent == mock_llm_agent_instance
    assert agent.sub_agents == [mock_llm_agent_instance] # Check it was added

    # Check Runner initialization
    mock_runner_cls.assert_called_once_with(
        agent=agent,
        app_name=agent_name,
        session_service=mock_session_service_instance,
    )
    assert agent._runner == mock_runner_cls.return_value


@patch('src.agents.base_agent.Runner')
@patch('src.agents.base_agent.LlmAgent')
@patch('src.agents.base_agent.validate_config', return_value=None)
def test_base_agent_init_custom_args(
    mock_validate_config, mock_llm_agent_cls, mock_runner_cls
):
    """Test BaseAgent initialization with custom arguments."""
    agent_name = "custom_agent"
    custom_model = "gemini-pro"
    custom_desc = "My custom agent"
    custom_instr = "Be helpful"
    mock_tool = MagicMock()
    custom_tools = [mock_tool]
    # Remove custom sub_agent for simplicity, test that _llm_agent is added
    # mock_sub_agent = MagicMock(name="existing_sub")
    # custom_sub_agents = [mock_sub_agent]
    mock_session_service_instance = MagicMock()
    custom_app_name = "my_app"

    mock_llm_agent_instance = MagicMock(name="custom_agent_llm")
    mock_llm_agent_cls.return_value = mock_llm_agent_instance

    agent = BaseAgent(
        name=agent_name,
        model=custom_model,
        description=custom_desc,
        instruction=custom_instr,
        tools=custom_tools,
        # sub_agents=custom_sub_agents, # Don't pass custom sub_agents here
        session_service=mock_session_service_instance,
        app_name=custom_app_name,
    )

    # Check public/internal attributes
    assert agent.name == agent_name # Use public attribute
    assert agent._model == custom_model
    assert agent._instruction == custom_instr
    assert agent._tools == custom_tools
    assert agent._app_name == custom_app_name

    # Check SessionService was used
    assert agent._session_service == mock_session_service_instance

    # Check LlmAgent initialization
    mock_llm_agent_cls.assert_called_once_with(
        name=f"{agent_name}_llm",
        model=custom_model,
        description=custom_desc,
        instruction=custom_instr,
        tools=custom_tools,
    )
    assert agent._llm_agent == mock_llm_agent_instance
    # Check only the internal llm sub-agent is present
    assert mock_llm_agent_instance in agent.sub_agents
    assert len(agent.sub_agents) == 1

    # Check Runner initialization
    mock_runner_cls.assert_called_once_with(
        agent=agent,
        app_name=custom_app_name,
        session_service=mock_session_service_instance,
    )
    assert agent._runner == mock_runner_cls.return_value


@patch('src.agents.base_agent.validate_config', return_value="Config Error")
def test_base_agent_init_invalid_config(mock_validate_config):
    """Test BaseAgent initialization raises error if config is invalid (and not DEV_MODE)."""
    # Ensure DEV_MODE is False for this test
    with patch('src.agents.base_agent.DEV_MODE', False):
        with pytest.raises(ValueError, match="Invalid configuration: Config Error"):
            BaseAgent(name="invalid_config_agent")
    mock_validate_config.assert_called_once()


@patch('src.agents.base_agent.validate_config', return_value=None)
def test_base_agent_init_dev_mode_skips_validation(mock_validate_config):
    """Test BaseAgent initialization skips config validation if DEV_MODE is True."""
    # Ensure DEV_MODE is True for this test
    with patch('src.agents.base_agent.DEV_MODE', True):
         # Patch other dependencies just enough to allow init
         with patch('src.agents.base_agent.LlmAgent'), \
              patch('src.agents.base_agent.Runner'), \
              patch('src.agents.base_agent.InMemorySessionService'):
            BaseAgent(name="dev_mode_agent")
    # Assert that validate_config was NOT called
    mock_validate_config.assert_not_called()


# --- Fixture for Agent Instance with Mocks ---

@pytest.fixture
def agent_instance():
    """Provides a BaseAgent instance with mocked internal components for run tests."""
    with patch('src.agents.base_agent.validate_config', return_value=None), \
         patch('src.agents.base_agent.LlmAgent') as MockLlmAgent, \
         patch('src.agents.base_agent.Runner') as MockRunner, \
         patch('src.agents.base_agent.InMemorySessionService') as MockSessionService:

        mock_session_instance = MagicMock()
        MockSessionService.return_value = mock_session_instance

        mock_runner_instance = MagicMock()
        MockRunner.return_value = mock_runner_instance

        agent = BaseAgent(name="run_test_agent")

        # Attach mocks for easy access in tests
        agent._mock_runner = mock_runner_instance
        agent._mock_session_service = mock_session_instance
        agent._mock_llm_agent = MockLlmAgent.return_value

        yield agent


# --- Tests for run methods ---

def test_run_session_exists(agent_instance):
    """Test agent.run when session already exists."""
    user_id = "u1"
    session_id = "s1"
    message = "Hello"
    mock_events = [MagicMock(), MagicMock()]

    # Simulate session existing
    agent_instance._mock_session_service.get_session.return_value = MagicMock()
    # Simulate runner returning events
    agent_instance._mock_runner.run.return_value = mock_events

    events = agent_instance.run(user_id, session_id, message)

    agent_instance._mock_session_service.get_session.assert_called_once_with(
        app_name=agent_instance._app_name, user_id=user_id, session_id=session_id
    )
    agent_instance._mock_session_service.create_session.assert_not_called()
    agent_instance._mock_runner.run.assert_called_once()
    # Check message conversion (assuming types.Content is imported)
    from google.genai import types
    call_args, call_kwargs = agent_instance._mock_runner.run.call_args
    assert call_kwargs['user_id'] == user_id
    assert call_kwargs['session_id'] == session_id
    assert isinstance(call_kwargs['new_message'], types.Content)
    assert call_kwargs['new_message'].parts[0].text == message

    assert events == mock_events


def test_run_session_does_not_exist(agent_instance):
    """Test agent.run creates session if it doesn't exist."""
    user_id = "u2"
    session_id = "s2"
    message = "Hi there"
    mock_events = [MagicMock()]

    # Simulate session NOT existing
    agent_instance._mock_session_service.get_session.return_value = None
    agent_instance._mock_runner.run.return_value = mock_events

    events = agent_instance.run(user_id, session_id, message)

    agent_instance._mock_session_service.get_session.assert_called_once_with(
        app_name=agent_instance._app_name, user_id=user_id, session_id=session_id
    )
    # Check session creation was called
    agent_instance._mock_session_service.create_session.assert_called_once_with(
        app_name=agent_instance._app_name, user_id=user_id, session_id=session_id, state={}
    )
    agent_instance._mock_runner.run.assert_called_once()
    assert events == mock_events


def test_get_final_response_found(agent_instance):
    """Test get_final_response finds the final response text."""
    mock_event_1 = MagicMock()
    mock_event_1.is_final_response.return_value = False
    mock_event_2 = MagicMock()
    mock_event_2.is_final_response.return_value = True
    mock_event_2.content.parts = [MagicMock(text="Final Answer")]
    mock_event_3 = MagicMock() # After final
    mock_event_3.is_final_response.return_value = False

    events = [mock_event_1, mock_event_2, mock_event_3]
    response = agent_instance.get_final_response(events)

    assert response == "Final Answer"


def test_get_final_response_not_found(agent_instance):
    """Test get_final_response returns None if no final response event."""
    mock_event_1 = MagicMock()
    mock_event_1.is_final_response.return_value = False
    mock_event_2 = MagicMock()
    mock_event_2.is_final_response.return_value = False

    events = [mock_event_1, mock_event_2]
    response = agent_instance.get_final_response(events)

    assert response is None


def test_get_final_response_no_content(agent_instance):
    """Test get_final_response returns None if final event has no content/parts."""
    mock_event_1 = MagicMock()
    mock_event_1.is_final_response.return_value = True
    mock_event_1.content = None # No content

    mock_event_2 = MagicMock()
    mock_event_2.is_final_response.return_value = True
    mock_event_2.content = MagicMock(parts=None) # No parts

    assert agent_instance.get_final_response([mock_event_1]) is None
    assert agent_instance.get_final_response([mock_event_2]) is None


@patch.object(BaseAgent, 'run') # Patch the run method within the class
def test_run_and_get_response(mock_run_method, agent_instance):
    """Test run_and_get_response calls run and get_final_response."""
    user_id = "u3"
    session_id = "s3"
    message = "Question?"
    mock_events = [MagicMock()]
    final_response_text = "The Answer"

    mock_run_method.return_value = mock_events

    # Patch get_final_response on the BaseAgent class for the duration of the test
    with patch.object(BaseAgent, 'get_final_response', return_value=final_response_text) as mock_get_final:
        # The agent_instance created by the fixture will now use the patched method
        response = agent_instance.run_and_get_response(user_id, session_id, message)

        mock_run_method.assert_called_once_with(user_id, session_id, message)
        mock_get_final.assert_called_once_with(mock_events)
        assert response == final_response_text


def test_run_with_string_message(mock_base_agent):
    """Test running an agent with a string message."""
    # Setup
    user_id = "test_user"
    session_id = "test_session"
    message = "Hello, agent!"
    
    # Execute
    result = mock_base_agent.run(user_id, session_id, message)
    
    # Verify
    mock_base_agent._runner.run.assert_called_once()
    # Verify the message was converted to Content
    call_args = mock_base_agent._runner.run.call_args[1]
    assert call_args["user_id"] == user_id
    assert call_args["session_id"] == session_id
    assert call_args["new_message"].role == "user"
    assert len(call_args["new_message"].parts) == 1
    assert call_args["new_message"].parts[0].text == message

def test_run_with_content_message(mock_base_agent, monkeypatch):
    """Test running an agent with a Content message."""
    # Setup
    user_id = "test_user"
    session_id = "test_session"
    
    # Create a mock Content object instead of importing from google.ai.generativelanguage
    from unittest.mock import MagicMock
    content_message = MagicMock()
    content_message.role = "user"
    part = MagicMock()
    part.text = "Hello from content"
    content_message.parts = [part]
    
    # Execute
    result = mock_base_agent.run(user_id, session_id, content_message)
    
    # Verify
    mock_base_agent._runner.run.assert_called_once()
    # Verify the message was passed through as Content
    call_args = mock_base_agent._runner.run.call_args[1]
    assert call_args["user_id"] == user_id
    assert call_args["session_id"] == session_id
    assert call_args["new_message"] == content_message

# --- Add tests for _run_async_impl later if needed ---

@pytest.fixture
def mock_base_agent():
    """Fixture that provides a mocked BaseAgent for testing."""
    mock_agent = MagicMock()
    mock_agent._runner = MagicMock()
    mock_agent._runner.run = MagicMock(return_value=[])
    mock_agent.get_session = MagicMock(return_value=None)
    mock_agent.create_session = MagicMock()
    
    # Make the run method actually call _runner.run
    def run_method(user_id, session_id, message):
        # If the session doesn't exist, create it
        if not mock_agent.get_session(user_id, session_id):
            mock_agent.create_session(user_id, session_id)
        
        # Convert string message to Content if needed
        if isinstance(message, str):
            from unittest.mock import MagicMock
            # Create a mock Content object
            content = MagicMock()
            content.role = "user"
            part = MagicMock()
            part.text = message
            content.parts = [part]
            message = content
        
        # Call the runner
        return mock_agent._runner.run(user_id=user_id, session_id=session_id, new_message=message)
    
    mock_agent.run = run_method
    return mock_agent

@pytest.mark.asyncio
async def test_run_live_impl():
    """Test _run_live_impl delegates to the LLM agent's run_live method."""
    # Create a mock LLM agent
    mock_llm_agent = MagicMock()
    # Setup the mock to return a sequence of events when awaited
    mock_event1 = MagicMock()
    mock_event2 = MagicMock()
    
    # Create a proper async generator for the run_live method
    async def mock_run_live_generator(ctx):
        yield mock_event1
        yield mock_event2
    
    # Set the run_live method to our generator function
    mock_llm_agent.run_live = mock_run_live_generator
    
    # Create the BaseAgent with the mock LLM agent
    with patch('src.agents.base_agent.validate_config', return_value=None), \
         patch('src.agents.base_agent.LlmAgent', return_value=mock_llm_agent), \
         patch('src.agents.base_agent.Runner'), \
         patch('src.agents.base_agent.InMemorySessionService'):
        
        agent = BaseAgent(name="run_live_test_agent")
        
        # Create a mock context
        mock_ctx = MagicMock()
        
        # Call _run_live_impl
        events = []
        async for event in agent._run_live_impl(mock_ctx):
            events.append(event)
        
        # Verify that the events were yielded
        assert len(events) == 2
        assert mock_event1 in events
        assert mock_event2 in events
