"""Framework State - Agent Control and Configuration Management.

This module provides comprehensive agent control and configuration management for the
Alpha Berkeley Agent Framework. The control system manages execution flow parameters,
approval workflows, EPICS operations, and runtime overrides through a unified
configuration interface.

**Core Components:**

- :class:`AgentControlState`: Unified control configuration with runtime overrides
- :func:`apply_slash_commands_to_agent_control_state`: Slash command processing utilities

**Configuration Management:**

The control system provides centralized management of agent behavior through
configuration parameters that can be overridden at runtime through various sources:

- **Global Configuration**: Base configuration from unified config system
- **User Valves**: User-specific overrides through UI controls
- **Slash Commands**: Real-time overrides through chat commands
- **Runtime Updates**: Programmatic overrides during execution

**Control Categories:**

1. **Planning Control**: Planning mode enablement and orchestration behavior
2. **EPICS Control**: EPICS write operation permissions and safety controls
3. **Approval Control**: Approval workflow configuration and requirements
4. **Execution Control**: Retry limits, timeouts, and execution boundaries

**State Integration:**

The control state integrates seamlessly with the main AgentState structure,
providing runtime configuration that affects execution behavior throughout
the framework. All control parameters support partial updates for LangGraph
compatibility.

.. note::
   All control state fields are optional to support partial updates in LangGraph's
   state management system. Default values are applied when fields are not provided.

.. seealso::
   :class:`framework.state.AgentState` : Main state structure using control state
   :mod:`configs.unified_config` : Base configuration system
   :mod:`framework.infrastructure.gateway` : Gateway applying slash commands
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Union
from typing_extensions import TypedDict
from dataclasses import dataclass, field
import logging



logger = logging.getLogger(__name__)


class AgentControlState(TypedDict, total=False):
    """Unified agent control configuration with comprehensive runtime override support.
    
    This TypedDict class serves as the single source of truth for all agent control
    parameters throughout the Alpha Berkeley Agent Framework. The control state manages
    execution flow, approval workflows, EPICS operations, and planning modes with
    support for runtime overrides from multiple sources including user interfaces,
    slash commands, and programmatic updates.
    
    **Configuration Architecture:**
    
    The control state implements a layered configuration approach:
    
    1. **Base Configuration**: Default values from unified configuration system
    2. **User Overrides**: User-specific settings through UI valve controls
    3. **Slash Commands**: Real-time overrides through chat-based commands
    4. **Runtime Updates**: Programmatic overrides during execution
    
    **Control Categories:**
    
    - **Planning Control**: Orchestration and planning mode management
    - **EPICS Control**: EPICS write operation permissions and safety
    - **Approval Control**: Workflow approval requirements and modes
    - **Execution Control**: Retry limits, timeouts, and execution boundaries
    
    **LangGraph Integration:**
    
    All fields are optional (total=False) to support LangGraph's partial state
    update patterns. The control state integrates seamlessly with AgentState
    and supports automatic merging of configuration updates.
    
    **Default Values:**
    
    When fields are not provided, the following defaults apply:
    
    - planning_mode_enabled: False (disabled for safety)
    - epics_writes_enabled: False (disabled for safety)
    - approval_global_mode: "selective" (balanced approval approach)
    - python_execution_approval_enabled: True (security-first approach)
    - python_execution_approval_mode: "all_code" (comprehensive approval)
    - memory_approval_enabled: True (protect user memory)
    - max_reclassifications: 1 (prevent infinite reclassification loops)
    - max_planning_attempts: 2 (allow retry but prevent excessive attempts)
    - max_step_retries: 0 (fail fast by default)
    - max_execution_time_seconds: 300 (5-minute execution limit)
    
    .. note::
       Default values prioritize safety and security by disabling potentially
       dangerous operations and enabling approval requirements. Production
       deployments may override these defaults through configuration.
    
    .. warning::
       Changes to control state affect agent behavior immediately. Ensure that
       runtime overrides are validated and appropriate for the execution context.
    
    Examples:
        Basic control state with defaults::
        
            >>> control = AgentControlState()
            >>> # All fields optional, defaults applied by StateManager
        
        Control state with planning enabled::
        
            >>> control = AgentControlState(
            ...     planning_mode_enabled=True,
            ...     max_planning_attempts=3
            ... )
        
        Security-focused configuration::
        
            >>> control = AgentControlState(
            ...     epics_writes_enabled=False,
            ...     approval_global_mode="all_capabilities",
            ...     python_execution_approval_mode="all_code"
            ... )
    
    .. seealso::
       :func:`apply_slash_commands_to_agent_control_state` : Runtime override utilities
       :class:`framework.state.AgentState` : Main state containing control state
       :mod:`configs.unified_config` : Base configuration system
    """
    
    # Planning control
    planning_mode_enabled: bool                         # Whether planning mode is enabled for the agent
    
    # EPICS execution control
    epics_writes_enabled: bool                          # Whether EPICS write operations are allowed
    
    # Approval control
    approval_global_mode: str                           # Global approval mode setting (disabled/selective/all_capabilities)
    python_execution_approval_enabled: bool            # Whether Python execution requires approval
    python_execution_approval_mode: str                # Python approval mode (disabled/epics_writes/all_code)
    memory_approval_enabled: bool                       # Whether memory operations require approval
    
    # Execution flow control
    max_reclassifications: int                          # Maximum number of task reclassifications allowed
    max_planning_attempts: int                          # Maximum number of planning attempts before giving up
    max_step_retries: int                              # Maximum number of retries per execution step
    max_execution_time_seconds: int                    # Maximum execution time in seconds
    

    

    
def apply_slash_commands_to_agent_control_state(agent_control_state: AgentControlState, commands: Dict[str, Optional[str]]) -> AgentControlState:
    """Apply slash command overrides to agent control configuration.
    
    This function processes slash commands from user input and applies them as
    runtime overrides to the agent control state. The function creates a new
    control state instance with the specified overrides applied, supporting
    various command formats and validation logic.
    
    The function handles the complete slash command processing workflow:
    
    1. **Command Validation**: Validates command format and options
    2. **State Copying**: Creates a new control state instance
    3. **Override Application**: Applies command-specific overrides
    4. **Logging**: Records applied changes for debugging and audit
    
    **Supported Commands:**
    
    - **/planning**: Enable/disable planning mode with optional on/off parameter
    - Future commands can be easily added following the same pattern
    
    :param agent_control_state: Current agent control state to override
    :type agent_control_state: AgentControlState
    :param commands: Dictionary mapping command names to their option values
    :type commands: Dict[str, Optional[str]]
    :return: New AgentControlState instance with slash command overrides applied
    :rtype: AgentControlState
    
    .. note::
       The function creates a new AgentControlState instance rather than modifying
       the input state, ensuring immutability and preventing side effects.
    
    .. warning::
       Command validation is performed but invalid options are logged as warnings
       rather than raising exceptions to maintain execution continuity.
    
    Examples:
        Planning mode commands::
        
            >>> current_state = AgentControlState(planning_mode_enabled=False)
            >>> commands = {"planning": None}  # Enable planning
            >>> new_state = apply_slash_commands_to_agent_control_state(
            ...     current_state, commands
            ... )
            >>> new_state['planning_mode_enabled']
            True
        
        Planning mode with explicit option::
        
            >>> commands = {"planning": "off"}  # Disable planning
            >>> new_state = apply_slash_commands_to_agent_control_state(
            ...     current_state, commands
            ... )
            >>> new_state['planning_mode_enabled']
            False
        
        Multiple commands::
        
            >>> commands = {
            ...     "planning": "on",
            ...     # Additional commands can be added here
            ... }
            >>> new_state = apply_slash_commands_to_agent_control_state(
            ...     current_state, commands
            ... )
        
        No commands (passthrough)::
        
            >>> new_state = apply_slash_commands_to_agent_control_state(
            ...     current_state, {}
            ... )
            >>> new_state == current_state
            True
    
    .. seealso::
       :class:`AgentControlState` : Control state structure being modified
       :mod:`framework.infrastructure.gateway` : Gateway parsing slash commands
    """
    if not commands:
        return agent_control_state
        
    # Create a copy for modification
    new_instance = AgentControlState(
        planning_mode_enabled=agent_control_state.get('planning_mode_enabled', False),
        epics_writes_enabled=agent_control_state.get('epics_writes_enabled', False),
        approval_global_mode=agent_control_state.get('approval_global_mode', 'selective'),
        python_execution_approval_enabled=agent_control_state.get('python_execution_approval_enabled', True),
        python_execution_approval_mode=agent_control_state.get('python_execution_approval_mode', 'all_code'),
        memory_approval_enabled=agent_control_state.get('memory_approval_enabled', True),
        max_reclassifications=agent_control_state.get('max_reclassifications', 1),
        max_planning_attempts=agent_control_state.get('max_planning_attempts', 2),
        max_step_retries=agent_control_state.get('max_step_retries', 0),
        max_execution_time_seconds=agent_control_state.get('max_execution_time_seconds', 300),
    )
    
    # Apply planning command: /planning or /planning:on/off
    if 'planning' in commands:
        option = commands['planning']
        if option is None or option in ['', 'on', 'true']:
            new_instance['planning_mode_enabled'] = True
            logger.info(f"Planning mode enabled by slash command: /planning")
        elif option in ['off', 'false']:
            new_instance['planning_mode_enabled'] = False
            logger.info(f"Planning mode disabled by slash command: /planning:{option}")
        else:
            logger.warning(f"Unknown planning option: {option}. Valid options: on, off")
    
    return new_instance