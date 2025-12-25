"""Utils for executing git commands in a local repository."""

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Union

from .git_commands import build_git_command


def execute_git_command(
    command: Union[str, list[str]],
    working_dir: str | None = None,
) -> str:
    """Execute a local git command and return the result.

    Args:
        command: Command as string or list of parts.
        working_dir: Directory to run the command in.

    Returns:
        Command output or error message.
    """
    try:
        if isinstance(command, str):
            cmd_list = shlex.split(command)
        else:
            cmd_list = command

        cwd = working_dir if working_dir else os.getcwd()

        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
            check=False,
        )

        if result.returncode == 0:
            return (
                result.stdout.strip()
                if result.stdout
                else "Command executed successfully"
            )
        return f"Error: {result.stderr.strip()}"

    except Exception as e:
        return f"Command execution failed: {e}"


def get_git_tools() -> list[dict[str, Any]]:
    """Load git tools from JSON file.

    Returns:
        List of git tool definitions.
    """
    tools_path = Path(__file__).parent.parent / "templates" / "tools" / "git_tools.json"
    with open(tools_path, "r", encoding="utf-8") as f:
        return json.load(f)


def git_tool_executor(tool_name: str, arguments: dict[str, Any]) -> str:
    """Execute git tools using dynamic command building.

    Args:
        tool_name: Name of the tool to execute.
        arguments: Arguments for the tool.

    Returns:
        Command output or error message.
    """
    try:
        # Extract directory parameter if provided (support multiple names)
        working_dir = (
            arguments.pop("directory", None)
            or arguments.pop("repo_path", None)
            or arguments.pop("working_directory", None)
        )

        # Handle legacy parameter mappings
        if "add_all" in arguments:
            arguments["all"] = arguments.pop("add_all")

        # Handle set_upstream flag for git push
        git_cmd = tool_name.replace("git_cli_git_", "").replace("git_", "")
        if git_cmd == "push" and arguments.get("set_upstream"):
            if "args" not in arguments:
                arguments["set_upstream_flag"] = True

        command = build_git_command(tool_name, arguments)
        return execute_git_command(command, working_dir)
    except Exception as e:
        return f"Failed to execute {tool_name}: {e}"
