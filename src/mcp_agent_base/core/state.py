"""State management for MCP agents."""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """Base state for MCP agents.

    This is a minimal state that can be extended by specific agents.
    Uses TypedDict for type safety and compatibility with various frameworks.
    """

    conversation_history: list[str]
    errors: list[str]
    warnings: list[str]


def create_state(
    conversation_history: list[str] | None = None,
    **kwargs: Any,
) -> AgentState:
    """Create a new agent state.

    Args:
        conversation_history: Initial conversation history.
        **kwargs: Additional state fields.

    Returns:
        New AgentState instance.
    """
    state: AgentState = {
        "conversation_history": conversation_history or [],
        "errors": [],
        "warnings": [],
    }
    state.update(kwargs)
    return state


def add_error_to_state(state: AgentState, error_message: str) -> AgentState:
    """Add an error message to the state errors list.

    Args:
        state: Current agent state.
        error_message: Error message to add.

    Returns:
        Updated state with the error added.
    """
    errors = state.get("errors", [])
    if errors is None:
        errors = []
    if error_message not in errors:
        errors.append(error_message)

    updated_state = state.copy()
    updated_state["errors"] = errors
    return updated_state


def add_warning_to_state(state: AgentState, warning_message: str) -> AgentState:
    """Add a warning message to the state warnings list.

    Args:
        state: Current agent state.
        warning_message: Warning message to add.

    Returns:
        Updated state with the warning added.
    """
    warnings = state.get("warnings", [])
    if warnings is None:
        warnings = []
    if warning_message not in warnings:
        warnings.append(warning_message)

    updated_state = state.copy()
    updated_state["warnings"] = warnings
    return updated_state
