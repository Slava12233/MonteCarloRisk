"""
Configuration settings for the Google ADK Agent Starter Kit.

This module handles loading configuration from environment variables and provides
default values for various settings.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google API settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Vertex AI settings
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE").upper() == "TRUE"
VERTEX_AI_SEARCH_DATASTORE_ID = os.getenv("VERTEX_AI_SEARCH_DATASTORE_ID")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Development settings
DEV_MODE = os.getenv("DEV_MODE", "FALSE").upper() == "TRUE"

# Web UI settings
WEB_UI_PORT = int(os.getenv("WEB_UI_PORT", "8000"))

# Default model settings
DEFAULT_MODEL = "gemini-2.0-flash"


def get_config() -> Dict[str, Any]:
    """
    Get the current configuration as a dictionary.

    Returns:
        Dict[str, Any]: The current configuration.
    """
    return {
        "google_api_key": GOOGLE_API_KEY,
        "google_cloud_project": GOOGLE_CLOUD_PROJECT,
        "google_cloud_region": GOOGLE_CLOUD_REGION,
        "google_application_credentials": GOOGLE_APPLICATION_CREDENTIALS,
        "use_vertex_ai": USE_VERTEX_AI,
        "vertex_ai_search_datastore_id": VERTEX_AI_SEARCH_DATASTORE_ID,
        "log_level": LOG_LEVEL,
        "dev_mode": DEV_MODE,
        "web_ui_port": WEB_UI_PORT,
        "default_model": DEFAULT_MODEL,
    }


def validate_config() -> Optional[str]:
    """
    Validate the current configuration.

    Returns:
        Optional[str]: An error message if the configuration is invalid, None otherwise.
    """
    if USE_VERTEX_AI:
        if not GOOGLE_CLOUD_PROJECT:
            return "GOOGLE_CLOUD_PROJECT is required when using Vertex AI"
        if not GOOGLE_CLOUD_REGION:
            return "GOOGLE_CLOUD_REGION is required when using Vertex AI"
    else:
        if not GOOGLE_API_KEY:
            return "GOOGLE_API_KEY is required when not using Vertex AI"

    return None


def print_config() -> None:
    """Print the current configuration (with sensitive values masked)."""
    config = get_config()
    
    # Mask sensitive values
    if config["google_api_key"]:
        config["google_api_key"] = f"{config['google_api_key'][:5]}...{config['google_api_key'][-5:]}"
    
    print("Current Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
