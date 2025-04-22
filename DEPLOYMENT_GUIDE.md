# Vertex AI Agent Engine Deployment Guide

This guide provides comprehensive instructions for deploying and managing agents on Google's Vertex AI Agent Engine.

## Overview

This project includes two complementary deployment tools:

1. **SDK-based Agent Management (`sdk_agent_deploy.py`)** - For managing deployed agents (list, create, test, delete)
2. **Direct Deployment (`direct_deploy.py`)** - For deploying a specific BaseAgent implementation to Agent Engine

## Prerequisites

Before deployment, ensure you have:

1. **Google Cloud Project**: An active Google Cloud project with the Vertex AI API enabled
2. **Storage Bucket**: A Google Cloud Storage bucket for staging deployment files
3. **Python Environment**: Python 3.9 or higher with required packages installed:
   ```bash
   pip install google-cloud-storage
   pip install 'google-cloud-aiplatform[adk,agent_engines]' python-dotenv
   ```
4. **Authentication**: Proper authentication to Google Cloud:
   ```bash
   gcloud auth application-default login
   ```
5. **API Enabled**: Ensure the Vertex AI API is enabled:
   ```bash
   gcloud services enable aiplatform.googleapis.com --project=your-project-id
   ```

## SDK-based Agent Management (Recommended)

The `sdk_agent_deploy.py` tool provides a comprehensive approach to managing agents throughout their lifecycle.

### Features

The SDK-based tool automatically:
1. Creates and uses a staging bucket for deployment
2. Handles different API versions and endpoints
3. Provides multiple fallback methods for deploying agents
4. Includes better error handling with descriptive messages
5. Properly displays agent details in the list command

### Usage

#### List existing agents

View all deployed agents in your project:

```bash
python sdk_agent_deploy.py list --project-id your-project-id
```

#### Deploy a new test agent

Deploy a sample agent with weather and time tools:

```bash
python sdk_agent_deploy.py deploy --name your_agent_name --project-id your-project-id
```

#### Test a specific agent

Test an existing agent by ID:

```bash
python sdk_agent_deploy.py test --agent-id <AGENT_ID> --project-id your-project-id
```

#### Delete an agent

Remove an agent when no longer needed:

```bash
python sdk_agent_deploy.py delete --agent-id <AGENT_ID> --project-id your-project-id
```

## Direct Deployment

The `direct_deploy.py` script provides a streamlined approach for deploying the built-in BaseAgent implementation.

### Configuration

The direct deployment script uses environment variables for configuration, which can be provided in a `.env` file or set directly in your environment:

```
# Required variables
GOOGLE_CLOUD_PROJECT=your-project-id
STAGING_BUCKET=your-bucket-name

# Optional variables (defaults shown)
GOOGLE_CLOUD_REGION=us-central1
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| GOOGLE_CLOUD_PROJECT | Your Google Cloud Project ID | None | Yes |
| STAGING_BUCKET | GCS bucket for staging (with or without gs:// prefix) | None | Yes |
| GOOGLE_CLOUD_REGION | Google Cloud region for deployment | us-central1 | No |

### Usage

To deploy your agent, simply run:

```bash
python direct_deploy.py
```

### What the Script Does

The `direct_deploy.py` script performs the following steps:

1. **Environment Setup**: Loads environment variables and configures logging
2. **Module Imports**: Imports necessary Vertex AI and ADK modules
3. **Vertex AI Initialization**: Initializes Vertex AI with your project settings
4. **Agent Creation**: Creates a BaseAgent instance with default parameters
5. **Local Testing**: Tests the agent locally before deployment
6. **Deployment**: Deploys the agent to Vertex AI Agent Engine
7. **Remote Testing**: Tests the deployed agent to verify success
8. **Configuration Update**: Updates the `chat.py` script with the new Agent Engine ID

## Deployment Flow

A typical deployment workflow includes:

1. First, list existing agents to see what's already deployed:
   ```bash
   python sdk_agent_deploy.py list --project-id your-project-id
   ```

2. Deploy a new agent (choose one method):
   - Using SDK-based deployment with custom tools:
     ```bash
     python sdk_agent_deploy.py deploy --name your_agent_name --project-id your-project-id
     ```
   - Using direct deployment with the built-in BaseAgent:
     ```bash
     python direct_deploy.py
     ```

3. Test the deployed agent:
   ```bash
   python sdk_agent_deploy.py test --agent-id <AGENT_ID> --project-id your-project-id
   ```

4. When no longer needed, delete the agent:
   ```bash
   python sdk_agent_deploy.py delete --agent-id <AGENT_ID> --project-id your-project-id
   ```

## Using the Deployed Agent

After successful deployment, you can interact with your agent using the `chat.py` script:

```bash
python chat.py
```

The `chat.py` script is automatically updated by the direct deployment script with your new Agent Engine ID.

## Troubleshooting

### Common Issues

#### Authentication Errors

**Symptom**: Error messages about missing authentication or permissions.

**Solution**:
1. Run `gcloud auth application-default login`
2. Verify your user account has the Vertex AI User role (roles/aiplatform.user)

#### Missing Dependencies

**Symptom**: Module import errors.

**Solution**:
```bash
pip install google-cloud-storage
pip install 'google-cloud-aiplatform[adk,agent_engines]' python-dotenv
```

#### Deployment Timeout

**Symptom**: The deployment appears to hang or takes extremely long.

**Solution**: 
1. Check your network connection
2. Verify the Vertex AI API is enabled in your project
3. Check Cloud Logging for detailed error messages

#### API Endpoint Errors (404)

**Symptom**: The SDK-based tool receives 404 errors when trying to list or manage agents.

**Solution**:
1. Ensure the Vertex AI API is enabled
2. Check if you have any agents deployed yet
3. Verify you have the correct permissions

## Best Practices

1. **Use Version Control**: Commit your deployment scripts to version control, but exclude .env files with sensitive information
2. **Create a Deployment User**: Create a dedicated service account for deployments with minimal permissions
3. **Verify After Deployment**: Always test your deployed agent with real queries before considering deployment complete
4. **Monitor Logs**: Check Cloud Logging after deployment for any warnings or errors
5. **Regular Backups**: Keep backups of your configuration files

## File Organization

- Root directory launchers:
  - `sdk_agent_deploy.py`: Launcher for SDK-based agent management
  - `direct_deploy.py`: Launcher for direct agent deployment
  
- Implementation files:
  - `src/deployment/sdk_agent_deploy.py`: Main implementation of SDK-based tools
  - `src/deployment/direct_deploy.py`: Implementation of direct deployment
  - `src/deployment/local.py`: Local deployment for testing

---

*Document Version: 1.0*  
*Last Updated: April 22, 2025*  
*Author: MonteCarloRisk_AI Team* 