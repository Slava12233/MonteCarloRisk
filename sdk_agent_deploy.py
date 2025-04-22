#!/usr/bin/env python
"""
Launcher script for the SDK-based Agent Engine management tools.

This script forwards command line arguments to the implementation in 
src/deployment/sdk_agent_deploy.py.

For usage instructions, run:
    python sdk_agent_deploy.py --help
"""

import sys
from src.deployment.sdk_agent_deploy import main

if __name__ == "__main__":
    main(sys.argv[1:]) 