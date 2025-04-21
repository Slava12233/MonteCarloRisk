#!/usr/bin/env python
"""
Deployment script for Google ADK Agent Starter Kit using Vertex AI Agent Engine.

This script deploys an agent to Vertex AI Agent Engine using the approach from the official documentation.
"""

import os
import sys
import argparse
import yaml
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("deploy_agent_engine")

def load_config(config_path: str = "deployment_config.yaml", environment: str = None) -> Dict[str, Any]:
    """
    Load the deployment configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file.
        environment: Optional environment name to load environment-specific configuration.
        
    Returns:
        The configuration as a dictionary.
        
    Raises:
        FileNotFoundError: If the configuration file is not found.
        yaml.YAMLError: If the configuration file is not valid YAML.
    """
    try:
        # Load the base configuration
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded base configuration from {config_path}")
        
        # Load environment-specific configuration if specified
        if environment:
            env_config_path = f"environments/{environment}.yaml"
            try:
                with open(env_config_path, "r") as f:
                    env_config = yaml.safe_load(f)
                logger.info(f"Loaded environment-specific configuration from {env_config_path}")
                
                # Merge environment-specific configuration with base configuration
                # Environment-specific configuration takes precedence
                config = deep_merge(config, env_config)
                logger.info(f"Merged configuration for environment: {environment}")
            except FileNotFoundError:
                logger.warning(f"Environment-specific configuration not found: {env_config_path}")
        
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with values from override taking precedence.
    
    Args:
        base: The base dictionary.
        override: The dictionary to override values in the base dictionary.
        
    Returns:
        The merged dictionary.
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, recursively merge them
            result[key] = deep_merge(result[key], value)
        else:
            # Otherwise, override the value
            result[key] = value
    
    return result

def deploy_to_agent_engine(
    config: Dict[str, Any],
    staging_bucket: Optional[str] = None,
) -> int:
    """
    Deploy the agent to Vertex AI Agent Engine.
    
    Args:
        config: The deployment configuration.
        staging_bucket: Optional Google Cloud Storage bucket for staging.
        
    Returns:
        0 if successful, non-zero otherwise.
    """
    logger.info("Starting deployment to Vertex AI Agent Engine")
    
    try:
        # Import the necessary modules
        import vertexai
        from vertexai import agent_engines
        from vertexai.preview import reasoning_engines
        from src.agents.search_agent import SearchAgent
        
        # Get Vertex AI configuration
        vertex_ai_config = config.get("vertex_ai", {})
        project_id = vertex_ai_config.get("project_id")
        region = vertex_ai_config.get("region")
        
        if not project_id or project_id == "your-project-id":
            logger.error("Project ID not configured. Please set vertex_ai.project_id in deployment_config.yaml")
            return 1
        
        # Get agent configuration
        agent_config = config.get("agent", {})
        agent_type = agent_config.get("type", "search")
        model = agent_config.get("model", "gemini-2.0-flash")
        description = agent_config.get("description", "Agent to answer questions using Google Search.")
        instruction = agent_config.get("instruction", "I can answer your questions by searching the internet. Just ask me anything!")
        
        # Initialize Vertex AI
        logger.info(f"Initializing Vertex AI with project {project_id} in region {region}")
        vertexai.init(
            project=project_id,
            location=region,
            staging_bucket=staging_bucket,
        )
        
        # Create the agent
        logger.info(f"Creating {agent_type} agent with model {model}")
        agent = SearchAgent(
            name=f"{agent_type}_agent",
            model=model,
            description=description,
            instruction=instruction,
        )
        
        # Prepare the agent for Agent Engine
        logger.info("Preparing agent for Agent Engine")
        app = reasoning_engines.AdkApp(
            agent=agent,
            enable_tracing=True,
        )
        
        # Try the agent locally before deploying
        logger.info("Testing agent locally before deployment")
        try:
            session = app.create_session(user_id="test_user")
            logger.info(f"Created local test session: {session.id}")
            
            # Send a test query
            logger.info("Sending test query to local agent")
            events = list(app.stream_query(
                user_id="test_user",
                session_id=session.id,
                message="Hello, can you help me?",
            ))
            logger.info(f"Received {len(events)} events from local agent")
        except Exception as e:
            logger.warning(f"Local agent test failed: {e}")
            logger.warning("Continuing with deployment anyway")
        
        # Deploy to Agent Engine
        logger.info("Deploying agent to Vertex AI Agent Engine")
        remote_app = agent_engines.create(
            agent_engine=agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]"
            ]
        )
        
        logger.info(f"Agent deployed successfully to Agent Engine: {remote_app}")
        
        # Create a test session on the remote agent
        logger.info("Creating test session on remote agent")
        try:
            remote_session = remote_app.create_session(user_id="test_user_remote")
            logger.info(f"Created remote test session: {remote_session['id']}")
            
            # Send a test query
            logger.info("Sending test query to remote agent")
            events = list(remote_app.stream_query(
                user_id="test_user_remote",
                session_id=remote_session["id"],
                message="Hello, can you help me?",
            ))
            logger.info(f"Received {len(events)} events from remote agent")
        except Exception as e:
            logger.warning(f"Remote agent test failed: {e}")
            logger.warning("Deployment may not be fully functional")
        
        logger.info("Agent Engine deployment completed successfully")
        return 0
    
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Make sure google-cloud-aiplatform[adk,agent_engines] is installed: pip install 'google-cloud-aiplatform[adk,agent_engines]'")
        return 1
    
    except Exception as e:
        logger.error(f"Failed to deploy agent to Vertex AI Agent Engine: {e}")
        return 1

def main():
    """Main entry point for the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy Google ADK Agent Starter Kit to Vertex AI Agent Engine")
    parser.add_argument("--config", default="deployment_config.yaml", help="Path to the deployment configuration file")
    parser.add_argument("--environment", choices=["development", "staging", "production"], help="Deployment environment")
    parser.add_argument("--staging-bucket", help="Google Cloud Storage bucket for staging")
    
    args = parser.parse_args()
    
    try:
        # Load configuration with environment-specific overrides
        config = load_config(args.config, args.environment)
        
        # If environment was specified in args but not loaded from environment-specific config,
        # override it in the config
        if args.environment and config.get("environment") != args.environment:
            config["environment"] = args.environment
            logger.info(f"Setting environment to {args.environment}")
        
        # Log the deployment environment
        environment = config.get("environment", "development")
        logger.info(f"Deploying to {environment} environment")
        
        # Deploy to Agent Engine
        result = deploy_to_agent_engine(config, args.staging_bucket)
        if result != 0:
            logger.error("Agent Engine deployment failed")
            return result
        
        logger.info("Deployment completed successfully")
        return 0
    
    except Exception as e:
        logger.exception(f"Deployment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
