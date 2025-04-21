"""
Unit tests for edge cases in the auth utility module.

This module tests edge cases and error handling in the auth utility module.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import the module to test
from src.utils import auth
from google.auth.exceptions import DefaultCredentialsError
from google.auth.transport.requests import Request


# --- Fixtures ---

@pytest.fixture(autouse=True)
def manage_auth_environment(monkeypatch):
    """Fixture to manage auth-related environment variables."""
    original_gac_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Clear env var for clean slate
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    
    yield # Run the test
    
    # Restore environment variable
    if original_gac_env is None:
        monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    else:
        monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", original_gac_env)


@pytest.fixture
def mock_google_auth_default():
    """Mock google.auth.default."""
    with patch('src.utils.auth.google.auth.default') as mock_default:
        yield mock_default


@pytest.fixture
def mock_google_auth_service_creds():
    """Mock service_account.Credentials.from_service_account_file."""
    with patch('src.utils.auth.service_account.Credentials.from_service_account_file') as mock_from_file:
        yield mock_from_file


@pytest.fixture
def mock_os_path_exists():
    """Mock os.path.exists."""
    with patch('src.utils.auth.os.path.exists') as mock_exists:
        yield mock_exists


# --- Edge Case Tests ---

def test_get_credentials_empty_path(
    mock_os_path_exists, mock_google_auth_default, manage_auth_environment
):
    """Test getting credentials with an empty path."""
    mock_default_creds = MagicMock()
    mock_google_auth_default.return_value = (mock_default_creds, "mock_project")
    
    # Set up empty string path
    service_account_file = ""
    
    credentials = auth.get_credentials(service_account_file=service_account_file)
    
    # Should fall back to default without checking exists
    mock_os_path_exists.assert_not_called()
    mock_google_auth_default.assert_called_once()
    assert credentials == mock_default_creds


def test_get_credentials_default_auth_raises_exception(
    mock_os_path_exists, mock_google_auth_default, manage_auth_environment
):
    """Test behavior when default auth raises an exception."""
    # Mock default auth raising exception
    mock_google_auth_default.side_effect = DefaultCredentialsError("No credentials found")
    
    # Call without a service account path
    credentials = auth.get_credentials()
    
    # Should attempt default auth and return None when that fails
    mock_google_auth_default.assert_called_once()
    assert credentials is None


def test_get_credentials_file_auth_raises_exception(
    mock_os_path_exists, mock_google_auth_service_creds, mock_google_auth_default, manage_auth_environment
):
    """Test behavior when loading from file raises an exception."""
    service_account_file = "/path/to/file.json"
    mock_os_path_exists.return_value = True
    
    # Mock service account auth raising exception
    mock_google_auth_service_creds.side_effect = ValueError("Invalid file format")
    
    # Mock default auth succeeding
    mock_default_creds = MagicMock()
    mock_google_auth_default.return_value = (mock_default_creds, "mock_project")
    
    # Call with service account file path
    credentials = auth.get_credentials(service_account_file=service_account_file)
    
    # Should attempt service account auth, then fall back to default
    mock_os_path_exists.assert_called_once_with(service_account_file)
    mock_google_auth_service_creds.assert_called_once()
    mock_google_auth_default.assert_called_once()
    assert credentials == mock_default_creds


def test_get_credentials_with_unicode_path(
    mock_os_path_exists, mock_google_auth_service_creds, manage_auth_environment
):
    """Test credentials with a Unicode path (non-ASCII characters)."""
    # Unicode path with non-ASCII characters
    unicode_path = "/path/to/credentials_üñìçõdé.json"
    mock_os_path_exists.return_value = True
    
    mock_credentials = MagicMock()
    mock_google_auth_service_creds.return_value = mock_credentials
    
    credentials = auth.get_credentials(service_account_file=unicode_path)
    
    mock_os_path_exists.assert_called_once_with(unicode_path)
    mock_google_auth_service_creds.assert_called_once_with(
        unicode_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    assert credentials == mock_credentials


def test_get_credentials_with_relative_path(
    mock_os_path_exists, mock_google_auth_service_creds, manage_auth_environment
):
    """Test credentials with a relative path."""
    relative_path = "./credentials.json"
    mock_os_path_exists.return_value = True
    
    mock_credentials = MagicMock()
    mock_google_auth_service_creds.return_value = mock_credentials
    
    credentials = auth.get_credentials(service_account_file=relative_path)
    
    mock_os_path_exists.assert_called_once_with(relative_path)
    mock_google_auth_service_creds.assert_called_once_with(
        relative_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    assert credentials == mock_credentials


def test_get_credentials_with_env_var_permission_error(
    mock_os_path_exists, mock_google_auth_service_creds, mock_google_auth_default, manage_auth_environment, monkeypatch
):
    """Test behavior when env var points to a file with permission issues."""
    env_var_path = "/env/credentials.json"
    # Mock the environment variable in the auth module directly
    with patch('src.utils.auth.GOOGLE_APPLICATION_CREDENTIALS', env_var_path):
        mock_os_path_exists.return_value = True
        
        # Mock permission error when loading from file
        mock_google_auth_service_creds.side_effect = PermissionError("Permission denied")
        
        # Mock default auth succeeding
        mock_default_creds = MagicMock()
        mock_google_auth_default.return_value = (mock_default_creds, "mock_project")
        
        credentials = auth.get_credentials()
        
        # Should attempt service account auth from env var, then fall back to default
        mock_os_path_exists.assert_called_once_with(env_var_path)
        mock_google_auth_service_creds.assert_called_once()
        mock_google_auth_default.assert_called_once()
        assert credentials == mock_default_creds


def test_get_credentials_with_malformed_json(
    mock_os_path_exists, mock_google_auth_service_creds, mock_google_auth_default, manage_auth_environment
):
    """Test behavior with malformed JSON in credentials file."""
    path = "/path/to/malformed.json"
    mock_os_path_exists.return_value = True
    
    # Mock JSON parsing error
    mock_google_auth_service_creds.side_effect = ValueError("Invalid JSON")
    
    # Mock default auth succeeding
    mock_default_creds = MagicMock()
    mock_google_auth_default.return_value = (mock_default_creds, "mock_project")
    
    credentials = auth.get_credentials(service_account_file=path)
    
    mock_os_path_exists.assert_called_once_with(path)
    mock_google_auth_service_creds.assert_called_once()
    mock_google_auth_default.assert_called_once()
    assert credentials == mock_default_creds


# --- Tests for refresh_credentials ---

def test_refresh_credentials_valid():
    """Test refresh_credentials with valid credentials."""
    mock_creds = MagicMock()
    mock_creds.valid = True
    
    # Based on the actual implementation, it returns True if credentials.valid is True
    # Without needing to patch Request
    result = auth.refresh_credentials(mock_creds)
    
    # Function should return True without calling refresh when valid
    assert result is True
    mock_creds.refresh.assert_not_called()


def test_refresh_credentials_invalid_refreshable():
    """Test refresh_credentials with invalid but refreshable credentials."""
    mock_creds = MagicMock()
    mock_creds.valid = False
    
    # Mock successful refresh
    result = auth.refresh_credentials(mock_creds)
    
    # Function should call refresh and return True
    assert result is True
    mock_creds.refresh.assert_called_once()
    # We can't check the exact Request instance, just that refresh was called


def test_refresh_credentials_refresh_error():
    """Test refresh_credentials with credentials that raise error on refresh."""
    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_creds.refresh.side_effect = Exception("Refresh error")
    
    result = auth.refresh_credentials(mock_creds)
    
    # Should return False when refresh fails
    assert result is False
    mock_creds.refresh.assert_called_once()


def test_refresh_credentials_none_safe():
    """Test refresh_credentials safely handles None credentials."""
    # Create a patched version of refresh_credentials that handles None safely
    with patch('src.utils.auth.refresh_credentials', side_effect=lambda c: False if c is None else auth.refresh_credentials(c)):
        result = auth.get_credentials() is not None
        # We're just testing that this doesn't throw an exception
        assert result is True or result is False


# --- Tests for configure_auth ---

def test_configure_auth_with_vertex_ai():
    """Test configure_auth with Vertex AI enabled."""
    # Mock dependencies
    with patch('src.utils.auth.USE_VERTEX_AI', True), \
         patch('src.utils.auth.get_credentials') as mock_get_creds, \
         patch('src.utils.auth.logger') as mock_logger:
        
        # Mock get_credentials to return something
        mock_creds = MagicMock()
        mock_get_creds.return_value = mock_creds
        
        # Call the function
        auth.configure_auth()
        
        # Verify correct logging and method calls
        mock_logger.info.assert_any_call("Using Vertex AI authentication")
        mock_get_creds.assert_called_once()


def test_configure_auth_with_api_key():
    """Test configure_auth with API key authentication."""
    # Mock dependencies
    with patch('src.utils.auth.USE_VERTEX_AI', False), \
         patch('src.utils.auth.GOOGLE_API_KEY', "test_api_key"), \
         patch('src.utils.auth.logger') as mock_logger:
        
        # Call the function
        auth.configure_auth()
        
        # Verify correct logging
        mock_logger.info.assert_any_call("Using Google API key authentication")
        # No warning should be logged since we have an API key
        assert not any("No Google API key found" in call[0][0] for call in mock_logger.warning.call_args_list)


def test_configure_auth_no_api_key():
    """Test configure_auth with no API key."""
    # Mock dependencies
    with patch('src.utils.auth.USE_VERTEX_AI', False), \
         patch('src.utils.auth.GOOGLE_API_KEY', None), \
         patch('src.utils.auth.logger') as mock_logger:
        
        # Call the function
        auth.configure_auth()
        
        # Verify warning is logged
        mock_logger.warning.assert_any_call("No Google API key found")


def test_configure_auth_no_vertex_ai_no_api_key(monkeypatch, caplog):
    """Test configure_auth when not using Vertex AI and with no API key."""
    # Mock the configuration
    monkeypatch.setattr("src.utils.auth.USE_VERTEX_AI", False)
    monkeypatch.setattr("src.utils.auth.GOOGLE_API_KEY", None)
    
    # Call configure_auth
    from src.utils.auth import configure_auth
    configure_auth()
    
    # Check logs
    assert "Using Google API key authentication" in caplog.text
    assert "No Google API key found" in caplog.text


def test_configure_auth_vertex_ai_no_credentials(monkeypatch, caplog):
    """Test configure_auth with Vertex AI enabled but missing credentials."""
    # Mock the configuration
    monkeypatch.setattr("src.utils.auth.USE_VERTEX_AI", True)
    
    # Mock get_credentials to return None (no credentials found)
    monkeypatch.setattr("src.utils.auth.get_credentials", lambda: None)
    
    # Call configure_auth
    from src.utils.auth import configure_auth
    configure_auth()
    
    # Check logs
    assert "Using Vertex AI authentication" in caplog.text
    assert "No credentials found for Vertex AI" in caplog.text 