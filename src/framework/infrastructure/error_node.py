"""
ALS Expert Agent - Dedicated Error Node

This module contains the ErrorNode that provides centralized, intelligent error handling
using LLM-generated responses with automatically generated context and suggestions.

Features:
- Single point for all error handling
- Automatic error context generation from execution state
- Dynamic suggestions based on error type
- Clean LLM prompt generation with minimal templates
- User-friendly error explanations
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import textwrap
import time
from datetime import datetime

from framework.base.decorators import infrastructure_node
from framework.base.nodes import BaseInfrastructureNode
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.state import AgentState, StateManager
from framework.models import get_chat_completion
from framework.registry import get_registry
from framework.prompts.loader import get_framework_prompts
from configs.unified_config import get_full_configuration, get_model_config
from configs.logger import get_logger
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer


# Use colored logger for error node
logger = get_logger("framework", "error")


class ErrorType(Enum):
    """Standard error types with associated recovery suggestions.
    
    Defines the various error categories that can occur during execution,
    each with specific handling and recovery strategies.
    """
    
    TIMEOUT = "timeout"
    STEP_FAILURE = "step_failure" 
    SAFETY_LIMIT = "safety_limit"
    RETRIABLE_FAILURE = "retriable_failure"
    RECLASSIFICATION_LIMIT = "reclassification_limit"
    CRITICAL_ERROR = "critical_error"
    INFRASTRUCTURE_ERROR = "infrastructure_error"
    EXECUTION_KILLED = "execution_killed"


@dataclass
class ErrorContext:
    """Context for error handling with all relevant information.
    
    Contains all information needed to generate comprehensive error responses
    including execution state, error details, and recovery suggestions.
    """
    
    error_type: ErrorType
    error_message: str
    failed_operation: str
    current_task: str
    capability_name: Optional[str] = None
    technical_details: Optional[str] = None
    total_operations: int = 0
    execution_time: Optional[float] = None
    retry_count: Optional[int] = None
    successful_steps: List[str] = None
    failed_steps: List[str] = None
    capability_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.successful_steps is None:
            self.successful_steps = []
        if self.failed_steps is None:
            self.failed_steps = []
        if self.capability_suggestions is None:
            self.capability_suggestions = []






# =============================================================================
# CONVENTION-BASED ERROR NODE
# =============================================================================

@infrastructure_node
class ErrorNode(BaseInfrastructureNode):
    """Convention-based error node with intelligent error handling and response generation.
    
    Provides centralized error handling with LLM-generated responses and automatic
    context generation. Creates user-friendly error explanations with recovery
    suggestions based on error type and execution context.
    
    Features:
    - Configuration-driven error classification and retry policies
    - LLM-generated error explanations with structured context
    - Automatic error context generation from execution state
    - Capability-specific recovery suggestions
    - Sophisticated error handling for different error types
    """
    
    name = "error"
    description = "Error Response Generation"
    
    @staticmethod
    def classify_error(exc: Exception, context: dict):
        """Built-in error classification for error handling operations.
        
        Any error in the error node is treated as FATAL to prevent infinite loops.
        If the error node fails, execution should terminate immediately rather than
        attempt any retry or recovery mechanisms.
        
        :param exc: Exception that occurred during error handling
        :type exc: Exception
        :param context: Execution context with error handling details
        :type context: dict
        :return: Error classification with FATAL severity
        :rtype: ErrorClassification
        """
        from framework.base.errors import ErrorClassification, ErrorSeverity
        
        # All errors in error node are FATAL - prevents infinite loops
        return ErrorClassification(
            severity=ErrorSeverity.FATAL,
            user_message="Error node failed during error handling",
            technical_details=f"Error node failure: {str(exc)}"
        )
        
    @staticmethod
    async def execute(
        state: AgentState, 
        **kwargs
    ) -> Dict[str, Any]:
        """Main error handling logic with sophisticated error response generation.
        
        Generates comprehensive error responses with LLM-generated explanations
        and automatic context generation from execution state.
        
        :param state: Current agent state
        :type state: AgentState
        :param kwargs: Additional LangGraph parameters
        :return: Dictionary of state updates for LangGraph
        :rtype: Dict[str, Any]
        """
        
        # Explicit logger retrieval - professional practice
        from configs.logger import get_logger
        logger = get_logger("framework", "error")
        
        logger.key_info("Starting error response generation")
        
        # Use get_stream_writer() for pure LangGraph streaming
        from langgraph.config import get_stream_writer
        streaming = get_stream_writer()
        
        if streaming:
            streaming({"event_type": "status", "message": "Generating error response...", "progress": 0.1})
        
        try:
            # Create error context from state
            error_context = _create_error_context_from_state(state)
            
            # Auto-populate execution summary and suggestions
            _populate_error_context(error_context, state)
            
            if streaming:
                streaming({"event_type": "status", "message": "Generating LLM explanation...", "progress": 0.5})
            
            # Generate LLM response with clean prompt
            response = await _generate_error_response(error_context)
            
            if streaming:
                streaming({"event_type": "status", "message": "Error response generated", "progress": 1.0, "complete": True})
            
            logger.key_info(f"Generated error response for {error_context.error_type.value}: {error_context.error_message}")
            
            # Return messages like respond capability so user sees the error response
            from langchain_core.messages import AIMessage
            return {
                "messages": [AIMessage(content=response)]
            }
            
        except Exception as e:
            # Fallback response if error handling fails
            logger.error(f"Error response generation failed: {e}")
            
            if streaming:
                streaming({"event_type": "status", "message": "Using fallback error response", "progress": 1.0, "complete": True})
            
            # Get the original error details for transparency
            error_info = state.get('control_error_info')
            if not isinstance(error_info, dict):
                error_info = {}
            original_error = error_info.get('original_error', 'Unknown error occurred')
            capability_name = error_info.get('capability_name') or error_info.get('node_name', 'unknown operation')
            
            fallback_response = f"""⚠️ **System Error During Error Handling**

**Original Issue:** The '{capability_name}' operation failed with: {original_error}

**Secondary Issue:** The error response generation system encountered an internal error: {str(e)}

This appears to be a system-level issue. The original operation failed (which may be expected), but the error handling system also experienced problems.
"""
            
            # Return fallback response as messages like respond capability
            from langchain_core.messages import AIMessage
            return {
                "messages": [AIMessage(content=fallback_response)]
            }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _create_error_context_from_state(state: AgentState) -> ErrorContext:
    """Create error context from agent state.
    
    Reads error information from control_error_info that was set by the router
    when retries were exhausted or when an error occurred.
    
    :param state: Current agent state
    :type state: AgentState
    :return: Constructed error context
    :rtype: ErrorContext
    """
    # Get current task from task state
    current_task = state.get("task_current_task", "Unknown task")
    
    # Get error information that was set by the router
    error_info = state.get('control_error_info')
    
    # Handle case where error_info is None or not a dictionary
    if not isinstance(error_info, dict):
        error_info = {}
    
    # Extract error details from router-provided error info
    capability_name = error_info.get('capability_name') or error_info.get('node_name')
    original_error = error_info.get('original_error', 'Unknown error occurred')
    user_message = error_info.get('user_message', original_error)
    technical_details = error_info.get('technical_details', original_error)
    execution_time = error_info.get('execution_time', 0.0)
    
    # Determine error type based on classification severity
    error_classification = error_info.get('classification')
    if error_classification and hasattr(error_classification, 'severity'):
        severity = error_classification.severity
        if hasattr(severity, 'value'):
            severity_value = severity.value
        else:
            severity_value = str(severity)
        
        # Map severity to error type
        if severity_value == "retriable":
            error_type = ErrorType.RETRIABLE_FAILURE  
        elif severity_value == "replanning":
            error_type = ErrorType.RECLASSIFICATION_LIMIT
        elif severity_value == "critical":
            error_type = ErrorType.CRITICAL_ERROR
        else:
            error_type = ErrorType.CRITICAL_ERROR
    else:
        error_type = ErrorType.CRITICAL_ERROR
    
    # Build failed operation description
    failed_operation = capability_name or "Unknown operation"
    
    # Get retry count from state
    retry_count = state.get('control_retry_count', 0)
    
    return ErrorContext(
        error_type=error_type,
        error_message=user_message,
        failed_operation=failed_operation,
        current_task=current_task,
        capability_name=capability_name,
        technical_details=technical_details,
        execution_time=execution_time,
        retry_count=retry_count,
        total_operations=StateManager.get_current_step_index(state) + 1
    )





def _populate_error_context(error_context: ErrorContext, state: AgentState) -> None:
    """Auto-populate execution summary and use capability-specific suggestions.
    
    :param error_context: Error context to populate
    :type error_context: ErrorContext
    :param state: Current agent state
    :type state: AgentState
    """
    
    # Generate execution summary from execution_step_results (ordered by step_index)
    step_results = state.get("execution_step_results", {})
    if step_results:
        # Sort by step_index for proper ordering
        ordered_results = sorted(step_results.items(), key=lambda x: x[1].get('step_index', 0))
        
        for step_key, result in ordered_results:
            step_index = result.get('step_index', 0)
            capability_name = result.get('capability', 'unknown')
            task_objective = result.get('task_objective', capability_name)
            
            if result.get('success', False):
                error_context.successful_steps.append(f"Step {step_index + 1}: {task_objective}")
            else:
                error_context.failed_steps.append(f"Step {step_index + 1}: {task_objective} - Failed")
    
    # Use capability-specific suggestions if available, otherwise generate generic ones
    if not error_context.capability_suggestions:
        error_context.capability_suggestions = _generate_generic_suggestions(error_context.error_type)


def _generate_generic_suggestions(error_type: ErrorType) -> List[str]:
    """Generate generic recovery suggestions when capability-specific ones aren't available.
    
    :param error_type: Type of error that occurred
    :type error_type: ErrorType
    :return: List of recovery suggestions
    :rtype: List[str]
    """
    
    generic_suggestions_map = {
        ErrorType.TIMEOUT: [
            "Reduce request complexity or scope",
            "Specify narrower time ranges for data queries"
        ],
        ErrorType.STEP_FAILURE: [
            "Rephrase request with clearer parameters",
            "Simplify query complexity"
        ],
        ErrorType.SAFETY_LIMIT: [
            "Reduce request scope to single operation",
            "Break complex tasks into sequential steps"
        ],
        ErrorType.RETRIABLE_FAILURE: [
            "Retry request (temporary service issue)",
            "Check system service status"
        ],
        ErrorType.RECLASSIFICATION_LIMIT: [
            "Clarify request with specific technical parameters",
            "Use domain-specific terminology"
        ],
        ErrorType.CRITICAL_ERROR: [
            "Contact user support for assistance",
            "Verify system prerequisites and permissions"
        ],
        ErrorType.INFRASTRUCTURE_ERROR: [
            "Contact user support for assistance",
            "Verify access permissions for requested resources"
        ],
        ErrorType.EXECUTION_KILLED: [
            "Reduce operation scope or complexity",
            "Review request against system constraints"
        ]
    }
    
    return generic_suggestions_map.get(error_type, [
        "Rephrase request with clearer parameters",
        "Simplify operation complexity"
    ])


async def _generate_error_response(error_context: ErrorContext) -> str:
    """Generate structured error response with clear separation of auto-generated vs LLM content.
    
    :param error_context: Error context with all relevant details
    :type error_context: ErrorContext
    :return: Complete error response
    :rtype: str
    """
    
    # Auto-generate structured error report sections
    error_report_sections = _build_structured_error_report(error_context)
    
    # Generate LLM explanation for the structured report
    # Run sync function in thread pool to avoid blocking event loop for streaming
    llm_explanation = await asyncio.to_thread(_generate_llm_explanation, error_context)
    
    # Combine structured report with LLM explanation
    full_report = f"{error_report_sections}\n\n{llm_explanation}"
    
    return full_report


def _build_structured_error_report(error_context: ErrorContext) -> str:
    """Build the structured, factual error report sections.
    
    :param error_context: Error context with all relevant details
    :type error_context: ErrorContext
    :return: Structured error report
    :rtype: str
    """
    from datetime import datetime
    
    # Header with timestamp and error type
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_sections = [
        f"⚠️  **ERROR REPORT** - {timestamp}",
        f"**Error Type:** {error_context.error_type.value.upper()}",
        f"**Task:** {error_context.current_task}",
        f"**Failed Operation:** {error_context.failed_operation}",
        f"**Error Message:** {error_context.error_message}"
    ]
    
    # Add capability information if available
    if error_context.capability_name:
        report_sections.append(f"**Capability:** {error_context.capability_name}")
    
    # Add technical details if available
    if error_context.technical_details:
        report_sections.append(f"**Technical Details:** {error_context.technical_details}")
    
    # Add execution statistics
    stats_parts = []
    if error_context.total_operations > 0:
        stats_parts.append(f"Total operations: {error_context.total_operations}")
    if error_context.execution_time is not None:
        stats_parts.append(f"Execution time: {error_context.execution_time:.1f}s")
    if error_context.retry_count is not None and error_context.retry_count > 0:
        stats_parts.append(f"Retry attempts: {error_context.retry_count}")
    
    if stats_parts:
        report_sections.append(f"**Execution Stats:** {', '.join(stats_parts)}")
    
    # Add execution summary if available
    if error_context.successful_steps or error_context.failed_steps:
        summary_lines = ["**Execution Summary:**"]
        if error_context.successful_steps:
            summary_lines.append("✅ **Completed successfully:**")
            for step in error_context.successful_steps:
                summary_lines.append(f"   • {step}")
        if error_context.failed_steps:
            summary_lines.append("❌ **Failed steps:**")
            for step in error_context.failed_steps:
                summary_lines.append(f"   • {step}")
        report_sections.extend(summary_lines)
    
    # Add recovery options if available
    if error_context.capability_suggestions:
        suggestions_lines = ["**Recovery Options:**"]
        for suggestion in error_context.capability_suggestions:
            suggestions_lines.append(f"• {suggestion}")
        report_sections.extend(suggestions_lines)
    
    return "\n".join(report_sections)


def _generate_llm_explanation(error_context: ErrorContext) -> str:
    """Generate LLM explanation that complements the structured report.
    
    :param error_context: Error context with all relevant details
    :type error_context: ErrorContext
    :return: LLM-generated explanation
    :rtype: str
    """
    
    try:
        # Get capabilities overview for system context
        capabilities_overview = get_registry().get_capabilities_overview()
        
        prompt_provider = get_framework_prompts()
        error_builder = prompt_provider.get_error_analysis_prompt_builder()
        
        prompt = error_builder.get_system_instructions(
            capabilities_overview=capabilities_overview,
            error_context=error_context
        )

        # Generate LLM explanation
        explanation = get_chat_completion(
            model_config=get_model_config("framework", "response"),
            message=prompt,
            max_tokens=500
        )
        
        if isinstance(explanation, str) and explanation.strip():
            return f"**Analysis:** {explanation.strip()}"
        else:
            return "**Analysis:** The error occurred during system operation. Please review the recovery options above."
        
    except Exception as e:
        logger.error(f"Error generating LLM explanation: {e}")
        return "**Analysis:** Error details are provided in the structured report above."