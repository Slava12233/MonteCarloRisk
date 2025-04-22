#!/usr/bin/env python
"""
Deploy and manage agents using the official Vertex AI SDK.

This script provides commands to create, list, and delete Agent Engines
using the official Vertex AI Python SDK.
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sdk_agent_deploy")

def initialize_vertexai(project_id=None, location="us-central1"):
    """Initialize the Vertex AI SDK."""
    try:
        import vertexai
        
        # If project_id is not provided, try to get from environment
        if not project_id:
            # Try to get from gcloud config
            import subprocess
            try:
                result = subprocess.run(
                    ["gcloud", "config", "get-value", "project"], 
                    capture_output=True, 
                    text=True,
                    check=True
                )
                project_id = result.stdout.strip()
            except Exception:
                pass
                
            # If still not found, try environment variable
            if not project_id:
                project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
                
            if not project_id:
                raise ValueError("No project ID provided and couldn't determine from environment")
                
        logger.info(f"Initializing Vertex AI with project: {project_id}, location: {location}")
        
        # Create a default staging bucket name based on the project ID
        staging_bucket = f"gs://{project_id}-vertex-agents"
        
        # Try to ensure the bucket exists
        try:
            from google.cloud import storage
            client = storage.Client(project=project_id)
            
            # Check if bucket exists
            if not client.bucket(f"{project_id}-vertex-agents").exists():
                logger.info(f"Creating staging bucket: {staging_bucket}")
                # Try to create the bucket
                client.create_bucket(f"{project_id}-vertex-agents", location=location)
        except Exception as e:
            logger.warning(f"Could not verify or create staging bucket: {e}")
            logger.warning("Deployment may fail if the bucket doesn't exist")
        
        # Initialize Vertex AI with the staging bucket
        vertexai.init(
            project=project_id,
            location=location,
            staging_bucket=staging_bucket,
        )
        
        return project_id, location
    except ImportError:
        logger.error("Vertex AI SDK not installed. Please install it with: pip install google-cloud-aiplatform[adk,agent_engines]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error initializing Vertex AI: {e}")
        sys.exit(1)

def list_agents(project_id=None, location="us-central1"):
    """List all Agent Engines deployed in the project."""
    try:
        # Initialize Vertex AI
        project_id, location = initialize_vertexai(project_id, location)
        
        try:
            # Import agent_engines
            from vertexai import agent_engines
            
            logger.info(f"Listing Agent Engines in project {project_id}, location {location}")
            
            # List all agents - convert generator to list if needed
            agents_raw = agent_engines.list()
            agents = list(agents_raw) if hasattr(agents_raw, '__iter__') and not isinstance(agents_raw, list) else agents_raw
            
            if agents:
                print("\nAgent Engines:")
                print("=" * 80)
                print(f"{'ID':<25} {'Display Name':<25} {'Status':<15} {'Creation Time'}")
                print("-" * 80)
                for agent in agents:
                    agent_id = getattr(agent, 'name', 'N/A')
                    display_name = getattr(agent, 'display_name', 'N/A')
                    state = getattr(agent, 'status', 'Unknown')
                    create_time = getattr(agent, 'create_time', 'N/A')
                    
                    print(f"{agent_id:<25} {display_name:<25} {state:<15} {create_time}")
                
                agent_count = len(agents) if isinstance(agents, list) else "multiple"
                logger.info(f"Found {agent_count} Agent Engines")
                
                print("\nTo test an agent, use:")
                print(f"python sdk_agent_deploy.py test --agent-id <AGENT_ID> --project-id {project_id}")
                print("\nTo delete an agent, use:")
                print(f"python sdk_agent_deploy.py delete --agent-id <AGENT_ID> --project-id {project_id}")
            else:
                print("No Agent Engines found.")
                logger.info("No Agent Engines found")
                print("\nTo deploy an Agent Engine, use:")
                print(f"python sdk_agent_deploy.py deploy --name my-test-agent --project-id {project_id}")
        except ImportError:
            logger.error("Agent Engine functionality not available in your Vertex AI SDK version.")
            logger.error("Please upgrade with: pip install --upgrade google-cloud-aiplatform[adk,agent_engines]")
            print("\nAgent Engine functionality not available in your Vertex AI SDK version.")
            print("Please upgrade with: pip install --upgrade google-cloud-aiplatform[adk,agent_engines]")
            
    except Exception as e:
        logger.error(f"Error listing Agent Engines: {e}")
        print(f"Error: {e}")

def delete_agent(agent_id, project_id=None, location="us-central1", force=False):
    """Delete an Agent Engine."""
    try:
        # Initialize Vertex AI
        project_id, location = initialize_vertexai(project_id, location)
        
        try:
            # Import agent_engines
            from vertexai import agent_engines
            
            # Confirm deletion if not forced
            if not force:
                print(f"You are about to delete Agent Engine: {agent_id}")
                confirmation = input("\nAre you sure you want to proceed? (y/N): ").lower()
                if confirmation != 'y' and confirmation != 'yes':
                    logger.info("Deletion cancelled by user")
                    print("Deletion cancelled.")
                    return
            
            logger.info(f"Deleting Agent Engine with ID: {agent_id}")
            
            try:
                # Get the agent
                agent = agent_engines.get(agent_id)
                
                # Delete the agent
                agent.delete(force=True)
                
                logger.info(f"Successfully deleted Agent Engine: {agent_id}")
                print(f"Successfully deleted Agent Engine: {agent_id}")
            except Exception as e:
                logger.error(f"Error with agent_engines.get/delete: {e}")
                print(f"Attempting alternative delete method...")
                
                # Try alternative method with delete function
                agent_engines.delete(agent_id, force=True)
                
                logger.info(f"Successfully deleted Agent Engine using alternative method: {agent_id}")
                print(f"Successfully deleted Agent Engine: {agent_id}")
            
        except ImportError as e:
            logger.error(f"Agent Engine functionality not available: {e}")
            logger.error("Please upgrade with: pip install --upgrade google-cloud-aiplatform[adk,agent_engines]")
            print("\nAgent Engine functionality not available in your Vertex AI SDK version.")
            print("Please upgrade with: pip install --upgrade google-cloud-aiplatform[adk,agent_engines]")
            
    except Exception as e:
        logger.error(f"Error deleting Agent Engine: {e}")
        print(f"Error: {e}")

def deploy_test_agent(name, project_id=None, location="us-central1"):
    """
    Deploy a simple test agent to Vertex AI Agent Engine.
    """
    try:
        # Initialize Vertex AI
        project_id, location = initialize_vertexai(project_id, location)
        
        try:
            # Import required modules
            import datetime
            import importlib
            
            # Check if zoneinfo is available (Python 3.9+)
            try:
                from zoneinfo import ZoneInfo
            except ImportError:
                # Fallback for Python < 3.9
                from backports.zoneinfo import ZoneInfo
                print("Using backports.zoneinfo for Python < 3.9")
            
            # Check for different module paths
            adk_agent_module = None
            for module_path in ["google.adk.agents", "vertexai.preview.adk.agents"]:
                try:
                    adk_agent_module = importlib.import_module(module_path)
                    logger.info(f"Found Agent module at: {module_path}")
                    break
                except ImportError:
                    continue
            
            if not adk_agent_module:
                raise ImportError("Could not find Google ADK Agent module")
            
            Agent = getattr(adk_agent_module, "Agent")
            
            # Import reasoning engines
            try:
                from vertexai.preview import reasoning_engines
            except ImportError:
                # Try alternative import
                from vertexai import reasoning_engines
            
            # Import agent engines
            from vertexai import agent_engines
            
            logger.info(f"Creating a simple test agent named: {name}")
            
            # Define tool functions
            def get_weather(city: str) -> dict:
                """Retrieves the current weather report for a specified city."""
                if city.lower() == "new york":
                    return {
                        "status": "success",
                        "report": (
                            "The weather in New York is sunny with a temperature of 25 degrees"
                            " Celsius (77 degrees Fahrenheit)."
                        ),
                    }
                else:
                    return {
                        "status": "error",
                        "error_message": f"Weather information for '{city}' is not available.",
                    }
            
            def get_current_time(city: str) -> dict:
                """Returns the current time in a specified city."""
                if city.lower() == "new york":
                    tz_identifier = "America/New_York"
                else:
                    return {
                        "status": "error",
                        "error_message": (
                            f"Sorry, I don't have timezone information for {city}."
                        ),
                    }
            
                tz = ZoneInfo(tz_identifier)
                now = datetime.datetime.now(tz)
                report = (
                    f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
                )
                return {"status": "success", "report": report}
            
            # Get available models
            available_models = ["gemini-1.5-flash", "gemini-1.0-pro", "gemini-pro", "gemini-flash"]
            model_to_use = available_models[0]  # Default to first model
            
            # Create the agent
            root_agent = Agent(
                name=name,
                model=model_to_use,
                description="Agent to answer questions about the time and weather in a city.",
                instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
                tools=[get_weather, get_current_time],
            )
            
            # Wrap the agent for Agent Engine
            try:
                app = reasoning_engines.AdkApp(
                    agent=root_agent,
                    enable_tracing=True,
                )
                
                logger.info("Testing the agent locally before deployment...")
                
                # Test locally
                try:
                    session = app.create_session(user_id="local_test")
                    print("Local test result:")
                    for event in app.stream_query(
                        user_id="local_test",
                        session_id=session.id,
                        message="What's the weather in New York?",
                    ):
                        if hasattr(event, "parts") and event.parts and hasattr(event.parts[0], "text"):
                            print(f"Agent response: {event.parts[0].text}")
                        elif isinstance(event, dict) and "parts" in event and event["parts"] and "text" in event["parts"][0]:
                            print(f"Agent response: {event['parts'][0]['text']}")
                except Exception as e:
                    logger.warning(f"Local test failed, but continuing with deployment: {e}")
                
                logger.info("Deploying agent to Vertex AI Agent Engine...")
                print("\nDeploying to Vertex AI Agent Engine. This may take several minutes...")
                
                # Deploy to Agent Engine
                remote_app = agent_engines.create(
                    agent_engine=root_agent,
                    requirements=[
                        "google-cloud-aiplatform[adk,agent_engines]"   
                    ]
                )
                
                # Get the agent ID
                agent_id = getattr(remote_app, "name", str(remote_app))
                
                logger.info(f"Agent successfully deployed with ID: {agent_id}")
                print(f"\nAgent successfully deployed!")
                print(f"Agent ID: {agent_id}")
                print("\nTo test your agent, use:")
                print(f"python sdk_agent_deploy.py test --agent-id {agent_id} --project-id {project_id}")
                print("\nTo delete your agent when finished, use:")
                print(f"python sdk_agent_deploy.py delete --agent-id {agent_id} --project-id {project_id}")
                
                return agent_id
            
            except Exception as e:
                logger.error(f"Error using AdkApp: {e}")
                print(f"Trying alternative deployment method...")
                
                # Try another approach - use Application directly instead of AgentClient
                from vertexai.preview import reasoning_engines
                
                # Create Application directly
                app = reasoning_engines.Application(
                    display_name=name,
                    tools=[get_weather, get_current_time]
                )
                
                # Deploy the application
                deployed_app = app.deploy(machine_type="e2-standard-2")
                
                agent_id = deployed_app.name
                logger.info(f"Agent successfully deployed with alternative method. ID: {agent_id}")
                print(f"\nAgent successfully deployed!")
                print(f"Agent ID: {agent_id}")
                print("\nTo test your agent, use:")
                print(f"python sdk_agent_deploy.py test --agent-id {agent_id} --project-id {project_id}")
                print("\nTo delete your agent when finished, use:")
                print(f"python sdk_agent_deploy.py delete --agent-id {agent_id} --project-id {project_id}")
                
                return agent_id
                
        except ImportError as e:
            logger.error(f"Missing required module: {e}")
            logger.error("Please install with: pip install google-cloud-aiplatform[adk,agent_engines]")
            print(f"\nMissing required module: {e}")
            print("Please install with: pip install google-cloud-aiplatform[adk,agent_engines]")
            
    except Exception as e:
        logger.error(f"Error deploying Agent Engine: {e}")
        print(f"Error: {e}")

def test_agent(agent_id, project_id=None, location="us-central1"):
    """Test an existing agent by sending a query."""
    try:
        # Initialize Vertex AI
        project_id, location = initialize_vertexai(project_id, location)
        
        try:
            # Import agent_engines
            from vertexai import agent_engines
            
            logger.info(f"Testing Agent Engine with ID: {agent_id}")
            
            try:
                # Get the agent
                remote_app = agent_engines.get(agent_id)
                
                # Create a session
                remote_session = remote_app.create_session(user_id="test_user")
                session_id = remote_session.get("id") if isinstance(remote_session, dict) else getattr(remote_session, "id", None)
                
                if not session_id:
                    raise ValueError("Could not get session ID")
                    
                logger.info(f"Created session with ID: {session_id}")
                
                # Send a test query
                print("\nSending test query to agent...")
                for event in remote_app.stream_query(
                    user_id="test_user",
                    session_id=session_id,
                    message="What's the weather in New York?",
                ):
                    # Handle different response formats
                    if isinstance(event, dict) and "parts" in event and event["parts"]:
                        if "text" in event["parts"][0]:
                            print(f"Agent response: {event['parts'][0]['text']}")
                    elif hasattr(event, "text"):
                        print(f"Agent response: {event.text}")
                    else:
                        print(f"Raw event: {event}")
                
                logger.info("Test completed successfully")
                
            except Exception as e:
                logger.error(f"Error with standard test approach: {e}")
                print(f"Attempting alternative test method...")
                
                # Try alternative method using client
                from vertexai import preview
                agent_client = preview.reasoning_engines.AgentClient()
                
                # Test with client
                session = agent_client.create_session(agent_id=agent_id, user_id="test_user_alt")
                
                for response in agent_client.query(
                    agent_id=agent_id,
                    session_id=session.name,
                    user_id="test_user_alt",
                    message="What's the weather in New York?",
                ):
                    if hasattr(response, "text"):
                        print(f"Agent response: {response.text}")
                    else:
                        print(f"Raw response: {response}")
                
                logger.info("Test completed successfully with alternative method")
            
        except ImportError as e:
            logger.error(f"Agent Engine functionality not available: {e}")
            logger.error("Please upgrade with: pip install --upgrade google-cloud-aiplatform[adk,agent_engines]")
            print("\nAgent Engine functionality not available in your Vertex AI SDK version.")
            print("Please upgrade with: pip install --upgrade google-cloud-aiplatform[adk,agent_engines]")
            
    except Exception as e:
        logger.error(f"Error testing Agent Engine: {e}")
        print(f"Error: {e}")

def main(args=None):
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Deploy and manage agents using Vertex AI SDK")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all Agent Engines")
    list_parser.add_argument("--project-id", help="Google Cloud project ID")
    list_parser.add_argument("--location", default="us-central1", help="Google Cloud region (default: us-central1)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an Agent Engine")
    delete_parser.add_argument("--agent-id", required=True, help="ID of the Agent Engine to delete")
    delete_parser.add_argument("--project-id", help="Google Cloud project ID")
    delete_parser.add_argument("--location", default="us-central1", help="Google Cloud region (default: us-central1)")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy a test agent to Vertex AI Agent Engine")
    deploy_parser.add_argument("--name", default="test-agent", help="Name for the test agent (default: test-agent)")
    deploy_parser.add_argument("--project-id", help="Google Cloud project ID")
    deploy_parser.add_argument("--location", default="us-central1", help="Google Cloud region (default: us-central1)")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test an existing Agent Engine")
    test_parser.add_argument("--agent-id", required=True, help="ID of the Agent Engine to test")
    test_parser.add_argument("--project-id", help="Google Cloud project ID")
    test_parser.add_argument("--location", default="us-central1", help="Google Cloud region (default: us-central1)")
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.command == "list":
        list_agents(
            project_id=parsed_args.project_id,
            location=parsed_args.location
        )
    elif parsed_args.command == "delete":
        delete_agent(
            agent_id=parsed_args.agent_id,
            project_id=parsed_args.project_id,
            location=parsed_args.location,
            force=parsed_args.force
        )
    elif parsed_args.command == "deploy":
        deploy_test_agent(
            name=parsed_args.name,
            project_id=parsed_args.project_id,
            location=parsed_args.location
        )
    elif parsed_args.command == "test":
        test_agent(
            agent_id=parsed_args.agent_id,
            project_id=parsed_args.project_id,
            location=parsed_args.location
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 