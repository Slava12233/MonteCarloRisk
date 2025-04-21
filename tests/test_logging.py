"""
Unit tests for the logging utility module.
"""

import os
import sys
import pytest
import logging
from unittest.mock import patch, MagicMock, mock_open, call

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import the module to test
from src.utils import logging as logging_util
from src import config # To patch DEV_MODE

# --- Fixtures ---

@pytest.fixture(autouse=True)
def reset_logging_state():
    """Reset logging configuration before and after each test."""
    # Store original handlers
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    yield # Run test

    # Restore original state
    root_logger.handlers = original_handlers
    root_logger.setLevel(original_level)
    # Reset levels for specific loggers if modified (optional, depends on test needs)
    logging.getLogger("google.adk").setLevel(logging.NOTSET)
    logging.getLogger("src").setLevel(logging.NOTSET)


# --- Test Cases for configure_logging ---

@patch('src.utils.logging.logging.StreamHandler')
@patch('src.utils.logging.logging.FileHandler')
def test_configure_logging_defaults(mock_file_handler, mock_stream_handler, monkeypatch):
    """Test configure_logging with default settings (non-dev mode)."""
    # Configure mock handlers to have a default level
    mock_stream_handler.return_value.level = logging.NOTSET
    mock_file_handler.return_value.level = logging.NOTSET

    # Patch DEV_MODE directly in the logging_util module
    monkeypatch.setattr(logging_util, 'DEV_MODE', False)
    # Patch LOG_LEVEL in the config module as it's read within the function
    monkeypatch.setattr(config, 'LOG_LEVEL', 'INFO')

    logging_util.configure_logging()

    # Check root logger level
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO

    # Check StreamHandler setup
    mock_stream_handler.assert_called_once_with(sys.stdout)
    stream_handler_instance = mock_stream_handler.return_value
    stream_handler_instance.setFormatter.assert_called_once()
    formatter_args = stream_handler_instance.setFormatter.call_args[0][0]
    assert formatter_args._fmt == logging_util.DEFAULT_FORMAT

    # Check FileHandler was not called
    mock_file_handler.assert_not_called()

    # Check specific logger levels
    assert logging.getLogger("google.adk").level == logging.INFO
    assert logging.getLogger("src").level == logging.INFO


@patch('src.utils.logging.logging.StreamHandler')
@patch('src.utils.logging.logging.FileHandler')
def test_configure_logging_dev_mode(mock_file_handler, mock_stream_handler, monkeypatch):
    """Test configure_logging with DEV_MODE enabled."""
    mock_stream_handler.return_value.level = logging.NOTSET
    mock_file_handler.return_value.level = logging.NOTSET

    # Patch DEV_MODE directly in the logging_util module
    monkeypatch.setattr(logging_util, 'DEV_MODE', True)
    monkeypatch.setattr(config, 'LOG_LEVEL', 'INFO')

    logging_util.configure_logging()

    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO

    # Check StreamHandler setup with DEV_FORMAT
    mock_stream_handler.assert_called_once_with(sys.stdout)
    stream_handler_instance = mock_stream_handler.return_value
    stream_handler_instance.setFormatter.assert_called_once()
    formatter_args = stream_handler_instance.setFormatter.call_args[0][0]
    assert formatter_args._fmt == logging_util.DEV_FORMAT


@patch('src.utils.logging.logging.StreamHandler')
@patch('src.utils.logging.logging.FileHandler')
def test_configure_logging_custom_level(mock_file_handler, mock_stream_handler, monkeypatch):
    """Test configure_logging with a custom level (DEBUG)."""
    mock_stream_handler.return_value.level = logging.NOTSET
    mock_file_handler.return_value.level = logging.NOTSET

    # Patch DEV_MODE directly in the logging_util module
    monkeypatch.setattr(logging_util, 'DEV_MODE', False)
    # LOG_LEVEL in config is not used when level is passed directly

    logging_util.configure_logging(level='DEBUG')

    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG
    assert logging.getLogger("google.adk").level == logging.DEBUG
    assert logging.getLogger("src").level == logging.DEBUG


@patch('src.utils.logging.logging.StreamHandler')
@patch('src.utils.logging.logging.FileHandler')
def test_configure_logging_custom_format(mock_file_handler, mock_stream_handler, monkeypatch):
    """Test configure_logging with a custom format string."""
    mock_stream_handler.return_value.level = logging.NOTSET
    mock_file_handler.return_value.level = logging.NOTSET

    # Patch DEV_MODE directly in the logging_util module
    monkeypatch.setattr(logging_util, 'DEV_MODE', False)
    custom_format = "%(levelname)s::%(message)s"

    logging_util.configure_logging(format_string=custom_format)

    mock_stream_handler.assert_called_once_with(sys.stdout)
    stream_handler_instance = mock_stream_handler.return_value
    stream_handler_instance.setFormatter.assert_called_once()
    formatter_args = stream_handler_instance.setFormatter.call_args[0][0]
    assert formatter_args._fmt == custom_format


@patch('src.utils.logging.logging.StreamHandler')
@patch('src.utils.logging.logging.FileHandler')
@patch('src.utils.logging.os.makedirs')
@patch('src.utils.logging.os.path.exists')
@patch('builtins.open', new_callable=mock_open) # Mock open for file handler
def test_configure_logging_with_file(
    mock_open_call, mock_path_exists, mock_makedirs, mock_file_handler, mock_stream_handler, monkeypatch
):
    """Test configure_logging with a log file specified."""
    mock_stream_handler.return_value.level = logging.NOTSET
    mock_file_handler.return_value.level = logging.NOTSET

    # Patch DEV_MODE directly in the logging_util module
    monkeypatch.setattr(logging_util, 'DEV_MODE', False)
    log_file_path = "/var/log/test_agent.log"
    log_dir = "/var/log"
    mock_path_exists.return_value = False # Simulate directory doesn't exist

    logging_util.configure_logging(log_file=log_file_path)

    # Check directory creation
    mock_path_exists.assert_called_once_with(log_dir)
    mock_makedirs.assert_called_once_with(log_dir)

    # Check FileHandler setup
    mock_file_handler.assert_called_once_with(log_file_path)
    file_handler_instance = mock_file_handler.return_value
    file_handler_instance.setFormatter.assert_called_once()
    formatter_args = file_handler_instance.setFormatter.call_args[0][0]
    assert formatter_args._fmt == logging_util.DEFAULT_FORMAT

    # Check StreamHandler is also added
    mock_stream_handler.assert_called_once()

    # Check root logger has both handlers
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) >= 2 # Should have at least stream and file


@patch('src.utils.logging.logging.StreamHandler')
@patch('src.utils.logging.logging.FileHandler')
@patch('src.utils.logging.os.makedirs')
@patch('src.utils.logging.os.path.exists')
@patch('builtins.open', new_callable=mock_open)
def test_configure_logging_with_file_dir_exists(
    mock_open_call, mock_path_exists, mock_makedirs, mock_file_handler, mock_stream_handler, monkeypatch
):
    """Test configure_logging with a log file where directory exists."""
    mock_stream_handler.return_value.level = logging.NOTSET
    mock_file_handler.return_value.level = logging.NOTSET

    # Patch DEV_MODE directly in the logging_util module
    monkeypatch.setattr(logging_util, 'DEV_MODE', False)
    log_file_path = "/var/log/test_agent.log"
    log_dir = "/var/log"
    mock_path_exists.return_value = True # Simulate directory exists

    logging_util.configure_logging(log_file=log_file_path)

    # Check directory creation was NOT called
    mock_path_exists.assert_called_once_with(log_dir)
    mock_makedirs.assert_not_called()

    # Check FileHandler setup
    mock_file_handler.assert_called_once_with(log_file_path)


# --- Test for get_logger ---

def test_get_logger():
    """Test get_logger returns a logger instance."""
    logger_name = "my_test_logger"
    logger = logging_util.get_logger(logger_name)
    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
