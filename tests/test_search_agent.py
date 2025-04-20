"""
Unit tests for the search agent.

This module contains unit tests for the search agent implementation.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.search_agent import SearchAgent


class TestSearchAgent(unittest.TestCase):
    """Tests for the SearchAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the google_search tool
        self.google_search_patch = patch("src.agents.search_agent.google_search")
        self.mock_google_search = self.google_search_patch.start()
        
        # Create a mock for the Runner.run method
        self.runner_run_patch = patch("src.agents.base_agent.Runner")
        self.mock_runner = self.runner_run_patch.start()
        self.mock_runner_instance = MagicMock()
        self.mock_runner.return_value = self.mock_runner_instance
        
        # Create a mock for the validate_config function to avoid configuration errors
        self.validate_config_patch = patch("src.agents.base_agent.validate_config")
        self.mock_validate_config = self.validate_config_patch.start()
        self.mock_validate_config.return_value = None  # No error
        
        # Create a mock for the LlmAgent
        self.llm_agent_patch = patch("src.agents.base_agent.LlmAgent")
        self.mock_llm_agent = self.llm_agent_patch.start()
        
        # Set up mock events
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = True
        mock_event.content.parts = [MagicMock(text="Mock response")]
        self.mock_runner_instance.run.return_value = [mock_event]
        
        # Create a mock for DEV_MODE
        self.dev_mode_patch = patch("src.agents.base_agent.DEV_MODE", True)
        self.mock_dev_mode = self.dev_mode_patch.start()
        
        # Create the agent
        self.agent = SearchAgent(
            name="test_search_agent",
            description="Test search agent",
            instruction="Test instruction",
        )

    def tearDown(self):
        """Tear down test fixtures."""
        self.google_search_patch.stop()
        self.runner_run_patch.stop()
        self.validate_config_patch.stop()
        self.llm_agent_patch.stop()
        self.dev_mode_patch.stop()

    def test_init(self):
        """Test initialization of the SearchAgent."""
        self.assertEqual(self.agent.name, "test_search_agent")
        self.assertEqual(self.agent.description, "Test search agent")
        self.assertEqual(self.agent._instruction, "Test instruction")
        self.assertEqual(len(self.agent._tools), 1)  # Should have google_search tool

    def test_search(self):
        """Test the search method."""
        # Call the search method
        response = self.agent.search("test query")
        
        # Check that the runner.run method was called with the correct arguments
        self.mock_runner_instance.run.assert_called_once()
        args, kwargs = self.mock_runner_instance.run.call_args
        self.assertEqual(kwargs["user_id"], "user")
        self.assertEqual(kwargs["session_id"], "session")
        
        # Check that the response is correct
        self.assertEqual(response, "Mock response")

    def test_search_with_custom_user_and_session(self):
        """Test the search method with custom user and session IDs."""
        # Call the search method with custom user and session IDs
        response = self.agent.search("test query", user_id="custom_user", session_id="custom_session")
        
        # Check that the runner.run method was called with the correct arguments
        self.mock_runner_instance.run.assert_called_once()
        args, kwargs = self.mock_runner_instance.run.call_args
        self.assertEqual(kwargs["user_id"], "custom_user")
        self.assertEqual(kwargs["session_id"], "custom_session")
        
        # Check that the response is correct
        self.assertEqual(response, "Mock response")

    def test_search_no_response(self):
        """Test the search method when there is no response."""
        # Set up mock events with no final response
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = False
        self.mock_runner_instance.run.return_value = [mock_event]
        
        # Call the search method
        response = self.agent.search("test query")
        
        # Check that the response is the default message
        self.assertEqual(response, "No response from the agent.")


if __name__ == "__main__":
    unittest.main()
