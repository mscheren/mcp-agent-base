"""Utils for executing GitHub environment management operations using PyGithub."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from github import Auth, Github
from github.GithubException import GithubException

from .github_env_api import GitHubEnvironmentAPI


def get_github_env_tools() -> list[dict[str, Any]]:
    """Load GitHub environment tools from JSON file.

    Returns:
        List of GitHub environment tool definitions.
    """
    tools_path = (
        Path(__file__).parent.parent / "templates" / "tools" / "github_env_tools.json"
    )
    with open(tools_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_github_token() -> str:
    """Get GitHub token from environment variable.

    Returns:
        GitHub personal access token.

    Raises:
        ValueError: If token is not set.
    """
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get(
        "GITHUB_TOKEN"
    )
    if not token:
        raise ValueError(
            "GitHub token not set. Set GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_TOKEN."
        )
    return token


def get_repo_from_arguments(g: Github, arguments: dict[str, Any]):
    """Get repository from arguments or current git repo.

    Args:
        g: GitHub client instance.
        arguments: Tool arguments.

    Returns:
        PyGithub Repository object.

    Raises:
        ValueError: If repository cannot be determined.
    """
    if "owner" in arguments and "repo" in arguments:
        return g.get_repo(f"{arguments['owner']}/{arguments['repo']}")
    if "repository" in arguments:
        return g.get_repo(arguments["repository"])

    # Handle case where only 'repo' is provided
    if "repo" in arguments:
        try:
            user = g.get_user()
            return g.get_repo(f"{user.login}/{arguments['repo']}")
        except Exception:
            pass

    # Default to current repo
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if result.returncode == 0:
        url = result.stdout.strip()
        if "github.com" in url:
            if url.startswith("git@github.com:"):
                repo_path = url.replace("git@github.com:", "").replace(".git", "")
            else:
                repo_path = url.split("github.com/")[1].replace(".git", "")
            return g.get_repo(repo_path)

    raise ValueError(
        "Could not determine repository. Specify 'owner' and 'repo', "
        "'repository', or ensure you're in a GitHub repository directory."
    )


def github_env_tool_executor(tool_name: str, arguments: dict[str, Any]) -> str:
    """Execute GitHub environment tools using command dispatch.

    Args:
        tool_name: Name of the tool to execute.
        arguments: Tool arguments.

    Returns:
        Execution result or error message.
    """
    try:
        token = get_github_token()
        auth = Auth.Token(token)
        g = Github(auth=auth)

        repo = get_repo_from_arguments(g, arguments)
        api = GitHubEnvironmentAPI(repo)

        # Extract command and dispatch
        handler = getattr(api, tool_name, None)

        if not handler:
            return f"Unknown command: {tool_name}"

        return handler(arguments)

    except GithubException as e:
        return f"GitHub API error: {e.status} - {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
