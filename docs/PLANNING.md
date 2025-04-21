# Google ADK Agent Starter Kit - Architecture & Planning

## Overview

This document outlines the architecture, design decisions, and roadmap for the Google ADK Agent Starter Kit. It serves as a consolidated reference for developers working on or with the project.

## Table of Contents

1. [Architecture](#architecture)
2. [Component Relationships](#component-relationships)
3. [Design Decisions](#design-decisions)
4. [Extension Points](#extension-points)
5. [Development Roadmap](#development-roadmap)
6. [Deployment Strategies](#deployment-strategies)

## Architecture

The Google ADK Agent Starter Kit follows a modular architecture designed for extensibility and maintainability. The key components of the architecture are:

### Core Components

1. **BaseAgent**: The foundational agent class that inherits from Google ADK's BaseAgent and implements custom orchestration logic.
2. **Tool System**: A framework for creating and using custom tools that agents can leverage.
3. **Registry**: A dynamic registry system for registering and retrieving agent types.
4. **Configuration**: Centralized configuration management supporting environment-specific settings.
5. **CLI**: Command-line interface for running and interacting with agents.

### Deployment Components

1. **Local Deployment**: Utilities for running agents locally with a web interface.
2. **Vertex AI Deployment**: Utilities for deploying agents to Vertex AI Agent Engine.

## Component Relationships

```
┌────────────┐         ┌─────────────┐         ┌────────────┐
│   CLI      │─────────▶   Registry  │─────────▶  BaseAgent │
└────────────┘         └─────────────┘         └────────────┘
                             │                        │
                             ▼                        ▼
                       ┌─────────────┐         ┌────────────┐
                       │  Config     │         │   Tools    │
                       └─────────────┘         └────────────┘
                             │                        │
                             ▼                        ▼
                       ┌─────────────┐         ┌────────────┐
                       │ Deployment  │◀────────▶   Session  │
                       └─────────────┘         └────────────┘
```

The CLI interfaces with the Registry to create agents of different types. The Registry instantiates the BaseAgent, which uses Tools and Config components. The Deployment system handles deploying agents locally or to Vertex AI. Session management is handled by both BaseAgent and Deployment components.

## Design Decisions

### 1. True Custom Agent Architecture

We've chosen to implement a true custom agent architecture by inheriting directly from Google's BaseAgent class, rather than using a higher-level abstraction. This gives us maximum flexibility and control over the agent's behavior.

### 2. Single BaseAgent with Dynamic Tools

Instead of creating separate agent classes for different functionality (e.g., SearchAgent), we've adopted a single BaseAgent class that can be configured with different tools. This simplifies the codebase and makes it easier to extend.

### 3. Pydantic Integration Approach

We've adopted a hybrid approach for Pydantic integration:

- Using `model_config = {"arbitrary_types_allowed": True}` to allow non-Pydantic types
- Implementing validation methods (`_validate_model()`, `_validate_tools()`) for explicit input validation
- Using private attributes (with leading underscores) to store parameters

This approach balances type safety with flexibility and compatibility with the ADK.

### 4. Environment-Specific Configuration

We've implemented a configuration system that supports environment-specific overrides (development, staging, production). This allows for different settings in different environments without changing the code.

### 5. Deployment Strategy

We've focused on Vertex AI Agent Engine as the primary deployment target, as it provides the most optimized environment for AI agents, including session management, scaling, and monitoring.

## Extension Points

The starter kit is designed to be extended in several ways:

### 1. Custom Agent Types

New agent types can be created by implementing a factory function and registering it with the Registry:

```python
from src.registry import register_agent_type
from src.agents.base_agent import BaseAgent

def _create_my_agent(**kwargs):
    # Create and configure the agent
    return BaseAgent(**kwargs, tools=[my_custom_tool])

# Register the agent type
register_agent_type("my_agent", _create_my_agent)
```

### 2. Custom Tools

New tools can be created using the CustomTool class or the create_custom_tool function:

```python
from src.tools.custom_tools import create_custom_tool

def get_weather(location: str, units: str = "metric") -> str:
    """Get the current weather for a location."""
    # Implementation...
    return f"The weather in {location} is sunny and 25°C."

weather_tool = create_custom_tool(get_weather)
```

### 3. Custom Deployment

New deployment methods can be added by implementing a deployment function in the deployment module.

## Development Roadmap

### Current Priorities

1. **Improve Deployment Experience**: Enhance the deployment process to make it more robust and user-friendly.
2. **Add More Examples**: Create more example agents to demonstrate different use cases.
3. **Enhance Documentation**: Expand and improve documentation, especially for new developers.

### Upcoming Features

1. **Agent Monitoring**: Add monitoring capabilities to track agent performance and usage.
2. **Multi-Agent Orchestration**: Add support for orchestrating multiple agents.
3. **Tool Library**: Expand the tool library with more useful tools.
4. **Web UI Improvements**: Enhance the web UI for better user experience.

## Deployment Strategies

### Development

For development, we recommend running the agent locally using the CLI's `run` command with the `--web` flag:

```bash
python run.py run base --web --port 8000
```

### Testing

Before deploying to production, we recommend deploying to a staging environment:

```bash
python deploy_agent_engine.py --environment staging --staging-bucket gs://your-staging-bucket
```

### Production

For production deployments, we recommend using the production environment configuration:

```bash
python deploy_agent_engine.py --environment production --staging-bucket gs://your-production-bucket
```

### Interacting with Deployed Agents

Deployed agents can be interacted with using the `chat.py` script, which uses the Vertex AI SDK:

```bash
python chat.py
```

---

*Document Version: 1.0*  
*Last Updated: April 22, 2025*  
*Author: CTO, AI Agents Company* 