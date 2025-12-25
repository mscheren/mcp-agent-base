"""GitHub agent for git and GitHub operations."""

import json
import os
from typing import Any

from ..core.base_agent import BaseAgent
from ..core.llm import LLMClient
from ..core.react_loop import load_agent_response_schema
from ..templates.template_loader import template_loader
from ..tools.git_tools import get_git_tools, git_tool_executor
from ..tools.github_tools import get_github_env_tools, github_env_tool_executor


class GitAgent(BaseAgent):
    """Agent for git and GitHub operations.

    This agent provides tools for:
    - Git CLI operations (status, add, commit, push, pull, etc.)
    - GitHub environment management (secrets, variables, etc.)
    - Optional: GitHub MCP server for extended GitHub API access
    """

    def __init__(
        self,
        llm_client: LLMClient,
        agent_name: str = "GitAgent",
        use_github_mcp_server: bool = False,
    ):
        """Initialize the GitAgent.

        Args:
            llm_client: LLM client for making calls.
            agent_name: Name of the agent for logging.
            use_github_mcp_server: Whether to include the GitHub MCP server.
        """
        super().__init__(llm_client, agent_name)
        self.use_github_mcp_server = use_github_mcp_server

    def get_system_prompt(self, tools: list[dict[str, Any]]) -> str:
        """Get the system prompt for the GitAgent.

        Args:
            tools: List of available tools.

        Returns:
            System prompt string.
        """
        # Format tools description
        tools_description = self._format_tools(tools)

        # Load response schema
        response_schema = json.dumps(load_agent_response_schema(), indent=2)

        # Load and render the prompt template
        prompt_template = template_loader.load_prompt_template("git_agent")
        return prompt_template.render(
            tools_description=tools_description,
            response_schema=response_schema,
        )

    def _format_tools(self, tools: list[dict[str, Any]]) -> str:
        """Format tools list for the system prompt.

        Args:
            tools: List of tool definitions.

        Returns:
            Formatted string describing available tools.
        """
        lines = []
        for tool in tools:
            name = tool.get("name", "unknown")
            description = tool.get("description", "No description")
            lines.append(f"- {name}: {description}")
        return "\n".join(lines)

    def setup_tools(self) -> None:
        """Configure the MCP client with git and GitHub tools."""
        # Add git CLI tools
        git_tools = get_git_tools()
        self.mcp_client.add_custom_tools("git_cli", git_tools, git_tool_executor)

        # Add GitHub environment tools
        github_env_tools = get_github_env_tools()
        self.mcp_client.add_custom_tools(
            "github_env", github_env_tools, github_env_tool_executor
        )

        # Optionally add GitHub MCP server
        if self.use_github_mcp_server:
            github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
            if github_token:
                self.mcp_client.add_server(
                    name="github",
                    mcp_command="docker",
                    mcp_args=[
                        "run",
                        "-i",
                        "--rm",
                        "-e",
                        f"GITHUB_PERSONAL_ACCESS_TOKEN={github_token}",
                        "ghcr.io/github/github-mcp-server",
                    ],
                    mcp_env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token},
                )
