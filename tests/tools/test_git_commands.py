"""Tests for the git commands module."""

import pytest

from mcp_agent_base.tools.git_commands import build_git_command


class TestBuildGitCommand:
    """Tests for build_git_command function."""

    def test_basic_status_command(self):
        """Test building basic git status command."""
        result = build_git_command("git_status", {})

        assert result == ["git", "status", "--show-current"]

    def test_status_with_porcelain(self):
        """Test git status with porcelain flag."""
        result = build_git_command("git_status", {"porcelain": True})

        assert "git" in result
        assert "status" in result
        assert "--porcelain" in result

    def test_add_with_all_flag(self):
        """Test git add with all flag."""
        result = build_git_command("git_add", {"all": True})

        assert result == ["git", "add", "-a"]

    def test_commit_with_message(self):
        """Test git commit with message."""
        result = build_git_command("git_commit", {"message": "Test commit"})

        assert result == ["git", "commit", "-m", "Test commit"]

    def test_commit_with_all_and_message(self):
        """Test git commit with all flag and message."""
        result = build_git_command("git_commit", {"all": True, "message": "Test"})

        assert "git" in result
        assert "commit" in result
        assert "-a" in result
        assert "-m" in result
        assert "Test" in result

    def test_push_with_remote_and_branch(self):
        """Test git push with remote and branch."""
        result = build_git_command(
            "git_push", {"remote": "origin", "branch": "main"}
        )

        assert result == ["git", "push", "origin", "main"]

    def test_push_with_force(self):
        """Test git push with force flag."""
        result = build_git_command("git_push", {"force": True})

        assert "--force" in result

    def test_push_with_set_upstream(self):
        """Test git push with set upstream flag."""
        result = build_git_command(
            "git_push", {"set_upstream_flag": True, "remote": "origin", "branch": "main"}
        )

        assert "-u" in result

    def test_log_with_max_count(self):
        """Test git log with max count."""
        result = build_git_command("git_log", {"max_count": 5})

        assert "-n" in result
        assert "5" in result

    def test_log_with_oneline(self):
        """Test git log with oneline flag."""
        result = build_git_command("git_log", {"oneline": True})

        assert "--oneline" in result

    def test_diff_with_cached(self):
        """Test git diff with cached flag."""
        result = build_git_command("git_diff", {"cached": True})

        assert "--cached" in result

    def test_remote_get_url(self):
        """Test git remote get-url command."""
        result = build_git_command("git_remote_get_url", {"remote": "origin"})

        assert result == ["git", "remote", "get-url", "origin"]

    def test_config_set_value(self):
        """Test git config set command."""
        result = build_git_command(
            "git_config", {"key": "user.name", "value": "Test User"}
        )

        assert result == ["git", "config", "user.name", "Test User"]

    def test_config_get_value(self):
        """Test git config get command."""
        result = build_git_command("git_config", {"key": "user.name"})

        assert result == ["git", "config", "user.name"]

    def test_config_with_global_flag(self):
        """Test git config with global flag."""
        result = build_git_command(
            "git_config", {"key": "user.name", "global": True}
        )

        assert "--global" in result

    def test_stash_with_action(self):
        """Test git stash with action."""
        result = build_git_command("git_stash", {"action": "pop"})

        assert result == ["git", "stash", "pop"]

    def test_raw_args(self):
        """Test passing raw args."""
        result = build_git_command("git_log", {"args": "--oneline -5"})

        assert result == ["git", "log", "--oneline", "-5"]

    def test_prefixed_tool_name(self):
        """Test with git_cli prefix in tool name."""
        result = build_git_command("git_cli_git_status", {"porcelain": True})

        assert "git" in result
        assert "status" in result
        assert "--porcelain" in result

    def test_files_argument(self):
        """Test with files list."""
        result = build_git_command("git_add", {"files": ["file1.py", "file2.py"]})

        assert "file1.py" in result
        assert "file2.py" in result
