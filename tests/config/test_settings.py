"""Tests for the settings module."""

import pytest
from unittest.mock import patch

from mcp_agent_base.config.settings import (
    AzureOpenAISettings,
    GitHubSettings,
    AgentSettings,
    Settings,
    get_settings,
)


class TestAzureOpenAISettings:
    """Tests for AzureOpenAISettings class."""

    def test_default_values(self):
        """Test default values."""
        with patch.dict("os.environ", {}, clear=True):
            settings = AzureOpenAISettings()

            assert settings.endpoint == ""
            assert settings.api_key == ""
            assert settings.deployment == "gpt-4o"
            assert settings.api_version == "2025-04-01-preview"

    def test_loads_from_env(self):
        """Test loading from environment variables."""
        env = {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_DEPLOYMENT": "gpt-4",
            "AZURE_OPENAI_API_VERSION": "2024-01-01",
        }
        with patch.dict("os.environ", env, clear=True):
            settings = AzureOpenAISettings()

            assert settings.endpoint == "https://test.openai.azure.com"
            assert settings.api_key == "test-key"
            assert settings.deployment == "gpt-4"
            assert settings.api_version == "2024-01-01"


class TestGitHubSettings:
    """Tests for GitHubSettings class."""

    def test_default_values(self):
        """Test default values."""
        with patch.dict("os.environ", {}, clear=True):
            settings = GitHubSettings()

            assert settings.github_token == ""

    def test_loads_github_token(self):
        """Test loading GITHUB_TOKEN."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "gh-token"}, clear=True):
            settings = GitHubSettings()

            assert settings.github_token == "gh-token"

    def test_get_token_prefers_personal_access_token(self):
        """Test that get_token prefers GITHUB_PERSONAL_ACCESS_TOKEN."""
        env = {
            "GITHUB_TOKEN": "gh-token",
            "GITHUB_PERSONAL_ACCESS_TOKEN": "pat-token",
        }
        with patch.dict("os.environ", env, clear=True):
            settings = GitHubSettings()

            assert settings.get_token() == "pat-token"

    def test_get_token_falls_back_to_github_token(self):
        """Test that get_token falls back to GITHUB_TOKEN."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "gh-token"}, clear=True):
            settings = GitHubSettings()

            assert settings.get_token() == "gh-token"


class TestAgentSettings:
    """Tests for AgentSettings class."""

    def test_default_values(self):
        """Test default values."""
        with patch.dict("os.environ", {}, clear=True):
            settings = AgentSettings()

            assert settings.default_temperature == 0.0
            assert settings.default_timeout == 120

    def test_loads_from_env(self):
        """Test loading from environment variables."""
        env = {
            "AGENT_DEFAULT_TEMPERATURE": "0.5",
            "AGENT_DEFAULT_TIMEOUT": "60",
        }
        with patch.dict("os.environ", env, clear=True):
            settings = AgentSettings()

            assert settings.default_temperature == 0.5
            assert settings.default_timeout == 60


class TestSettings:
    """Tests for Settings class."""

    def test_creates_nested_settings(self):
        """Test that nested settings are created."""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()

            assert isinstance(settings.azure_openai, AzureOpenAISettings)
            assert isinstance(settings.github, GitHubSettings)
            assert isinstance(settings.agents, AgentSettings)

    def test_from_env(self):
        """Test from_env class method."""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings.from_env()

            assert isinstance(settings, Settings)


class TestGetSettings:
    """Tests for get_settings function."""

    def test_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        # Clear the cache first
        get_settings.cache_clear()

        with patch.dict("os.environ", {}, clear=True):
            settings = get_settings()

            assert isinstance(settings, Settings)

    def test_caches_result(self):
        """Test that result is cached."""
        get_settings.cache_clear()

        with patch.dict("os.environ", {}, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()

            assert settings1 is settings2
