"""MCP Agent Base - A framework for building MCP-based agents."""

from .agents.git_agent import GitAgent
from .config.settings import Settings, get_settings
from .core.base_agent import BaseAgent
from .core.llm import LLMClient, create_llm_client
from .core.mcp_client import MCPClient, MultiMCPClient
from .core.react_loop import agent_react_step, load_agent_response_schema
from .core.state import AgentState, add_error_to_state, create_state
from .core.logging_setup import setup_logging

__version__ = "0.1.0"

__all__ = [
    # Core
    "BaseAgent",
    "LLMClient",
    "create_llm_client",
    "MCPClient",
    "MultiMCPClient",
    "agent_react_step",
    "load_agent_response_schema",
    "AgentState",
    "add_error_to_state",
    "create_state",
    "setup_logging",
    # Agents
    "GitAgent",
    # Config
    "Settings",
    "get_settings",
]
