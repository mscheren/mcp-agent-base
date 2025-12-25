"""LLM client abstraction for structured output generation."""

import json
import logging
from typing import Any

from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for making structured LLM calls via Azure OpenAI."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str = "2024-08-01-preview",
        temperature: float = 0.1,
    ):
        """Initialize the LLM client.

        Args:
            endpoint: Azure OpenAI endpoint URL.
            api_key: API key for authentication.
            deployment: Model deployment name.
            api_version: API version to use.
            temperature: Sampling temperature for responses.
        """
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        self.deployment = deployment
        self.temperature = temperature

    def call(
        self,
        system_prompt: str,
        user_message: str,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a structured LLM call that returns JSON.

        Args:
            system_prompt: System message for the LLM.
            user_message: User message containing the query.
            schema: Optional JSON schema for structured output.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            ValueError: If response cannot be parsed as JSON.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        kwargs: dict[str, Any] = {
            "model": self.deployment,
            "messages": messages,
            "temperature": self.temperature,
        }

        if schema:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        if not content:
            raise ValueError("Empty response from LLM")

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response: %s", content[:200])
            raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e


def create_llm_client(
    endpoint: str,
    api_key: str,
    deployment: str,
    api_version: str = "2024-08-01-preview",
    temperature: float = 0.1,
) -> LLMClient:
    """Factory function to create an LLM client.

    Args:
        endpoint: Azure OpenAI endpoint URL.
        api_key: API key for authentication.
        deployment: Model deployment name.
        api_version: API version to use.
        temperature: Sampling temperature for responses.

    Returns:
        Configured LLMClient instance.
    """
    return LLMClient(
        endpoint=endpoint,
        api_key=api_key,
        deployment=deployment,
        api_version=api_version,
        temperature=temperature,
    )
