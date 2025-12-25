"""Tests for the GitAgent module."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from mcp_agent_base.agents.git_agent import GitAgent


class TestGitAgent:
    """Tests for GitAgent class."""

    def test_init_default(self):
        """Test GitAgent initialization with defaults."""
        mock_llm = MagicMock()

        agent = GitAgent(llm_client=mock_llm)

        assert agent.llm_client == mock_llm
        assert agent.agent_name == "GitAgent"
        assert agent.use_github_mcp_server is False

    def test_init_custom_name(self):
        """Test GitAgent initialization with custom name."""
        mock_llm = MagicMock()

        agent = GitAgent(llm_client=mock_llm, agent_name="CustomAgent")

        assert agent.agent_name == "CustomAgent"

    def test_init_with_github_mcp_server(self):
        """Test GitAgent initialization with GitHub MCP server enabled."""
        mock_llm = MagicMock()

        agent = GitAgent(llm_client=mock_llm, use_github_mcp_server=True)

        assert agent.use_github_mcp_server is True

    def test_format_tools(self):
        """Test _format_tools method."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm)

        tools = [
            {"name": "git_status", "description": "Show status"},
            {"name": "git_add", "description": "Add files"},
        ]

        result = agent._format_tools(tools)

        assert "git_status" in result
        assert "git_add" in result
        assert "Show status" in result
        assert "Add files" in result

    def test_setup_tools_adds_git_cli(self):
        """Test that setup_tools adds git CLI tools."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm)

        with patch.object(agent.mcp_client, "add_custom_tools") as mock_add:
            agent.setup_tools()

            # Check that git_cli tools were added
            calls = mock_add.call_args_list
            prefixes = [call[0][0] for call in calls]
            assert "git_cli" in prefixes

    def test_setup_tools_adds_github_env(self):
        """Test that setup_tools adds GitHub env tools."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm)

        with patch.object(agent.mcp_client, "add_custom_tools") as mock_add:
            agent.setup_tools()

            calls = mock_add.call_args_list
            prefixes = [call[0][0] for call in calls]
            assert "github_env" in prefixes

    def test_setup_tools_adds_github_server_when_enabled(self):
        """Test that setup_tools adds GitHub MCP server when enabled."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm, use_github_mcp_server=True)

        with patch.dict("os.environ", {"GITHUB_PERSONAL_ACCESS_TOKEN": "test-token"}):
            with patch.object(agent.mcp_client, "add_custom_tools"):
                with patch.object(agent.mcp_client, "add_server") as mock_add_server:
                    agent.setup_tools()

                    mock_add_server.assert_called_once()
                    call_kwargs = mock_add_server.call_args
                    assert call_kwargs[1]["name"] == "github"

    def test_setup_tools_skips_github_server_without_token(self):
        """Test that GitHub MCP server is skipped without token."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm, use_github_mcp_server=True)

        with patch.dict("os.environ", {}, clear=True):
            with patch.object(agent.mcp_client, "add_custom_tools"):
                with patch.object(agent.mcp_client, "add_server") as mock_add_server:
                    agent.setup_tools()

                    mock_add_server.assert_not_called()

    def test_get_system_prompt(self):
        """Test get_system_prompt method."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm)

        tools = [{"name": "test_tool", "description": "A test tool"}]

        with patch(
            "mcp_agent_base.agents.git_agent.template_loader"
        ) as mock_loader:
            mock_template = MagicMock()
            mock_template.render.return_value = "Rendered prompt"
            mock_loader.load_prompt_template.return_value = mock_template

            result = agent.get_system_prompt(tools)

            mock_loader.load_prompt_template.assert_called_with("git_agent")
            mock_template.render.assert_called_once()
            assert result == "Rendered prompt"

    @pytest.mark.asyncio
    async def test_run_async(self):
        """Test run_async method."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm)

        state = {"conversation_history": ["USER: Test"], "errors": [], "warnings": []}

        with patch.object(agent, "setup_tools"):
            with patch.object(agent.mcp_client, "session") as mock_session:
                with patch.object(agent.mcp_client, "list_tools") as mock_list:
                    with patch(
                        "mcp_agent_base.core.base_agent.agent_react_step"
                    ) as mock_react:
                        mock_session.return_value.__aenter__ = AsyncMock(
                            return_value=mock_session
                        )
                        mock_session.return_value.__aexit__ = AsyncMock(
                            return_value=None
                        )
                        mock_list.return_value = []
                        mock_react.return_value = ("Done", None)

                        result = await agent.run_async(state)

                        assert "conversation_history" in result

    def test_run_sync(self):
        """Test run (sync) method."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm)

        state = {"conversation_history": ["USER: Test"], "errors": [], "warnings": []}

        with patch.object(agent, "run_async") as mock_async:
            mock_async.return_value = state

            with patch("asyncio.run") as mock_run:
                mock_run.return_value = state

                result = agent.run(state)

                mock_run.assert_called_once()

    def test_callable(self):
        """Test that agent is callable."""
        mock_llm = MagicMock()
        agent = GitAgent(llm_client=mock_llm)

        state = {"conversation_history": [], "errors": [], "warnings": []}

        with patch.object(agent, "run") as mock_run:
            mock_run.return_value = state

            result = agent(state)

            mock_run.assert_called_once_with(state)
