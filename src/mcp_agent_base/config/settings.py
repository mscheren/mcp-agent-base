"""Configuration settings for MCP agents using pydantic-settings."""

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Fixed config location for .env file
CONFIG_DIR = Path.home() / ".config" / "mcp-agent-base"
ENV_FILE = CONFIG_DIR / ".env"


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI configuration.

    Environment variables:
        - AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL
        - AZURE_OPENAI_API_KEY: Azure OpenAI API key
        - AZURE_OPENAI_DEPLOYMENT: Model deployment name
        - AZURE_OPENAI_API_VERSION: API version
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")
    deployment: str = Field(default="gpt-4o", alias="AZURE_OPENAI_DEPLOYMENT")
    api_version: str = Field(
        default="2024-08-01-preview", alias="AZURE_OPENAI_API_VERSION"
    )


class GitHubSettings(BaseSettings):
    """GitHub configuration.

    Environment variables:
        - GITHUB_TOKEN: GitHub personal access token
        - GITHUB_PERSONAL_ACCESS_TOKEN: Alternative GitHub token (takes precedence)
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    github_token: str = Field(default="", alias="GITHUB_TOKEN")

    def get_token(self) -> str:
        """Get the GitHub token, checking both possible env vars.

        Returns:
            GitHub token string.
        """
        # GITHUB_PERSONAL_ACCESS_TOKEN takes precedence
        return os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", self.github_token)


class AgentSettings(BaseSettings):
    """Agent configuration.

    Environment variables:
        - AGENT_DEFAULT_TEMPERATURE: Default LLM temperature
        - AGENT_DEFAULT_TIMEOUT: Default timeout in seconds
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        env_prefix="AGENT_",
        extra="ignore",
    )

    default_temperature: float = Field(default=0.0)
    default_timeout: int = Field(default=120)


class Settings(BaseSettings):
    """Main settings class combining all configuration sections.

    Loads configuration from environment variables and .env file.
    The .env file is loaded from ~/.config/mcp-agent-base/.env
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    azure_openai: AzureOpenAISettings = Field(default_factory=AzureOpenAISettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    agents: AgentSettings = Field(default_factory=AgentSettings)

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables.

        Returns:
            Settings instance populated from environment.
        """
        return cls(
            azure_openai=AzureOpenAISettings(),
            github=GitHubSettings(),
            agents=AgentSettings(),
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Cached Settings instance.
    """
    return Settings.from_env()
