"""Tests for the GitHub tools module."""

import pytest
from unittest.mock import patch, MagicMock

from mcp_agent_base.tools.github_tools import (
    get_github_token,
    get_repo_from_arguments,
    get_github_env_tools,
    github_env_tool_executor,
)


class TestGetGitHubToken:
    """Tests for get_github_token function."""

    def test_returns_personal_access_token(self):
        """Test returning GITHUB_PERSONAL_ACCESS_TOKEN."""
        with patch.dict(
            "os.environ",
            {"GITHUB_PERSONAL_ACCESS_TOKEN": "pat-token"},
            clear=True,
        ):
            token = get_github_token()

            assert token == "pat-token"

    def test_returns_github_token(self):
        """Test returning GITHUB_TOKEN as fallback."""
        with patch.dict(
            "os.environ",
            {"GITHUB_TOKEN": "gh-token"},
            clear=True,
        ):
            token = get_github_token()

            assert token == "gh-token"

    def test_prefers_personal_access_token(self):
        """Test that GITHUB_PERSONAL_ACCESS_TOKEN takes precedence."""
        with patch.dict(
            "os.environ",
            {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "pat-token",
                "GITHUB_TOKEN": "gh-token",
            },
            clear=True,
        ):
            token = get_github_token()

            assert token == "pat-token"

    def test_raises_on_missing_token(self):
        """Test that ValueError is raised when no token is set."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="token not set"):
                get_github_token()


class TestGetRepoFromArguments:
    """Tests for get_repo_from_arguments function."""

    def test_uses_owner_and_repo(self):
        """Test using owner and repo arguments."""
        mock_github = MagicMock()
        mock_github.get_repo.return_value = "repo-object"

        result = get_repo_from_arguments(
            mock_github, {"owner": "testowner", "repo": "testrepo"}
        )

        mock_github.get_repo.assert_called_with("testowner/testrepo")
        assert result == "repo-object"

    def test_uses_repository_argument(self):
        """Test using repository argument."""
        mock_github = MagicMock()
        mock_github.get_repo.return_value = "repo-object"

        result = get_repo_from_arguments(
            mock_github, {"repository": "owner/repo"}
        )

        mock_github.get_repo.assert_called_with("owner/repo")

    def test_falls_back_to_git_remote(self):
        """Test falling back to git remote URL."""
        mock_github = MagicMock()
        mock_github.get_repo.return_value = "repo-object"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="git@github.com:testowner/testrepo.git\n",
            )

            result = get_repo_from_arguments(mock_github, {})

            mock_github.get_repo.assert_called_with("testowner/testrepo")

    def test_handles_https_url(self):
        """Test handling HTTPS remote URL."""
        mock_github = MagicMock()
        mock_github.get_repo.return_value = "repo-object"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="https://github.com/testowner/testrepo.git\n",
            )

            result = get_repo_from_arguments(mock_github, {})

            mock_github.get_repo.assert_called_with("testowner/testrepo")

    def test_raises_on_no_repo(self):
        """Test raising error when repo cannot be determined."""
        mock_github = MagicMock()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)

            with pytest.raises(ValueError, match="Could not determine"):
                get_repo_from_arguments(mock_github, {})


class TestGetGitHubEnvTools:
    """Tests for get_github_env_tools function."""

    def test_loads_tools_from_json(self):
        """Test that tools are loaded from JSON file."""
        tools = get_github_env_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_contains_expected_tools(self):
        """Test that expected tools are present."""
        tools = get_github_env_tools()
        tool_names = [t["name"] for t in tools]

        assert "create_environment" in tool_names
        assert "list_environments" in tool_names
        assert "create_secret" in tool_names
        assert "list_secrets" in tool_names


class TestGitHubEnvToolExecutor:
    """Tests for github_env_tool_executor function."""

    def test_executes_list_environments(self):
        """Test executing list_environments command."""
        with patch("mcp_agent_base.tools.github_tools.get_github_token") as mock_token:
            with patch("mcp_agent_base.tools.github_tools.Github") as mock_gh_class:
                with patch(
                    "mcp_agent_base.tools.github_tools.get_repo_from_arguments"
                ) as mock_repo:
                    mock_token.return_value = "test-token"
                    mock_repo_obj = MagicMock()
                    mock_repo_obj.get_environments.return_value = []
                    mock_repo.return_value = mock_repo_obj

                    result = github_env_tool_executor("list_environments", {})

                    assert "environments" in result

    def test_handles_github_exception(self):
        """Test handling of GitHub API exceptions."""
        from github.GithubException import GithubException

        with patch("mcp_agent_base.tools.github_tools.get_github_token") as mock_token:
            with patch("mcp_agent_base.tools.github_tools.Github") as mock_gh_class:
                mock_token.return_value = "test-token"
                mock_gh_class.side_effect = GithubException(
                    status=404, data={"message": "Not Found"}, headers={}
                )

                result = github_env_tool_executor("list_environments", {})

                assert "GitHub API error" in result

    def test_handles_unknown_command(self):
        """Test handling of unknown command."""
        with patch("mcp_agent_base.tools.github_tools.get_github_token") as mock_token:
            with patch("mcp_agent_base.tools.github_tools.Github"):
                with patch(
                    "mcp_agent_base.tools.github_tools.get_repo_from_arguments"
                ) as mock_repo:
                    mock_token.return_value = "test-token"
                    mock_repo.return_value = MagicMock()

                    result = github_env_tool_executor("unknown_command", {})

                    assert "Unknown command" in result

    def test_handles_general_exception(self):
        """Test handling of general exceptions."""
        with patch("mcp_agent_base.tools.github_tools.get_github_token") as mock_token:
            mock_token.side_effect = Exception("Test error")

            result = github_env_tool_executor("list_environments", {})

            assert "Error executing" in result
            assert "Test error" in result
