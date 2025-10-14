"""
Alpha Berkeley Agentic Framework - Classification Node

Task classification and capability selection with sophisticated analysis.
Combines LangGraph infrastructure with core classification logic.

Analyzes user queries to determine required capabilities and data dependencies.
Convention-based LangGraph-native implementation with built-in error handling and retry policies.
"""

from __future__ import annotations
import asyncio

from typing import Optional, Dict, Any, List


from framework.base.decorators import infrastructure_node
from framework.base.errors import ReclassificationRequiredError
from framework.state import AgentState
from framework.state.state import create_status_update
from framework.registry import get_registry
from framework.base import BaseCapability, ClassifierExample, CapabilityMatch
from framework.models import get_chat_completion
from framework.prompts.loader import get_framework_prompts
from configs.config import get_model_config
from configs.logger import get_logger
from configs.streaming import get_streamer
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.nodes import BaseInfrastructureNode


# Use colored logger for classifier
logger = get_logger("framework", "classifier")


@infrastructure_node
class ClassificationNode(BaseInfrastructureNode):
    """Convention-based classification node with sophisticated capability selection logic.
    
    Analyzes user tasks and selects appropriate capabilities using parallel
    LLM-based classification with few-shot examples. Handles both initial
    classification and reclassification scenarios.
    
    Uses LangGraph's sophisticated state merging with built-in error handling
    and retry policies optimized for LLM-based classification operations.
    """
    
    # Loaded through registry configuration
    name = "classifier"
    description = "Task Classification and Capability Selection"
    
    @staticmethod
    def classify_error(exc: Exception, context: Dict[str, Any]) -> ErrorClassification:
        """Built-in error classification for classifier operations.
        
        :param exc: Exception that occurred
        :param context: Error context information
        :return: Classification with severity and retry guidance
        """
        
        # Retry LLM timeouts and network errors
        if hasattr(exc, '__class__') and 'timeout' in exc.__class__.__name__.lower():
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message="Classification service temporarily unavailable, retrying...",
                metadata={"technical_details": f"LLM timeout: {str(exc)}"}
            )
        
        if isinstance(exc, (ConnectionError, TimeoutError)):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message="Network connectivity issues during classification, retrying...",
                metadata={"technical_details": f"Network error: {str(exc)}"}
            )
        
        # Don't retry validation errors (data/logic issues)
        if isinstance(exc, (ValueError, TypeError)):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message="Task classification configuration error",
                metadata={
                    "technical_details": f"Validation error: {str(exc)}",
                    "safety_abort_reason": "Classification system misconfiguration detected"
                }
            )
        
        # Don't retry import/module errors (missing dependencies or path issues)
        # Check both the exception itself and any chained exceptions
        def is_import_error(e):
            if isinstance(e, (ImportError, ModuleNotFoundError, NameError)):
                return True
            # Check chained exceptions (from "raise X from Y")
            if hasattr(e, '__cause__') and e.__cause__:
                return isinstance(e.__cause__, (ImportError, ModuleNotFoundError, NameError))
            return False
        
        if is_import_error(exc):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message="Task classification dependencies not available",
                metadata={
                    "technical_details": f"Import error: {str(exc)}",
                    "safety_abort_reason": "Required classification dependencies missing"
                }
            )
        
        # Handle reclassification requirement
        if isinstance(exc, ReclassificationRequiredError):
            return ErrorClassification(
                severity=ErrorSeverity.RECLASSIFICATION,
                user_message=f"Task needs reclassification: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        
        # Default: CRITICAL for unknown errors (fail safe principle)
        # Only explicitly known errors should be RETRIABLE
        return ErrorClassification(
            severity=ErrorSeverity.CRITICAL,
            user_message=f"Unknown classification error: {str(exc)}",
            metadata={
                "technical_details": f"Error type: {type(exc).__name__}, Details: {str(exc)}",
                "safety_abort_reason": "Unhandled classification system error"
            }
        )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Custom retry policy for LLM-based classification operations.
        
        Classification uses parallel LLM calls for capability selection and can be flaky due to:
        - Multiple concurrent LLM requests
        - Network timeouts to LLM services
        - LLM provider rate limiting
        - Classification model variability
        
        Use more attempts with moderate delays for better reliability.
        """
        return {
            "max_attempts": 4,        # More attempts for LLM classification
            "delay_seconds": 1.0,     # Moderate delay for parallel LLM calls
            "backoff_factor": 1.8     # Moderate backoff to handle rate limiting
        }

    
    @staticmethod
    async def execute(
        state: AgentState, 
        **kwargs
    ) -> Dict[str, Any]:
        """Main classification logic with bypass support and sophisticated capability selection.
        
        Analyzes user tasks and selects appropriate capabilities using parallel
        LLM-based classification. Handles both initial classification and 
        reclassification scenarios with state preservation.
        
        Supports bypass mode where all available capabilities are activated,
        skipping LLM-based classification for performance optimization.
        
        :param state: Current agent state
        :type state: AgentState
        :param kwargs: Additional LangGraph parameters
        :return: Dictionary of state updates for LangGraph
        :rtype: Dict[str, Any]
        """
        
        # Get the current task from state
        current_task = state.get("task_current_task")
        
        if not current_task:
            logger.error("No current task found in state")
            raise ReclassificationRequiredError("No current task found")
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("framework", "classifier", state)
        
        # Check if capability selection bypass is enabled
        bypass_enabled = state.get("agent_control", {}).get("capability_selection_bypass_enabled", False)
        
        if bypass_enabled:
            logger.info("Capability selection bypass enabled - activating all capabilities")
            streamer.status("Bypassing capability selection - activating all capabilities")
            
            # Get all capability names directly from registry
            registry = get_registry()
            active_capabilities = registry.get_stats()['capability_names']
            
            logger.key_info(f"Bypass mode: activated all {len(active_capabilities)} capabilities")
            streamer.status("All capabilities activated")
            
            # Return standardized classification result
            return _create_classification_result(
                active_capabilities=active_capabilities,
                state=state,
                message=f"Bypass mode: activated all {len(active_capabilities)} capabilities",
                is_bypass=True
            )
        
        # Original classification logic continues here...
        # Get previous failure context (may be None for initial classification)
        previous_failure = state.get('control_reclassification_reason')
        reclassification_count = state.get('control_reclassification_count', 0)
        
        if previous_failure:
            streamer.status(f"Reclassifying task (attempt {reclassification_count + 1})...")
            logger.info(f"Reclassifying task (attempt {reclassification_count + 1})...")
            logger.warning(f"Previous failure reason: {previous_failure}")
        else:
            streamer.status("Analyzing task requirements...")
            logger.info("Analyzing task requirements...")
        
        logger.info(f"Classifying task: {current_task}")
                
        # Get available capabilities from capability registry
        registry = get_registry()
        available_capabilities = registry.get_all_capabilities()
        
        logger.debug(f"Available capabilities: {len(available_capabilities)}")
        
        # Run capability selection using the task analyzer (core business logic)
        active_capabilities = await select_capabilities(
            task=current_task,  # Updated parameter name
            available_capabilities=available_capabilities,
            state=state,
            logger=logger,
            previous_failure=previous_failure  # Pass failure context for reclassification
        )
        
        logger.key_info(f"Classification completed with {len(active_capabilities)} active capabilities")
        logger.debug(f"Active capabilities: {active_capabilities}")
        streamer.status("Task classification complete")
        logger.info("Classification completed")
        
        # Return standardized classification result
        return _create_classification_result(
            active_capabilities=active_capabilities,
            state=state,
            message=f"Classification completed with {len(active_capabilities)} capabilities",
            is_bypass=False,
            previous_failure=previous_failure
        )


# ====================================================
# Classification helper functions
# ====================================================

def _create_classification_result(
    active_capabilities: List[str],
    state: AgentState,
    message: str,
    is_bypass: bool = False,
    previous_failure: Optional[str] = None
) -> Dict[str, Any]:
    """Create standardized classification result with all required state updates.
    
    Consolidates the creation of planning fields, control flow updates, and status events
    into a single function to eliminate code duplication between bypass and normal
    classification paths.
    
    :param active_capabilities: List of capability names that were selected
    :param state: Current agent state for extracting reclassification count
    :param message: Status message to display
    :param is_bypass: Whether this is a bypass mode result
    :param previous_failure: Previous failure reason (for reclassification detection)
    :return: Complete state update dictionary for LangGraph
    """
    reclassification_count = state.get('control_reclassification_count', 0)
    
    # Planning state updates
    planning_fields = {
        "planning_active_capabilities": active_capabilities,
        "planning_execution_plan": None,
        "planning_current_step_index": 0
    }
    
    # Control flow updates
    control_flow_update = {
        "control_reclassification_count": reclassification_count + 1,
        "control_reclassification_reason": None
    }
    
    # Status event with comprehensive metadata
    status_event = create_status_update(
        message=message,
        progress=1.0,
        complete=True,
        node="classifier",
        capabilities_selected=len(active_capabilities),
        capability_names=active_capabilities,
        reclassification=bool(previous_failure),
        reclassification_count=reclassification_count + 1,
        bypass_mode=is_bypass
    )
    
    return {**planning_fields, **control_flow_update, **status_event}

async def select_capabilities(
    task: str,
    available_capabilities: List[BaseCapability],
    state: AgentState,
    logger,
    previous_failure: Optional[str] = None
) -> List[str]:  # Return capability names instead of instances
    """Select capabilities needed for the task by using classification.
    
    :param task: Task description for analysis
    :type task: str
    :param available_capabilities: Available capabilities to choose from
    :type available_capabilities: List[BaseCapability]
    :param state: Current agent state
    :type state: AgentState
    :param logger: Logger instance
    :return: List of capability names needed for the task
    :rtype: List[str]
    """
    
    # Get registry to access always-active capability names
    registry = get_registry()
    always_active_names = registry.get_always_active_capability_names()
    
    active_capabilities: List[str] = []  # Store capability names instead of instances
    
    # Step 1: Add always-active capabilities from registry configuration
    for capability in available_capabilities:
        if capability.name in always_active_names:
            active_capabilities.append(capability.name)  # Store name instead of instance
    
    # Step 2: Classify remaining capabilities (those not marked as always_active)
    remaining_capabilities = [cap for cap in available_capabilities if cap.name not in always_active_names]
    
    # Classify each remaining capability
    for capability in remaining_capabilities:
        is_required = await _classify_capability(capability, task, state, logger, previous_failure)
        
        if is_required:
            active_capabilities.append(capability.name)  # Store name instead of instance
    
    logger.info(f"{len(active_capabilities)} capabilities required: {active_capabilities}")
    return active_capabilities


async def _classify_capability(capability: BaseCapability, task: str, state: AgentState, logger, previous_failure: Optional[str] = None) -> bool:
    """Classify a single capability to determine if it's needed.
    
    :param capability: The capability to analyze
    :type capability: BaseCapability
    :param task: Task description for analysis
    :type task: str
    :param state: Current agent state
    :type state: AgentState
    :param logger: Logger instance
    :return: True if capability is required, False otherwise
    :rtype: bool
    """
    # Skip capabilities without classifiers - handle errors during classifier loading
    try:
        classifier = capability.classifier_guide
        if not classifier:
            logger.warning(f"No classifier found for capability '{capability.name}' - skipping")
            return False
    except Exception as e:
        logger.error(f"Error loading classifier for capability '{capability.name}': {e}")
        # For import errors, skip this capability instead of failing entire classification
        if isinstance(e, (ImportError, ModuleNotFoundError, NameError)):
            logger.warning(f"Skipping capability '{capability.name}' due to import error: {e}")
            return False
        # For other errors, re-raise with capability context for better error reporting
        raise Exception(f"Capability '{capability.name}' classifier failed: {e}") from e
        
    capability_instructions = classifier.instructions
    examples_string = ClassifierExample.join(classifier.examples, randomize=True)
    
    # Get classification prompt directly
    prompt_provider = get_framework_prompts()
    classification_builder = prompt_provider.get_classification_prompt_builder()
    system_prompt = classification_builder.get_system_instructions(
        capability_instructions=capability_instructions,
        classifier_examples=examples_string,
        context=None,
        previous_failure=previous_failure
    )
    message = f"{system_prompt}\n\nUser request:\n{task}"
    
    logger.debug(f"\n\nTask Analyzer System Prompt for capability '{capability.name}':\n{message}\n\n")

    try:
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=get_model_config("framework", "classifier"),
            message=message,
            output_model=CapabilityMatch,
        )
        
        if isinstance(response_data, CapabilityMatch):
            single_output = response_data
        else:
            logger.error(f"Classification call for '{capability.name}' did not return a CapabilityMatch. Got: {type(response_data)}")
            single_output = CapabilityMatch(is_match=False)
        
        logger.info(f" >>> Capability '{capability.name}' >>> {single_output.is_match}")
        return single_output.is_match

    except Exception as e:
        logger.error(f"Error in capability classification for '{capability.name}': {e}")
        return False

