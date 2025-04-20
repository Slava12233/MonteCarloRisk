from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements from requirements.txt
with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if not line.startswith("#") and line.strip()]

setup(
    name="google-adk-starter-kit",
    version="0.1.0",
    description="A minimal, extensible starter kit for building AI agents with Google's Agent Development Kit (ADK)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Organization",
    author_email="your.email@example.com",
    url="https://github.com/your-organization/agent-starter-kit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="google, adk, agent, ai, vertex, gemini",
    project_urls={
        "Documentation": "https://github.com/your-organization/agent-starter-kit/blob/main/README.md",
        "Source": "https://github.com/your-organization/agent-starter-kit",
        "Tracker": "https://github.com/your-organization/agent-starter-kit/issues",
    },
    entry_points={
        "console_scripts": [
            "adk-starter=src.cli:main",
        ],
    },
)
