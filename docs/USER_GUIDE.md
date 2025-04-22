# User Guide: Local Development vs Deployment Options

## Introduction

This guide provides clear instructions for both local development and deployment of agents built with the Google ADK Agent Starter Kit. It's designed to help you understand when to use each option and how to get started quickly.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Local Development](#local-development)
   - [Running in Interactive Mode](#running-in-interactive-mode)
   - [Running with Web UI](#running-with-web-ui)
   - [Developing Custom Agents](#developing-custom-agents)
3. [Deployment Options](#deployment-options)
   - [Option 1: SDK-based Agent Management (Recommended)](#option-1-sdk-based-agent-management-recommended)
   - [Option 2: Direct Deployment](#option-2-direct-deployment)
4. [Interacting with Deployed Agents](#interacting-with-deployed-agents)
5. [Comparison of Options](#comparison-of-options)
6. [Troubleshooting](#troubleshooting)

## Environment Setup

### Prerequisites

- Python 3.8+ installed
- Google Cloud account (for deployments)
- Google API Key (for Gemini models)
- Google Cloud project with Vertex AI API enabled (for deployments)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/google-adk-agent-starter-kit.git
   cd google-adk-agent-starter-kit
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file:
   ```
   # Required for all uses
   GOOGLE_API_KEY=your-api-key
   DEFAULT_MODEL=gemini-2.0-flash
   
   # Required for deployment
   GOOGLE_CLOUD_PROJECT=your-project-id
   STAGING_BUCKET=your-bucket-name
   GOOGLE_CLOUD_REGION=us-central1
   ```

## Local Development

Local development is ideal for:
- Rapid prototyping and testing
- Developing and debugging custom agents
- Testing with different tools and configurations
- Demoing agent capabilities without cloud deployment

### Running in Interactive Mode

Interactive mode allows you to have a conversation with your agent via the command line:

```bash
python run.py run base --interactive
```

This will start an interactive terminal session. Type your query and press Enter to get a response. Type `exit` or `quit` to end the session.

Example:
```
$ python run.py run base --interactive
Welcome to the Interactive Mode with base_agent
Type 'exit' or 'quit' to end the session.

You: What is the capital of France?
Agent: The capital of France is Paris.

You: exit
Goodbye!
```

### Running with Web UI

The Web UI provides a more user-friendly interface with chat history:

```bash
python run.py run base --web --port 8000
```

This starts a local web server. Open `http://localhost:8000` in your browser to interact with the agent.

Key features of the Web UI:
- Chat-like interface with message history
- Real-time streaming responses
- Ability to view session history
- Multiple sessions support

### Developing Custom Agents

1. Create a new agent by extending `BaseAgent` or using the registry:

   ```python
   # Option 1: Create a custom agent class
   from src.agents.base_agent import BaseAgent
   
   class MyCustomAgent(BaseAgent):
       def __init__(self, name="my_custom_agent", **kwargs):
           super().__init__(name=name, **kwargs)
           # Custom initialization code
   
   # Option 2: Register a factory function
   from src.registry import register_agent_type
   
   def _create_custom_agent(**kwargs):
       return BaseAgent(
           name=kwargs.get('name', 'custom_agent'),
           description="My custom agent",
           tools=[custom_tool1, custom_tool2],
           **kwargs
       )
   
   register_agent_type("custom", _create_custom_agent)
   ```

2. Run your custom agent:
   ```bash
   # If registered with the registry
   python run.py run custom --interactive
   
   # Or programmatically
   from src.agents.my_custom_agent import MyCustomAgent
   
   agent = MyCustomAgent()
   response = agent.run_and_get_response(
       user_id="user1",
       session_id="session1",
       message="Hello, agent!"
   )
   print(response)
   ```

## Deployment Options

We offer two deployment approaches for running your agents in production on Google Cloud's Vertex AI Agent Engine. For comprehensive details, refer to our [unified deployment guide](../DEPLOYMENT_GUIDE.md).

### Option 1: SDK-based Agent Management (Recommended)

The most flexible approach for managing agents throughout their lifecycle:

```bash
# List existing agents
python sdk_agent_deploy.py list --project-id your-project-id

# Deploy a new test agent
python sdk_agent_deploy.py deploy --name your_agent_name --project-id your-project-id

# Test a deployed agent
python sdk_agent_deploy.py test --agent-id <AGENT_ID> --project-id your-project-id 
```

**Benefits:**
- Complete control over agent lifecycle (list, create, test, delete)
- Easy management of multiple agents
- Robust error handling and diagnostics
- Support for different agent configurations

### Option 2: Direct Deployment

For quickly deploying the built-in BaseAgent implementation:

```bash
python direct_deploy.py
```

**Benefits:**
- Streamlined deployment process with minimal configuration
- Reads settings directly from `.env` file
- Automatically tests the agent before deployment
- Updates `chat.py` with the new Agent Engine ID
- Creates a backup of the original configuration

Refer to our [unified deployment guide](../DEPLOYMENT_GUIDE.md) for complete details on both deployment options, including prerequisites, configuration, and troubleshooting.

## Interacting with Deployed Agents

After deployment, interact with your agent using `chat.py`:

```bash
python chat.py
```

This script:
- Connects to your deployed agent using the Vertex AI SDK
- Provides an interactive terminal interface
- Handles streaming responses
- Maintains conversation context

## Comparison of Options

| Feature | Local Interactive | Local Web UI | Direct Deployment | Configurable Deployment |
|---------|------------------|--------------|-------------------|-------------------------|
| **Setup Complexity** | Low | Low | Medium | High |
| **Use Case** | Quick testing | Development/Demos | Production (simple) | Production (complex) |
| **Infrastructure** | None | Local server | Vertex AI | Vertex AI |
| **Persistence** | Session only | Multiple sessions | Persistent | Persistent |
| **Scaling** | No | Limited | Automatic | Automatic |
| **Cost** | Free | Free | Pay-per-use | Pay-per-use |
| **Monitoring** | Limited | Limited | Cloud Logging | Cloud Logging |

## Troubleshooting

### Local Development Issues

**Web UI not loading:**
- Check if the port is in use (`netstat -an | findstr 8000`)
- Verify the server is running (check terminal output)
- Try a different port (`python run.py run base --web --port 8001`)

**API Key errors:**
- Ensure `GOOGLE_API_KEY` is set correctly in `.env`
- Verify the API key has access to Gemini models

### Deployment Issues

**Authentication errors:**
- Run `gcloud auth application-default login`
- Ensure your account has the necessary permissions

**Deployment failures:**
- Check that Vertex AI API is enabled in your project
- Verify your Cloud Storage bucket exists and is accessible
- Check Cloud Logging for detailed error messages

**Agent not responding:**
- Verify the agent was deployed successfully
- Check the Agent Engine ID in `chat.py`
- Ensure your project has quota for Vertex AI Agent Engine

For more detailed troubleshooting, refer to the [Deployment Guide](../DEPLOYMENT_GUIDE.md).

---

This guide covers the essentials for both local development and deployment options. For more detailed information, refer to the specific documentation files referenced throughout this guide. 