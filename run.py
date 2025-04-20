#!/usr/bin/env python
"""
Main entry point for the Google ADK Agent Starter Kit.

This script runs the command-line interface for the starter kit.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the CLI module
from src.cli import main

if __name__ == "__main__":
    # Run the CLI
    main()
