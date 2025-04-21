# Deployment Guide for Google ADK Agent Starter Kit

This guide provides instructions for deploying the Google ADK Agent Starter Kit to various environments.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Deployment Script](#deployment-script)
5. [Deployment Options](#deployment-options)
6. [Continuous Integration/Continuous Deployment (CI/CD)](#continuous-integrationcontinuous-deployment-cicd)
7. [Troubleshooting](#troubleshooting)

## Overview

The deployment process for the Google ADK Agent Starter Kit involves the following steps:

1. Configure the deployment settings in `deployment_config.yaml`
2. Run the deployment script `deploy.py`
3. Verify the deployment

## Prerequisites

Before deploying, ensure you have the following:

- Python 3.8 or higher
- Google API key for Gemini models
- Google Cloud project (for Vertex AI deployment)
- Required Python packages installed (`pip install -r requirements.txt`)
- For Vertex AI deployment:
  - Google Cloud SDK installed and configured
  - Appropriate permissions to deploy to Vertex AI

## Configuration

The deployment configuration is stored in `deployment_config.yaml` as the base configuration. Environment-specific configurations are stored in the `environments/` directory.

### Configuration Files

- **deployment_config.yaml**: Base configuration with default settings
- **environments/development.yaml**: Development environment configuration
- **environments/staging.yaml**: Staging environment configuration
- **environments/production.yaml**: Production environment configuration

When you specify an environment using the `--environment` flag, the deployment script will load the base configuration and then merge it with the environment-specific configuration, with the environment-specific settings taking precedence.

### Configuration Sections

- **Environment Settings**: Specifies the deployment environment (development, staging, production)
- **Vertex AI Deployment Settings**: Settings for deploying to Vertex AI
- **Local Deployment Settings**: Settings for local deployment
- **Agent Settings**: Configuration for the agent being deployed
- **Monitoring Settings**: Settings for logging, tracing, and metrics
- **Security Settings**: Security-related configuration
- **Deployment Steps**: Steps to execute during deployment

### Example Base Configuration

```yaml
# Environment Settings
environment: production  # Options: development, staging, production

# Vertex AI Deployment Settings
vertex_ai:
  project_id: your-project-id
  region: us-central1
  machine_type: n1-standard-2
  min_replica_count: 1
  max_replica_count: 5

# Agent Settings
agent:
  type: search
  model: gemini-2.0-flash
  description: "Production search agent"
```

### Example Environment-Specific Configuration

```yaml
# Development Environment Configuration
environment: development

# Vertex AI Deployment Settings
vertex_ai:
  project_id: your-dev-project-id
  machine_type: n1-standard-1
  min_replica_count: 1
  max_replica_count: 1

# Local Deployment Settings
local:
  host: 127.0.0.1
  port: 8000
  log_level: debug
  reload: true
```

### Environment-Specific Deployment

To deploy using an environment-specific configuration:

```bash
python deploy.py --environment development
```

This will:
1. Load the base configuration from `deployment_config.yaml`
2. Load the environment-specific configuration from `environments/development.yaml`
3. Merge the configurations, with environment-specific settings taking precedence
4. Deploy using the merged configuration

## Deployment Script

The `deploy.py` script automates the deployment process using the configuration in `deployment_config.yaml`.

### Usage

```bash
# Deploy using the default configuration
python deploy.py

# Deploy to a specific environment
python deploy.py --environment production

# Deploy locally only
python deploy.py --local

# Deploy to Vertex AI only
python deploy.py --vertex

# Run deployment steps only
python deploy.py --steps

# Use a custom configuration file
python deploy.py --config custom_config.yaml
```

### Command-Line Arguments

- `--config`: Path to the deployment configuration file (default: `deployment_config.yaml`)
- `--environment`: Deployment environment (choices: `development`, `staging`, `production`)
- `--local`: Deploy locally
- `--vertex`: Deploy to Vertex AI
- `--steps`: Run deployment steps

## Deployment Options

### Local Deployment

Local deployment runs the agent on your local machine with a web interface.

```bash
python deploy.py --local
```

This will:
1. Start a web server on the configured host and port
2. Run the agent with the specified configuration
3. Provide a web interface for interacting with the agent

### Vertex AI Deployment

Vertex AI deployment deploys the agent to Google Cloud's Vertex AI platform.

```bash
python deploy.py --vertex
```

This will:
1. Build a deployment package
2. Upload the package to Vertex AI
3. Deploy the agent as a Vertex AI endpoint
4. Configure the endpoint with the specified settings

## Continuous Integration/Continuous Deployment (CI/CD)

You can integrate the deployment script into your CI/CD pipeline to automate deployments.

### GitHub Actions Example

```yaml
name: Deploy to Vertex AI

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest
    - name: Deploy to Vertex AI
      run: |
        python deploy.py --vertex --environment production
      env:
        GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}
```

## Troubleshooting

### Common Issues

#### Deployment Script Errors

- **Configuration file not found**: Ensure `deployment_config.yaml` exists in the current directory or specify the correct path with `--config`.
- **Invalid YAML**: Check the syntax of your configuration file.
- **Missing required configuration**: Ensure all required configuration values are set.

#### Local Deployment Issues

- **Port already in use**: Change the port in the configuration file.
- **Permission denied**: Ensure you have permission to bind to the specified port.

#### Vertex AI Deployment Issues

- **Authentication errors**: Ensure you have the correct credentials and permissions.
- **Project not found**: Verify the project ID in the configuration file.
- **Region not available**: Ensure the specified region is available for Vertex AI.
- **Quota exceeded**: Check your Vertex AI quotas.

### Logs

The deployment script logs information to the console. For more detailed logs, check:

- Local deployment: Check the console output and logs directory
- Vertex AI deployment: Check the Google Cloud Console and Cloud Logging

## Additional Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-development-kit/overview)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/) (for local deployment)
