#!/usr/bin/env python
"""
Direct deployment script for Google ADK Agent to Vertex AI Agent Engine.
This script bypasses the deploy_agent_engine.py script to directly deploy the agent.
"""

import os
import sys
import logging
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("direct_deploy")

def main():
    """Main entry point for the direct deployment script."""
    # Get configuration from environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "risk-manager-457219")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    staging_bucket = os.getenv("STAGING_BUCKET", "risk7")
    
    # Ensure staging_bucket has gs:// prefix
    if not staging_bucket.startswith("gs://"):
        staging_bucket = f"gs://{staging_bucket}"
    
    logger.info(f"Using Project ID: {project_id}")
    logger.info(f"Using Region: {region}")
    logger.info(f"Using Staging Bucket: {staging_bucket}")
    
    try:
        # Import required modules
        logger.info("Importing required modules")
        try:
            import vertexai
            from vertexai import agent_engines
            from vertexai.preview import reasoning_engines
            from src.agents.base_agent import BaseAgent
            
            logger.info("All modules imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            logger.error("Make sure all dependencies are installed")
            return 1
        
        # Initialize Vertex AI
        logger.info(f"Initializing Vertex AI with project {project_id} in region {region}")
        vertexai.init(
            project=project_id,
            location=region,
            staging_bucket=staging_bucket,
        )
        
        # Create the agent
        logger.info("Creating agent instance")
        agent = BaseAgent(
            name="direct_deploy_agent",
            model="gemini-2.0-flash",
            description="Agent deployed directly using direct_deploy.py",
            instruction="I can answer your questions by searching the internet. Just ask me anything!",
        )
        
        # Prepare the agent for Agent Engine
        logger.info("Preparing agent for Agent Engine")
        app = reasoning_engines.AdkApp(
            agent=agent,
            enable_tracing=True,
        )
        
        # Test the agent locally
        logger.info("Testing agent locally before deployment")
        try:
            session = app.create_session(user_id="test_user")
            logger.info(f"Created local test session: {session.id}")
            
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
            ],
            # Include the 'src' directory in the deployment package
            extra_packages=['./src']
        )
        
        agent_engine_id = remote_app.name.split('/')[-1]
        logger.info(f"Agent deployed successfully to Agent Engine: {agent_engine_id}")
        
        # Create a test session on the remote agent
        logger.info("Creating test session on remote agent")
        try:
            remote_session = remote_app.create_session(user_id="test_user_remote")
            logger.info(f"Created remote test session: {remote_session['id']}")
            
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
        
        # Update chat.py with the new Agent Engine ID
        chat_script_path = "chat.py"
        if os.path.isfile(chat_script_path):
            logger.info(f"Updating {chat_script_path} with new Agent Engine ID: {agent_engine_id}")
            
            # Read the chat script
            with open(chat_script_path, "r") as f:
                content = f.read()
            
            # Create a backup
            backup_path = f"{chat_script_path}.{uuid.uuid4().hex}.bak"
            with open(backup_path, "w") as f:
                f.write(content)
            logger.info(f"Created backup of chat.py at {backup_path}")
            
            # Update the Agent Engine ID
            import re
            new_content = re.sub(
                r'AGENT_ENGINE_ID\s*=\s*"(\d+)"',
                f'AGENT_ENGINE_ID = "{agent_engine_id}"',
                content
            )
            
            # Update the Project ID
            new_content = re.sub(
                r'PROJECT_ID\s*=\s*"([^"]*)"',
                f'PROJECT_ID = "{project_id}"',
                new_content
            )
            
            # Update the Location
            new_content = re.sub(
                r'LOCATION\s*=\s*"([^"]*)"',
                f'LOCATION = "{region}"',
                new_content
            )
            
            # Write the updated content back to the file
            with open(chat_script_path, "w") as f:
                f.write(new_content)
            
            logger.info(f"Updated {chat_script_path} with new configuration")
        else:
            logger.warning(f"Chat script {chat_script_path} not found. Unable to update.")
            
        logger.info("Direct deployment completed successfully!")
        logger.info(f"Agent Engine ID: {agent_engine_id}")
        logger.info(f"You can now interact with your agent using 'python chat.py'")
        return 0
        
    except Exception as e:
        logger.exception(f"Direct deployment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
