"""Unified Approval System for Production-Ready Workflow Management.

This module provides a comprehensive approval system that integrates with the
LangGraph-native framework architecture for clean approval handling across
all capabilities. The system enables secure, configurable approval workflows
for operations requiring human oversight.

The approval system consists of several key components:

1. **Core Approval Functions**: Create approval interrupts and manage approval state
2. **Configuration Management**: Type-safe configuration loading and validation
3. **Business Logic Evaluators**: Capability-specific approval decision logic
4. **Policy Management**: Centralized approval policy configuration

Key Features:
    - LangGraph-native approval interrupts with structured data
    - Dynamic approval type generation for any capability
    - Configurable approval modes (disabled, selective, all_capabilities)
    - Type-safe configuration management with validation
    - Clean separation between configuration and business logic
    - Production-ready error handling and logging

Examples:
    Basic approval interrupt creation::
    
        >>> from framework.approval import create_code_approval_interrupt
        >>> interrupt_data = create_code_approval_interrupt(
        ...     code="print('Hello World')",
        ...     analysis_details={'safety_level': 'low'},
        ...     execution_mode='readonly',
        ...     safety_concerns=[]
        ... )
        >>> # interrupt_data contains structured data for LangGraph
        
    Configuration management::
    
        >>> from framework.approval import get_approval_manager
        >>> manager = get_approval_manager()
        >>> config = manager.get_python_execution_config()
        >>> print(f"Python approval enabled: {config.enabled}")

.. note::
   This module automatically initializes approval configuration from the global
   config system. Ensure your config.yml contains proper approval settings.

.. warning::
   Approval configuration is security-critical. Missing or invalid configuration
   will cause immediate startup failures to maintain system security.
"""

from .approval_system import (
    create_approval_type,
    create_plan_approval_interrupt,
    create_code_approval_interrupt,
    create_memory_approval_interrupt,
    get_approved_payload_from_state,
    get_approval_resume_data,
    clear_approval_state,
    handle_service_with_interrupts
)
from .approval_manager import ApprovalManager, get_approval_manager
from .config_models import (
    ApprovalMode,
    PythonExecutionApprovalConfig,
    MemoryApprovalConfig,
    GlobalApprovalConfig
)
from .evaluators import (
    ApprovalDecision,
    PythonExecutionApprovalEvaluator,
    MemoryApprovalEvaluator
)

__all__ = [
    # Core approval functions
    'create_approval_type',
    'create_plan_approval_interrupt',
    'create_code_approval_interrupt',
    'create_memory_approval_interrupt',
    'get_approved_payload_from_state',
    'get_approval_resume_data',
    'clear_approval_state',
    'handle_service_with_interrupts',
    
    # Configuration and policy management
    'ApprovalManager',
    'get_approval_manager',
    
    # Configuration models
    'ApprovalMode',
    'PythonExecutionApprovalConfig',
    'MemoryApprovalConfig',
    'GlobalApprovalConfig',
    
    # Business logic evaluators
    'ApprovalDecision',
    'PythonExecutionApprovalEvaluator',
    'MemoryApprovalEvaluator',
] 