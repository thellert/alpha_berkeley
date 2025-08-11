"""Python Capability - Service Gateway for Code Generation and Execution

This capability acts as the sophisticated gateway between the main agent graph and
the Python executor service, providing seamless integration for code generation,
execution, and result processing. It handles the complete Python execution workflow
including service invocation, approval management, interrupt propagation, and
structured result processing.

The capability provides a clean abstraction layer that:
1. **Service Integration**: Manages communication with the Python executor service
2. **Approval Workflows**: Integrates with the approval system for code execution control
3. **Context Management**: Handles context data passing and result context creation
4. **Error Handling**: Provides sophisticated error classification and recovery
5. **Result Processing**: Structures execution results for capability integration

Key architectural features:
    - Service gateway pattern for clean separation of concerns
    - LangGraph-native approval workflow integration
    - Comprehensive context management for cross-capability data flow
    - Structured result processing with execution metadata
    - Error classification with domain-specific recovery strategies

The capability uses the @capability_node decorator for full LangGraph integration
including streaming, configuration management, error handling, and checkpoint support.

.. note::
   This capability requires the Python executor service to be available in the
   framework registry. All code execution is managed by the separate service.

.. warning::
   Python code execution may require user approval depending on the configured
   approval policies. Execution may be suspended pending user confirmation.

.. seealso::
   :class:`framework.services.python_executor.PythonExecutorService` : Execution service
   :class:`PythonResultsContext` : Execution result context structure
   :class:`framework.approval.ApprovalManager` : Code execution approval workflows  
"""

import asyncio
from typing import Dict, Any, Optional, ClassVar
from dataclasses import dataclass

from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.context.base import CapabilityContext
from framework.context.context_manager import ContextManager
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.state import AgentState, StateManager
from framework.registry import get_registry
from framework.base.examples import OrchestratorGuide, TaskClassifierGuide, ClassifierExample
from framework.services.python_executor.exceptions import CodeRuntimeError
from framework.services.python_executor import PythonServiceResult
from framework.services.python_executor.models import PythonExecutionRequest
from framework.approval import get_approval_resume_data, clear_approval_state, create_approval_type, handle_service_with_interrupts
from configs.logger import get_logger
from configs.streaming import get_streamer
from configs.config import get_full_configuration
from framework.prompts.loader import get_framework_prompts
from langgraph.types import Command, interrupt
from langgraph.errors import GraphInterrupt

logger = get_logger("framework", "python")


registry = get_registry()


# ========================================================
# Context Class
# ========================================================

class PythonResultsContext(CapabilityContext):
    """Context for Python execution results with comprehensive execution metadata.
    
    Provides structured context for Python code execution results including
    generated code, execution output, computed results, performance metrics,
    and resource links. This context enables other capabilities to access
    both the execution process details and the computed results.
    
    The context maintains complete execution metadata including timing information,
    output logs, error details, and generated resources like figures and notebooks.
    This comprehensive tracking enables sophisticated debugging, result analysis,
    and cross-capability integration.
    
    :param code: Generated Python code that was executed
    :type code: str
    :param output: Complete stdout/stderr output from code execution
    :type output: str
    :param results: Structured results dictionary from execution (from results.json)
    :type results: Optional[Dict[str, Any]]
    :param error: Error message if execution failed
    :type error: Optional[str]
    :param execution_time: Total execution time in seconds
    :type execution_time: float
    :param folder_path: Path to execution folder containing generated files
    :type folder_path: Optional[str]
    :param notebook_path: Path to generated Jupyter notebook file
    :type notebook_path: Optional[str]
    :param notebook_link: URL link to access the generated notebook
    :type notebook_link: Optional[str]
    :param figure_paths: List of paths to generated figure/visualization files
    :type figure_paths: Optional[list]
    
    .. note::
       The results field contains structured data computed by the Python code,
       while output contains the raw execution logs and print statements.
    
    .. seealso::
       :class:`framework.context.base.CapabilityContext` : Base context functionality
       :class:`framework.services.python_executor.PythonServiceResult` : Service result structure
    """
    
    code: str
    output: str
    results: Optional[Dict[str, Any]] = None  # Actual computed results from results.json
    error: Optional[str] = None
    execution_time: float = 0.0
    folder_path: Optional[str] = None
    notebook_path: Optional[str] = None
    notebook_link: Optional[str] = None
    figure_paths: Optional[list] = None
    
    CONTEXT_TYPE: ClassVar[str] = "PYTHON_RESULTS"
    CONTEXT_CATEGORY: ClassVar[str] = "COMPUTATIONAL_DATA"
    
    def __post_init__(self):
        if self.figure_paths is None:
            self.figure_paths = []
    
    @property
    def context_type(self) -> str:
        return self.CONTEXT_TYPE
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide comprehensive access information for Python execution results.
        
        Generates detailed access information for other capabilities to understand
        how to interact with Python execution results. Includes access patterns,
        data structure descriptions, and usage examples for both computed results
        and execution metadata.
        
        :param key_name: Optional context key name for access pattern generation
        :type key_name: Optional[str]
        :return: Dictionary containing comprehensive access details and examples
        :rtype: Dict[str, Any]
        
        .. note::
           Access details distinguish between execution metadata (code, output, timing)
           and computed results (structured data from results.json).
        """
        key_ref = key_name if key_name else "key_name"
        return {
            "code": "Python code that was executed",
            "output": "Stdout/stderr logs from code execution", 
            "results": "Computed results dictionary from results.json" if self.results else "No computed results",
            "error": "Error message if execution failed" if self.error else "No errors",
            "execution_time": f"Execution time: {self.execution_time:.2f} seconds",
            "folder_path": "Path to execution folder",
            "notebook_link": "Jupyter notebook link for review",
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.results",
            "example_usage": f"context.{self.CONTEXT_TYPE}.{key_ref}.results gives the computed results dictionary"
        }
    
    def get_human_summary(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate human-readable summary of Python execution for display and analysis.
        
        Creates a comprehensive summary of the Python execution including both
        metadata (execution time, status, resource counts) and actual computed
        results for display in user interfaces and inclusion in agent responses.
        
        The summary includes structured data rather than pre-formatted strings
        to enable robust LLM processing and flexible presentation formatting.
        
        :param key_name: Optional context key name for reference
        :type key_name: Optional[str]
        :return: Dictionary containing human-readable execution summary with results
        :rtype: Dict[str, Any]
        
        .. note::
           Includes both execution metadata and computed results to provide
           complete context for response generation and analysis.
        """
        summary = {
            "type": "Python Results",
            "code_lines": len(self.code.split('\n')) if self.code else 0,
            "execution_time": f"{self.execution_time:.2f}s",
            "notebook_available": bool(self.notebook_link),
            "figure_count": len(self.figure_paths) if self.figure_paths else 0,
            "status": "Failed" if self.error else "Success"
        }
        
        # Include actual execution results for LLM consumption
        if self.results:
            summary["results"] = self.results  # Include computed results dictionary
        if self.output:
            summary["output"] = self.output
        if self.error:
            summary["error"] = self.error
        if self.code:
            summary["code"] = self.code
            
        return summary


# ========================================================
# Private Helper Functions
# ========================================================

def _create_python_context(service_result: PythonServiceResult) -> PythonResultsContext:
    """Create Python results context from structured service execution result.
    
    Transforms the structured result from the Python executor service into a
    capability context object suitable for framework integration. The service
    guarantees result structure validation, enabling clean context creation
    without additional validation requirements.
    
    This helper function provides a clean abstraction between the service result
    format and the capability context structure, enabling easy maintenance if
    either structure evolves independently.
    
    :param service_result: Structured execution result from Python executor service
    :type service_result: PythonServiceResult
    :return: Ready-to-store context object containing all execution details
    :rtype: PythonResultsContext
    
    .. note::
       The service guarantees execution_result validity and structure,
       eliminating the need for additional validation in this helper.
    
    .. seealso::
       :class:`framework.services.python_executor.PythonServiceResult` : Input structure
       :class:`PythonResultsContext` : Output context structure
       :func:`_create_python_capability_prompts` : Related prompt generation helper
       :meth:`PythonCapability.execute` : Main capability method that uses this helper
    """
    # Service guarantees execution_result is valid, so just extract fields directly
    execution_result = service_result.execution_result
    
    return PythonResultsContext(
        code=service_result.generated_code,
        output=execution_result.stdout,
        results=execution_result.results,
        execution_time=execution_result.execution_time,
        folder_path=str(execution_result.folder_path),
        notebook_path=str(execution_result.notebook_path),
        notebook_link=execution_result.notebook_link,
        figure_paths=execution_result.figure_paths
    )


def _create_python_capability_prompts(task_objective: str, user_query: str, context_description: str = "") -> list[str]:
    """Create capability-specific prompts for Python code generation and execution.
    
    Builds structured prompts that provide the Python executor service with
    comprehensive context about the user's request, task objectives, and
    available data context. These prompts guide the LLM in generating
    appropriate Python code for the specific task.
    
    The function creates focused prompts that distinguish between the specific
    task objective, broader user context, and available data sources to enable
    sophisticated code generation that leverages all available information.
    
    :param task_objective: Specific task objective from the execution plan step
    :type task_objective: str
    :param user_query: Original user query or broader task description
    :type user_query: str
    :param context_description: Description of available context data for code access
    :type context_description: str
    :return: List of structured prompts for Python code generation
    :rtype: list[str]
    
    .. note::
       Prompts are structured to provide clear guidance while avoiding
       redundancy when task_objective and user_query contain similar information.
    
    .. seealso::
       :class:`framework.services.python_executor.PythonExecutionRequest` : Request structure
       :func:`_create_python_context` : Related context creation helper
       :class:`framework.context.context_manager.ContextManager` : Context access description source
       :meth:`PythonCapability.execute` : Main capability method that uses these prompts
    """
    prompts = []
    
    if task_objective:
        prompts.append(f"TASK: {task_objective}")
    if user_query and user_query != task_objective:
        prompts.append(f"USER REQUEST: {user_query}")
    if context_description:
        prompts.append(f"CONTEXT ACCESS DESCRIPTION: {context_description}")
        
    return prompts


# ========================================================
# Convention-Based Capability Implementation
# ========================================================

@capability_node
class PythonCapability(BaseCapability):
    """Python execution capability providing comprehensive code generation and execution.
    
    Acts as the sophisticated gateway between the main agent graph and the Python
    executor service, providing seamless integration for Python code generation,
    execution, and result processing. The capability handles the complete Python
    execution workflow including approval management, context integration, and
    structured result processing.
    
    The capability implements a dual-execution pattern that handles both normal
    execution flows and approval resume scenarios:
    
    1. **Normal Execution**: Creates execution requests with context data and invokes
       the Python executor service with comprehensive prompt engineering
    2. **Approval Resume**: Handles resumption of execution after user approval
       with proper state management and cleanup
    
    Key architectural features:
        - Service gateway pattern for clean separation between capability and executor
        - Comprehensive context management for cross-capability data access
        - LangGraph-native approval workflow integration with interrupt handling
        - Structured result processing with execution metadata and computed results
        - Domain-specific error classification for sophisticated recovery strategies
    
    The capability leverages the framework's registry system for service discovery,
    configuration management for proper service setup, and context management for
    seamless data flow between capabilities.
    
    .. note::
       Requires Python executor service availability in framework registry.
       All actual code generation and execution is delegated to the service.
    
    .. warning::
       Python code execution may trigger approval interrupts that suspend
       execution until user confirmation is received.
    
    .. seealso::
       :class:`framework.base.capability.BaseCapability` : Base capability functionality
       :class:`framework.services.python_executor.PythonExecutorService` : Execution backend
       :class:`PythonResultsContext` : Execution result context structure
    """
    
    name = "python"
    description = "Generate and execute Python code using the Python executor service"
    provides = ["PYTHON_RESULTS"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute Python capability with comprehensive service integration and approval handling.
        
        Implements the complete Python execution workflow including service invocation,
        approval management, and result processing. The method handles both normal
        execution scenarios and approval resume scenarios with proper state management.
        
        The execution follows this sophisticated pattern:
        1. **Service Setup**: Retrieves Python executor service and configures execution environment
        2. **Approval Check**: Determines if this is an approval resume or new execution
        3. **Request Creation**: Builds comprehensive execution request with context data
        4. **Service Invocation**: Invokes Python executor with proper configuration
        5. **Result Processing**: Creates structured context from execution results
        
        The method integrates with the framework's approval system to handle code
        execution approval workflows, ensuring user control over potentially sensitive
        code execution while maintaining seamless execution flow.
        
        :param state: Current agent state containing execution context and history
        :type state: AgentState
        :param kwargs: Additional execution parameters from the framework
        :type kwargs: dict
        :return: State updates with Python execution results and context data
        :rtype: Dict[str, Any]
        
        :raises RuntimeError: If Python executor service is not available in registry
        :raises CodeRuntimeError: If Python code execution fails
        :raises ServiceInvocationError: If service communication fails
        
        .. note::
           Uses the framework's configuration system to pass all necessary
           configuration to the Python executor service including thread IDs.
        
        .. warning::
           May trigger LangGraph interrupts for approval workflows that suspend
           execution until user responds to approval requests.
        """
        
        # ========================================
        # GENERIC SETUP (needed for both paths)
        # ========================================
        
        # Extract current step
        step = StateManager.get_current_step(state)
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("framework", "python", state)
        streamer.status("Initializing Python executor service...")
        
        # Get Python executor service from registry
        python_service = registry.get_service("python_executor")
        
        if not python_service:
            raise RuntimeError("Python executor service not available in registry")
        
        # Get the full configurable from main graph (needed for both approval and normal cases)
        main_configurable = get_full_configuration()
        
        # Create service config by extending main graph's configurable
        service_config = {
            "configurable": {
                **main_configurable,  # Pass all main graph configuration to service
                "thread_id": f"python_service_{step.get('context_key', 'default')}",  # Override thread ID for service
                "checkpoint_ns": "python_executor"  # Add checkpoint namespace for service
            }
        }
        
        # ========================================
        # APPROVAL CASE (handle first)
        # ========================================
        
        
        # Check if this is a resume from approval using centralized function
        has_approval_resume, approved_payload = get_approval_resume_data(state, create_approval_type("python_executor"))

        if has_approval_resume:
            if approved_payload:
                logger.resume(f"Sending approval response to Python executor service")
                logger.debug(f"Additional payload keys: {list(approved_payload.keys())}")
                
                # Resume execution with approval response
                resume_response = {"approved": True}
                resume_response.update(approved_payload)
            else:
                # Explicitly rejected
                logger.key_info("Python execution was rejected by user")
                resume_response = {"approved": False}
            
            # Resume the service with full configurable
            service_result = await python_service.ainvoke(
                Command(resume=resume_response),
                config=service_config
            )
            
            logger.info("✅ Python executor service completed successfully after approval")
            
            # Add approval cleanup to prevent state pollution
            approval_cleanup = clear_approval_state()
            
        else:
            # ========================================
            # REGULAR EXECUTION CASE  
            # ========================================
            
            # Create execution request
            # Build capability-specific prompts with task information
            user_query = state.get("input_output", {}).get("user_query", "")
            task_objective = step.get("task_objective", "")
            
            # Build capability-specific prompts
            context_manager = ContextManager(state)
            context_description = context_manager.get_context_access_description(step.get('inputs', []))
            
            # Create capability-specific prompts
            capability_prompts = _create_python_capability_prompts(
                task_objective=task_objective,
                user_query=user_query,
                context_description=context_description
            )
            
            if step.get('inputs', []):
                logger.info(f"Added context access description for {len(step.get('inputs', []))} inputs")
            
            # Get main graph's context data (raw dictionary that contains context data)
            # Python service will recreate ContextManager from this dictionary data
            capability_contexts = state.get('capability_context_data', {})
            
            # DEBUG: Log context data availability
            logger.debug(f"capability_context_data keys: {list(capability_contexts.keys())}")
            logger.debug(f"full state keys: {list(state.keys())}")
            
            execution_request = PythonExecutionRequest(
                user_query=user_query,
                task_objective=task_objective,
                expected_results={},
                capability_prompts=capability_prompts,
                execution_folder_name="python_capability",
                capability_context_data=capability_contexts,
                config=state.get("config"),
                retries=3
            )
            
            streamer.status("Invoking Python executor service...")
            
            # Normal service execution using centralized interrupt handler
            service_result = await handle_service_with_interrupts(
                service=python_service,
                request=execution_request,
                config=service_config,
                logger=logger,
                capability_name="Python"
            )
        
        # Process results - single path for both approval and normal execution
        streamer.status("Processing Python execution results...")
        
        # Create context using private helper function - ultra-clean!
        results_context = _create_python_context(service_result)
        
        # Service only returns on success, so always provide success feedback
        execution_time = results_context.execution_time
        figure_count = len(results_context.figure_paths)
        streamer.status(f"Python execution complete - {execution_time:.2f}s, {figure_count} figures")
        
        # Store context using StateManager
        result_updates = StateManager.store_context(
            state, 
            registry.context_types.PYTHON_RESULTS, 
            step.get("context_key"), 
            results_context
        )
        
        # Combine with approval cleanup (if approval case)
        if has_approval_resume:
            return {**result_updates, **approval_cleanup}
        else:
            return result_updates
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Classify Python execution errors for appropriate recovery strategies.
        
        Provides domain-specific error classification for Python execution failures,
        enabling appropriate recovery strategies based on the specific failure mode.
        Most Python execution errors are classified as RETRIABLE since they often
        represent transient service issues rather than fundamental capability problems.
        
        :param exc: The exception that occurred during Python execution
        :type exc: Exception
        :param context: Error context including capability info and execution state
        :type context: dict
        :return: Error classification with recovery strategy and user messaging
        :rtype: ErrorClassification
        
        .. note::
           Service-related errors are generally retriable since they often
           represent temporary communication or resource issues.
        
        .. seealso::
           :class:`framework.base.errors.ErrorClassification` : Error classification structure
           :class:`framework.services.python_executor.exceptions.CodeRuntimeError` : Service-specific error
           :func:`handle_service_with_interrupts` : Service invocation with error handling
           :class:`framework.base.errors.ErrorSeverity` : Available error severity levels
           :meth:`PythonCapability.execute` : Main method that uses this error classification
        """
        
        # Service-related errors are generally retriable
        return ErrorClassification(
            severity=ErrorSeverity.RETRIABLE,
            user_message=f"Python execution service error: {exc}",
            technical_details=str(exc)
        )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create orchestrator integration guide from prompt builder system.
        
        Retrieves sophisticated orchestration guidance from the application's
        prompt builder system. This guide teaches the orchestrator when and how
        to invoke Python execution within execution plans.
        
        :return: Orchestrator guide for Python capability integration
        :rtype: Optional[OrchestratorGuide]
        
        .. note::
           Guide content is provided by the application layer through the
           framework's prompt builder system for domain-specific customization.
        
        .. seealso::
           :class:`framework.base.examples.OrchestratorGuide` : Guide structure returned by this method
           :meth:`_create_classifier_guide` : Complementary classifier guide creation
           :class:`framework.prompts.loader.FrameworkPrompts` : Prompt system integration
        """
        prompt_provider = get_framework_prompts()
        python_builder = prompt_provider.get_python_prompt_builder()
        
        return python_builder.get_orchestrator_guide()
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create task classification guide from prompt builder system.
        
        Retrieves task classification guidance from the application's prompt
        builder system. This guide teaches the classifier when user requests
        should be routed to Python code execution.
        
        :return: Classification guide for Python capability activation
        :rtype: Optional[TaskClassifierGuide]
        
        .. note::
           Guide content is provided by the application layer through the
           framework's prompt builder system for domain-specific examples.
        """
        prompt_provider = get_framework_prompts()
        python_builder = prompt_provider.get_python_prompt_builder()
        
        return python_builder.get_classifier_guide()


