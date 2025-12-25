"""ReAct loop implementation for MCP agents."""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Union

from .llm import LLMClient

logger = logging.getLogger(__name__)


def load_agent_response_schema() -> dict[str, Any]:
    """Load the agent response JSON schema."""
    schema_path = (
        Path(__file__).parent.parent
        / "templates"
        / "schemas"
        / "agent_response_schema.json"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_response(response: dict[str, Any], schema: dict[str, Any]) -> bool:
    """Basic validation of response against schema.

    Args:
        response: Response dictionary to validate.
        schema: JSON schema to validate against.

    Returns:
        True if valid, False otherwise.
    """
    # Check that at least one of answer, tool_calls, or routing is present
    has_answer = response.get("answer") is not None
    has_tool_calls = bool(response.get("tool_calls"))
    has_routing = response.get("routing") is not None

    return has_answer or has_tool_calls or has_routing


async def agent_react_step(
    mcp_client,
    system_prompt: str,
    conversation_history: list[str],
    agent_name: str,
    llm_client: LLMClient,
    schema: dict[str, Any] | None = None,
) -> tuple[str, str | None]:
    """Execute a ReAct loop with an MCP client.

    Args:
        mcp_client: MCP client instance (MCPClient or MultiMCPClient).
        system_prompt: System prompt for the agent.
        conversation_history: Conversation history list (modified in place).
        agent_name: Name of the agent for logging.
        llm_client: LLM client for making calls.
        schema: Optional JSON schema for responses.

    Returns:
        Tuple of (answer, routing) where routing may be None.
    """
    if schema is None:
        schema = load_agent_response_schema()

    async with mcp_client.session() as session:
        while True:
            user_message = "\n\n###\n\n".join(conversation_history)

            response_dict = llm_client.call(system_prompt, user_message, schema=schema)

            if not validate_response(response_dict, schema):
                error_msg = (
                    "Invalid response format. Please ensure your response follows "
                    "the required schema with 'answer', 'tool_calls', or 'routing' fields."
                )
                conversation_history.append(f"System: {error_msg}")
                logger.warning("%s: Schema validation failed: %s", agent_name, response_dict)
                continue

            # Handle reasoning
            if response_dict.get("reasoning"):
                reasoning = response_dict["reasoning"]
                logger.info("%s: Reasoning: %s...", agent_name, reasoning[:200])
                conversation_history.append(f"{agent_name} Reasoning: {reasoning}")

            # Handle tool calls
            if response_dict.get("tool_calls"):
                for tool_call in response_dict["tool_calls"]:
                    tool_name = tool_call["tool_name"]
                    arguments = tool_call["arguments"]

                    logger.info(
                        "%s: Calling tool: %s with args: %s...",
                        agent_name,
                        tool_name,
                        str(arguments)[:200],
                    )
                    tool_result = await mcp_client.call_tool(session, tool_name, arguments)
                    logger.info("%s: Tool Result: %s...", agent_name, str(tool_result)[:200])

                    conversation_history.append(f"Tool Call: {tool_name}({arguments})")
                    conversation_history.append(f"Tool Result: {tool_result}")
            else:
                # No tool calls - check for answer
                if response_dict.get("answer"):
                    routing = response_dict.get("routing", None)
                    return response_dict["answer"], routing

                # No answer or tool calls - provide feedback
                feedback_msg = (
                    "Please provide either an 'answer' to complete the task or "
                    "'tool_calls' to continue with tool execution."
                )
                conversation_history.append(f"System: {feedback_msg}")


class ToolClient:
    """Simple tool client for non-MCP tools that mimics MCP client interface."""

    def __init__(
        self,
        tools: list[dict[str, Any]],
        tool_executor: Callable[[str, dict[str, Any]], Union[str, Any]],
    ):
        """Initialize with tools and executor function."""
        self.tools = tools
        self.tool_executor = tool_executor

    def session(self):
        """Mock session context manager."""
        return self

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    async def call_tool(
        self,
        session,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """Execute tool using the provided executor."""
        return self.tool_executor(tool_name, arguments)


async def agent_react_step_with_tools(
    tools: list[dict[str, Any]],
    tool_executor: Callable[[str, dict[str, Any]], Union[str, Any]],
    system_prompt: str,
    conversation_history: list[str],
    agent_name: str,
    llm_client: LLMClient,
    schema: dict[str, Any] | None = None,
) -> tuple[str, str | None]:
    """Execute ReAct loop with custom tools (non-MCP).

    Args:
        tools: List of tool definitions.
        tool_executor: Function to execute tools.
        system_prompt: System prompt for the agent.
        conversation_history: Conversation history list.
        agent_name: Name of the agent for logging.
        llm_client: LLM client for making calls.
        schema: Optional JSON schema for responses.

    Returns:
        Tuple of (answer, routing) where routing may be None.
    """
    tool_client = ToolClient(tools, tool_executor)

    return await agent_react_step(
        tool_client,
        system_prompt,
        conversation_history,
        agent_name,
        llm_client,
        schema,
    )


# Alias for backwards compatibility
run_react_loop = agent_react_step
