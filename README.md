# Google ADK Agent Starter Kit

A robust, extensible starter kit for building AI agents with Google's Agent Development Kit (ADK), featuring true custom agent architecture.

![Google ADK](https://google.github.io/adk-docs/assets/images/adk-logo.png)

## Overview

This starter kit provides a standardized foundation for building AI agents using Google's Agent Development Kit (ADK). It implements a true custom agent architecture that inherits directly from Google's BaseAgent class and follows the recommended patterns for custom agent development. The kit includes reusable components, patterns, and examples that developers can use as templates for their own agent implementations.

### Key Features

- **True Custom Agent Architecture**: Inherits directly from Google's BaseAgent class and implements the required methods
- **LLM Integration**: Uses Google's Gemini models for natural language understanding and generation
- **Tool Integration**: Seamless integration with Google Search and custom tools
- **Flexible Orchestration**: Supports complex orchestration patterns like conditional logic and state management
- **Comprehensive Testing**: Includes unit tests for all components
- **Interactive Mode**: Supports interactive conversations with the agent
- **Detailed Documentation**: Comprehensive guidelines and best practices

## Getting Started

### Prerequisites

- Python 3.8+
- Google API key for Gemini models
- Google Cloud project (for Vertex AI deployment)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-organization/agent-starter-kit.git
cd agent-starter-kit
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Quick Start

#### Interactive Mode

Run the search agent in interactive mode:

```bash
python run.py run search --interactive
```

This will start an interactive session where you can chat with the agent.

#### Programmatic Use

Create a simple search agent:

```python
from src.agents.search_agent import SearchAgent

# Create a search agent
agent = SearchAgent(
    name="my_search_agent",
    description="My custom search agent",
    instruction="Answer questions using Google Search",
)

# Search for information
response = agent.search("What is the capital of France?")
print(response)
```

#### Creating a Custom Agent

To create a new agent, extend the `BaseAgent` class and implement the required methods:

```python
from src.agents.base_agent import BaseAgent
from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

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
        # ... other parameters
    ):
        super().__init__(
            name=name,
            model=model,
            description=description,
            instruction=instruction,
            # ... other parameters
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

## Project Structure

```
google-adk-agent-starter-kit/
├── README.md                 # Documentation and getting started guide
├── requirements.txt          # Dependencies
├── .env.example              # Template for environment variables
├── .env                      # Environment variables (not in version control)
├── setup.py                  # Package setup for distribution
├── run.py                    # CLI entry point
├── docs/                     # Documentation directory
│   ├── DOCUMENTATION_1.md    # Comprehensive documentation
│   ├── PLANNING_1.md         # Project architecture and design decisions
│   └── TASKS_1.md            # Implementation tasks and timeline
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration settings
│   ├── cli.py                # CLI implementation
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py     # True custom agent implementation
│   │   └── search_agent.py   # Example Google Search agent implementation
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
    ├── test_search_agent.py         # Tests for the search agent
    └── test_custom_tools.py         # Tests for custom tools
```

## Key Components

### BaseAgent

The `BaseAgent` class is the foundation of our agent architecture. It inherits directly from Google's `BaseAgent` class and implements the required methods for custom agent development.

Key features:
- Implements `_run_async_impl` for custom orchestration logic
- Manages sub-agents, including an LlmAgent for reasoning
- Handles session management and state
- Provides convenience methods for running the agent and getting responses
- Uses a hybrid approach for Pydantic with validation methods

### SearchAgent

The `SearchAgent` class extends `BaseAgent` to provide a specialized agent that can search the web using Google Search to answer questions.

Key features:
- Integrates with Google Search tool
- Implements custom orchestration logic for search queries
- Provides a convenient `search` method for direct use

### Custom Tools

The starter kit includes support for custom tools that can be used by agents to perform specific tasks.

Key features:
- Implements a `CustomTool` class for creating new tools
- Provides examples of custom tool implementation
- Includes unit tests for custom tools

## Running the Agent

### Interactive Mode

Run the agent in interactive mode:

```bash
python run.py run search --interactive
```

This will start an interactive session where you can chat with the agent.

### Deployment

#### Local Development

For local development and testing:

```bash
python run.py run search --port 8000
```

#### Vertex AI Deployment

For deploying to Vertex AI:

```bash
python run.py deploy search --project your-project-id --region us-central1
```

## Documentation

For more detailed documentation, see:

- [Comprehensive Documentation](docs/DOCUMENTATION_1.md) - Detailed guide to the starter kit
- [Planning Document](docs/PLANNING_1.md) - Project architecture and design decisions
- [Tasks Document](docs/TASKS_1.md) - Implementation tasks and timeline
- [Pydantic Usage Guidelines](docs/PYDANTIC_USAGE.md) - Guidelines for using Pydantic in agent classes
- [Test Report](docs/TEST_REPORT.md) - Test coverage and results
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-development-kit/overview) - Official ADK documentation

## Pydantic Usage

This project uses a hybrid approach for Pydantic integration in agent classes:

1. **Model Configuration**: All agent classes define `model_config = {"arbitrary_types_allowed": True}` to allow non-Pydantic types.

2. **Validation Methods**: Instead of using Pydantic fields directly, we use validation methods like `_validate_model()` and `_validate_tools()` to validate inputs.

3. **Private Attributes**: Parameters are stored as instance attributes with leading underscores to indicate they are "private".

This approach provides several benefits:
- Maintains compatibility with the ADK's BaseAgent class
- Allows for explicit validation of inputs
- Follows Python conventions for private attributes
- Simplifies the code structure

For more details, see the [Pydantic Usage Guidelines](docs/PYDANTIC_USAGE.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
