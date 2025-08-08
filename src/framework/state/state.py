"""LangGraph-Native Conversational Agent State.

This module implements the core state structure for the Alpha Berkeley Agent Framework
using LangGraph's native patterns for optimal performance and compatibility. The state
system provides a clean separation between persistent context data and execution-scoped
fields that reset automatically between conversation turns.

**Architecture Overview:**

The state system is built on LangGraph's MessagesState foundation with a flat structure
that eliminates the need for complex custom reducers. Only capability context data
persists across conversation turns, while all execution-related fields reset automatically
between graph invocations.

**Key Components:**

- :class:`AgentState`: Main conversational state extending MessagesState
- :func:`merge_capability_context_data`: Custom reducer for context persistence
- :func:`create_status_update`: Utility for creating status update events
- :func:`create_progress_event`: Utility for creating progress tracking events
- :type:`StateUpdate`: Type alias for LangGraph state update dictionaries

**State Field Organization:**

The state fields are organized with logical prefixes for clarity:

- **task_*** : Task extraction and input processing
- **planning_*** : Classification and orchestration  
- **execution_*** : Step execution and results
- **control_*** : Control flow runtime state
- **ui_*** : UI-specific results and commands

**Persistence Strategy:**

- **Persistent Field**: Only `capability_context_data` accumulates across conversations
- **Execution-Scoped**: All other fields reset automatically each invocation
- **No Custom Reducers**: Leverages LangGraph's native message handling

**Context Data Structure:**

The capability_context_data field uses a three-level dictionary structure optimized
for LangGraph serialization::

    {
        context_type: {
            context_key: {
                field: value,
                ...
            }
        }
    }

This structure enables efficient context storage, retrieval, and merging while
maintaining compatibility with LangGraph's checkpointing system.

.. note::
   TypedDict classes cannot have default values in their class definition.
   Use StateManager.create_fresh_state() to create state instances with
   proper defaults. Only capability_context_data will be preserved from
   previous state if available.

.. warning::
   The state structure is optimized for LangGraph's native patterns. Direct
   manipulation of state fields may interfere with automatic checkpointing
   and serialization. Use StateManager utilities for state operations.

.. seealso::
   :class:`framework.state.StateManager` : State creation and management utilities
   :class:`framework.context.ContextManager` : Context data management
   :mod:`framework.base.planning` : Execution planning and step structures
"""

import copy
from typing import Annotated, List, Dict, Any, Optional

# LangGraph native imports
from langgraph.graph import MessagesState

# Import context manager for type hints and helper functions
from framework.base.planning import ExecutionPlan
from framework.base.results import ExecutionResult


from .execution import ApprovalRequest


# ===== CUSTOM REDUCER FOR PURE DICTIONARY CONTEXT DATA =====

def merge_capability_context_data(
    existing: Optional[Dict[str, Dict[str, Dict[str, Any]]]], 
    new: Dict[str, Dict[str, Dict[str, Any]]]
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Merge capability context data dictionaries for LangGraph-native checkpointing.
    
    This custom reducer function enables capability context data to accumulate across
    conversation turns while maintaining pure dictionary structure for optimal LangGraph
    serialization and checkpointing performance. The function implements deep merging
    logic that preserves existing context while integrating new context data.
    
    The merge operation follows a three-level dictionary structure that organizes
    context data hierarchically by type, key, and field values. This structure
    provides efficient access patterns for context retrieval while maintaining
    serialization compatibility.
    
    :param existing: Existing capability context data dictionary from previous state
    :type existing: Optional[Dict[str, Dict[str, Dict[str, Any]]]]
    :param new: New capability context data to merge into existing structure
    :type new: Dict[str, Dict[str, Dict[str, Any]]]
    :return: Merged dictionary maintaining all existing data with new updates applied
    :rtype: Dict[str, Dict[str, Dict[str, Any]]]
    
    .. note::
       The function performs deep copying to prevent mutation of input dictionaries,
       ensuring state immutability and preventing side effects in LangGraph operations.
    
    .. warning::
       New context data will override existing context data for the same context_type
       and context_key combination. This is intentional for capability result updates
       but should be considered when designing context key strategies.
    
    Examples:
        Basic context merging::
        
            >>> existing = {"PV_ADDRESSES": {"step1": {"pvs": ["SR:C01:MAG:1"]}}}
            >>> new = {"PV_ADDRESSES": {"step2": {"pvs": ["SR:C02:MAG:1"]}}}
            >>> result = merge_capability_context_data(existing, new)
            >>> len(result["PV_ADDRESSES"])
            2
        
        Context override behavior::
        
            >>> existing = {"DATA": {"key1": {"value": "old"}}}
            >>> new = {"DATA": {"key1": {"value": "new", "extra": "data"}}}
            >>> result = merge_capability_context_data(existing, new)
            >>> result["DATA"]["key1"]["value"]
            'new'
    
    .. seealso::
       :class:`AgentState` : Main state class using this reducer
       :class:`framework.context.ContextManager` : Context data management utilities
    """
    if existing is None:
        # Deep copy to avoid mutation of input
        return copy.deepcopy(new)
    
    # Deep copy existing data to avoid mutation
    result = copy.deepcopy(existing)
    
    # Merge in new data, which may override existing keys
    for context_type, contexts in new.items():
        if context_type not in result:
            result[context_type] = {}
        
        for context_key, context_data in contexts.items():
            # Update the entire context data for this key
            result[context_type][context_key] = copy.deepcopy(context_data)
    
    return result





# ===== MAIN CONVERSATIONAL STATE =====

class AgentState(MessagesState):
    """LangGraph-native conversational agent state with comprehensive execution tracking.
    
    This TypedDict class extends LangGraph's MessagesState to provide a complete state
    structure for conversational AI agents. The state design implements selective
    persistence where only capability context data accumulates across conversation
    turns, while all execution-related fields reset automatically between graph
    invocations for optimal performance and state clarity.
    
    **State Architecture:**
    
    The state follows a flat structure with logical field prefixes for organization:
    
    - **Persistent Fields**: Only capability_context_data persists across conversations
    - **Execution-Scoped Fields**: All other fields reset automatically each invocation
    - **No Custom Reducers**: Leverages LangGraph's native message handling patterns
    - **Type Safety**: Comprehensive TypedDict definitions with proper type annotations
    
    **Field Organization by Prefix:**
    
    - **task_*** : Task extraction and input processing state
    - **planning_*** : Classification and orchestration management
    - **execution_*** : Step execution results and tracking
    - **control_*** : Control flow and retry logic state
    - **ui_*** : UI-specific results and command generation
    - **runtime_*** : Runtime metadata and checkpoint information
    
    **Context Data Structure:**
    
    The capability_context_data field uses a three-level dictionary optimized for
    LangGraph serialization and efficient context retrieval::
    
        {
            context_type: {
                context_key: {
                    field: value,
                    ...
                }
            }
        }
    
    **State Lifecycle:**
    
    1. **Fresh State Creation**: StateManager.create_fresh_state() initializes defaults
    2. **Context Preservation**: Only capability_context_data carries forward
    3. **Execution Reset**: All execution fields reset to defaults each turn
    4. **Message Handling**: LangGraph manages message history automatically
    
    .. note::
       TypedDict classes cannot define default values in the class definition.
       Always use StateManager.create_fresh_state() to create properly initialized
       state instances. Only capability_context_data will be preserved from
       previous state if available.
    
    .. warning::
       Direct manipulation of state fields may interfere with LangGraph's automatic
       checkpointing and serialization. Use StateManager utilities for all state
       operations to ensure compatibility and proper behavior.
    
    Examples:
        Creating fresh state through StateManager::
        
            >>> from framework.state import StateManager
            >>> state = StateManager.create_fresh_state(
            ...     user_input="Find beam current PV addresses",
            ...     current_state=previous_state
            ... )
            >>> state['task_current_task']
            None
        
        Accessing persistent context data::
        
            >>> context_data = state['capability_context_data']
            >>> pv_addresses = context_data.get('PV_ADDRESSES', {})
            >>> len(pv_addresses)
            3
    
    .. seealso::
       :class:`framework.state.StateManager` : State creation and management utilities
       :class:`framework.context.ContextManager` : Context data access and storage
       :func:`merge_capability_context_data` : Custom reducer for context persistence
       :class:`framework.base.planning.ExecutionPlan` : Execution planning structures
    """
    
    # ===== PERSISTENT FIELD (Accumulates across conversation) =====
    
    # Core persistent context - LangGraph-native dictionary storage
    # Data structure: {context_type: {context_key: {field: value}}}
    capability_context_data: Annotated[Dict[str, Dict[str, Dict[str, Any]]], merge_capability_context_data]
    
    # ===== EXECUTION-SCOPED FIELDS (Reset each invocation) =====
    
    # Agent control state - resets to defaults each conversation turn
    agent_control: Dict[str, Any]
    
    # Event accumulation - reset each execution
    status_updates: List[Dict[str, Any]]
    progress_events: List[Dict[str, Any]]
    
    # Task processing fields
    task_current_task: Optional[str]
    task_depends_on_chat_history: bool
    task_depends_on_user_memory: bool
    task_custom_message: Optional[str]
    
    # Planning fields
    planning_active_capabilities: List[str]
    planning_execution_plan: Optional[ExecutionPlan]
    planning_current_step_index: int
    
    # Execution fields
    execution_step_results: Dict[str, Any]
    execution_last_result: Optional[ExecutionResult]
    execution_pending_approvals: Dict[str, ApprovalRequest]
    execution_start_time: Optional[float]
    execution_total_time: Optional[float]
    
    # Approval handling fields (for interrupt flows)
    approval_approved: Optional[bool]  # True/False/None for approved/rejected/no-approval
    approved_payload: Optional[Dict[str, Any]]  # Direct payload access
    
    # Control flow fields
    control_needs_reclassification: bool
    control_reclassification_reason: Optional[str]
    control_reclassification_count: int
    control_plans_created_count: int           # Number of plans created by orchestrator for current task
    control_current_step_retry_count: int
    control_retry_count: int  # Total retry count for current capability
    control_has_error: bool  # Error state for manual retry handling
    control_error_info: Optional[Dict[str, Any]]  # Error details for retry logic
    control_last_error: Optional[Dict[str, Any]]  # Last error information for retry logic
    control_max_retries: int  # Maximum retries (typically 3)

    control_is_killed: bool
    control_kill_reason: Optional[str]
    control_is_awaiting_validation: bool
    control_validation_context: Optional[Dict[str, Any]]
    control_validation_timestamp: Optional[float]
    
    # UI result fields
    ui_notebook_links: List[str]

    ui_captured_figures: List[str]
    ui_agent_context: Optional[Dict[str, Any]]
    
    # Runtime metadata fields
    runtime_checkpoint_metadata: Optional[Dict[str, Any]]
    runtime_info: Optional[Dict[str, Any]]


# ===== UTILITY FUNCTIONS FOR EVENT UPDATES =====

def create_status_update(message: str, progress: float, complete: bool = False, **metadata) -> Dict[str, Any]:
    """Create a status update event for LangGraph state integration.
    
    This utility function creates properly formatted status update events that can be
    merged into agent state using LangGraph's native state update mechanisms. The
    function generates timestamped status events with progress tracking and metadata
    support for comprehensive execution monitoring.
    
    Status updates are used throughout the framework to provide real-time feedback
    on execution progress, capability status, and system operations. The events are
    automatically formatted for consumption by UI components and logging systems.
    
    :param message: Descriptive message about the current status or operation
    :type message: str
    :param progress: Progress value between 0.0 and 1.0 indicating completion percentage
    :type progress: float
    :param complete: Whether this status update indicates completion of the operation
    :type complete: bool
    :param metadata: Additional metadata fields to include in the status event
    :type metadata: Any
    :return: Dictionary containing status_updates list for LangGraph state merging
    :rtype: Dict[str, Any]
    
    .. note::
       The returned dictionary contains a 'status_updates' key with a list containing
       the new status event. This format is compatible with LangGraph's automatic
       list merging for state updates.
    
    Examples:
        Basic status update::
        
            >>> update = create_status_update("Processing data", 0.5)
            >>> update['status_updates'][0]['message']
            'Processing data'
            >>> update['status_updates'][0]['progress']
            0.5
        
        Completion status with metadata::
        
            >>> update = create_status_update(
            ...     "Analysis complete", 1.0, complete=True,
            ...     node="data_analysis", items_processed=150
            ... )
            >>> update['status_updates'][0]['complete']
            True
            >>> update['status_updates'][0]['items_processed']
            150
    
    .. seealso::
       :func:`create_progress_event` : Create progress tracking events
       :class:`AgentState` : Main state class containing status_updates field
    """
    return {
        "status_updates": [{
            "message": message,
            "progress": progress,
            "complete": complete,
            "timestamp": __import__('time').time(),
            **metadata
        }]
    }


def create_progress_event(current: int, total: int, operation: str, **metadata) -> Dict[str, Any]:
    """Create a progress tracking event for LangGraph state integration.
    
    This utility function creates properly formatted progress events that track
    incremental progress through multi-step operations. The function automatically
    calculates progress percentages and provides timestamped events for detailed
    execution monitoring and user feedback.
    
    Progress events are particularly useful for long-running operations, batch
    processing, and multi-step workflows where users need visibility into
    execution progress and current operation status.
    
    :param current: Current step or item number being processed (1-based)
    :type current: int
    :param total: Total number of steps or items to be processed
    :type total: int
    :param operation: Descriptive name of the operation being performed
    :type operation: str
    :param metadata: Additional metadata fields to include in the progress event
    :type metadata: Any
    :return: Dictionary containing progress_events list for LangGraph state merging
    :rtype: Dict[str, Any]
    
    .. note::
       Progress is automatically calculated as current/total, with safe handling
       for division by zero. The returned dictionary format is compatible with
       LangGraph's automatic list merging for state updates.
    
    .. warning::
       The current parameter should be 1-based (first item is 1, not 0) for
       intuitive progress reporting. The progress calculation handles this
       appropriately.
    
    Examples:
        Basic progress tracking::
        
            >>> event = create_progress_event(3, 10, "Processing files")
            >>> event['progress_events'][0]['current']
            3
            >>> event['progress_events'][0]['progress']
            0.3
        
        Progress with metadata::
        
            >>> event = create_progress_event(
            ...     5, 20, "Analyzing data points",
            ...     file_name="data.csv", bytes_processed=1024
            ... )
            >>> event['progress_events'][0]['operation']
            'Analyzing data points'
            >>> event['progress_events'][0]['file_name']
            'data.csv'
        
        Handling edge cases::
        
            >>> event = create_progress_event(0, 0, "Empty operation")
            >>> event['progress_events'][0]['progress']
            0.0
    
    .. seealso::
       :func:`create_status_update` : Create status update events
       :class:`AgentState` : Main state class containing progress_events field
    """
    return {
        "progress_events": [{
            "current": current,
            "total": total,
            "operation": operation,
            "progress": current / total if total > 0 else 0.0,
            "timestamp": __import__('time').time(),
            **metadata
        }]
    }


# Type aliases for convenience
StateUpdate = Dict[str, Any] 