#!/usr/bin/env python
"""
Deployment script for Google ADK Agent Starter Kit.

This script automates the deployment process using the configuration in deployment_config.yaml.
"""

import os
import sys
import subprocess
import argparse
import yaml
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("deploy")

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

def format_command(command: str, config: Dict[str, Any]) -> str:
    """
    Format a command string with values from the configuration.
    
    Args:
        command: The command string with placeholders.
        config: The configuration dictionary.
        
    Returns:
        The formatted command string.
    """
    # Replace placeholders like {vertex_ai.project_id} with values from config
    formatted_command = command
    
    # Find all placeholders in the format {section.key}
    import re
    placeholders = re.findall(r"\{([^}]+)\}", command)
    
    for placeholder in placeholders:
        # Split the placeholder into section and key
        parts = placeholder.split(".")
        if len(parts) == 2:
            section, key = parts
            # Get the value from the config
            if section in config and key in config[section]:
                value = config[section][key]
                formatted_command = formatted_command.replace(f"{{{placeholder}}}", str(value))
    
    return formatted_command

def run_command(command: str) -> int:
    """
    Run a shell command.
    
    Args:
        command: The command to run.
        
    Returns:
        The return code of the command.
    """
    logger.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        logger.info(f"Command output: {result.stdout}")
    
    if result.stderr:
        logger.warning(f"Command error output: {result.stderr}")
    
    if result.returncode != 0:
        logger.error(f"Command failed with return code {result.returncode}")
    else:
        logger.info(f"Command completed successfully")
    
    return result.returncode

def deploy_to_vertex_ai(config: Dict[str, Any]) -> int:
    """
    Deploy the agent to Vertex AI.
    
    Args:
        config: The deployment configuration.
        
    Returns:
        0 if successful, non-zero otherwise.
    """
    logger.info("Starting deployment to Vertex AI")
    
    try:
        # Import the necessary modules
        from src.agents.search_agent import SearchAgent
        from src.deployment.vertex import deploy_to_vertex
        
        # Get Vertex AI configuration
        vertex_ai_config = config.get("vertex_ai", {})
        project_id = vertex_ai_config.get("project_id")
        region = vertex_ai_config.get("region")
        machine_type = vertex_ai_config.get("machine_type", "n1-standard-2")
        min_replica_count = vertex_ai_config.get("min_replica_count", 1)
        max_replica_count = vertex_ai_config.get("max_replica_count", 1)
        
        if not project_id or project_id == "your-project-id":
            logger.error("Project ID not configured. Please set vertex_ai.project_id in deployment_config.yaml")
            return 1
        
        # Get agent configuration
        agent_config = config.get("agent", {})
        agent_type = agent_config.get("type", "search")
        model = agent_config.get("model", "gemini-2.0-flash")
        description = agent_config.get("description", "Agent to answer questions using Google Search.")
        instruction = agent_config.get("instruction", "I can answer your questions by searching the internet. Just ask me anything!")
        
        # Create the agent
        logger.info(f"Creating {agent_type} agent with model {model}")
        agent = SearchAgent(
            name=f"{agent_type}_agent",  # Use underscore instead of hyphen
            model=model,
            description=description,
            instruction=instruction,
        )
        
        # Deploy the agent to Vertex AI
        logger.info(f"Deploying agent to Vertex AI in project {project_id}, region {region}")
        endpoint_id = deploy_to_vertex(
            agent=agent,
            project_id=project_id,
            location=region,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            deployment_name=f"{agent_type}-endpoint",
            output_dir="deploy",
        )
        
        logger.info(f"Agent deployed successfully to endpoint: {endpoint_id}")
        return 0
    
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Make sure google-cloud-aiplatform is installed: pip install google-cloud-aiplatform")
        return 1
    
    except Exception as e:
        logger.error(f"Failed to deploy agent to Vertex AI: {e}")
        return 1

def deploy_locally(config: Dict[str, Any]) -> int:
    """
    Deploy the agent locally.
    
    Args:
        config: The deployment configuration.
        
    Returns:
        0 if successful, non-zero otherwise.
    """
    logger.info("Starting local deployment")
    
    # Get local configuration
    local_config = config.get("local", {})
    host = local_config.get("host", "127.0.0.1")
    port = local_config.get("port", 8000)
    log_level = local_config.get("log_level", "info")
    reload = local_config.get("reload", False)
    
    # Get agent configuration
    agent_config = config.get("agent", {})
    agent_type = agent_config.get("type", "search")
    
    # Build the deployment command
    command = f"python run.py run {agent_type} --web --host {host} --port {port} --log-level {log_level}"
    
    if reload:
        command += " --reload"
    
    # Run the command
    return run_command(command)

def run_deployment_steps(config: Dict[str, Any]) -> int:
    """
    Run the deployment steps defined in the configuration.
    
    Args:
        config: The deployment configuration.
        
    Returns:
        0 if all steps are successful, non-zero otherwise.
    """
    logger.info("Running deployment steps")
    
    # Get deployment steps
    steps = config.get("deployment_steps", [])
    
    for i, step in enumerate(steps):
        step_name = step.get("name", f"Step {i+1}")
        step_command = step.get("command", "")
        
        if not step_command:
            logger.warning(f"Skipping step '{step_name}' because no command is defined")
            continue
        
        logger.info(f"Running step '{step_name}'")
        
        # Format the command with values from the configuration
        formatted_command = format_command(step_command, config)
        
        # Run the command
        return_code = run_command(formatted_command)
        
        if return_code != 0:
            logger.error(f"Step '{step_name}' failed with return code {return_code}")
            return return_code
    
    logger.info("All deployment steps completed successfully")
    return 0

def main():
    """Main entry point for the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy Google ADK Agent Starter Kit")
    parser.add_argument("--config", default="deployment_config.yaml", help="Path to the deployment configuration file")
    parser.add_argument("--environment", choices=["development", "staging", "production"], help="Deployment environment")
    parser.add_argument("--local", action="store_true", help="Deploy locally")
    parser.add_argument("--vertex", action="store_true", help="Deploy to Vertex AI")
    parser.add_argument("--steps", action="store_true", help="Run deployment steps")
    
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
        
        # Determine what to deploy
        deploy_local = args.local
        deploy_vertex = args.vertex
        run_steps = args.steps
        
        # If no specific deployment is requested, run all
        if not deploy_local and not deploy_vertex and not run_steps:
            deploy_local = True
            deploy_vertex = True
            run_steps = True
        
        # Run deployment steps
        if run_steps:
            result = run_deployment_steps(config)
            if result != 0:
                logger.error("Deployment steps failed")
                return result
        
        # Deploy locally
        if deploy_local:
            result = deploy_locally(config)
            if result != 0:
                logger.error("Local deployment failed")
                return result
        
        # Deploy to Vertex AI
        if deploy_vertex:
            result = deploy_to_vertex_ai(config)
            if result != 0:
                logger.error("Vertex AI deployment failed")
                return result
        
        logger.info("Deployment completed successfully")
        return 0
    
    except Exception as e:
        logger.exception(f"Deployment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
