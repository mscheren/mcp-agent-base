"""GitHub Environment API operations using native PyGithub methods."""

import json
from typing import Any


class GitHubEnvironmentAPI:
    """GitHub Environment API operations using PyGithub."""

    def __init__(self, repo):
        """Initialize with a repository.

        Args:
            repo: PyGithub Repository object.
        """
        self.repo = repo

    def create_environment(self, arguments: dict[str, Any]) -> str:
        """Create a GitHub environment using native PyGithub.

        Args:
            arguments: Must contain 'environment_name', optional 'wait_timer',
                      'reviewers', 'protected_branches', 'custom_branch_policies'.

        Returns:
            Result message.
        """
        env_name = arguments["environment_name"]

        env = self.repo.create_environment(
            environment_name=env_name,
            wait_timer=arguments.get("wait_timer", 0),
            reviewers=arguments.get("reviewers", []),
            deployment_branch_policy={
                "protected_branches": arguments.get("protected_branches", False),
                "custom_branch_policies": arguments.get("custom_branch_policies", True),
            },
        )
        return f"Environment creation result: {env}"

    def list_environments(self, arguments: dict[str, Any]) -> str:
        """List all environments using native PyGithub.

        Args:
            arguments: No required arguments.

        Returns:
            JSON string with list of environments.
        """
        environments = self.repo.get_environments()
        env_list = []
        for env in environments:
            env_data = {
                "name": env.name,
                "id": env.id,
                "created_at": env.created_at.isoformat() if env.created_at else None,
                "updated_at": env.updated_at.isoformat() if env.updated_at else None,
            }
            env_list.append(env_data)
        return json.dumps({"environments": env_list}, indent=2)

    def get_environment(self, arguments: dict[str, Any]) -> str:
        """Get environment details using native PyGithub.

        Args:
            arguments: Must contain 'environment_name'.

        Returns:
            JSON string with environment details.
        """
        env_name = arguments["environment_name"]
        env = self.repo.get_environment(env_name)
        env_data = {
            "name": env.name,
            "id": env.id,
            "created_at": env.created_at.isoformat() if env.created_at else None,
            "updated_at": env.updated_at.isoformat() if env.updated_at else None,
        }
        return json.dumps(env_data, indent=2)

    def delete_environment(self, arguments: dict[str, Any]) -> str:
        """Delete environment using native PyGithub.

        Args:
            arguments: Must contain 'environment_name'.

        Returns:
            Success message.
        """
        env_name = arguments["environment_name"]
        env = self.repo.get_environment(env_name)
        env.delete()
        return f"Environment '{env_name}' deleted successfully"

    def create_secret(self, arguments: dict[str, Any]) -> str:
        """Create an environment secret using native PyGithub.

        Args:
            arguments: Must contain 'environment_name', 'secret_name'/'name',
                      'secret_value'/'value'.

        Returns:
            Success message.
        """
        env_name = arguments["environment_name"]
        secret_name = arguments.get("secret_name") or arguments.get("name")
        secret_value = arguments.get("secret_value") or arguments.get("value")

        if not secret_name:
            raise ValueError("Secret name is required (use 'secret_name' or 'name')")
        if not secret_value:
            raise ValueError("Secret value is required (use 'secret_value' or 'value')")

        env = self.repo.get_environment(env_name)
        env.create_secret(secret_name, secret_value)
        return f"Secret '{secret_name}' created in environment '{env_name}'"

    def list_secrets(self, arguments: dict[str, Any]) -> str:
        """List environment secrets using native PyGithub.

        Args:
            arguments: Must contain 'environment_name'.

        Returns:
            JSON string with list of secrets.
        """
        env_name = arguments["environment_name"]
        env = self.repo.get_environment(env_name)
        secrets = env.get_secrets()

        secret_list = []
        for secret in secrets:
            secret_data = {
                "name": secret.name,
                "created_at": (
                    secret.created_at.isoformat() if secret.created_at else None
                ),
                "updated_at": (
                    secret.updated_at.isoformat() if secret.updated_at else None
                ),
            }
            secret_list.append(secret_data)
        return json.dumps({"secrets": secret_list}, indent=2)

    def delete_secret(self, arguments: dict[str, Any]) -> str:
        """Delete an environment secret using native PyGithub.

        Args:
            arguments: Must contain 'environment_name', 'secret_name'/'name'.

        Returns:
            Success message.
        """
        env_name = arguments["environment_name"]
        secret_name = arguments.get("secret_name") or arguments.get("name")

        if not secret_name:
            raise ValueError("Secret name is required (use 'secret_name' or 'name')")

        env = self.repo.get_environment(env_name)
        secret = env.get_secret(secret_name)
        secret.delete()
        return f"Secret '{secret_name}' deleted from environment '{env_name}'"

    def create_variable(self, arguments: dict[str, Any]) -> str:
        """Create an environment variable using native PyGithub.

        Args:
            arguments: Must contain 'environment_name', 'variable_name'/'name',
                      'variable_value'/'value'.

        Returns:
            Success message.
        """
        env_name = arguments["environment_name"]
        var_name = arguments.get("variable_name") or arguments.get("name")
        var_value = arguments.get("variable_value") or arguments.get("value")

        if not var_name:
            raise ValueError(
                "Variable name is required (use 'variable_name' or 'name')"
            )
        if not var_value:
            raise ValueError(
                "Variable value is required (use 'variable_value' or 'value')"
            )

        env = self.repo.get_environment(env_name)
        env.create_variable(var_name, var_value)
        return f"Variable '{var_name}' created in environment '{env_name}'"

    def list_variables(self, arguments: dict[str, Any]) -> str:
        """List environment variables using native PyGithub.

        Args:
            arguments: Must contain 'environment_name'.

        Returns:
            JSON string with list of variables.
        """
        env_name = arguments["environment_name"]
        env = self.repo.get_environment(env_name)
        variables = env.get_variables()

        var_list = []
        for var in variables:
            var_data = {
                "name": var.name,
                "value": var.value,
                "created_at": var.created_at.isoformat() if var.created_at else None,
                "updated_at": var.updated_at.isoformat() if var.updated_at else None,
            }
            var_list.append(var_data)
        return json.dumps({"variables": var_list}, indent=2)

    def delete_variable(self, arguments: dict[str, Any]) -> str:
        """Delete an environment variable using native PyGithub.

        Args:
            arguments: Must contain 'environment_name', 'variable_name'/'name'.

        Returns:
            Success message.
        """
        env_name = arguments["environment_name"]
        var_name = arguments.get("variable_name") or arguments.get("name")

        if not var_name:
            raise ValueError(
                "Variable name is required (use 'variable_name' or 'name')"
            )

        env = self.repo.get_environment(env_name)
        variable = env.get_variable(var_name)
        variable.delete()
        return f"Variable '{var_name}' deleted from environment '{env_name}'"
