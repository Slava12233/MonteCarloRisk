# Google ADK Agent Starter Kit

## Executive Summary

As the co-founder and CTO of our AI Agents company, I'm pleased to present our Google ADK Agent Starter Kit. This toolkit provides a robust foundation for building intelligent agents using Google's Agent Development Kit (ADK). It implements a true custom agent architecture that follows Google's recommended patterns while providing flexibility for future expansion.

This documentation serves as a comprehensive guide for our development team to understand, use, and extend the starter kit for building specialized agents for various use cases.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Implementation Details](#implementation-details)
5. [Getting Started](#getting-started)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Future Roadmap](#future-roadmap)
12. [References](#references)

## Introduction

The Google ADK Agent Starter Kit provides a standardized foundation for building intelligent agents using Google's Agent Development Kit. It implements a true custom agent architecture that inherits directly from Google's BaseAgent class and follows the recommended patterns for custom agent development.

### Key Features

- **True Custom Agent Architecture**: Inherits directly from Google's BaseAgent class and implements the required methods.
- **LLM Integration**: Uses Google's Gemini models for natural language understanding and generation.
- **Tool Integration**: Seamlessly integrates with Google Search and custom tools.
- **Flexible Orchestration**: Supports complex orchestration patterns like conditional logic and state management.
- **Comprehensive Testing**: Includes unit tests for all components.
- **Interactive Mode**: Supports interactive conversations with the agent.

## Architecture Overview

Our starter kit follows a layered architecture that separates concerns and promotes modularity:

```
┌─────────────────────────────────────────┐
│               Client Layer              │
│  (CLI, Web UI, API, etc.)               │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│             Agent Layer                 │
│  (BaseAgent, etc.)                      │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│           Orchestration Layer           │
│  (Custom logic in _run_async_impl)      │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│             Tool Layer                  │
│  (Google Search, Custom Tools, etc.)    │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│             Model Layer                 │
│  (Gemini models via Google AI API)      │
└─────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Each layer has a specific responsibility.
2. **Modularity**: Components are designed to be reusable and replaceable.
3. **Extensibility**: The architecture allows for easy extension with new agents, tools, and models.
4. **Testability**: All components are designed to be easily testable.

## Core Components

### BaseAgent

The `BaseAgent` class is the foundation of our agent architecture. It inherits directly from Google's `BaseAgent` class and implements the required methods for custom agent development.

Key features:
- Implements `_run_async_impl` for custom orchestration logic
- Manages sub-agents, including an LlmAgent for reasoning
- Handles session management and state
- Provides convenience methods for running the agent and getting responses

### Custom Tools

The starter kit includes support for custom tools that can be used by agents to perform specific tasks.

Key features:
- Implements a `CustomTool` class for creating new tools
- Provides examples of custom tool implementation
- Includes unit tests for custom tools

## Implementation Details

### BaseAgent Implementation

The `BaseAgent` class inherits from Google's `BaseAgent` class and implements the required methods for custom agent development:

```python
class BaseAgent(ADKBaseAgent):
    """
    Base agent template with common functionality.

    This class provides a standardized foundation for building agents with
    Google's Agent Development Kit (ADK). It inherits directly from ADK's BaseAgent
    and implements custom orchestration logic.
    """

    # Define model_config for Pydantic
    model_config = {"arbitrary_types_allowed": True}

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
        # Initialize the parent class first
        super().__init__(
            name=name,
            description=description,
            sub_agents=sub_agents or [],
            **kwargs,
        )
        
        # Store parameters as instance attributes
        self._model = model
        self._instruction = instruction
        self._tools = tools or []
        self._app_name = app_name or name
        
        # Create the LLM agent that will handle the actual reasoning
        self._llm_agent = LlmAgent(
            name=f"{name}_llm",
            model=model or DEFAULT_MODEL,  # Ensure model is never None
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

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implement the custom orchestration logic for this agent.
        
        This is the core method that defines how this agent processes requests and
        orchestrates its sub-agents.
        """
        logger.info(f"[{self.name}] Starting agent execution")
        
        # Process the user's message using the LLM agent
        logger.info(f"[{self.name}] Running LLM agent")
        async for event in self._llm_agent.run_async(ctx):
            # You can add custom logic here to process events
            yield event
        
        logger.info(f"[{self.name}] Agent execution completed")
```

### Custom Tools Implementation

The starter kit includes support for custom tools:

```python
def get_current_time() -> str:
    """
    Get the current time.

    Returns:
        str: The current time in ISO format.
    """
    return datetime.datetime.now().isoformat()

def get_random_number(min_value: int = 0, max_value: int = 100) -> int:
    """
    Generate a random number between min_value and max_value.

    Args:
        min_value: The minimum value (inclusive).
        max_value: The maximum value (inclusive).

    Returns:
        int: A random number between min_value and max_value.
    """
    return random.randint(min_value, max_value)
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google API key for Gemini models
- Google Cloud project (for Vertex AI deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/google-adk-agent-starter-kit.git
   cd google-adk-agent-starter-kit
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### Project Structure

The project follows a modular structure designed for extensibility:

```
google-adk-agent-starter-kit/
├── README.md                 # Documentation and getting started guide
├── requirements.txt          # Dependencies
├── .env.example              # Template for environment variables
├── .env                      # Environment variables (not in version control)
├── setup.py                  # Package setup for distribution
├── run.py                    # CLI entry point
├── chat.py                   # Script to interact with deployed agent via SDK
├── deploy_agent_engine.py    # Script for Vertex AI Agent Engine deployment
├── deployment_config.yaml    # Base configuration for deployment
├── environments/             # Environment-specific configurations
│   ├── development.yaml      # Development environment configuration
│   ├── staging.yaml          # Staging environment configuration
│   └── production.yaml       # Production environment configuration
├── docs/
│   ├── DOCUMENTATION_1.md    # This document (comprehensive documentation)
│   ├── PLANNING.md           # Architecture and planning document
│   ├── PYDANTIC_USAGE.md     # Guidelines for using Pydantic
│   ├── AGENT_ENGINE_DEPLOYMENT.md # Guide for Agent Engine deployment
│   ├── project_visualization.html # Project structure visualization
│   ├── project_visualization.md   # Project structure in markdown
│   └── ACTION_ITEMS.md       # Action items and improvements
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration settings
│   ├── cli.py                # CLI implementation
│   ├── registry.py           # Agent registry for dynamic agent creation
│   ├── agents/
│   │   ├── __init__.py
│   │   └── base_agent.py     # Base agent implementation (includes search tool)
│   ├── tools/
│   │   ├── __init__.py
│   │   └── custom_tools.py   # Template for creating custom tools
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication utilities
│   │   └── logging.py        # Logging configuration
│   └── deployment/
│       ├── __init__.py
│       ├── local.py          # Local deployment utilities
│       └── vertex.py         # Vertex AI deployment utilities
├── examples/
│   ├── simple_search_agent.py       # Basic search agent example
│   ├── multi_tool_agent.py          # Example with multiple tools
│   └── streaming_agent.py           # Example with streaming capabilities
└── tests/
    ├── __init__.py
    └── test_custom_tools.py         # Tests for custom tools
```

Key files and directories:

1. **run.py**: Entry point for running agents via CLI
2. **chat.py**: Script for interacting with agents deployed on Vertex AI Agent Engine
3. **deploy_agent_engine.py**: Script for deploying agents to Vertex AI Agent Engine
4. **src/registry.py**: Registry for agent types, allowing dynamic agent creation
5. **src/agents/base_agent.py**: Base agent implementation that inherits from Google's BaseAgent
6. **src/tools/custom_tools.py**: Templates and utilities for creating custom tools

### Running the Agent

#### Interactive Mode

Run the base agent in interactive mode:

```bash
python run.py run base --interactive
```

This will start an interactive session where you can chat with the agent.

#### Programmatic Use

You can also use the agent programmatically in your code:

```python
from src.agents.base_agent import BaseAgent # Use BaseAgent now

# Create a base agent (includes search tool via registry)
agent = BaseAgent(
    name="my_base_agent",
    description="My custom base agent with search",
    instruction="Answer questions using Google Search",
)

# Run the agent
response = agent.run_and_get_response(user_id="prog_user", session_id="prog_session", message="What is the capital of France?")
print(response)
```

## Development Workflow

### Creating a New Agent

To create a new agent, extend the `BaseAgent` class and implement the required methods:

```python
from src.agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    """
    My custom agent implementation.
    """

    def __init__(
        self,
        name: str = "my_custom_agent",
        model: str = "gemini-2.0-flash",
        description: str = "My custom agent",
        instruction: str = "I am a custom agent",
        session_service: Optional[Any] = None,
        app_name: Optional[str] = None,
        additional_tools: Optional[List[Any]] = None,
    ):
        # Initialize tools
        tools = []
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
        Implement the custom orchestration logic for this agent.
        """
        # Implement your custom logic here
        async for event in self._llm_agent.run_async(ctx):
            yield event
```

### Creating a New Tool

To create a new tool, define a function with a descriptive docstring:

```python
def my_custom_tool(param1: str, param2: int) -> str:
    """
    My custom tool that does something useful.

    Args:
        param1: The first parameter.
        param2: The second parameter.

    Returns:
        str: The result of the tool.
    """
    # Implement your tool logic here
    return f"Result: {param1}, {param2}"
```

Then, add the tool to your agent:

```python
from src.tools.custom_tools import my_custom_tool

agent = MyCustomAgent(
    name="my_agent",
    additional_tools=[my_custom_tool],
)
```

### Advanced Orchestration

For more complex orchestration patterns, you can implement custom logic in the `_run_async_impl` method:

```python
@override
async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    """
    Implement complex orchestration logic.
    """
    # Get the user's message from the context
    user_message = ctx.session.state.get("user_message", "")
    
    # Conditional logic based on the message
    if "search" in user_message.lower():
        # Use the search agent
        async for event in self._search_agent.run_async(ctx):
            yield event
    elif "calculate" in user_message.lower():
        # Use the calculator agent
        async for event in self._calculator_agent.run_async(ctx):
            yield event
    else:
        # Use the default LLM agent
        async for event in self._llm_agent.run_async(ctx):
            yield event
```

## Testing

### Running Tests

Run the tests using pytest:

```bash
pytest tests/
```

### Writing Tests

When creating a new agent or tool, write unit tests to ensure it works correctly:

```python
def test_my_custom_tool():
    """Test the my_custom_tool function."""
    result = my_custom_tool("test", 42)
    assert result == "Result: test, 42"

class TestMyCustomAgent(unittest.TestCase):
    """Tests for the MyCustomAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = MyCustomAgent(
            name="test_agent",
            description="Test agent",
            instruction="Test instruction",
        )

    def test_init(self):
        """Test initialization of the agent."""
        self.assertEqual(self.agent.name, "test_agent")
        self.assertEqual(self.agent.description, "Test agent")
        self.assertEqual(self.agent._instruction, "Test instruction")

    def test_run(self):
        """Test running the agent."""
        # Mock the necessary components
        # ...
        
        # Run the agent
        response = self.agent.run_and_get_response("user", "session", "test message")
        
        # Check the response
        self.assertEqual(response, "Expected response")
```

## Deployment

### Local Deployment

For local development and testing, you can run the agent using the CLI:

```bash
python run.py run search --interactive
```

### Vertex AI Deployment

For production deployment, you can deploy the agent to Vertex AI using one of two approaches:

#### Option 1: Vertex AI Endpoint Deployment (Alternative)

This option deploys the agent as a Vertex AI endpoint using the traditional approach via `deploy.py`:

1. Set up your Google Cloud project:
   ```bash
   gcloud config set project your-project-id
   ```

2. Enable the required APIs:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

3. Deploy the agent:
   ```bash
   python deploy.py --vertex --environment production
   ```
*(Note: This uses a different deployment script and method than Agent Engine)*

#### Option 2: Vertex AI Agent Engine Deployment (Recommended)

This option deploys the agent to Vertex AI Agent Engine, which is a fully managed service specifically designed for AI agents:

1. Set up your Google Cloud project:
   ```bash
   gcloud config set project your-project-id
   ```

2. Enable the required APIs:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

3. Install the required dependencies:
   ```bash
   pip install 'google-cloud-aiplatform[adk,agent_engines]'
   ```

4. Deploy the agent:
   ```bash
   python deploy_agent_engine.py --environment production --staging-bucket gs://your-bucket-name
   ```

For detailed instructions on deploying to Agent Engine, see the [Agent Engine Deployment Guide](docs/AGENT_ENGINE_DEPLOYMENT.md).

## Best Practices

### Agent Design

1. **Keep Agents Focused**: Each agent should have a clear, specific purpose.
2. **Use Descriptive Names**: Choose clear, descriptive names for agents and tools.
3. **Write Clear Instructions**: Provide clear, detailed instructions for the agent.
4. **Leverage Tools**: Use tools to extend the agent's capabilities.
5. **Implement Proper Error Handling**: Handle errors gracefully and provide helpful error messages.

### Tool Design

1. **Keep Tools Simple**: Each tool should do one thing well.
2. **Write Clear Docstrings**: Provide clear, detailed docstrings for tools.
3. **Validate Inputs**: Validate inputs to prevent errors.
4. **Return Structured Data**: Return structured data that's easy to process.
5. **Handle Errors Gracefully**: Catch and handle errors appropriately.

### Testing

1. **Write Unit Tests**: Write unit tests for all components.
2. **Test Edge Cases**: Test edge cases and error conditions.
3. **Use Mocks**: Use mocks to isolate components during testing.
4. **Test Integration**: Test the integration between components.
5. **Automate Testing**: Set up CI/CD to run tests automatically.

## Troubleshooting

### Common Issues

#### API Key Issues

**Symptom**: Error message about invalid or missing API key.

**Solution**: 
1. Check that your API key is set correctly in the `.env` file.
2. Verify that the API key is valid and has the necessary permissions.
3. If using Vertex AI, ensure that the service account has the necessary permissions.

#### Model Issues

**Symptom**: Error message about invalid model or model not found.

**Solution**:
1. Check that the model name is correct and supported.
2. Verify that the model is available in your region.
3. If using a custom model, ensure that it's properly deployed and accessible.

#### Tool Issues

**Symptom**: Error message about tool execution failure.

**Solution**:
1. Check that the tool is properly implemented and registered.
2. Verify that the tool's inputs are valid.
3. Check the tool's error handling to ensure it handles errors gracefully.

### Debugging

#### Enabling Debug Logging

To enable debug logging, set the `LOG_LEVEL` environment variable to `DEBUG`:

```bash
export LOG_LEVEL=DEBUG
```

Or in your `.env` file:

```
LOG_LEVEL=DEBUG
```

#### Using the Debugger

You can use the Python debugger to step through the code:

```python
import pdb

# Add a breakpoint
pdb.set_trace()
```

#### Inspecting State

To inspect the agent's state, you can add logging statements:

```python
logger.debug(f"Session state: {ctx.session.state}")
```

## Future Roadmap

### Short-term Goals (1-3 months)

1. **Enhance Tool Support**: Add more built-in tools for common tasks.
2. **Improve Documentation**: Expand documentation with more examples and tutorials.
3. **Add Monitoring**: Implement monitoring and logging for better observability.

### Medium-term Goals (3-6 months)

1. **Multi-agent Orchestration**: Implement more advanced multi-agent orchestration patterns.
2. **Memory and Context Management**: Improve memory and context management for longer conversations.
3. **Performance Optimization**: Optimize performance for faster response times.

### Long-term Goals (6-12 months)

1. **Advanced Reasoning**: Implement more advanced reasoning capabilities.
2. **Multi-modal Support**: Add support for images, audio, and video.
3. **Enterprise Integration**: Integrate with enterprise systems and workflows.

## References

### Project Documentation

- [README.md](../README.md) - Overview and getting started guide
- [PLANNING.md](PLANNING.md) - Architecture, design decisions, and development roadmap
- [PYDANTIC_USAGE.md](PYDANTIC_USAGE.md) - Guidelines for using Pydantic in agent classes
- [AGENT_ENGINE_DEPLOYMENT.md](AGENT_ENGINE_DEPLOYMENT.md) - Guide for deploying to Vertex AI Agent Engine
- [ACTION_ITEMS.md](ACTION_ITEMS.md) - Action items and improvements for the project
- [TASK.md](../TASK.md) - Current and completed tasks

### Google ADK Documentation

- [Google ADK Overview](https://cloud.google.com/vertex-ai/docs/agent-development-kit/overview)
- [Custom Agents](https://cloud.google.com/vertex-ai/docs/agent-development-kit/custom-agents)
- [LLM Agents](https://cloud.google.com/vertex-ai/docs/agent-development-kit/llm-agents)
- [Tools](https://cloud.google.com/vertex-ai/docs/agent-development-kit/tools)

### Gemini API Documentation

- [Gemini API Overview](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [Gemini API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini-api)

### Python Documentation

- [Python 3.8 Documentation](https://docs.python.org/3.8/)
- [asyncio Documentation](https://docs.python.org/3.8/library/asyncio.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## Conclusion

This documentation provides a comprehensive guide to our Google ADK Agent Starter Kit. It covers the architecture, implementation details, usage instructions, and best practices for building intelligent agents using Google's Agent Development Kit.

This document works in conjunction with the `PLANNING.md` file, which provides a more focused view of the architecture, design decisions, and roadmap. While this document provides comprehensive details on implementation and usage, `PLANNING.md` offers a higher-level strategic overview that can be useful for new team members and for making architectural decisions.

As we continue to develop and enhance this starter kit, we'll update both this documentation and the related documentation files to reflect new features and improvements. If you have any questions or feedback, please don't hesitate to reach out to the development team.

Happy agent building!

---

*Document Version: 1.2*  
*Last Updated: April 22, 2025*  
*Author: [Your Name], CTO*

## Recent Updates

The following improvements have been made to the Google ADK Agent Starter Kit:

1. **Creation of Consolidated Planning Document**: A new `PLANNING.md` document has been created to serve as a centralized reference for the project's architecture, design decisions, and roadmap. This document complements the comprehensive information in this documentation file.

2. **Fixed Vertex AI Agent Engine Deployment**: Fixed deployment to Vertex AI Agent Engine by adding `extra_packages=['./src']` to the `agent_engines.create` call in `deploy_agent_engine.py`. Also created `chat.py` to interact with the deployed agent via the Python SDK due to lack of Console UI and `gcloud` support.

3. **Updated Project Documentation**: Updated README.md and other documentation to reflect the current project structure and removed references to non-existent files.

4. **Fixed Vertex AI Deployment Mechanism**: The Vertex AI deployment mechanism (for standard endpoints via `deploy.py`) was redesigned to correctly package and instantiate custom agent classes. *(Note: This is separate from the Agent Engine deployment fix)*.

5. **Improved CLI Extensibility**: The CLI was refactored to use a registry pattern (`src/registry.py`) for agent types, making it easier to add new agent types without modifying the CLI code directly.

6. **Refactored Local Deployment UI**: The local deployment UI has been refactored to use static HTML templates and separate CSS and JavaScript files, improving maintainability and separation of concerns. The UI now has a more modern look and feel with responsive design elements.

7. **Standardized Pydantic Usage**: We've implemented a hybrid approach for Pydantic usage in agent classes. This approach uses validation methods like `_validate_model()` and `_validate_tools()` to validate inputs, while maintaining compatibility with the ADK's BaseAgent class. See the [Pydantic Usage Guidelines](PYDANTIC_USAGE.md) for more details.

8. **Migrated Tests to pytest**: All tests have been migrated from unittest to pytest, improving test readability and maintainability. The test suite now uses fixtures for common test scenarios and assertions use the pytest style. See the [Test Report](TEST_REPORT.md) for more details.

9. **Improved Port Handling in Local Deployment**: The local deployment mechanism now handles the case where the default port is already in use by automatically trying the next available port.

These improvements address the issues identified in the code review report and make the starter kit more robust and extensible.

## Documentation Resources

For additional information about the project, please refer to the following resources:

- [PLANNING.md](PLANNING.md) - A consolidated reference for the project's architecture, design decisions, and development roadmap.
- [PYDANTIC_USAGE.md](PYDANTIC_USAGE.md) - Guidelines for using Pydantic in agent classes.
- [AGENT_ENGINE_DEPLOYMENT.md](AGENT_ENGINE_DEPLOYMENT.md) - Detailed guide for deploying to Vertex AI Agent Engine.

## Pydantic Usage

Our starter kit uses a hybrid approach for Pydantic integration in agent classes:

### Current Implementation

```python
class BaseAgent(ADKBaseAgent):
    # Define model_config for Pydantic
    model_config = {"arbitrary_types_allowed": True}

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
        
    def _validate_model(self, model: Optional[str]) -> str:
        """Validate the model parameter."""
        if not model:
            return DEFAULT_MODEL
        # Add additional validation logic here
        return model
        
    def _validate_tools(self, tools: Optional[List[Any]]) -> List[Any]:
        """Validate the tools parameter."""
        if not tools:
            return []
        # Add additional validation logic here
        return tools
```

### Key Features

1. **Model Configuration**: All agent classes define `model_config = {"arbitrary_types_allowed": True}` to allow non-Pydantic types.

2. **Validation Methods**: Instead of using Pydantic fields directly, we use validation methods like `_validate_model()` and `_validate_tools()` to validate inputs.

3. **Private Attributes**: Parameters are stored as instance attributes with leading underscores to indicate they are "private".

### Benefits

This approach provides several benefits:
- Maintains compatibility with the ADK's BaseAgent class
- Allows for explicit validation of inputs
- Follows Python conventions for private attributes
- Simplifies the code structure

For more details, see the [Pydantic Usage Guidelines](PYDANTIC_USAGE.md).
