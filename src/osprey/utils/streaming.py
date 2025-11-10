"""
Streaming Event Helper for LangGraph

Provides a unified API for creating streaming events that parallel the logger pattern.
Handles automatic step counting for task preparation phases and eliminates the need
for manual writer availability checks.

Usage:
    from osprey.utils.streaming import get_streamer

    streamer = get_streamer("orchestrator", state)
    streamer.status("Creating execution plan...")
    streamer.success("Plan created")
"""

import time
from typing import Any

from langgraph.config import get_stream_writer

from osprey.utils.logger import get_logger

# Hard-coded step mapping for task preparation phases
TASK_PREPARATION_STEPS = {
    "task_extraction": {"step": 1, "total_steps": 3, "phase": "Task Preparation"},
    "classifier": {"step": 2, "total_steps": 3, "phase": "Task Preparation"},
    "orchestrator": {"step": 3, "total_steps": 3, "phase": "Task Preparation"},
}


class StreamWriter:
    """
    Stream writer that provides consistent streaming events with automatic step counting.

    Eliminates the need for manual `if writer:` checks and provides step context
    for task preparation phases.
    """

    def __init__(self, component: str, state: Any | None = None, *, source: str = None):
        """
        Initialize stream writer with component context.

        Args:
            component: Component name (e.g., "orchestrator", "python_executor")
            state: Optional AgentState for extracting execution context
            source: (Deprecated) Source type - no longer needed with flat config structure
        """
        import warnings
        if source is not None:
            warnings.warn(
                f"The 'source' parameter in StreamWriter('{source}', '{component}') is deprecated. "
                f"Use StreamWriter('{component}') instead.",
                DeprecationWarning,
                stacklevel=2
            )

        self.source = source or "osprey"  # Keep for event metadata
        self.component = component
        self.writer = get_stream_writer()
        self.logger = get_logger(component)

        # Determine step context
        self.step_info = self._get_step_info(component, state)

    def _get_step_info(self, component: str, state: Any | None) -> dict[str, Any]:
        """Get step information for the current component"""

        # Check if this is a task preparation component
        if component in TASK_PREPARATION_STEPS:
            return TASK_PREPARATION_STEPS[component]

        # For execution phase components, use StateManager utilities
        if state and hasattr(state, 'get'):
            try:
                from osprey.state.state_manager import StateManager

                # Get execution plan and current step index
                execution_plan = state.get('planning_execution_plan')
                if execution_plan and execution_plan.get('steps'):
                    current_step_index = StateManager.get_current_step_index(state)
                    total_steps = len(execution_plan.get('steps', []))

                    if total_steps > 0:
                        return {
                            "step": current_step_index + 1,  # Display as 1-based
                            "total_steps": total_steps,
                            "phase": "Execution"
                        }
            except Exception as e:
                # Graceful degradation if StateManager unavailable
                self.logger.debug(f"Could not extract step info from state: {e}")

        # Default: no step info
        return {"step": None, "total_steps": None, "phase": component.replace("_", " ").title()}

    def _emit_event(self, event_type: str, message: str, **kwargs) -> None:
        """Emit a streaming event with consistent structure"""

        # Build base event
        event = {
            "event_type": event_type,
            "message": message,
            "source": self.source,
            "component": self.component,
            "timestamp": time.time(),
            **self.step_info,
            **kwargs
        }

        # Clean up None values
        event = {k: v for k, v in event.items() if v is not None}

        # Emit to stream if available
        if self.writer:
            self.writer(event)

        # Also log for debugging
        step_info = ""
        if self.step_info.get("step") and self.step_info.get("total_steps"):
            step_info = f" ({self.step_info['step']}/{self.step_info['total_steps']})"

        self.logger.debug(f"Stream: {message}{step_info}")

    def status(self, message: str) -> None:
        """Emit a status update event"""
        self._emit_event("status", message)

    def error(self, message: str, error_data: dict[str, Any] | None = None) -> None:
        """Emit an error event"""
        self._emit_event("status", message, error=True, complete=True, data=error_data or {})

    def warning(self, message: str) -> None:
        """Emit a warning event"""
        self._emit_event("status", message, warning=True)


def get_streamer(component: str, state: Any | None = None, *, source: str = None) -> StreamWriter:
    """
    Get a stream writer for consistent streaming events.

    Parallels the get_logger() pattern for familiar usage.

    Args:
        component: Component name (e.g., "orchestrator", "python_executor")
        state: Optional AgentState for extracting execution context
        source: (Deprecated) Source type - no longer needed with flat config structure

    Returns:
        StreamWriter instance that handles event emission automatically

    Example:
        streamer = get_streamer("orchestrator", state)
        streamer.status("Creating execution plan...")
        streamer.success("Plan created")

    .. deprecated::
        The two-parameter API get_streamer(source, component, state) is deprecated.
        Use get_streamer(component, state) instead to match the simplified logger API.
    """
    import warnings
    if source is not None:
        warnings.warn(
            f"The 'source' parameter in get_streamer('{source}', '{component}') is deprecated. "
            f"Use get_streamer('{component}') instead.",
            DeprecationWarning,
            stacklevel=2
        )

    return StreamWriter(component, state, source=source)
