# Direct Deployment Guide for Vertex AI Agent Engine

## Overview

This guide explains how to use the `direct_deploy.py` script, which is the recommended method for deploying your Google ADK agent to Vertex AI Agent Engine. This streamlined script simplifies the deployment process by handling environment setup, agent creation, deployment, and configuration updates in a single step.

## Prerequisites

Before using direct_deploy.py, ensure you have:

1. **Google Cloud Project**: An active Google Cloud project with the Vertex AI API enabled
2. **Storage Bucket**: A Google Cloud Storage bucket for staging deployment files
3. **Python Environment**: Python 3.9 or higher with required packages installed:
   ```bash
   pip install 'google-cloud-aiplatform[adk,agent_engines]' python-dotenv
   ```
4. **Authentication**: Proper authentication to Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

## Configuration

The script uses environment variables for configuration, which can be provided in a `.env` file or set directly in your environment:

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

## Usage

To deploy your agent, simply run:

```bash
python direct_deploy.py
```

## What the Script Does

The `direct_deploy.py` script performs the following steps:

1. **Environment Setup**:
   - Loads environment variables from `.env` file
   - Configures logging
   - Validates and formats configuration values

2. **Module Imports**:
   - Imports necessary Vertex AI and ADK modules
   - Imports the BaseAgent class from your project

3. **Vertex AI Initialization**:
   - Initializes Vertex AI with your project ID, region, and staging bucket

4. **Agent Creation**:
   - Creates a BaseAgent instance with default or configured parameters
   - Prepares the agent for Agent Engine deployment using ADK

5. **Local Testing**:
   - Tests the agent locally before deployment
   - Creates a test session and sends a test query
   - Validates that the agent responds correctly

6. **Deployment**:
   - Deploys the agent to Vertex AI Agent Engine
   - Includes your project's `src` directory in the deployment package
   - Captures the Agent Engine ID for future reference

7. **Remote Testing**:
   - Creates a test session on the deployed agent
   - Sends a test query to verify deployment success

8. **Configuration Update**:
   - Updates the `chat.py` script with the new Agent Engine ID
   - Creates a backup of the original file
   - Updates Project ID and Location if necessary

## Example Output

A successful deployment will produce output similar to:

```
2025-04-21 08:33:41,030 - direct_deploy - INFO - Using Project ID: risk-manager-457219
2025-04-21 08:33:41,030 - direct_deploy - INFO - Using Region: us-central1
2025-04-21 08:33:41,030 - direct_deploy - INFO - Using Staging Bucket: gs://risk7
...
2025-04-21 08:37:48,023 - direct_deploy - INFO - Agent deployed successfully to Agent Engine: 1578942677951447040
...
2025-04-21 08:37:52,590 - direct_deploy - INFO - Direct deployment completed successfully!
2025-04-21 08:37:52,590 - direct_deploy - INFO - Agent Engine ID: 1578942677951447040
2025-04-21 08:37:52,590 - direct_deploy - INFO - You can now interact with your agent using 'python chat.py'
```

## Using the Deployed Agent

After successful deployment, you can interact with your agent using the `chat.py` script:

```bash
python chat.py
```

The `chat.py` script is automatically updated with your new Agent Engine ID, so you don't need to make any manual changes.

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
pip install 'google-cloud-aiplatform[adk,agent_engines]' python-dotenv
```

#### Deployment Timeout

**Symptom**: The deployment appears to hang or takes extremely long.

**Solution**: 
1. Check your network connection
2. Verify the Vertex AI API is enabled in your project
3. Check Cloud Logging for detailed error messages

#### chat.py Not Found or Not Updated

**Symptom**: The script cannot find or update chat.py.

**Solution**: 
1. Create a basic chat.py file in the project root if it doesn't exist
2. Ensure you have write permissions to the file

## Comparison with Other Deployment Methods

| Feature | direct_deploy.py | deploy_agent_engine.py | redeploy.py |
|---------|-----------------|------------------------|-------------|
| Configuration Source | Environment variables | YAML configuration files | YAML and command line |
| Environment Support | Single environment | Multiple environments | Multiple environments |
| chat.py Update | Automatic | Manual | Automatic |
| Complexity | Low | Medium | Medium |
| Use Case | Quick deployments | Complex configuration | Redeployments with config |

## Best Practices

1. **Use Version Control**: Commit your deployment script to version control, but exclude .env files with sensitive information
2. **Create a Deployment User**: Create a dedicated service account for deployments with minimal permissions
3. **Verify After Deployment**: Always test your deployed agent with real queries before considering deployment complete
4. **Monitor Logs**: Check Cloud Logging after deployment for any warnings or errors
5. **Regular Backups**: Keep backups of your chat.py file (the script does this automatically)

---

*Document Version: 1.0*  
*Last Updated: April 21, 2025*  
*Author: [Your Name], CTO* 