"""
Clarify Capability

This capability asks users specific questions when their queries are ambiguous 
or missing critical information needed for execution. It helps refine user 
intent before proceeding with technical operations.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field
import textwrap

from pydantic_ai import Agent
from framework.base import BaseCapability
from framework.base.decorators import capability_node
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.context.context_manager import ContextManager
from framework.state import AgentState, ChatHistoryFormatter, StateManager
from framework.base.planning import PlannedStep
from framework.models import get_chat_completion
from framework.prompts.loader import get_framework_prompts
from configs.logger import get_logger
from configs.unified_config import get_full_configuration, get_model_config
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


# --- Pydantic Model for Clarifying Questions ---

class ClarifyingQuestionsResponse(BaseModel):
    """Structured response for clarifying questions.
    
    Contains the reason for clarification and specific questions to ask
    the user to gather missing information.
    
    :param reason: Brief explanation of why clarification is needed
    :type reason: str
    :param questions: List of specific, targeted questions to clarify the user's request
    :type questions: List[str]
    :param missing_info: List of types of missing information
    :type missing_info: List[str]
    """
    
    reason: str = Field(description="Brief explanation of why clarification is needed")
    questions: List[str] = Field(
        description="List of specific, targeted questions to clarify the user's request",
        min_items=1,
        max_items=4
    )
    missing_info: List[str] = Field(
        description="List of types of missing information (e.g., 'time_range', 'system_specification')",
        default=[]
    )





# --- Convention-Based Capability Definition ---

@capability_node
class ClarifyCapability(BaseCapability):
    """Ask user for clarification when queries are ambiguous.
    
    Communication capability that generates targeted questions to clarify
    user intent when requests lack sufficient detail or context.
    """
    
    name = "clarify"
    description = "Ask specific questions when user queries are ambiguous or missing critical details"
    provides = []  # Communication capability - no context output (questions go to user via chat history)
    requires = []  # Can work with any execution context
    
    @staticmethod
    async def execute(state: AgentState, **kwargs):
        """Generate specific questions to ask user based on missing information.
        
        :param state: Current agent state
        :type state: AgentState
        :param kwargs: Additional parameters (may include step)
        :return: State update with clarification response
        :rtype: Dict[str, Any]
        """
        
        # Explicit logger retrieval - professional practice
        logger = get_logger("framework", "clarify")
        
        # Extract step if provided
        step = kwargs.get('step', {})
        
        try:
            logger.info("Starting clarification generation")
            
            # Use get_stream_writer() for pure LangGraph streaming
            streaming = get_stream_writer()
            
            if streaming:
                streaming({"event_type": "status", "message": "Analyzing query for clarification...", "progress": 0.2})
            
            # Generate clarifying questions using PydanticAI
            # Run sync function in thread pool to avoid blocking event loop for streaming
            questions_response = await asyncio.to_thread(
                _generate_clarifying_questions, state, step.get('task_objective', 'unknown')
            )
            
            if streaming:
                streaming({"event_type": "status", "message": "Generating clarification questions...", "progress": 0.6})
            
            # Format questions for user interaction
            formatted_questions = _format_questions_for_user(questions_response)
            
            if streaming:
                streaming({"event_type": "status", "message": "Clarification ready", "progress": 1.0, "complete": True})
            
            logger.info(f"Generated {len(questions_response.questions)} clarifying questions")
            
            # Return clarifying questions using native LangGraph pattern
            return {
                "messages": [AIMessage(content=formatted_questions)]
            }
            
        except Exception as e:
            logger.error(f"Error generating clarifying questions: {e}")
            # Let the decorator handle error classification
            raise

    # Optional: Add error classification if needed
    @staticmethod
    def classify_error(exc: Exception, context: dict):
        """Clarify error classification."""
        from framework.base.errors import ErrorClassification, ErrorSeverity
        
        return ErrorClassification(
            severity=ErrorSeverity.RETRIABLE,
            user_message=f"Failed to generate clarifying questions: {str(exc)}",
            technical_details=str(exc)
        )

    def _create_orchestrator_guide(self):
        """Get orchestrator snippet from prompt builder.
        
        :return: Orchestrator prompt snippet for this capability
        """
        
        prompt_provider = get_framework_prompts()  # Registry will determine the right provider
        clarification_builder = prompt_provider.get_clarification_prompt_builder()
        
        return clarification_builder.get_orchestrator_guide()
    
    def _create_classifier_guide(self):
        """Get classifier config from prompt builder.
        
        :return: Classifier configuration for this capability
        """
        
        prompt_provider = get_framework_prompts()  # Registry will determine the right provider
        clarification_builder = prompt_provider.get_clarification_prompt_builder()
        
        return clarification_builder.get_classifier_guide()


# --- Helper Functions ---

def _generate_clarifying_questions(state, task_objective: str) -> ClarifyingQuestionsResponse:
    """Generate specific clarifying questions using PydanticAI.
    
    :param state: Current agent state
    :param task_objective: The task objective to clarify
    :type task_objective: str
    :return: Structured clarifying questions response
    :rtype: ClarifyingQuestionsResponse
    """
    
    # Format entire chat history for context using native message types
    messages = state.get("input_output", {}).get("messages", [])
    chat_history_str = ChatHistoryFormatter.format_for_llm(messages)
    
    # Get relevant context using ContextManager's proper method
    context_manager = ContextManager(state)
    current_step = StateManager.get_current_step(state)
    relevant_context = context_manager.get_human_summaries(current_step)
    
    # Get question generation prompt from framework prompt builder
    prompt_provider = get_framework_prompts()
    clarification_builder = prompt_provider.get_clarification_prompt_builder()
    clarification_query = clarification_builder.build_clarification_query(chat_history_str, task_objective)

    # Use structured LLM generation for clarifying questions
    system_instructions = clarification_builder.get_system_instructions()
    
    # Include available context in the prompt so clarification can be context-aware
    context_info = ""
    if relevant_context:
        context_items = []
        for context_key, context_data in relevant_context.items():
            context_items.append(f"- {context_key}: {context_data}")
        context_info = f"\n\nAvailable context data:\n" + "\n".join(context_items)
    
    message = f"{system_instructions}\n\n{clarification_query}{context_info}"
    
    response_config = get_model_config("framework", "response")
    result = get_chat_completion(
        message=message,
        model_config=response_config,
        output_model=ClarifyingQuestionsResponse
    )
    
    return result



def _format_questions_for_user(questions_response: ClarifyingQuestionsResponse) -> str:
    """Format clarifying questions for direct user interaction.
    
    :param questions_response: The structured questions response
    :type questions_response: ClarifyingQuestionsResponse
    :return: Formatted questions string for user
    :rtype: str
    """
    questions_text = "I need some clarification:\n\n"
    for i, question in enumerate(questions_response.questions, 1):
        questions_text += f"{i}. {question}\n"
    return questions_text


