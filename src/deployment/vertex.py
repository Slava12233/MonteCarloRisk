"""
Vertex AI deployment utilities for the Google ADK Agent Starter Kit.

This module provides utilities for deploying agents to Vertex AI.
"""

import logging
import os
import json
import tempfile
import shutil
import zipfile
from typing import Any, Dict, List, Optional, Union

from ..config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_REGION
from ..utils.logging import get_logger
from ..utils.auth import get_credentials

# Configure logging
logger = get_logger(__name__)

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import Model
except ImportError:
    logger.warning("google-cloud-aiplatform not installed. Vertex AI deployment will not be available.")
    aiplatform = None
    Model = None


def prepare_deployment_package(
    agent: Any,
    output_dir: Optional[str] = None,
    include_files: Optional[List[str]] = None,
    requirements_file: str = "requirements.txt",
) -> str:
    """
    Prepare a deployment package for Vertex AI.

    Args:
        agent: The agent to deploy.
        output_dir: Directory to write the deployment package to (default: temporary directory).
        include_files: Additional files to include in the package (default: None).
        requirements_file: Path to requirements.txt file (default: requirements.txt).

    Returns:
        Path to the deployment package (ZIP file).
    """
    # Create a temporary directory if output_dir is not provided
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Preparing deployment package in {output_dir}")
    
    # Create deployment directory structure
    deploy_dir = os.path.join(output_dir, "deploy")
    os.makedirs(deploy_dir, exist_ok=True)
    
    # Copy the src directory to the deployment package
    src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
    deploy_src_dir = os.path.join(deploy_dir, "src")
    shutil.copytree(src_dir, deploy_src_dir)
    
    # Create main.py for the deployment
    with open(os.path.join(deploy_dir, "main.py"), "w") as f:
        f.write(f"""
import os
import sys
import json
import logging
from typing import Dict, Any

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.cloud import aiplatform
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import our custom agent
from src.agents.search_agent import SearchAgent
from src.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Initialize agent
def init():
    global agent, runner, session_service
    
    # Create our custom SearchAgent
    agent = SearchAgent(
        name="{agent.name}",
        model="{agent.model}",
        description="{agent.description}",
        instruction="{agent.instruction}",
    )
    
    # Set up session management
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="{agent.name}",
        session_service=session_service
    )
    
    logger.info("Custom SearchAgent initialized")

# Handle prediction requests
def predict(request: Dict[str, Any]) -> Dict[str, Any]:
    # Extract request data
    instances = request.get("instances", [])
    if not instances:
        return {{"predictions": []}}
    
    predictions = []
    
    for instance in instances:
        # Extract user_id, session_id, and message
        user_id = instance.get("user_id", "user")
        session_id = instance.get("session_id", "session")
        message = instance.get("message", "")
        
        # Ensure session exists
        if not session_service.get_session(app_name="{agent.app_name}", user_id=user_id, session_id=session_id):
            session_service.create_session(app_name="{agent.app_name}", user_id=user_id, session_id=session_id)
        
        # Create content
        content = types.Content(role="user", parts=[types.Part(text=message)])
        
        # Run the agent
        logger.info(f"Running agent for user: {{user_id}}, session: {{session_id}}")
        events = list(runner.run(user_id=user_id, session_id=session_id, new_message=content))
        
        # Extract final response
        final_response = None
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        # Add prediction
        predictions.append({{"response": final_response or "No response from the agent."}})
    
    return {{"predictions": predictions}}

# Initialize on module load
init()
        """)
    
    # Copy requirements.txt
    if os.path.exists(requirements_file):
        shutil.copy(requirements_file, os.path.join(deploy_dir, "requirements.txt"))
    else:
        logger.warning(f"Requirements file {requirements_file} not found. Creating a minimal one.")
        with open(os.path.join(deploy_dir, "requirements.txt"), "w") as f:
            f.write("""
google-adk>=0.5.0
google-generativeai>=0.3.0
google-cloud-aiplatform>=1.36.0
            """)
    
    # Copy additional files
    if include_files:
        for file_path in include_files:
            if os.path.exists(file_path):
                dest_path = os.path.join(deploy_dir, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                logger.info(f"Copied {file_path} to {dest_path}")
            else:
                logger.warning(f"File {file_path} not found. Skipping.")
    
    # Create ZIP file
    zip_path = os.path.join(output_dir, f"{agent.name}_deployment.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    logger.info(f"Created deployment package: {zip_path}")
    
    return zip_path


def deploy_to_vertex(
    agent: Any,
    project_id: Optional[str] = None,
    location: Optional[str] = None,
    machine_type: str = "n1-standard-2",
    min_replica_count: int = 1,
    max_replica_count: int = 1,
    deployment_name: Optional[str] = None,
    output_dir: Optional[str] = None,
    include_files: Optional[List[str]] = None,
    requirements_file: str = "requirements.txt",
) -> str:
    """
    Deploy an agent to Vertex AI.

    Args:
        agent: The agent to deploy.
        project_id: Google Cloud project ID (default: from config).
        location: Google Cloud region (default: from config).
        machine_type: Machine type for the deployment (default: n1-standard-2).
        min_replica_count: Minimum number of replicas (default: 1).
        max_replica_count: Maximum number of replicas (default: 1).
        deployment_name: Name for the deployment (default: agent name).
        output_dir: Directory to write the deployment package to (default: temporary directory).
        include_files: Additional files to include in the package (default: None).
        requirements_file: Path to requirements.txt file (default: requirements.txt).

    Returns:
        The endpoint ID of the deployed agent.

    Raises:
        ValueError: If project_id or location is not provided and not in config.
        ImportError: If google-cloud-aiplatform is not installed.
    """
    if aiplatform is None:
        raise ImportError("google-cloud-aiplatform not installed. Please install it with pip install google-cloud-aiplatform.")
    
    # Get project_id and location from config if not provided
    project_id = project_id or GOOGLE_CLOUD_PROJECT
    location = location or GOOGLE_CLOUD_REGION
    
    if not project_id:
        raise ValueError("project_id is required but not provided and not in config.")
    
    if not location:
        raise ValueError("location is required but not provided and not in config.")
    
    # Get deployment name
    deployment_name = deployment_name or f"{agent.name}-endpoint"
    
    # Get credentials
    credentials = get_credentials()
    
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=location, credentials=credentials)
    
    # Prepare deployment package
    zip_path = prepare_deployment_package(
        agent=agent,
        output_dir=output_dir,
        include_files=include_files,
        requirements_file=requirements_file,
    )
    
    # Upload model to Vertex AI Model Registry
    logger.info(f"Uploading model to Vertex AI Model Registry in project {project_id}, location {location}")
    
    model = aiplatform.Model.upload(
        display_name=agent.name,
        artifact_uri=os.path.dirname(zip_path),
        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/python-cpu.default:latest",
        serving_container_predict_route="/predict",
        serving_container_health_route="/health",
        serving_container_environment_variables={
            "PYTHONPATH": "/app",
        },
    )
    
    logger.info(f"Model uploaded: {model.resource_name}")
    
    # Deploy model to endpoint
    logger.info(f"Deploying model to endpoint: {deployment_name}")
    
    endpoint = model.deploy(
        deployed_model_display_name=agent.name,
        machine_type=machine_type,
        min_replica_count=min_replica_count,
        max_replica_count=max_replica_count,
        endpoint_name=deployment_name,
    )
    
    logger.info(f"Model deployed to endpoint: {endpoint.resource_name}")
    
    return endpoint.resource_name


def predict(
    endpoint_id: str,
    message: str,
    user_id: str = "user",
    session_id: str = "session",
    project_id: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """
    Send a prediction request to a deployed agent.

    Args:
        endpoint_id: The endpoint ID of the deployed agent.
        message: The message to send to the agent.
        user_id: The ID of the user (default: "user").
        session_id: The ID of the session (default: "session").
        project_id: Google Cloud project ID (default: from config).
        location: Google Cloud region (default: from config).

    Returns:
        The agent's response.

    Raises:
        ValueError: If project_id or location is not provided and not in config.
        ImportError: If google-cloud-aiplatform is not installed.
    """
    if aiplatform is None:
        raise ImportError("google-cloud-aiplatform not installed. Please install it with pip install google-cloud-aiplatform.")
    
    # Get project_id and location from config if not provided
    project_id = project_id or GOOGLE_CLOUD_PROJECT
    location = location or GOOGLE_CLOUD_REGION
    
    if not project_id:
        raise ValueError("project_id is required but not provided and not in config.")
    
    if not location:
        raise ValueError("location is required but not provided and not in config.")
    
    # Get credentials
    credentials = get_credentials()
    
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=location, credentials=credentials)
    
    # Get endpoint
    endpoint = aiplatform.Endpoint(endpoint_id)
    
    # Send prediction request
    instances = [
        {
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
        }
    ]
    
    response = endpoint.predict(instances=instances)
    
    # Extract response
    predictions = response.predictions
    if predictions and len(predictions) > 0:
        return predictions[0].get("response", "No response from the agent.")
    
    return "No response from the agent."
