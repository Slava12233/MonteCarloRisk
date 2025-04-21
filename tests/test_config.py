"""
Unit tests for the config module.
"""

import os
import sys
import pytest
from unittest.mock import patch

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from importlib import reload # Keep reload for resetting module state if needed, but rely on setattr
from src import config


# --- Fixtures ---

@pytest.fixture(autouse=True)
def manage_environment(monkeypatch):
    """Fixture to reset config module state using reload."""
    # This ensures each test gets a fresh look at the module,
    # even though we'll primarily use setattr for specific values.
    reload(config)
    yield
    reload(config) # Reload again after test to clean up


# --- Test Cases for validate_config ---

def test_validate_config_non_vertex_with_key(manage_environment, monkeypatch):
    """Test valid config: Non-Vertex AI with API key."""
    monkeypatch.setattr(config, 'USE_VERTEX_AI', False)
    monkeypatch.setattr(config, 'GOOGLE_API_KEY', 'test_api_key')
    assert config.validate_config() is None

def test_validate_config_non_vertex_no_key(manage_environment, monkeypatch):
    """Test invalid config: Non-Vertex AI without API key."""
    monkeypatch.setattr(config, 'USE_VERTEX_AI', False)
    monkeypatch.setattr(config, 'GOOGLE_API_KEY', None) # Explicitly set to None
    validation_result = config.validate_config()
    assert validation_result is not None
    assert "GOOGLE_API_KEY is required" in validation_result

def test_validate_config_vertex_with_project_region(manage_environment, monkeypatch):
    """Test valid config: Vertex AI with Project ID and Region."""
    monkeypatch.setattr(config, 'USE_VERTEX_AI', True)
    monkeypatch.setattr(config, 'GOOGLE_CLOUD_PROJECT', 'test_project')
    monkeypatch.setattr(config, 'GOOGLE_CLOUD_REGION', 'test_region')
    assert config.validate_config() is None

def test_validate_config_vertex_no_project(manage_environment, monkeypatch):
    """Test invalid config: Vertex AI without Project ID."""
    monkeypatch.setattr(config, 'USE_VERTEX_AI', True)
    monkeypatch.setattr(config, 'GOOGLE_CLOUD_PROJECT', None) # Explicitly set to None
    monkeypatch.setattr(config, 'GOOGLE_CLOUD_REGION', 'test_region')
    validation_result = config.validate_config()
    assert validation_result is not None
    assert "GOOGLE_CLOUD_PROJECT is required" in validation_result

def test_validate_config_vertex_no_region(manage_environment, monkeypatch):
    """Test invalid config: Vertex AI without Region (should pass due to default)."""
    monkeypatch.setattr(config, 'USE_VERTEX_AI', True)
    monkeypatch.setattr(config, 'GOOGLE_CLOUD_PROJECT', 'test_project')
    # Patch the variable directly to simulate it being None *before* validation
    # Note: config.py sets a default, so this tests if validation *itself* checks for None/empty
    monkeypatch.setattr(config, 'GOOGLE_CLOUD_REGION', None)
    validation_result = config.validate_config()
    # The validation logic correctly checks the variable *after* it's been potentially set by os.getenv or patched.
    # Since we patched it to None, the validation `if not GOOGLE_CLOUD_REGION:` should fail.
    assert validation_result is not None
    assert "GOOGLE_CLOUD_REGION is required" in validation_result


# --- Add tests for get_config and print_config if needed ---
# Example:
# def test_get_config_values(monkeypatch):
#     monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
#     monkeypatch.setenv("WEB_UI_PORT", "9999")
#     from importlib import reload
#     from src import config
#     reload(config)
#     cfg = config.get_config()
#     assert cfg["google_api_key"] == "test_key"
#     assert cfg["web_ui_port"] == 9999

def test_get_config_includes_all_settings():
    """Test that get_config returns a dictionary with all expected settings."""
    from src.config import get_config
    
    config = get_config()
    
    # Check that the config contains all expected keys
    expected_keys = [
        "google_api_key",
        "google_cloud_project",
        "google_cloud_region",
        "google_application_credentials",
        "use_vertex_ai",
        "vertex_ai_search_datastore_id",
        "log_level",
        "dev_mode",
        "web_ui_port",
        "default_model",
    ]
    
    for key in expected_keys:
        assert key in config, f"Expected key '{key}' not found in config"

def test_print_config_masks_api_key(monkeypatch, capsys):
    """Test that print_config masks the API key."""
    # Mock the API key
    test_api_key = "abcdefghijklmnopqrstuvwxyz"
    monkeypatch.setattr("src.config.GOOGLE_API_KEY", test_api_key)
    
    # Call print_config
    from src.config import print_config
    print_config()
    
    # Check the output
    captured = capsys.readouterr()
    assert "Current Configuration:" in captured.out
    
    # Check that the API key is masked
    assert test_api_key not in captured.out
    assert f"{test_api_key[:5]}...{test_api_key[-5:]}" in captured.out

def test_print_config_empty_api_key(monkeypatch, capsys):
    """Test that print_config handles empty API key properly."""
    # Mock an empty API key
    monkeypatch.setattr("src.config.GOOGLE_API_KEY", None)
    
    # Call print_config
    from src.config import print_config
    print_config()
    
    # Check the output
    captured = capsys.readouterr()
    assert "Current Configuration:" in captured.out
    assert "google_api_key: None" in captured.out
