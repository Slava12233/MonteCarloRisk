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

Run the base agent in interactive mode:

```bash
python run.py run base --interactive
```

This will start an interactive session where you can chat with the agent.

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
MonteCarloRisk_AI/
├── README.md                 # Documentation and getting started guide
├── requirements.txt          # Dependencies for the project
├── .env.example              # Template for environment variables
├── .env                      # Environment variables (not in version control)
├── setup.py                  # Package setup for distribution
├── run.py                    # CLI entry point
├── chat.py                   # Script to interact with deployed agent via SDK
├── direct_deploy.py          # Streamlined script for direct deployment (recommended)
├── TASK.md                   # Current and completed tasks
├── commands.txt              # Useful commands for reference
├── pytest.ini                # Configuration for pytest
├── docs/
│   ├── DOCUMENTATION_1.md    # Comprehensive documentation
│   ├── DIRECT_DEPLOY.md      # Guide for direct deployment (recommended)
│   ├── PYDANTIC_USAGE.md     # Guidelines for using Pydantic
│   ├── AGENT_ENGINE_DEPLOYMENT.md # Guide for Agent Engine deployment
│   ├── project_visualization.html # Project structure visualization
│   ├── project_visualization.md   # Project structure in markdown
│   ├── PLANNING.md           # Architecture and design decisions
│   ├── ACTION_ITEMS.md       # Action items and improvements
│   └── index.md              # Documentation index
├── backup/                   # Backup files (ignored by git)
├── environments/             # Environment-specific configurations
│   ├── development.yaml      # Development environment configuration
│   ├── staging.yaml          # Staging environment configuration
│   └── production.yaml       # Production environment configuration
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

> Note: Some additional files like .git/, .coverage, .pytest_cache/, and venv/ are excluded from this structure as they are generated files or directories.

## Key Components

### BaseAgent

The `BaseAgent` class is the foundation of our agent architecture. It inherits directly from Google's `BaseAgent` class and implements the required methods for custom agent development.

Key features:
- Implements `_run_async_impl` for custom orchestration logic
- Manages sub-agents, including an LlmAgent for reasoning
- Handles session management and state
- Provides convenience methods for running the agent and getting responses
- Uses a hybrid approach for Pydantic with validation methods

### Custom Tools

The starter kit includes support for custom tools that can be used by agents to perform specific tasks.

Key features:
- Implements a `CustomTool` class for creating new tools
- Provides examples of custom tool implementation
- Includes unit tests for custom tools

## Running the Agent

### Interactive Mode

Run the base agent in interactive mode:

```bash
python run.py run base --interactive
```

This will start an interactive session where you can chat with the agent.

### Deployment

#### Local Development Web UI

For local development and testing with a web interface:

```bash
# Ensure GOOGLE_API_KEY or DEV_MODE=TRUE is set in your environment/.env
python run.py run base --web --port 8000
```
Access the interface at `http://localhost:8000`. 

**Key Web UI Features:**
- Chat-like interface with message history
- Real-time streaming responses 
- Session management (create new sessions or view history of past sessions)
- Accessing session history via `/api/sessions/{user_id}` and `/api/sessions/{user_id}/{session_id}/history` endpoints
- WebSocket-based streaming for responsive experience

If the page shows ERR_EMPTY_RESPONSE despite the server starting, check browser developer console for errors and ensure ports are not blocked by firewall.

#### Vertex AI Agent Engine Deployment

For deploying to Vertex AI Agent Engine:

##### Using direct_deploy.py (Recommended Method)

The simplest and most reliable deployment method:

```bash
# Ensure your .env file has GOOGLE_CLOUD_PROJECT and STAGING_BUCKET set
python direct_deploy.py
```

This streamlined script:
- Reads configuration from environment variables
- Creates and tests the agent locally
- Deploys to Vertex AI Agent Engine
- Automatically updates chat.py with the new Agent Engine ID
- Creates a backup of the original chat.py file

See `docs/DIRECT_DEPLOY.md` for full details and environment variable configuration.

##### Using deploy_agent_engine.py (Alternative Method)

For deployments with complex configuration requirements:

```bash
# Ensure environments/your_env.yaml is configured with project_id, etc.
# Ensure you have run 'gcloud auth application-default login'
python deploy_agent_engine.py --environment <your_env> --staging-bucket gs://your-bucket-name
```

For redeploying after making changes to the codebase, you can use the automated redeployment script:

```bash
# This script handles both deployment and updating chat.py with the new Agent Engine ID
python redeploy.py --environment <your_env>
```

The deployment scripts read configuration values from your `.env` file:
- `GOOGLE_CLOUD_PROJECT`
- `STAGING_BUCKET`
- `GOOGLE_CLOUD_REGION`

You can also override these values with command-line arguments.

See `docs/AGENT_ENGINE_DEPLOYMENT.md` for full details and troubleshooting.

#### Interacting with Deployed Agent

Use the `chat.py` script to interact with the agent deployed on Vertex AI Agent Engine via the Python SDK:

```bash
# The direct_deploy.py and redeploy.py scripts automatically update chat.py
python chat.py
```

## Documentation

For more detailed documentation, see:

- [Documentation Index](docs/index.md) - Central index of all documentation resources.
- [User Guide](docs/USER_GUIDE.md) - Comprehensive guide comparing local development vs. deployment options.
- [Direct Deployment Guide](docs/DIRECT_DEPLOY.md) - Guide for the recommended deployment method.
- [Agent Engine Deployment Guide](docs/AGENT_ENGINE_DEPLOYMENT.md) - Comprehensive guide for Vertex AI Agent Engine deployment.
- [Planning Document](docs/PLANNING.md) - Project architecture and design decisions.
- [Task List](TASK.md) - Current and completed tasks.
- [Pydantic Usage Guidelines](docs/PYDANTIC_USAGE.md) - Guidelines for using Pydantic in agent classes.
- [Test Report](docs/test_report.md) - Comprehensive test coverage report with 100% coverage.
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-development-kit/overview) - Official ADK documentation.
- [Action Items](docs/ACTION_ITEMS.md) - Action items and improvements for the project.
*(Other files in `docs/` may contain historical or specific reports)*

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