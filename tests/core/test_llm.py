"""Tests for the LLM client module."""

import json
import pytest
from unittest.mock import MagicMock, patch

from mcp_agent_base.core.llm import LLMClient, create_llm_client


class TestLLMClient:
    """Tests for LLMClient class."""

    def test_init(self):
        """Test LLMClient initialization."""
        with patch("mcp_agent_base.core.llm.AzureOpenAI") as mock_azure:
            client = LLMClient(
                endpoint="https://test.openai.azure.com",
                api_key="test-key",
                deployment="gpt-4o",
                api_version="2025-04-01-preview",
                temperature=0.1,
            )

            mock_azure.assert_called_once_with(
                azure_endpoint="https://test.openai.azure.com",
                api_key="test-key",
                api_version="2025-04-01-preview",
            )
            assert client.deployment == "gpt-4o"
            assert client.temperature == 0.1

    def test_call_returns_parsed_json(self):
        """Test that call() returns parsed JSON response."""
        with patch("mcp_agent_base.core.llm.AzureOpenAI") as mock_azure:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content='{"answer": "test"}'))
            ]
            mock_azure.return_value.chat.completions.create.return_value = mock_response

            client = LLMClient(
                endpoint="https://test.openai.azure.com",
                api_key="test-key",
                deployment="gpt-4o",
            )

            result = client.call("System prompt", "User message")

            assert result == {"answer": "test"}

    def test_call_with_schema(self):
        """Test that call() uses json_object format when schema provided."""
        with patch("mcp_agent_base.core.llm.AzureOpenAI") as mock_azure:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content='{"tool_calls": []}'))
            ]
            mock_azure.return_value.chat.completions.create.return_value = mock_response

            client = LLMClient(
                endpoint="https://test.openai.azure.com",
                api_key="test-key",
                deployment="gpt-4o",
            )

            schema = {"type": "object", "properties": {"answer": {"type": "string"}}}
            result = client.call("System prompt", "User message", schema=schema)

            call_kwargs = mock_azure.return_value.chat.completions.create.call_args
            assert call_kwargs.kwargs["response_format"] == {"type": "json_object"}

    def test_call_raises_on_empty_response(self):
        """Test that call() raises ValueError on empty response."""
        with patch("mcp_agent_base.core.llm.AzureOpenAI") as mock_azure:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content=None))]
            mock_azure.return_value.chat.completions.create.return_value = mock_response

            client = LLMClient(
                endpoint="https://test.openai.azure.com",
                api_key="test-key",
                deployment="gpt-4o",
            )

            with pytest.raises(ValueError, match="Empty response"):
                client.call("System prompt", "User message")

    def test_call_raises_on_invalid_json(self):
        """Test that call() raises ValueError on invalid JSON response."""
        with patch("mcp_agent_base.core.llm.AzureOpenAI") as mock_azure:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content="not valid json"))
            ]
            mock_azure.return_value.chat.completions.create.return_value = mock_response

            client = LLMClient(
                endpoint="https://test.openai.azure.com",
                api_key="test-key",
                deployment="gpt-4o",
            )

            with pytest.raises(ValueError, match="Failed to parse"):
                client.call("System prompt", "User message")


class TestCreateLLMClient:
    """Tests for create_llm_client factory function."""

    def test_creates_client_with_defaults(self):
        """Test factory function creates client with default values."""
        with patch("mcp_agent_base.core.llm.AzureOpenAI"):
            client = create_llm_client(
                endpoint="https://test.openai.azure.com",
                api_key="test-key",
                deployment="gpt-4o",
            )

            assert isinstance(client, LLMClient)
            assert client.temperature == 0.1

    def test_creates_client_with_custom_values(self):
        """Test factory function creates client with custom values."""
        with patch("mcp_agent_base.core.llm.AzureOpenAI"):
            client = create_llm_client(
                endpoint="https://test.openai.azure.com",
                api_key="test-key",
                deployment="gpt-4o",
                api_version="2024-01-01",
                temperature=0.5,
            )

            assert client.temperature == 0.5
