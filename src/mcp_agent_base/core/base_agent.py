"""Abstract base agent for MCP-based agents."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

from .llm import LLMClient
from .mcp_client import MultiMCPClient
from .react_loop import agent_react_step
from .state import AgentState

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for MCP-based agents.

    Subclasses must implement:
        - get_system_prompt(): Returns the system prompt for the agent.
        - setup_tools(): Configures the MCP client with tools.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        agent_name: str = "Agent",
    ):
        """Initialize the base agent.

        Args:
            llm_client: LLM client for making calls.
            agent_name: Name of the agent for logging.
        """
        self.llm_client = llm_client
        self.agent_name = agent_name
        self.mcp_client = MultiMCPClient()

    @abstractmethod
    def get_system_prompt(self, tools: list[dict[str, Any]]) -> str:
        """Get the system prompt for the agent.

        Args:
            tools: List of available tools.

        Returns:
            System prompt string.
        """
        pass

    @abstractmethod
    def setup_tools(self) -> None:
        """Configure the MCP client with tools.

        This method should call self.mcp_client.add_server() and/or
        self.mcp_client.add_custom_tools() to register available tools.
        """
        pass

    async def run_async(self, state: AgentState) -> AgentState:
        """Run the agent asynchronously.

        Args:
            state: Current agent state.

        Returns:
            Updated agent state.
        """
        try:
            self.setup_tools()

            async with self.mcp_client.session() as session:
                tools = await self.mcp_client.list_tools(session)
                system_prompt = self.get_system_prompt(tools)

                conversation_history = list(state.get("conversation_history", []))

                answer, routing = await agent_react_step(
                    self.mcp_client,
                    system_prompt,
                    conversation_history,
                    self.agent_name,
                    self.llm_client,
                )

                updated_state = state.copy()
                updated_state["conversation_history"] = conversation_history
                conversation_history.append(f"{self.agent_name}: {answer}")

                return updated_state

        except Exception as e:
            logger.error("%s error: %s", self.agent_name, e)
            errors = list(state.get("errors", []))
            errors.append(f"{self.agent_name} error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"] = errors
            return updated_state

    def run(self, state: AgentState) -> AgentState:
        """Run the agent synchronously.

        Args:
            state: Current agent state.

        Returns:
            Updated agent state.
        """
        return asyncio.run(self.run_async(state))

    def __call__(self, state: AgentState) -> AgentState:
        """Allow calling the agent as a function.

        Args:
            state: Current agent state.

        Returns:
            Updated agent state.
        """
        return self.run(state)
