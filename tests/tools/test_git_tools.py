"""Tests for the git tools module."""

import pytest
from unittest.mock import patch, MagicMock

from mcp_agent_base.tools.git_tools import (
    execute_git_command,
    get_git_tools,
    git_tool_executor,
)


class TestExecuteGitCommand:
    """Tests for execute_git_command function."""

    def test_executes_string_command(self):
        """Test executing command as string."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="output", stderr=""
            )

            result = execute_git_command("git status")

            mock_run.assert_called_once()
            assert result == "output"

    def test_executes_list_command(self):
        """Test executing command as list."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="output", stderr=""
            )

            result = execute_git_command(["git", "status"])

            assert result == "output"

    def test_uses_working_directory(self):
        """Test that working directory is used."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="output", stderr=""
            )

            execute_git_command("git status", working_dir="/tmp")

            call_kwargs = mock_run.call_args
            assert call_kwargs.kwargs["cwd"] == "/tmp"

    def test_returns_error_on_failure(self):
        """Test that error is returned on command failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="fatal: not a git repository"
            )

            result = execute_git_command("git status")

            assert "Error:" in result
            assert "not a git repository" in result

    def test_returns_success_on_empty_output(self):
        """Test success message on empty output."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="", stderr=""
            )

            result = execute_git_command("git status")

            assert result == "Command executed successfully"

    def test_handles_exception(self):
        """Test handling of exceptions."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test error")

            result = execute_git_command("git status")

            assert "Command execution failed" in result
            assert "Test error" in result


class TestGetGitTools:
    """Tests for get_git_tools function."""

    def test_loads_tools_from_json(self):
        """Test that tools are loaded from JSON file."""
        tools = get_git_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check structure of first tool
        first_tool = tools[0]
        assert "name" in first_tool
        assert "description" in first_tool
        assert "inputSchema" in first_tool

    def test_contains_expected_tools(self):
        """Test that expected tools are present."""
        tools = get_git_tools()
        tool_names = [t["name"] for t in tools]

        assert "git_status" in tool_names
        assert "git_add" in tool_names
        assert "git_commit" in tool_names
        assert "git_push" in tool_names
        assert "git_pull" in tool_names


class TestGitToolExecutor:
    """Tests for git_tool_executor function."""

    def test_executes_git_command(self):
        """Test executing a git command."""
        with patch("mcp_agent_base.tools.git_tools.execute_git_command") as mock_exec:
            mock_exec.return_value = "Success"

            result = git_tool_executor("git_status", {"porcelain": True})

            assert result == "Success"
            mock_exec.assert_called_once()

    def test_extracts_directory_parameter(self):
        """Test that directory parameter is extracted."""
        with patch("mcp_agent_base.tools.git_tools.execute_git_command") as mock_exec:
            mock_exec.return_value = "Success"

            git_tool_executor("git_status", {"directory": "/tmp", "porcelain": True})

            call_args = mock_exec.call_args
            assert call_args[0][1] == "/tmp"

    def test_extracts_repo_path_parameter(self):
        """Test that repo_path parameter is extracted."""
        with patch("mcp_agent_base.tools.git_tools.execute_git_command") as mock_exec:
            mock_exec.return_value = "Success"

            git_tool_executor("git_status", {"repo_path": "/repo"})

            call_args = mock_exec.call_args
            assert call_args[0][1] == "/repo"

    def test_handles_add_all_legacy_parameter(self):
        """Test that add_all is converted to all."""
        with patch("mcp_agent_base.tools.git_tools.execute_git_command") as mock_exec:
            with patch("mcp_agent_base.tools.git_tools.build_git_command") as mock_build:
                mock_build.return_value = ["git", "add", "-a"]
                mock_exec.return_value = "Success"

                git_tool_executor("git_add", {"add_all": True})

                # Check that build_git_command received "all" not "add_all"
                call_args = mock_build.call_args
                assert "all" in call_args[0][1]
                assert "add_all" not in call_args[0][1]

    def test_handles_exception(self):
        """Test handling of exceptions."""
        with patch("mcp_agent_base.tools.git_tools.build_git_command") as mock_build:
            mock_build.side_effect = Exception("Build error")

            result = git_tool_executor("git_status", {})

            assert "Failed to execute" in result
            assert "Build error" in result

    def test_handles_prefixed_tool_name(self):
        """Test handling of prefixed tool names."""
        with patch("mcp_agent_base.tools.git_tools.execute_git_command") as mock_exec:
            mock_exec.return_value = "Success"

            result = git_tool_executor("git_cli_git_status", {"porcelain": True})

            assert result == "Success"
