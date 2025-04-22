#!/usr/bin/env python
"""
Launcher script for direct deployment to Vertex AI Agent Engine.

This script forwards command line arguments to the implementation in 
src/deployment/direct_deploy.py.

For usage instructions, run:
    python direct_deploy.py --help
"""

import sys
from src.deployment.direct_deploy import main

if __name__ == "__main__":
    sys.exit(main()) 