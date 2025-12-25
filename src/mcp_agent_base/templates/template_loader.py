"""Template file loader utilities."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template


class TemplateLoader:
    """Load templates from various file formats."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize template loader with base path.

        Args:
            base_path: Base path for templates. Defaults to this module's parent.
        """
        if base_path is None:
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.base_path)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def load_text_file(self, file_path: str) -> str:
        """Load content from a text file.

        Args:
            file_path: Relative path to the file.

        Returns:
            File content as string.
        """
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Template file not found: {full_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def load_prompt_template(self, prompt_name: str) -> Template:
        """Load a prompt template file as Jinja2 template.

        Args:
            prompt_name: Name of the prompt (without extension).

        Returns:
            Jinja2 Template object.
        """
        file_path = f"prompts/{prompt_name}.txt"
        return self.jinja_env.get_template(file_path)

    def load_json_data(self, file_path: str) -> Dict[str, Any]:
        """Load data from a JSON file.

        Args:
            file_path: Relative path to the JSON file.

        Returns:
            Parsed JSON data.
        """
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"JSON file not found: {full_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_tools(self, tool_file: str) -> list:
        """Load tool definitions from JSON file.

        Args:
            tool_file: Name of the tools file (without extension).

        Returns:
            List of tool definitions.
        """
        file_path = f"tools/{tool_file}.json"
        return self.load_json_data(file_path)

    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load a JSON schema file.

        Args:
            schema_name: Name of the schema file (without extension).

        Returns:
            Schema dictionary.
        """
        file_path = f"schemas/{schema_name}.json"
        return self.load_json_data(file_path)

    def list_available_prompt_templates(self) -> list:
        """List all available prompt template names.

        Returns:
            List of prompt template names.
        """
        prompts_dir = self.base_path / "prompts"

        if not prompts_dir.exists():
            return []

        return [txt_file.stem for txt_file in prompts_dir.glob("*.txt")]


# Global template loader instance
template_loader = TemplateLoader()
