"""Tests for the MCP client module."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from mcp_agent_base.core.mcp_client import MCPClient, MultiMCPClient


class TestMCPClient:
    """Tests for MCPClient class."""

    def test_init(self):
        """Test MCPClient initialization."""
        client = MCPClient(
            mcp_args=["run", "-i", "test-image"],
            mcp_env={"TOKEN": "test"},
            mcp_command="docker",
        )

        assert client.mcp_args == ["run", "-i", "test-image"]
        assert client.mcp_env == {"TOKEN": "test"}
        assert client.mcp_command == "docker"
        assert client.tools_cache is None
        assert client.custom_tools == []

    def test_extend_tools(self):
        """Test extending client with custom tools."""
        client = MCPClient(mcp_args=[], mcp_env={})

        custom_tools = [{"name": "custom_tool", "description": "A custom tool"}]
        client.extend_tools(custom_tools)

        assert len(client.custom_tools) == 1
        assert client.custom_tools[0]["name"] == "custom_tool"

    def test_is_custom_tool(self):
        """Test checking if tool is custom."""
        client = MCPClient(mcp_args=[], mcp_env={})
        client.custom_tools = [{"name": "custom_tool"}]

        assert client._is_custom_tool("custom_tool") is True
        assert client._is_custom_tool("other_tool") is False

    def test_set_custom_tool_executor(self):
        """Test setting custom tool executor."""
        client = MCPClient(mcp_args=[], mcp_env={})

        def executor(name, args):
            return "result"

        client.set_custom_tool_executor(executor)

        assert client.custom_tool_executor == executor


class TestMultiMCPClient:
    """Tests for MultiMCPClient class."""

    def test_init(self):
        """Test MultiMCPClient initialization."""
        client = MultiMCPClient()

        assert client.servers == {}
        assert client.custom_tools == {}
        assert client.custom_executors == {}
        assert client._tools_cache is None

    def test_add_server(self):
        """Test adding MCP server."""
        client = MultiMCPClient()

        client.add_server(
            name="github",
            mcp_args=["run", "-i", "github-server"],
            mcp_env={"TOKEN": "test"},
            mcp_command="docker",
        )

        assert "github" in client.servers
        assert client._tools_cache is None  # Cache invalidated

    def test_add_custom_tools(self):
        """Test adding custom tools with executor."""
        client = MultiMCPClient()

        tools = [
            {"name": "git_status", "description": "Show status"},
            {"name": "git_add", "description": "Add files"},
        ]

        def executor(name, args):
            return f"Executed {name}"

        client.add_custom_tools("git_cli", tools, executor)

        assert "git_cli_git_status" in client.custom_tools
        assert "git_cli_git_add" in client.custom_tools
        assert "git_cli" in client.custom_executors
        assert client._tools_cache is None  # Cache invalidated

    def test_custom_tool_name_prefixing(self):
        """Test that custom tools get proper prefix."""
        client = MultiMCPClient()

        tools = [{"name": "status", "description": "Show status"}]
        client.add_custom_tools("git", tools, lambda n, a: "")

        tool_info = client.custom_tools["git_status"]
        assert tool_info["name"] == "git_status"
        assert tool_info["original_name"] == "status"
        assert tool_info["prefix"] == "git"

    @pytest.mark.asyncio
    async def test_list_tools_returns_custom_tools(self):
        """Test that list_tools returns custom tools."""
        client = MultiMCPClient()

        tools = [{"name": "test", "description": "Test tool", "inputSchema": {}}]
        client.add_custom_tools("prefix", tools, lambda n, a: "")

        result = await client.list_tools()

        assert len(result) == 1
        assert result[0]["name"] == "prefix_test"

    @pytest.mark.asyncio
    async def test_list_tools_caches_results(self):
        """Test that list_tools caches results."""
        client = MultiMCPClient()

        tools = [{"name": "test", "description": "Test", "inputSchema": {}}]
        client.add_custom_tools("prefix", tools, lambda n, a: "")

        await client.list_tools()
        assert client._tools_cache is not None

        # Modify and check cache is used
        client.custom_tools["new_tool"] = {"name": "new"}
        result = await client.list_tools()
        assert len(result) == 1  # Still 1 because cached

    @pytest.mark.asyncio
    async def test_call_tool_custom(self):
        """Test calling a custom tool."""
        client = MultiMCPClient()

        def executor(name, args):
            return f"Executed {name} with {args}"

        tools = [{"name": "test", "description": "Test"}]
        client.add_custom_tools("prefix", tools, executor)

        result = await client.call_tool(None, "prefix_test", {"arg": "value"})

        assert "Executed test" in result
        assert "arg" in result

    @pytest.mark.asyncio
    async def test_call_tool_not_found(self):
        """Test calling non-existent tool."""
        client = MultiMCPClient()

        result = await client.call_tool(None, "nonexistent_tool", {})

        assert "not found" in result
