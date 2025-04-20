"""
Authentication utilities for the Google ADK Agent Starter Kit.

This module provides utilities for authenticating with Google services.
"""

import os
import logging
from typing import Optional

import google.auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from ..config import GOOGLE_API_KEY, GOOGLE_APPLICATION_CREDENTIALS, USE_VERTEX_AI

# Configure logging
logger = logging.getLogger(__name__)


def get_credentials(
    scopes: Optional[list] = None,
    service_account_file: Optional[str] = None,
) -> Optional[google.auth.credentials.Credentials]:
    """
    Get Google Cloud credentials.

    This function attempts to get credentials in the following order:
    1. From the provided service account file
    2. From the GOOGLE_APPLICATION_CREDENTIALS environment variable
    3. From application default credentials

    Args:
        scopes: The scopes to request (default: None).
        service_account_file: Path to a service account file (default: None).

    Returns:
        The credentials, or None if no credentials could be obtained.
    """
    credentials = None
    scopes = scopes or ["https://www.googleapis.com/auth/cloud-platform"]

    # Try to get credentials from the provided service account file
    if service_account_file and os.path.exists(service_account_file):
        try:
            logger.info(f"Loading credentials from service account file: {service_account_file}")
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file, scopes=scopes
            )
            return credentials
        except Exception as e:
            logger.warning(f"Failed to load credentials from service account file: {e}")

    # Try to get credentials from the GOOGLE_APPLICATION_CREDENTIALS environment variable
    if GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        try:
            logger.info(f"Loading credentials from GOOGLE_APPLICATION_CREDENTIALS: {GOOGLE_APPLICATION_CREDENTIALS}")
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes
            )
            return credentials
        except Exception as e:
            logger.warning(f"Failed to load credentials from GOOGLE_APPLICATION_CREDENTIALS: {e}")

    # Try to get application default credentials
    try:
        logger.info("Loading application default credentials")
        credentials, project = google.auth.default(scopes=scopes)
        return credentials
    except Exception as e:
        logger.warning(f"Failed to load application default credentials: {e}")

    logger.warning("No credentials could be obtained")
    return None


def refresh_credentials(credentials: google.auth.credentials.Credentials) -> bool:
    """
    Refresh credentials if they are expired or close to expiring.

    Args:
        credentials: The credentials to refresh.

    Returns:
        True if the credentials were refreshed, False otherwise.
    """
    if not credentials.valid:
        try:
            logger.info("Refreshing credentials")
            credentials.refresh(Request())
            return True
        except Exception as e:
            logger.warning(f"Failed to refresh credentials: {e}")
            return False
    return False


def configure_auth() -> None:
    """
    Configure authentication for Google services.

    This function sets up authentication based on the configuration.
    """
    if USE_VERTEX_AI:
        logger.info("Using Vertex AI authentication")
        # Vertex AI uses application default credentials
        credentials = get_credentials()
        if not credentials:
            logger.warning("No credentials found for Vertex AI")
    else:
        logger.info("Using Google API key authentication")
        if not GOOGLE_API_KEY:
            logger.warning("No Google API key found")
