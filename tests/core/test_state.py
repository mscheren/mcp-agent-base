"""Tests for the state management module."""

import pytest

from mcp_agent_base.core.state import (
    AgentState,
    create_state,
    add_error_to_state,
    add_warning_to_state,
)


class TestCreateState:
    """Tests for create_state function."""

    def test_creates_empty_state(self):
        """Test creating state with defaults."""
        state = create_state()

        assert state["conversation_history"] == []
        assert state["errors"] == []
        assert state["warnings"] == []

    def test_creates_state_with_conversation_history(self):
        """Test creating state with initial conversation."""
        state = create_state(conversation_history=["USER: Hello"])

        assert state["conversation_history"] == ["USER: Hello"]

    def test_creates_state_with_extra_fields(self):
        """Test creating state with additional fields."""
        state = create_state(custom_field="value")

        assert state.get("custom_field") == "value"


class TestAddErrorToState:
    """Tests for add_error_to_state function."""

    def test_adds_error_to_empty_list(self):
        """Test adding error to state with no errors."""
        state: AgentState = {"conversation_history": [], "errors": [], "warnings": []}

        updated = add_error_to_state(state, "Test error")

        assert "Test error" in updated["errors"]

    def test_adds_error_to_existing_list(self):
        """Test adding error to state with existing errors."""
        state: AgentState = {
            "conversation_history": [],
            "errors": ["Existing error"],
            "warnings": [],
        }

        updated = add_error_to_state(state, "New error")

        assert len(updated["errors"]) == 2
        assert "Existing error" in updated["errors"]
        assert "New error" in updated["errors"]

    def test_does_not_duplicate_errors(self):
        """Test that duplicate errors are not added."""
        state: AgentState = {
            "conversation_history": [],
            "errors": ["Same error"],
            "warnings": [],
        }

        updated = add_error_to_state(state, "Same error")

        assert len(updated["errors"]) == 1

    def test_handles_none_errors_list(self):
        """Test handling state with None errors list."""
        state: AgentState = {"conversation_history": [], "errors": None, "warnings": []}

        updated = add_error_to_state(state, "Test error")

        assert updated["errors"] == ["Test error"]

    def test_does_not_modify_original_state(self):
        """Test that original state is not modified."""
        state: AgentState = {"conversation_history": [], "errors": [], "warnings": []}

        add_error_to_state(state, "Test error")

        assert state["errors"] == []


class TestAddWarningToState:
    """Tests for add_warning_to_state function."""

    def test_adds_warning_to_empty_list(self):
        """Test adding warning to state with no warnings."""
        state: AgentState = {"conversation_history": [], "errors": [], "warnings": []}

        updated = add_warning_to_state(state, "Test warning")

        assert "Test warning" in updated["warnings"]

    def test_does_not_duplicate_warnings(self):
        """Test that duplicate warnings are not added."""
        state: AgentState = {
            "conversation_history": [],
            "errors": [],
            "warnings": ["Same warning"],
        }

        updated = add_warning_to_state(state, "Same warning")

        assert len(updated["warnings"]) == 1
