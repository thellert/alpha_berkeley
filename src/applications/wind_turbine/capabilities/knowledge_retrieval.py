"""
Knowledge Retrieval Capability

This capability retrieves domain-specific knowledge from the wind farm knowledge base
using RAG-style LLM-enhanced query processing to extract relevant technical parameters.
"""

import logging
import textwrap
from typing import Dict, Any, Optional

from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.examples import OrchestratorGuide, OrchestratorExample, ClassifierActions, ClassifierExample, TaskClassifierGuide
from framework.state import AgentState, StateManager
from framework.registry import get_registry
from framework.data_management import DataSourceRequester, create_data_source_request, get_data_source_manager
from applications.wind_turbine.context_classes import TurbineKnowledgeContext
from configs.streaming import get_streamer
from configs.logger import get_logger

logger = get_logger("wind_turbine", "knowledge_retrieval")

registry = get_registry()

# === Knowledge Retrieval Errors ===
class KnowledgeRetrievalError(Exception):
    """Base class for knowledge retrieval related errors."""
    pass

class DataSourceError(KnowledgeRetrievalError):
    """Raised when data source communication fails."""
    pass

@capability_node
class KnowledgeRetrievalCapability(BaseCapability):
    """Retrieve domain-specific knowledge from wind farm knowledge base."""
    
    name = "knowledge_retrieval"
    description = "Retrieve technical standards and performance benchmarks from wind farm knowledge base"
    provides = [registry.context_types.TURBINE_KNOWLEDGE]
    requires = []  # Can work independently, query derived from user intent
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute knowledge retrieval from wind farm knowledge base."""
        
        # Extract current step from execution plan
        step = StateManager.get_current_step(state)
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("wind_turbine", "knowledge_retrieval", state)
        streamer.status("Retrieving wind farm knowledge...")
        
        try:
            # Get data source manager
            data_manager = get_data_source_manager()
            
            # Extract query from step or user input
            user_query = state.get("input_output", {}).get("user_query", "")
            task_objective = step.get("task_objective", "")
            
            # Create knowledge retrieval query
            knowledge_query = task_objective or f"Retrieve wind farm performance standards for: {user_query}"
            
            logger.info(f"Requesting knowledge retrieval for: '{knowledge_query}'")
            
            # Create data source request using helper function
            requester = DataSourceRequester("capability_execution", "knowledge_retrieval")
            request = create_data_source_request(
                state, 
                requester, 
                query=knowledge_query,
                metadata={"user_query": user_query, "task_objective": task_objective}
            )
            
            # Request knowledge from data manager
            retrieval_result = await data_manager.retrieve_all_context(request)
            
            if not retrieval_result.has_data:
                raise DataSourceError("No knowledge retrieved from data sources")
            
            # Extract the knowledge context from result
            knowledge_context = None
            for context in retrieval_result.context_data.values():
                if context.context_type == "TURBINE_KNOWLEDGE":
                    knowledge_context = context.data
                    break
            
            if not knowledge_context:
                raise DataSourceError("Knowledge context not found in retrieved data")
            
            if not isinstance(knowledge_context, TurbineKnowledgeContext):
                raise DataSourceError(f"Expected TurbineKnowledgeContext, got {type(knowledge_context)}")
            
            logger.info(f"Successfully retrieved knowledge with {len(knowledge_context.knowledge_data)} parameters")
            
            # Streaming completion
            streamer.status("Knowledge retrieval complete")
            
            # Store context using StateManager
            context_updates = StateManager.store_context(
                state, 
                registry.context_types.TURBINE_KNOWLEDGE, 
                step.get("context_key"), 
                knowledge_context
            )
            
            return context_updates
            
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {e}")
            raise KnowledgeRetrievalError(f"Failed to retrieve knowledge: {e}") from e
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Knowledge retrieval error classification."""
        
        if isinstance(exc, DataSourceError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Data source communication failed: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, KnowledgeRetrievalError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Knowledge retrieval error: {str(exc)}",
                technical_details=str(exc)
            )
        else:
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Unknown error: {str(exc)}",
                technical_details=str(exc)
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create prompt snippet for knowledge retrieval."""
        
        knowledge_example = OrchestratorExample(
            step={
                "context_key": "performance_standards",
                "capability": "knowledge_retrieval",
                "task_objective": "Retrieve industry performance standards and benchmarks for turbine analysis",
                "expected_output": registry.context_types.TURBINE_KNOWLEDGE,
                "success_criteria": "Performance thresholds and benchmarks retrieved from knowledge base",
                "inputs": []
            },
            scenario_description="Knowledge retrieval for performance benchmarking analysis",
            notes=f"Retrieves domain expertise from knowledge base. Output stored under {registry.context_types.TURBINE_KNOWLEDGE} context type."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "knowledge_retrieval" steps:**
                - When tasks require industry standards, benchmarks, or technical specifications
                - For performance analysis that needs comparison thresholds
                - When domain expertise is needed for decision making
                - For retrieving technical parameters and operational guidelines

                **Required Dependencies:**
                - None (works independently based on query)

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "performance_standards")
                - task_objective: Specific knowledge needed for the task
                - inputs: [] (no dependencies required)
                
                **Output: {registry.context_types.TURBINE_KNOWLEDGE}**
                - Contains: extracted numerical parameters, thresholds, specifications
                - Available fields: efficiency thresholds, capacity factor benchmarks, operational ranges
                - Generated using LLM extraction from technical documentation

                **Knowledge capabilities:**
                - Technical specification extraction
                - Performance benchmark retrieval
                - Threshold and guideline provision
                - Industry standard comparisons
                """),
            examples=[knowledge_example],
            order=5
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for knowledge retrieval."""
        return TaskClassifierGuide(
            instructions="Determine if the task requires domain-specific knowledge, standards, or benchmarks.",
            examples=[
                ClassifierExample(
                    query="What are the industry standards for turbine efficiency?", 
                    result=True, 
                    reason="Request explicitly asks for industry standards."
                ),
                ClassifierExample(
                    query="Compare turbine performance against benchmarks", 
                    result=True, 
                    reason="Performance comparison requires benchmark knowledge."
                ),
                ClassifierExample(
                    query="Show turbine data for last month", 
                    result=False, 
                    reason="Request is for historical data, not knowledge retrieval."
                ),
                ClassifierExample(
                    query="Analyze performance and identify maintenance needs", 
                    result=True, 
                    reason="Analysis requires knowledge of maintenance thresholds and standards."
                ),
                ClassifierExample(
                    query="What maintenance threshold should trigger intervention?", 
                    result=True, 
                    reason="Request asks for specific knowledge about maintenance criteria."
                ),
            ],
            actions_if_true=ClassifierActions()
        )