"""Tests for the ReAct loop module."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from mcp_agent_base.core.react_loop import (
    load_agent_response_schema,
    validate_response,
    agent_react_step,
    ToolClient,
)


class TestLoadAgentResponseSchema:
    """Tests for load_agent_response_schema function."""

    def test_loads_schema(self):
        """Test that schema is loaded successfully."""
        schema = load_agent_response_schema()

        assert "$schema" in schema
        assert "properties" in schema
        assert "answer" in schema["properties"]
        assert "tool_calls" in schema["properties"]
        assert "reasoning" in schema["properties"]


class TestValidateResponse:
    """Tests for validate_response function."""

    def test_valid_with_answer(self):
        """Test validation passes with answer."""
        response = {"answer": "Test answer"}
        schema = {}

        assert validate_response(response, schema) is True

    def test_valid_with_tool_calls(self):
        """Test validation passes with tool_calls."""
        response = {"tool_calls": [{"tool_name": "test", "arguments": {}}]}
        schema = {}

        assert validate_response(response, schema) is True

    def test_valid_with_routing(self):
        """Test validation passes with routing."""
        response = {"routing": "NEXT_AGENT"}
        schema = {}

        assert validate_response(response, schema) is True

    def test_invalid_empty_response(self):
        """Test validation fails with empty response."""
        response = {}
        schema = {}

        assert validate_response(response, schema) is False

    def test_invalid_only_reasoning(self):
        """Test validation fails with only reasoning."""
        response = {"reasoning": "Just thinking"}
        schema = {}

        assert validate_response(response, schema) is False


class TestToolClient:
    """Tests for ToolClient class."""

    def test_init(self):
        """Test ToolClient initialization."""
        tools = [{"name": "test"}]
        executor = lambda n, a: "result"

        client = ToolClient(tools, executor)

        assert client.tools == tools
        assert client.tool_executor == executor

    @pytest.mark.asyncio
    async def test_call_tool(self):
        """Test calling a tool."""
        executor = lambda n, a: f"Executed {n}"
        client = ToolClient([], executor)

        result = await client.call_tool(None, "test_tool", {})

        assert result == "Executed test_tool"

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using as async context manager."""
        client = ToolClient([], lambda n, a: "")

        async with client as session:
            assert session is client


class TestAgentReactStep:
    """Tests for agent_react_step function."""

    @pytest.mark.asyncio
    async def test_returns_answer_when_provided(self):
        """Test that loop returns when answer is provided."""
        mock_client = AsyncMock()
        mock_client.session.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.session.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_llm = MagicMock()
        mock_llm.call.return_value = {"answer": "Final answer"}

        conversation = ["USER: Test"]

        answer, routing = await agent_react_step(
            mock_client,
            "System prompt",
            conversation,
            "TestAgent",
            mock_llm,
        )

        assert answer == "Final answer"
        assert routing is None

    @pytest.mark.asyncio
    async def test_executes_tool_calls(self):
        """Test that tool calls are executed."""
        mock_client = AsyncMock()
        mock_client.session.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.call_tool = AsyncMock(return_value="Tool result")

        mock_llm = MagicMock()
        mock_llm.call.side_effect = [
            {"tool_calls": [{"tool_name": "test", "arguments": {}}]},
            {"answer": "Done"},
        ]

        conversation = ["USER: Test"]

        answer, routing = await agent_react_step(
            mock_client,
            "System prompt",
            conversation,
            "TestAgent",
            mock_llm,
        )

        mock_client.call_tool.assert_called_once()
        assert "Tool Call:" in conversation[-3]
        assert "Tool Result:" in conversation[-2]

    @pytest.mark.asyncio
    async def test_handles_reasoning(self):
        """Test that reasoning is added to conversation."""
        mock_client = AsyncMock()
        mock_client.session.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.session.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_llm = MagicMock()
        mock_llm.call.side_effect = [
            {"reasoning": "Thinking about this...", "tool_calls": []},
            {"answer": "Done"},
        ]

        conversation = ["USER: Test"]

        await agent_react_step(
            mock_client,
            "System prompt",
            conversation,
            "TestAgent",
            mock_llm,
        )

        assert any("Reasoning:" in msg for msg in conversation)

    @pytest.mark.asyncio
    async def test_returns_routing_with_answer(self):
        """Test that routing is returned with answer."""
        mock_client = AsyncMock()
        mock_client.session.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.session.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_llm = MagicMock()
        mock_llm.call.return_value = {"answer": "Done", "routing": "NEXT_AGENT"}

        conversation = ["USER: Test"]

        answer, routing = await agent_react_step(
            mock_client,
            "System prompt",
            conversation,
            "TestAgent",
            mock_llm,
        )

        assert answer == "Done"
        assert routing == "NEXT_AGENT"
