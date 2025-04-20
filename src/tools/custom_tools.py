"""
Custom tools template for the Google ADK Agent Starter Kit.

This module provides templates and utilities for creating custom tools.
"""

import logging
from typing import Any, Dict, List, Optional, Callable, TypeVar, cast
import inspect
import functools

from google.adk.tools import FunctionTool

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for function return type
T = TypeVar("T")


def create_custom_tool(
    func: Callable[..., T],
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> FunctionTool:
    """
    Create a custom tool from a function.

    This utility function creates a FunctionTool from a Python function.

    Args:
        func: The function to convert to a tool.
        name: The name of the tool (default: function name).
        description: The description of the tool (default: function docstring).

    Returns:
        A FunctionTool that can be used with an agent.

    Example:
        ```python
        def get_weather(location: str, units: str = "metric") -> str:
            \"\"\"Get the current weather for a location.\"\"\"
            # Implementation...
            return f"The weather in {location} is sunny and 25°C."

        weather_tool = create_custom_tool(get_weather)
        ```
    """
    # If name or description is provided, create a wrapper function with the updated metadata
    if name or description:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Update the wrapper's metadata
        if name:
            wrapper.__name__ = name
        if description:
            wrapper.__doc__ = description
        
        # Create the tool with the wrapper
        return FunctionTool(wrapper)
    
    # If no customization is needed, create the tool directly
    return FunctionTool(func)


class CustomToolBuilder:
    """
    Builder for creating custom tools.

    This class provides a fluent interface for creating custom tools with
    more control over the behavior.

    Example:
        ```python
        weather_tool = (
            CustomToolBuilder("get_weather")
            .description("Get the current weather for a location.")
            .set_handler(lambda location="New York", units="metric": f"The weather in {location} is sunny and 25°C.")
            .build()
        )
        ```
    """

    def __init__(self, name: str):
        """
        Initialize a new CustomToolBuilder.

        Args:
            name: The name of the tool.
        """
        self.name = name
        self.tool_description = f"Run the {name} function."
        self.handler = None

    def description(self, description: str) -> "CustomToolBuilder":
        """
        Set the description of the tool.

        Args:
            description: The description of the tool.

        Returns:
            The builder instance for method chaining.
        """
        self.tool_description = description
        return self

    def set_handler(self, handler: Callable) -> "CustomToolBuilder":
        """
        Set the handler function for the tool.

        Args:
            handler: The function that will be called when the tool is used.

        Returns:
            The builder instance for method chaining.
        """
        self.handler = handler
        return self

    def build(self) -> FunctionTool:
        """
        Build the tool.

        Returns:
            The built FunctionTool instance.

        Raises:
            ValueError: If no handler is set.
        """
        if not self.handler:
            raise ValueError("No handler set for the tool.")

        # Create a function with the specified name and description
        def wrapper(*args, **kwargs):
            return self.handler(*args, **kwargs)
        
        wrapper.__name__ = self.name
        wrapper.__doc__ = self.tool_description
        
        # Create the tool
        return FunctionTool(wrapper)


# Example custom tool implementation
def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current time in a specific timezone.

    Args:
        timezone: The timezone to get the time for (default: UTC).

    Returns:
        The current time in the specified timezone.
    """
    # This is a placeholder implementation
    # In a real implementation, you would use a library like pytz or datetime
    return f"The current time in {timezone} is 12:00 PM."


# Example of creating a custom tool
current_time_tool = create_custom_tool(get_current_time)
