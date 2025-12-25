"""Shared pytest fixtures for mcp-agent-base tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_llm_response():
    """Standard mock LLM response with tool calls."""
    return {
        "reasoning": "I need to check the git status first.",
        "tool_calls": [
            {
                "tool_name": "git_cli_git_status",
                "arguments": {"porcelain": True},
            }
        ],
    }


@pytest.fixture
def mock_llm_answer():
    """Mock LLM response with final answer."""
    return {
        "answer": "Successfully pushed changes to the repository.",
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock = MagicMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"answer": "Test response"}'))]
    )
    return mock


@pytest.fixture
def mock_mcp_session():
    """Mock MCP session."""
    session = AsyncMock()
    session.initialize = AsyncMock()
    session.list_tools = AsyncMock(return_value=MagicMock(tools=[]))
    session.call_tool = AsyncMock(return_value=MagicMock(content=[]))
    return session


@pytest.fixture
def sample_tools():
    """Sample tool definitions for testing."""
    return [
        {
            "name": "git_status",
            "description": "Show the working tree status",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "porcelain": {"type": "boolean", "default": True},
                },
            },
        },
        {
            "name": "git_add",
            "description": "Add file contents to the index",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "files": {"type": "array", "items": {"type": "string"}},
                    "all": {"type": "boolean", "default": False},
                },
            },
        },
    ]


@pytest.fixture
def sample_state():
    """Sample agent state for testing."""
    return {
        "conversation_history": ["USER: Check git status"],
        "errors": [],
        "warnings": [],
    }
