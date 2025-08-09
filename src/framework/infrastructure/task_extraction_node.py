"""
ALS Expert Agent - Task Extraction Node

Converts chat conversation history into focused, actionable tasks.
Implemented using convention-based class architecture for LangGraph compatibility.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
import asyncio
import time

# Updated imports for LangGraph compatibility with TypedDict state
from framework.state import AgentState
from framework.base.decorators import infrastructure_node
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.nodes import BaseInfrastructureNode
from framework.registry import get_registry
from framework.models import get_chat_completion
from framework.prompts.loader import get_framework_prompts
    
from configs.logger import get_logger
from configs.streaming import get_streamer
from configs.unified_config import get_model_config, get_config_value
from pydantic_ai import Agent


from framework.prompts.defaults.task_extraction import ExtractedTask
from framework.data_management import (
    get_data_source_manager, 
    create_data_source_request, 
    DataSourceRequester
)

# Native LangGraph message types for checkpointing compatibility
from langchain_core.messages import BaseMessage


logger = get_logger("framework", "task_extraction")
registry = get_registry()

# =============================================================================
# PROMPT BUILDING HELPER FUNCTIONS
# =============================================================================

def build_task_extraction_prompt(messages: List[BaseMessage], retrieval_result) -> str:
    """Build the system prompt with examples, current chat, and integrated data sources context.
    
    :param messages: The native LangGraph messages to extract task from
    :param retrieval_result: Data retrieval result from external sources
    :return: Complete prompt for task extraction
    :rtype: str
    """
    
    prompt_provider = get_framework_prompts()
    task_extraction_builder = prompt_provider.get_task_extraction_prompt_builder()
    
    return task_extraction_builder.get_system_instructions(
        messages=messages,
        retrieval_result=retrieval_result
    )


def _extract_task(messages: List[BaseMessage], retrieval_result, logger) -> ExtractedTask:
    """Extract actionable task from native LangGraph messages with integrated data sources.
    
    Uses PydanticAI agent to analyze conversation and extract structured
    task information including context dependencies.
    
    :param messages: The native LangGraph messages
    :param retrieval_result: DataRetrievalResult containing data from all available sources
    :param logger: Logger instance
    :type logger: logging.Logger
    :return: ExtractedTask with parsed task and context information
    :rtype: ExtractedTask
    """
    if retrieval_result and retrieval_result.has_data:
        logger.debug(f"Injecting data sources into task extraction: {retrieval_result.get_summary()}")
    
    prompt = build_task_extraction_prompt(messages, retrieval_result)
    
    # Use structured LLM generation for task extraction
    task_extraction_config = get_model_config("framework", "task_extraction")
    response = get_chat_completion(
        message=prompt,
        model_config=task_extraction_config,
        output_model=ExtractedTask
    )
    
    return response

# =============================================================================
# CONVENTION-BASED TASK EXTRACTION NODE
# =============================================================================

@infrastructure_node
class TaskExtractionNode(BaseInfrastructureNode):
    """Convention-based task extraction node with sophisticated task processing logic.
    
    Extracts and processes user tasks with context analysis, dependency detection,
    and task refinement. Handles both initial task extraction and task updates
    from conversations.
    
    Features:
    - Configuration-driven error classification and retry policies
    - LLM-based task extraction with fallback mechanisms
    - Context-aware task processing
    - Dependency analysis for chat history and user memory
    - Sophisticated error handling for LLM operations
    """
    
    name = "task_extraction"
    description = "Task Extraction and Processing"
    
    @staticmethod
    def classify_error(exc: Exception, context: dict):
        """Built-in error classification for task extraction operations.
        
        :param exc: Exception that occurred during task extraction
        :type exc: Exception
        :param context: Execution context with task extraction details
        :type context: dict
        :return: Error classification for retry decisions
        :rtype: ErrorClassification
        """
        # Retry on network/API timeouts (LLM can be flaky)
        if isinstance(exc, (ConnectionError, TimeoutError)):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message="Network timeout during task extraction, retrying...",
                technical_details=str(exc)
            )
        
        # Don't retry on validation or configuration errors  
        if isinstance(exc, (ValueError, TypeError)):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message="Task extraction configuration error",
                technical_details=str(exc)
            )
        
        # Don't retry on import/module errors (missing dependencies)
        if isinstance(exc, (ImportError, ModuleNotFoundError)):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message="Task extraction dependencies not available",
                technical_details=str(exc)
            )
        
        # Default: CRITICAL for unknown errors (fail safe principle)
        # Only explicitly known errors should be RETRIABLE
        return ErrorClassification(
            severity=ErrorSeverity.CRITICAL,
            user_message=f"Unknown task extraction error: {str(exc)}",
            technical_details=f"Error type: {type(exc).__name__}, Details: {str(exc)}"
        )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Custom retry policy for LLM-based task extraction operations.
        
        Task extraction uses LLM calls to parse user queries and can be flaky due to:
        - Network timeouts to LLM services
        - LLM provider rate limiting
        - Complex query parsing requirements
        
        Use standard retry attempts with moderate delays since task extraction
        is the entry point and should be reliable but not overly aggressive.
        """
        return {
            "max_attempts": 3,        # Standard attempts for entry point operation
            "delay_seconds": 1.0,     # Moderate delay for LLM service calls
            "backoff_factor": 1.5     # Standard backoff for network issues
        }
    
    @staticmethod
    async def execute(
        state: AgentState, 
        **kwargs
    ) -> Dict[str, Any]:
        """Main task extraction logic with sophisticated error handling and fallback.
        
        Converts conversational exchanges into clear, actionable task descriptions.
        Analyzes native LangGraph messages and external data sources to extract the user's
        actual intent and dependencies on previous conversation context.
        
        :param state: Current agent state (TypedDict)
        :type state: AgentState
        :param kwargs: Additional LangGraph parameters
        :return: Dictionary of state updates to apply
        :rtype: Dict[str, Any]
        """
        
        # Explicit logger retrieval - professional practice
        logger = get_logger("framework", "task_extraction")
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("framework", "task_extraction", state)
        
        # Get native LangGraph messages from flat state structure (move outside try block)
        messages = state["messages"]
        
        try:
            streamer.status("Extracting actionable task from conversation")
            
            # Attempt to retrieve context from data sources if available
            retrieval_result = None
            try:
                data_manager = get_data_source_manager()
                requester = DataSourceRequester("task_extraction", "task_extraction")
                request = create_data_source_request(state, requester)
                retrieval_result = await data_manager.retrieve_all_context(request)
                logger.info(f"Retrieved data from {retrieval_result.total_sources_attempted} sources")
            except (ImportError, ModuleNotFoundError):
                logger.warning("Data source system not available - proceeding without external context")
            except Exception as e:
                logger.warning(f"Data source retrieval failed, proceeding without external context: {e}")
                        
            # Extract task using LLM with or without integrated data sources
            # Run sync function in thread pool to avoid blocking event loop for streaming
            processed_task = await asyncio.to_thread(
                _extract_task, messages, retrieval_result, logger
            )
            
            logger.info(f" * Extracted: '{processed_task.task}...'")
            logger.info(f" * Builds on previous context: {processed_task.depends_on_chat_history}")
            logger.info(f" * Uses memory context: {processed_task.depends_on_user_memory}")
            
            streamer.status("Task extraction completed")
            
            # Create direct state update with correct field names
            return {
                "task_current_task": processed_task.task,
                "task_depends_on_chat_history": processed_task.depends_on_chat_history,
                "task_depends_on_user_memory": processed_task.depends_on_user_memory
            }
            
        except Exception as e:
            # Task extraction failed
            logger.error(f"Task extraction failed: {e}")
            streamer.error(f"Task extraction failed: {str(e)}")
            raise e  # Raise original error for better debugging 