"""Git command building utilities."""

from typing import Any


# Mapping of argument names to git flags
ARG_MAPPINGS = {
    "all": "-a",
    "A": "-A",
    "force": "--force",
    "cached": "--cached",
    "porcelain": "--porcelain",
    "oneline": "--oneline",
    "graph": "--graph",
    "short": "--short",
    "verbose": "-v",
    "no_ff": "--no-ff",
    "squash": "--squash",
    "hard": "--hard",
    "soft": "--soft",
    "mixed": "--mixed",
    "interactive": "-i",
    "rebase": "--rebase",
    "amend": "--amend",
    "name_only": "--name-only",
    "set_upstream": "-u",
    "set_upstream_flag": "-u",
    "create_branch": "-b",
    "force_delete": "-D",
    "include_untracked": "-u",
    "dry_run": "--dry-run",
    "directories": "-d",
    "ignore_case": "-i",
    "summary": "--summary",
    "numbered": "--numbered",
    "tags": "--tags",
    "others": "--others",
    "ignored": "--ignored",
    "global": "--global",
    "local": "--local",
    "bare": "--bare",
    "no_commit": "--no-commit",
    "recursive": "--recursive",
}


def build_git_command(tool_name: str, arguments: dict[str, Any]) -> list[str]:
    """Build git command from tool name and arguments.

    Args:
        tool_name: Name of the git tool (e.g., 'git_status', 'git_cli_git_commit').
        arguments: Arguments for the command.

    Returns:
        List of command parts to execute.
    """
    # Extract git command from tool name
    git_cmd = tool_name.replace("git_cli_git_", "").replace("git_", "")

    # Start with base command
    cmd_parts = ["git", git_cmd]

    # Add boolean flags (with command-specific overrides)
    for arg, flag in ARG_MAPPINGS.items():
        if arguments.get(arg, False):
            # git add uses --all or -A, not -a
            if arg == "all" and git_cmd == "add":
                cmd_parts.append("-A")
            else:
                cmd_parts.append(flag)

    # Handle options array
    if "options" in arguments:
        options = arguments["options"]
        if isinstance(options, list):
            cmd_parts.extend(options)
        elif isinstance(options, str):
            cmd_parts.append(options)

    # Handle raw args
    if "args" in arguments:
        args_str = arguments["args"]
        if isinstance(args_str, str):
            cmd_parts.extend(args_str.split())
        elif isinstance(args_str, list):
            cmd_parts.extend(args_str)
        return cmd_parts

    # Handle common arguments
    if "message" in arguments:
        cmd_parts.extend(["-m", arguments["message"]])

    # Handle files for git commit (after message, with -- separator)
    if git_cmd == "commit" and "files" in arguments:
        files = arguments.pop("files")  # Remove so it's not added again below
        if files:
            cmd_parts.append("--")
            cmd_parts.extend(files)

    if "max_count" in arguments:
        cmd_parts.extend(["-n", str(arguments["max_count"])])

    if "remote" in arguments and git_cmd in ["push", "pull", "remote_get_url"]:
        cmd_parts.append(arguments["remote"])

    if "branch" in arguments and git_cmd in ["push", "pull", "checkout"]:
        cmd_parts.append(arguments["branch"])

    if "filepattern" in arguments:
        cmd_parts.append(arguments["filepattern"])

    if "repository" in arguments:
        cmd_parts.append(arguments["repository"])
    if "refspec" in arguments:
        cmd_parts.append(arguments["refspec"])

    if "pathspec" in arguments:
        pathspec = arguments["pathspec"]
        if isinstance(pathspec, list):
            cmd_parts.extend(pathspec)
        else:
            cmd_parts.append(pathspec)

    if "files" in arguments:
        cmd_parts.extend(arguments["files"])

    # Handle special commands
    cmd_parts = _handle_special_commands(git_cmd, arguments, cmd_parts)

    return cmd_parts


def _handle_special_commands(
    git_cmd: str,
    arguments: dict[str, Any],
    cmd_parts: list[str],
) -> list[str]:
    """Handle special git command cases.

    Args:
        git_cmd: The git subcommand.
        arguments: Command arguments.
        cmd_parts: Current command parts.

    Returns:
        Updated command parts.
    """
    if git_cmd == "remote_get_url":
        return ["git", "remote", "get-url", arguments.get("remote", "origin")]

    if git_cmd == "branch" and not any(
        k in arguments for k in ["create", "delete", "all"]
    ):
        cmd_parts.append("--show-current")

    elif git_cmd == "remote" and "action" in arguments:
        action = arguments["action"]
        if action == "get-url":
            return ["git", "remote", "get-url", arguments.get("name", "origin")]
        if action in ["add", "remove"] and "name" in arguments:
            cmd_parts.extend([action, arguments["name"]])
            if action == "add" and "url" in arguments:
                cmd_parts.append(arguments["url"])

    elif git_cmd == "stash" and "action" in arguments:
        action = arguments["action"]
        return ["git", "stash", action]

    elif git_cmd == "config":
        cmd_parts = _handle_config_command(arguments, cmd_parts)

    return cmd_parts


def _handle_config_command(
    arguments: dict[str, Any],
    cmd_parts: list[str],
) -> list[str]:
    """Handle git config command.

    Args:
        arguments: Command arguments.
        cmd_parts: Current command parts.

    Returns:
        Updated command parts.
    """
    if "key" in arguments and "value" in arguments:
        cmd_parts = ["git", "config", arguments["key"], arguments["value"]]
    elif "key" in arguments:
        cmd_parts = ["git", "config", arguments["key"]]
    elif "action" in arguments:
        action = arguments["action"]
        if action == "list":
            cmd_parts = ["git", "config", "--list"]
        elif action == "get" and "key" in arguments:
            cmd_parts = ["git", "config", arguments["key"]]
        elif action == "set" and "key" in arguments and "value" in arguments:
            cmd_parts = ["git", "config", arguments["key"], arguments["value"]]
        elif action == "unset" and "key" in arguments:
            cmd_parts = ["git", "config", "--unset", arguments["key"]]

    # Add global/local flags
    if arguments.get("global", False) and "--global" not in cmd_parts:
        cmd_parts.insert(2, "--global")
    elif arguments.get("local", False) and "--local" not in cmd_parts:
        cmd_parts.insert(2, "--local")

    return cmd_parts
