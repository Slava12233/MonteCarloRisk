"""
Unit tests for custom tools.

This module contains unit tests for the custom tools implementation.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.custom_tools import create_custom_tool, CustomToolBuilder


class TestCreateCustomTool(unittest.TestCase):
    """Tests for the create_custom_tool function."""

    def test_create_custom_tool_basic(self):
        """Test creating a custom tool with basic function."""
        # Define a simple function
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        # Create a tool from the function
        tool = create_custom_tool(add)
        
        # Check that the function works
        result = tool.func(2, 3)
        self.assertEqual(result, 5)
        
        # Check the function name and docstring
        self.assertEqual(tool.func.__name__, "add")
        self.assertEqual(tool.func.__doc__, "Add two numbers.")

    def test_create_custom_tool_with_custom_name_and_description(self):
        """Test creating a custom tool with custom name and description."""
        # Define a simple function
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b
        
        # Create a tool from the function with custom name and description
        tool = create_custom_tool(
            multiply,
            name="multiplication_tool",
            description="A tool for multiplying numbers",
        )
        
        # Check the function name and docstring
        self.assertEqual(tool.func.__name__, "multiplication_tool")
        self.assertEqual(tool.func.__doc__, "A tool for multiplying numbers")
        
        # Check that the function works
        result = tool.func(2, 3)
        self.assertEqual(result, 6)

    def test_create_custom_tool_with_default_values(self):
        """Test creating a custom tool with default parameter values."""
        # Define a function with default values
        def greet(name: str, greeting: str = "Hello") -> str:
            """Greet someone."""
            return f"{greeting}, {name}!"
        
        # Create a tool from the function
        tool = create_custom_tool(greet)
        
        # Check that the function works with default value
        result = tool.func("World")
        self.assertEqual(result, "Hello, World!")
        
        # Check that the function works with custom value
        result = tool.func("World", "Hi")
        self.assertEqual(result, "Hi, World!")


class TestCustomToolBuilder(unittest.TestCase):
    """Tests for the CustomToolBuilder class."""

    def test_builder_basic(self):
        """Test creating a tool with the builder pattern."""
        # Create a tool with the builder
        tool = (
            CustomToolBuilder("echo")
            .description("Echo the input")
            .set_handler(lambda message="Hello, world!": message)
            .build()
        )
        
        # Check the function name and docstring
        self.assertEqual(tool.func.__name__, "echo")
        self.assertEqual(tool.func.__doc__, "Echo the input")
        
        # Check that the function works
        result = tool.func("Hello, world!")
        self.assertEqual(result, "Hello, world!")

    def test_builder_with_multiple_parameters(self):
        """Test creating a tool with multiple parameters."""
        # Create a tool with the builder
        tool = (
            CustomToolBuilder("format_name")
            .description("Format a name")
            .set_handler(lambda first_name, last_name, title="Mr.": f"{title} {first_name} {last_name}")
            .build()
        )
        
        # Check the function name and docstring
        self.assertEqual(tool.func.__name__, "format_name")
        self.assertEqual(tool.func.__doc__, "Format a name")
        
        # Check that the function works with default value
        result = tool.func("John", "Doe")
        self.assertEqual(result, "Mr. John Doe")
        
        # Check that the function works with custom value
        result = tool.func("Jane", "Doe", "Dr.")
        self.assertEqual(result, "Dr. Jane Doe")

    def test_builder_missing_handler(self):
        """Test that building a tool without a handler raises an error."""
        # Create a builder without setting a handler
        builder = (
            CustomToolBuilder("test")
            .description("Test tool")
        )
        
        # Check that building without a handler raises an error
        with self.assertRaises(ValueError):
            builder.build()


if __name__ == "__main__":
    unittest.main()
