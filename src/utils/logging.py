"""
Logging utilities for the Google ADK Agent Starter Kit.

This module provides utilities for configuring logging.
"""

import logging
import sys
import os
from typing import Optional, Union, TextIO

from ..config import LOG_LEVEL, DEV_MODE

# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Development log format (more verbose)
DEV_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"


def configure_logging(
    level: Optional[Union[int, str]] = None,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
    stream: Optional[TextIO] = None,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: The log level (default: from config).
        format_string: The log format string (default: based on DEV_MODE).
        log_file: Path to a log file (default: None).
        stream: Stream to log to (default: sys.stdout).
    """
    # Get log level from config if not provided
    if level is None:
        level = LOG_LEVEL
    
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Get format string based on DEV_MODE if not provided
    if format_string is None:
        format_string = DEV_FORMAT if DEV_MODE else DEFAULT_FORMAT
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Add stream handler
    if stream is None:
        stream = sys.stdout
    
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure google.adk logger
    adk_logger = logging.getLogger("google.adk")
    adk_logger.setLevel(level)
    
    # Configure our package logger
    package_logger = logging.getLogger("src")
    package_logger.setLevel(level)
    
    # Log configuration
    package_logger.info(f"Logging configured with level: {logging.getLevelName(level)}")
    if log_file:
        package_logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: The name of the logger.

    Returns:
        A logger instance.
    """
    return logging.getLogger(name)
