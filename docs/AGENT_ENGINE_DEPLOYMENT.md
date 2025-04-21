# Vertex AI Agent Engine Deployment Guide

## Overview

This guide provides detailed instructions for deploying agents to Google Cloud's Vertex AI Agent Engine using our deployment infrastructure. Agent Engine is a fully managed service specifically designed for AI agents, offering advantages over traditional Vertex AI endpoints.

## Table of Contents

1. [Introduction to Agent Engine](#introduction-to-agent-engine)
2. [Prerequisites](#prerequisites)
3. [Deployment Infrastructure](#deployment-infrastructure)
4. [Deployment Methods](#deployment-methods)
5. [Managing Deployed Agents](#managing-deployed-agents)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Introduction to Agent Engine

Vertex AI Agent Engine is a fully managed Google Cloud service enabling developers to deploy, manage, and scale AI agents in production. Agent Engine handles the infrastructure to scale agents in production so you can focus on creating intelligent and impactful applications.

### Advantages over Traditional Vertex AI Endpoints

- **Built-in Session Management**: Agent Engine provides built-in session management for maintaining conversation state.
- **Automatic Scaling**: Agent Engine automatically scales based on demand.
- **Improved Monitoring and Tracing**: Agent Engine provides enhanced monitoring and tracing capabilities.
- **Optimized for Agent Workloads**: Agent Engine is specifically designed for agent workloads, providing better performance and reliability.

## Prerequisites

Before deploying to Agent Engine, ensure you have the following:

- Python 3.9 or higher (Agent Engine only supports Python >=3.9 and <=3.12)
- Google Cloud project with Vertex AI API enabled
- Google Cloud Storage bucket for staging
- Required Python packages installed:
  ```bash
  pip install 'google-cloud-aiplatform[adk,agent_engines]'
  ```
- Google Cloud SDK installed and configured
- Appropriate permissions:
  - Vertex AI User (roles/aiplatform.user) for your service account

## Deployment Infrastructure

Our deployment infrastructure includes the following components:

- **direct_deploy.py**: Streamlined script for direct deployment (recommended method)
- **deploy_agent_engine.py**: Configurable deployment script using deployment_config.yaml
- **redeploy.py**: Wrapper script that includes deployment and chat.py updates
- **deployment_config.yaml**: Base configuration file for deploy_agent_engine.py
- **environments/**: Directory containing environment-specific configurations for deploy_agent_engine.py
  - **development.yaml**: Development environment configuration
  - **staging.yaml**: Staging environment configuration
  - **production.yaml**: Production environment configuration

### Configuration Structure

The configuration files follow a hierarchical structure:

```yaml
# Environment Settings
environment: development

# Vertex AI Deployment Settings
vertex_ai:
  project_id: your-project-id
  region: us-central1
  machine_type: n1-standard-1
  min_replica_count: 1
  max_replica_count: 1

# Agent Settings
agent:
  type: search
  model: gemini-2.0-flash
  description: "Development search agent"
  instruction: "I can answer your questions by searching the internet. Just ask me anything!"
```

## Deployment Methods

### Method 1: Using direct_deploy.py (Recommended)

The simplest and most reliable deployment method uses the direct_deploy.py script, which:
- Reads configuration directly from environment variables
- Handles the entire deployment process in a single script
- Automatically updates chat.py with the new Agent Engine ID

```bash
python direct_deploy.py
```

This script:
1. Creates an agent instance based on environment variables
2. Tests the agent locally
3. Deploys the agent to Vertex AI Agent Engine
4. Updates chat.py with the new Agent Engine ID
5. Tests the deployed agent

You can configure the deployment by setting these environment variables (or using .env file):
- GOOGLE_CLOUD_PROJECT: Your Google Cloud project ID
- GOOGLE_CLOUD_REGION: Your Google Cloud region (default: us-central1)
- STAGING_BUCKET: Your Google Cloud Storage bucket for staging (with or without gs:// prefix)

### Method 2: Using deploy_agent_engine.py

For more configurable deployments, use the deploy_agent_engine.py script:

```bash
python deploy_agent_engine.py --environment development --staging-bucket gs://your-bucket-name
```

This will:
1. Load the configuration for the specified environment
2. Create an agent with the specified configuration
3. Test the agent locally
4. Deploy the agent to Vertex AI Agent Engine
5. Create a test session to verify the deployment

### Method 3: Using redeploy.py

For redeployment with automatic chat.py updates:

```bash
python redeploy.py --environment development --staging-bucket gs://your-bucket-name
```

This script:
1. Runs deploy_agent_engine.py with the specified parameters
2. Extracts the Agent Engine ID from the output
3. Updates chat.py with the new Agent Engine ID
4. Creates a backup of the original chat.py file

### Verify Deployment

All deployment methods verify deployment by creating a test session and sending a test query. If successful, you'll see output similar to:

```
Agent deployed successfully to Agent Engine: <agent_id>
Created remote test session: <session_id>
Received <n> events from remote agent
```

## Managing Deployed Agents

### Listing Deployed Agents

To list your deployed agents, you can use the Google Cloud Console or the `gcloud` command:

```bash
# Note: As of April 2025, the 'agent-engines' subcommand may not be available
# in all gcloud installations. Use the Python SDK or Cloud Console if available.
gcloud ai agent-engines list --region=us-central1
```

### Verifying Deployment Status

As of April 2025, the Google Cloud Console UI for Agent Engine is not yet available, and `gcloud` commands (`gcloud ai agent-engines` or `gcloud ai reasoning-engines`) may not work depending on your `gcloud` version and components.

The most reliable way to verify deployment status and interact with the agent is currently via the **Python SDK**:

```python
import vertexai
from vertexai import agent_engines

# Replace with your details
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
AGENT_ENGINE_ID = "your-agent-engine-id" 
AGENT_ENGINE_NAME = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}" # Note: Uses 'reasoningEngines' path

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    agent_engine = agent_engines.get(AGENT_ENGINE_NAME)
    print(f"Successfully connected to agent engine: {AGENT_ENGINE_NAME}")
    # You can now use agent_engine.create_session(), agent_engine.stream_query(), etc.
except Exception as e:
    print(f"Failed to connect to agent engine: {e}")

```
*(See `chat.py` in the project root for a full interaction example)*

### Deleting Deployed Agents

To delete a deployed agent, you can use the Python SDK (as the Console UI may not be available):

```python
from vertexai import agent_engines

# Get the remote app
remote_app = agent_engines.get(name="<agent_id>")

# Delete the agent
remote_app.delete(force=True)
```

The `force=True` parameter will also delete any child resources that were generated from the deployed agent, such as sessions.

## Monitoring and Logging

### Cloud Logging

Agent Engine logs are available in Cloud Logging. You can view them in the Google Cloud Console or using the `gcloud` command:

```bash
# Note: Use ReasoningEngine as the resource type based on observed logs (April 2025)
# Enclose the filter in single quotes for shell compatibility
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND resource.labels.reasoning_engine_id="<agent_id>"' --project=<your-project-id> --format=json --limit=50
```

### Cloud Monitoring

Agent Engine metrics are available in Cloud Monitoring. You can create custom dashboards and alerts based on these metrics.

## Troubleshooting

### Common Issues

#### Authentication Errors

**Symptom**: Error message about authentication failure.

**Solution**:
1. Ensure you're authenticated with the Google Cloud SDK:
   ```bash
   gcloud auth application-default login
   ```
2. Verify that your service account has the necessary permissions.

#### Missing Dependencies

**Symptom**: Error message about missing dependencies.

**Solution**:
1. Install the required dependencies:
   ```bash
   pip install 'google-cloud-aiplatform[adk,agent_engines]'
   ```

#### Deployment Failures

**Symptom**: Error message about deployment failure.

**Solution**:
1. Check the error message for specific details.
2. Verify that your Google Cloud project has the necessary APIs enabled.
3. Ensure your service account has the necessary permissions.
4. Check that your staging bucket exists and is accessible.

#### ModuleNotFoundError during Deployment

**Symptom**: Deployment fails with a 500 error. Cloud Logs show `ModuleNotFoundError: No module named 'src'` (or similar for other project directories).

**Cause**: The deployment process packages the agent object (`.pkl`) but doesn't automatically include local source code directories needed for the agent to be deserialized and run in the Agent Engine environment.

**Solution**:
1. Locate the `agent_engines.create(...)` call in your deployment script (e.g., `deploy_agent_engine.py`).
2. Add the `extra_packages` parameter, listing the relative paths to the required source directories. For this project structure, include the `src` directory:
   ```python
   remote_app = agent_engines.create(
       agent_engine=agent,
       requirements=[...],
       # Include the 'src' directory in the deployment package
       extra_packages=['./src'] 
   )
   ```
3. Re-run the deployment script.

## Best Practices

### Configuration Management

1. **Use Environment Variables for Direct Deployment**: For simple deployments, use environment variables with direct_deploy.py.
2. **Use Environment-Specific Configurations**: For complex scenarios, create separate configuration files for development, staging, and production environments.
3. **Store Sensitive Information Securely**: Use environment variables or secret management services for sensitive information.
4. **Version Control Configurations**: Store configuration files in version control, but exclude sensitive information.

### Deployment Strategy

1. **Test Locally First**: Always test your agent locally before deploying to Agent Engine.
2. **Use Staging Environment**: Deploy to a staging environment before deploying to production.
3. **Automate Deployments**: Use CI/CD pipelines to automate deployments.
4. **Monitor Deployments**: Set up monitoring and alerts for your deployed agents.

### Resource Management

1. **Clean Up Unused Resources**: Delete unused agents and sessions to avoid unnecessary costs.
2. **Set Resource Limits**: Configure appropriate resource limits for your agents.
3. **Monitor Resource Usage**: Regularly monitor resource usage to optimize costs.

---

*Document Version: 1.2*  
*Last Updated: April 21, 2025*  
*Author: [Your Name], CTO*
