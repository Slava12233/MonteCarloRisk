"""
Unit tests for the auth utility module.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import the module to test
from src.utils import auth
from src import config # Needed to patch config variables like GOOGLE_APPLICATION_CREDENTIALS

# --- Fixtures ---

@pytest.fixture(autouse=True)
def manage_auth_environment(monkeypatch):
    """Fixture to manage auth-related environment variables."""
    """Fixture to manage auth-related environment variables and auth module import."""
    original_gac_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    original_gac_auth = getattr(auth, 'GOOGLE_APPLICATION_CREDENTIALS', None) # Store original value in auth module

    # Clear env var for clean slate
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    # Ensure auth module sees None initially if env var was cleared
    monkeypatch.setattr(auth, 'GOOGLE_APPLICATION_CREDENTIALS', None, raising=False)

    yield # Run the test

    # Restore environment variable
    if original_gac_env is None:
        monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    else:
        monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", original_gac_env)

    # Restore original value in auth module
    monkeypatch.setattr(auth, 'GOOGLE_APPLICATION_CREDENTIALS', original_gac_auth, raising=False)


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

# --- Test Cases for get_credentials ---

def test_get_credentials_from_provided_file_success(
    mock_os_path_exists, mock_google_auth_service_creds, manage_auth_environment
):
    """Test getting credentials successfully from a provided file path."""
    mock_os_path_exists.return_value = True
    mock_credentials = MagicMock()
    mock_google_auth_service_creds.return_value = mock_credentials
    service_account_file = "/fake/path/to/creds.json"

    credentials = auth.get_credentials(service_account_file=service_account_file)

    mock_os_path_exists.assert_called_once_with(service_account_file)
    mock_google_auth_service_creds.assert_called_once_with(
        service_account_file, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    assert credentials == mock_credentials

def test_get_credentials_from_provided_file_not_exist(
    mock_os_path_exists, mock_google_auth_default, manage_auth_environment
):
    """Test fallback when provided file doesn't exist."""
    mock_os_path_exists.return_value = False # File doesn't exist
    mock_default_creds = MagicMock()
    mock_google_auth_default.return_value = (mock_default_creds, "mock_project")
    service_account_file = "/fake/path/to/creds.json"

    credentials = auth.get_credentials(service_account_file=service_account_file)

    mock_os_path_exists.assert_called_once_with(service_account_file)
    mock_google_auth_default.assert_called_once() # Should fall back to default
    assert credentials == mock_default_creds

def test_get_credentials_from_env_var_success(
    mock_os_path_exists, mock_google_auth_service_creds, manage_auth_environment, monkeypatch
):
    """Test getting credentials successfully from GOOGLE_APPLICATION_CREDENTIALS."""
    env_var_path = "/env/creds.json"
    # Set the attribute directly in the auth module
    monkeypatch.setattr(auth, 'GOOGLE_APPLICATION_CREDENTIALS', env_var_path)
    mock_os_path_exists.return_value = True # Assume path exists
    mock_credentials = MagicMock()
    mock_google_auth_service_creds.return_value = mock_credentials

    credentials = auth.get_credentials() # No specific file provided

    # os.path.exists called once: only for the env var path, as service_account_file is None
    assert mock_os_path_exists.call_count == 1
    mock_os_path_exists.assert_called_with(env_var_path) # Check it was called with the right path
    mock_google_auth_service_creds.assert_called_once_with(
        env_var_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    assert credentials == mock_credentials

def test_get_credentials_from_env_var_fail_fallback_default(
    mock_os_path_exists, mock_google_auth_service_creds, mock_google_auth_default, manage_auth_environment, monkeypatch
):
    """Test fallback to default when env var file load fails."""
    env_var_path = "/env/creds.json"
    # Set the attribute directly in the auth module
    monkeypatch.setattr(auth, 'GOOGLE_APPLICATION_CREDENTIALS', env_var_path)
    mock_os_path_exists.return_value = True # Assume path exists
    mock_google_auth_service_creds.side_effect = Exception("Load failed") # Simulate failure
    mock_default_creds = MagicMock()
    mock_google_auth_default.return_value = (mock_default_creds, "mock_project")

    credentials = auth.get_credentials()

    # os.path.exists called once for the env var path
    assert mock_os_path_exists.call_count == 1
    mock_os_path_exists.assert_called_with(env_var_path)
    mock_google_auth_service_creds.assert_called_once() # Attempted env var load
    mock_google_auth_default.assert_called_once() # Fell back to default
    assert credentials == mock_default_creds


def test_get_credentials_from_default_success(
    mock_os_path_exists, mock_google_auth_default, manage_auth_environment
):
    """Test getting credentials successfully from application default."""
    # No file provided, env var not set (by fixture)
    mock_os_path_exists.return_value = False # Both file checks fail
    mock_default_creds = MagicMock()
    mock_google_auth_default.return_value = (mock_default_creds, "mock_project")

    credentials = auth.get_credentials()

    # os.path.exists is never called as both file and env var are None/empty
    assert mock_os_path_exists.call_count == 0
    mock_google_auth_default.assert_called_once()
    assert credentials == mock_default_creds

def test_get_credentials_all_fail(
    mock_os_path_exists, mock_google_auth_service_creds, mock_google_auth_default, manage_auth_environment
):
    """Test case where all credential methods fail."""
    mock_os_path_exists.return_value = True # Assume files exist
    mock_google_auth_service_creds.side_effect = Exception("Load failed") # File loads fail
    mock_google_auth_default.side_effect = Exception("Default failed") # Default fails

    credentials = auth.get_credentials(service_account_file="/fake/path.json")

    assert mock_os_path_exists.call_count >= 1 # Checks provided file
    assert mock_google_auth_service_creds.call_count >= 1 # Tries provided file
    # Depending on exact path, might try env var too if provided file fails
    mock_google_auth_default.assert_called_once() # Tries default
    assert credentials is None

# --- Add tests for refresh_credentials and configure_auth ---
# Example for refresh_credentials:
# def test_refresh_credentials_valid():
#     mock_creds = MagicMock()
#     mock_creds.valid = True
#     assert auth.refresh_credentials(mock_creds) is False
#     mock_creds.refresh.assert_not_called()

# def test_refresh_credentials_invalid_success():
#     mock_creds = MagicMock()
#     mock_creds.valid = False
#     assert auth.refresh_credentials(mock_creds) is True
#     mock_creds.refresh.assert_called_once()

# def test_refresh_credentials_invalid_fail():
#     mock_creds = MagicMock()
#     mock_creds.valid = False
#     mock_creds.refresh.side_effect = Exception("Refresh failed")
#     assert auth.refresh_credentials(mock_creds) is False
#     mock_creds.refresh.assert_called_once()
