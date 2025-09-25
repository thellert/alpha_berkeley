"""
Data Analysis Capability

This capability serves as a specialized prompt engineering and context preparation layer 
for data analysis tasks. It prepares domain-specific prompts and curated data contexts 
that guide the Python Executor Agent to generate appropriate analysis code.
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
import json
import textwrap
from pydantic import BaseModel, Field
from langgraph.types import Command

# Third-party imports

# Import from new framework architecture
from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.base.planning import PlannedStep
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.examples import (
    OrchestratorGuide, OrchestratorExample,
    ClassifierExample, TaskClassifierGuide, ClassifierActions
)
from framework.state import AgentState, StateManager
from framework.state.state_manager import get_execution_steps_summary
from framework.registry import get_registry
from framework.services.python_executor import (
    PythonExecutionRequest,
    PythonServiceResult
)
from framework.models import get_chat_completion
from framework.approval import create_approval_type
from framework.approval.approval_system import (
    get_approval_resume_data,
    clear_approval_state,
    handle_service_with_interrupts
)
from framework.context.context_manager import ContextManager
from configs.config import get_model_config, get_full_configuration
from configs.streaming import get_streamer
from configs.logger import get_logger
from applications.als_assistant.context_classes import AnalysisResultsContext

logger = get_logger("als_assistant", "data_analysis")


registry = get_registry()

# === Capability-Specific Error Classes ===

class DataAnalysisError(Exception):
    """Base class for all data analysis capability errors."""
    pass

class PromptGenerationError(DataAnalysisError):
    """Raised when prompt generation fails."""
    pass

class DataValidationError(DataAnalysisError):
    """Raised when input data validation fails."""
    pass

class ExecutorCommunicationError(DataAnalysisError):
    """Raised when communication with Python Executor fails."""
    pass

class ResultProcessingError(DataAnalysisError):
    """Raised when processing executor results fails."""
    pass

# === Hierarchical Analysis Plan ===

class AnalysisPhase(BaseModel):
    """Individual phase in the analysis plan with detailed subtasks."""
    phase: str = Field(description="Name of the major analytical phase (e.g., 'Data Preprocessing', 'Statistical Analysis')")
    subtasks: List[str] = Field(description="List of specific computational/analytical tasks within this phase")
    output_state: str = Field(description="What this phase accomplishes or produces as input for subsequent phases")

class AnalysisPlan(BaseModel):
    """Wrapper for a list of analysis phases."""
    phases: List[AnalysisPhase] = Field(description="List of analysis phases for the data analysis plan")

async def create_analysis_plan(current_step: Dict[str, Any], task_objective: str, state: AgentState) -> List[AnalysisPhase]:
    """Use a LLM to create a hierarchical analysis plan from the high level task_objective."""
    
    # Use state utility function for execution context information
    execution_steps = get_execution_steps_summary(state)
    
    # Build high level input context information 
    input_info = []
    if current_step.get('inputs'):
        for input_dict in current_step['inputs']:
            for input_type, context_key in input_dict.items():
                input_info.append(f"- {input_type} data will be available from context key '{context_key}'")
    
    input_context = "\n".join(input_info) if input_info else "No specific input context defined."
    
    system_prompt = textwrap.dedent(f"""
        You are an expert in data analysis for the Advanced Light Source (ALS) accelerator facility.
        You are given a specific analysis task that is part of a larger execution plan.
        
        EXECUTION CONTEXT:
        The full execution plan includes these steps:
        {chr(10).join(execution_steps)}
        
        CURRENT TASK FOCUS:
        You are planning for: "{task_objective}"
        
        AVAILABLE INPUTS:
        {input_context}
        
        IMPORTANT CONSTRAINTS:
        - ONLY plan the computational/analytical aspects of the current task
        - Required data inputs are already handled by previous steps and will be available
        - Focus ONLY on calculations, statistics, transformations, and analysis logic
        - **MATCH ANALYSIS COMPLEXITY TO THE REQUEST**: Simple requests should get simple, focused plans
        
        COMPLEXITY ASSESSMENT:
        - Simple requests (e.g., "get min/max values", "calculate average"): Use 1 focused phase
        - Moderate requests (e.g., "analyze trends", "compare periods"): Use 1-2 phases  
        - Complex requests (e.g., "comprehensive analysis", "detect anomalies and patterns"): Use 2-3+ phases
        
        Create a hierarchical analysis plan organized into phases. Each phase should represent a major analytical step with detailed subtasks.
        
        Structure each phase with:
        - phase: Name of the major analytical phase
        - subtasks: List of specific computational/analytical tasks within this phase
        - output_state: What this phase accomplishes or produces

        **Keep it focused and proportional to what the user actually requested.**
        """)

    logging.debug(f"\n\nSystem prompt for analysis plan: {system_prompt}\n\n")
    
    try:
        # Use unified model configuration
        data_analysis_config = get_model_config("als_assistant", "data_analysis")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=data_analysis_config,
            message=f"{system_prompt}\n\nCreate the hierarchical analysis plan based on the given context.",
            output_model=AnalysisPlan,
        )
        
        if isinstance(response_data, AnalysisPlan):
            return response_data.phases
        else:
            raise PromptGenerationError(f"Expected AnalysisPlan, got {type(response_data)}")
        
    except Exception as e:
        raise PromptGenerationError(f"Failed to generate analysis plan: {e}")

def _format_analysis_plan(analysis_plan: List[AnalysisPhase]) -> str:
    """Format the hierarchical plan for the prompt"""
    plan_text = ""
    for i, phase in enumerate(analysis_plan, 1):
        plan_text += f"Phase {i}: {phase.phase}\n"
        if phase.subtasks:
            for subtask in phase.subtasks:
                plan_text += f"  • {subtask}\n"
        if phase.output_state:
            plan_text += f"  → Output: {phase.output_state}\n"
        plan_text += "\n"
    return plan_text

# === Results Dictionary ===

class ResultsDictionary(BaseModel):
    """Dictionary of results for the data analysis."""
    results: Dict[str, Any] = Field(description="Nested dictionary structure template with placeholder values indicating expected data types for analysis results")

async def create_results_dictionary(analysis_plan: List[AnalysisPhase]) -> Dict[str, Any]:
    """Use a LLM to create a results dictionary structure template from the hierarchical analysis plan."""
    
    plan_text = _format_analysis_plan(analysis_plan)
  
    system_prompt = textwrap.dedent(f"""
        You are an expert in data analysis for the Advanced Light Source (ALS) accelerator facility.
        You are given a hierarchical analysis plan and you need to create a results dictionary STRUCTURE TEMPLATE.
        
        This is NOT actual results data, but a template showing what the output structure should look like.
        Use placeholder values that clearly indicate the expected data types and content.
        
        **CRITICAL**: Keep the structure MINIMAL and FOCUSED - only include what's directly needed for the analysis phases.
        Do NOT add extensive metadata, summaries, or auxiliary information unless specifically required by the plan. 
        
        Use these placeholder patterns:
        - "<float>" for numerical values
        - "<int>" for integer counts
        - "<string>" for text descriptions
        - "<list>" for lists of values
        - "<dict>" for nested dictionaries
        - "<timestamp>" for time-related data
        - "<dataframe>" for pandas DataFrames
        - "<array>" for numpy arrays
        
        Example structure (adjust to the analysis plan!):
        results = {{
            "metrics": {{
                "mean_value": "<float>",
                "std_deviation": "<float>",
                "data_points": "<int>"
            }},
            "findings": {{
                "anomalies": "<list>",
                "patterns": "<string>"
            }}
        }}
        
        **Your structure should match the complexity and scope of the analysis plan - don't over-engineer simple requests.**
        Be descriptive with key names so downstream tasks can easily access the right data.
        
        Return the structured template directly - do not wrap in markdown or code blocks. The system will enforce the correct structure automatically.
        
        Hierarchical analysis plan:
        {plan_text}
        """)
    logging.debug(f"\n\nSystem prompt for results dictionary: {system_prompt}\n\n")
    
    try:
        data_analysis_config = get_model_config("als_assistant", "data_analysis")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=data_analysis_config,
            message=f"{system_prompt}\n\nCreate the results dictionary structure template based on the analysis plan.",
            output_model=ResultsDictionary,
        )
        
        if isinstance(response_data, ResultsDictionary):
            return response_data.results
        else:
            raise PromptGenerationError(f"Expected ResultsDictionary, got {type(response_data)}")
        
    except Exception as e:
        raise PromptGenerationError(f"Failed to generate results dictionary: {e}")

def _get_analysis_system_prompts(analysis_plan: List[AnalysisPhase], expected_results: Dict[str, Any], context_description: str) -> List[str]:
    """Prepare minimalistic capability-specific system prompts for the Python Executor"""
    prompts = []
    
    # Pass structured analysis plan
    prompts.append(textwrap.dedent(f"""
        **STRUCTURED EXECUTION PLAN:**
        {_format_analysis_plan(analysis_plan)}
        """))

    # Create output format based on expected results structure
    results_structure = json.dumps(expected_results, indent=2)
    prompts.append(textwrap.dedent(f"""
        **REQUIRED OUTPUT FORMAT:**
        Your code must create a results dictionary matching this exact structure template:
        
        {results_structure}
        
        IMPORTANT: 
        - Replace all placeholder values (like "<float>", "<string>", "<list>") with actual computed values
        - The dictionary keys and nested structure must match exactly
        - Store the final results in a variable called 'results'
        - Downstream tasks depend on this specific structure for accessing your analysis results
        """))
    
    # Add detailed context description
    prompts.append(textwrap.dedent(f"""
        **AVAILABLE CONTEXT DATA:**
        {context_description}
        """))

    return prompts

# --- Capability Definition ---

def _validate_context_data(state: AgentState, step: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and extract required context data for data analysis.
    
    Args:
        state: Current agent state
        step: Current execution step with input requirements
        
    Returns:
        Dict of extracted contexts as specified in step inputs
        
    Raises:
        DataValidationError: If required contexts cannot be extracted or step has no inputs
    """
    
    # Require explicit context specifications from orchestrator
    if not step.get('inputs'):
        raise DataValidationError(
            "Data analysis requires explicit context inputs from the orchestrator. "
            "Step must specify which contexts to analyze (e.g., PV_DATA, ANALYSIS_RESULTS)."
        )
    
    try:
        context_manager = ContextManager(state)
        contexts = context_manager.extract_from_step(step, state)
        if not contexts:
            raise DataValidationError("No contexts could be extracted from specified step inputs.")
        return contexts
    except ValueError as e:
        raise DataValidationError(f"Failed to extract required contexts: {str(e)}")


def _create_analysis_context(service_result: PythonServiceResult) -> AnalysisResultsContext:
    """
    Create AnalysisResultsContext from structured service result.
    
    No validation needed - service guarantees structure and raises exceptions on failure.
    Still performs analysis-specific logic for result extraction.
    
    Args:
        service_result: Structured result from Python executor service
        
    Returns:
        AnalysisResultsContext: Ready-to-store context object
        
    Raises:
        RuntimeError: If analysis results are empty (analysis-specific requirement)
    """
    # Service guarantees execution_result is valid
    execution_result = service_result.execution_result
    analysis_results = execution_result.results
    expected_results = getattr(execution_result, 'expected_results', {})
    
    # Analysis-specific validation: require non-empty results
    if not analysis_results:
        raise RuntimeError(
            "Python executor returned no results. This indicates the generated Python code "
            "did not create a 'results' variable or the variable was not structured correctly."
        )
    
    # Create analysis context with results in the standardized container
    return AnalysisResultsContext(
        results=analysis_results,  # Pass all results in the standardized results field
        expected_schema=expected_results
    )


@capability_node
class DataAnalysisCapability(BaseCapability):
    """Data analysis capability that prepares prompts for the Python Executor Agent."""
    
    name = "data_analysis"
    description = "General data analysis capability that prepares prompts and context for the Python Executor Agent"
    provides = ["ANALYSIS_RESULTS"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute data analysis by preparing prompts for the Python Executor."""
                
        # Define streaming helper here for step awareness
        streamer = get_streamer("als_assistant", "data_analysis", state)
        streamer.status("Preparing data analysis...")
        
        # Extract current step from execution plan
        step = StateManager.get_current_step(state)
        
        # Get Python executor service (needed for both approval and normal cases)
        python_service = registry.get_service("python_executor")
        if not python_service:
            raise RuntimeError("Python executor service not available in registry")
        
        # Get service configuration
        main_configurable = get_full_configuration()
        
        service_config = {
            "configurable": {
                **main_configurable,
                "thread_id": f"data_analysis_{step.get('context_key', 'default')}",
                "checkpoint_ns": "python_executor"
            }
        }
        
        # =====================================================================
        # PHASE 1: CHECK FOR APPROVED CODE EXECUTION
        # =====================================================================
        
        # Check if this is a resume from approval using centralized function
        has_approval_resume, approved_payload = get_approval_resume_data(state, create_approval_type("data_analysis"))
        
        if has_approval_resume:
            if approved_payload:
                logger.success("Using approved code execution from previous approval")
                
                streamer.status("Executing approved code...")
                
                # Resume execution with approval response
                resume_response = {"approved": True}
                resume_response.update(approved_payload)
            else:
                # Explicitly rejected
                logger.info("Data analysis was rejected by user")
                resume_response = {"approved": False}
            
            # Resume the service with Command pattern
            service_result = await python_service.ainvoke(
                Command(resume=resume_response),
                config=service_config
            )
            
            logger.success("✅ Data analysis completed successfully after approval")
            
            # Both approval and normal paths converge to single processing below
            approval_cleanup = clear_approval_state()
        else:
            # =====================================================================  
            # PHASE 2: NORMAL DATA ANALYSIS FLOW
            # =====================================================================
            
            # 1. Validate and extract context data
            extracted_contexts = _validate_context_data(state, step)
        
            # 2. Generate detailed plan and expected results structure using LLMs
            streamer.status("Generating analysis plan...")
            
            analysis_plan = await create_analysis_plan(
                current_step=step, 
                task_objective=step.get('task_objective', 'Analyze available data'),
                state=state,
            )
            logger.info(f"Generated hierarchical plan with {len(analysis_plan)} phases: {[p.phase for p in analysis_plan]}")
            
            streamer.status("Creating results structure template...")
            
            expected_results = await create_results_dictionary(analysis_plan)
            logger.info(f"Generated expected results structure with keys: {list(expected_results.keys()) if expected_results else 'None'}")
            
            # 3. Get context description for available data
            context_manager = ContextManager(state)
            context_description = context_manager.get_context_access_description(step.get('inputs', []))

            # 4. Create adaptive prompts with detailed plan and expected results
            prompts = _get_analysis_system_prompts(analysis_plan, expected_results, context_description)
            
            # 5. Create type-safe execution request (matching framework Python capability pattern)
            user_query = state.get("input_output", {}).get("user_query", "")
            task_objective = step.get("task_objective", "Analyze available data")
            python_config = get_model_config("framework", "python_code_generator")
            
            # Get raw context data
            capability_contexts = state.get('capability_context_data', {})
            
            execution_request = PythonExecutionRequest(
                user_query=user_query,
                task_objective=task_objective,
                capability_prompts=prompts,
                expected_results=expected_results,
                execution_folder_name="data_analysis",
                capability_context_data=capability_contexts,
                config=kwargs.get("config", {}),
                retries=python_config.get("retries", 3)
            )
            
            streamer.status("Generating python code for data analysis...")
            
            logger.info("Calling Python Agent for data analysis")
            await asyncio.sleep(0.01)  # Give event loop time to process observer message
            
            # Use centralized service interrupt handler
            service_result = await handle_service_with_interrupts(
                service=python_service,
                request=execution_request,
                config=service_config,
                logger=logger,
                capability_name="DataAnalysis"
            )
            
            logger.success("Data analysis completed successfully")
            
            # Normal flow doesn't need approval cleanup
            approval_cleanup = None
        
        # ====================================================================
        # CONVERGENCE POINT: Both approval and normal paths meet here
        # ====================================================================
        
        # Process results - single path for both approval and normal execution
        streamer.status("Processing analysis results...")
        
        # Create context using private helper function (handles all complexity)
        analysis_context = _create_analysis_context(service_result)
        
        # Store context using StateManager
        step = StateManager.get_current_step(state)
        context_updates = StateManager.store_context(
            state, 
            registry.context_types.ANALYSIS_RESULTS, 
            step.get("context_key"), 
            analysis_context
        )
        
        # Register generated figures in centralized UI registry
        figure_updates = {}
        if hasattr(service_result, 'execution_result') and service_result.execution_result.figure_paths:
            # Register figures using StateManager with proper accumulation
            accumulating_figures = None  # Start with None for first registration
            
            for figure_path in service_result.execution_result.figure_paths:
                figure_update = StateManager.register_figure(
                    state,
                    capability="data_analysis",
                    figure_path=str(figure_path),
                    display_name="Data Analysis Plot",
                    metadata={
                        "execution_folder": service_result.execution_result.folder_path,
                        "notebook_link": service_result.execution_result.notebook_link,
                        "execution_time": service_result.execution_result.execution_time,
                        "context_key": step.get("context_key"),
                    },
                    current_figures=accumulating_figures  # Pass accumulating list
                )
                # Get the updated list for next iteration
                accumulating_figures = figure_update["ui_captured_figures"]
            
            # Final state update with all accumulated figures
            figure_updates = figure_update  # Last update contains all figures
        
        # Register notebook in centralized UI registry
        notebook_updates = {}
        if hasattr(service_result, 'execution_result') and service_result.execution_result.notebook_link:
            notebook_updates = StateManager.register_notebook(
                state,
                capability="data_analysis",
                notebook_path=str(service_result.execution_result.notebook_path),
                notebook_link=service_result.execution_result.notebook_link,
                display_name="Data Analysis Notebook",
                metadata={
                    "execution_folder": service_result.execution_result.folder_path,
                    "execution_time": service_result.execution_result.execution_time,
                    "context_key": step.get("context_key"),
                }
            )
        
        streamer.status("Data analysis completed successfully")
        
        logger.info(f"Stored AnalysisResultsContext to context under {registry.context_types.ANALYSIS_RESULTS}.{step.get('context_key')}")
        
        # Return results with conditional approval cleanup, figure updates, and notebook updates
        if approval_cleanup:
            return {**context_updates, **approval_cleanup, **figure_updates, **notebook_updates}
        else:
            return {**context_updates, **figure_updates, **notebook_updates}
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Data analysis error classification."""
        
        if isinstance(exc, DataValidationError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,  # Need different data or preprocessing
                user_message=f"Data validation failed: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, PromptGenerationError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Prompt generation failed: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, ExecutorCommunicationError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,  # Python execution not reachable
                user_message=f"Python Executor communication failed: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, ResultProcessingError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,  # Can retry processing
                user_message=f"Result processing failed: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, DataAnalysisError):
            # Generic data analysis error
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Data analysis error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        else:
            # Unknown errors should be classified as RETRIABLE by default
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Unexpected data analysis error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )

    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """
        Create prompt snippet that teaches the orchestrator when and how to use this capability.
        """
        # Define structured examples
        trend_analysis_example = OrchestratorExample(
            step=PlannedStep(
                context_key="trend_analysis_results",
                capability="data_analysis",
                task_objective="Analyze trends and patterns in historical beam current data to identify drift and anomalies",
                expected_output=registry.context_types.ANALYSIS_RESULTS,
                success_criteria="Trend analysis completed with insights",
                inputs=[{registry.context_types.ARCHIVER_DATA: "historical_beam_current_data"}]
            ),
            scenario_description="Trend and pattern analysis of time-series data",
            notes=f"Output stored under {registry.context_types.ANALYSIS_RESULTS} context type. Analyzes historical data to identify trends, anomalies, and patterns."
        )
        
        statistical_analysis_example = OrchestratorExample(
            step=PlannedStep(
                context_key="statistical_analysis_results",
                capability="data_analysis",
                task_objective="Calculate statistical metrics and correlations for control system data comparison",
                expected_output=registry.context_types.ANALYSIS_RESULTS,
                success_criteria="Statistical analysis completed successfully",
                inputs=[
                    {registry.context_types.PV_VALUES: "current_pv_values"}, 
                    {registry.context_types.ARCHIVER_DATA: "historical_beam_current_data"}
                ],
            ),
            scenario_description="Statistical analysis combining current and historical data",
            notes=f"Output stored under {registry.context_types.ANALYSIS_RESULTS} context type. Combines multiple data sources for comprehensive statistical analysis."
        )
        
        outlier_detection_example = OrchestratorExample(
            step=PlannedStep(
                context_key="outlier_analysis_results", 
                capability="data_analysis",
                task_objective="Detect outliers and anomalies in power supply voltage time series using statistical methods",
                expected_output=registry.context_types.ANALYSIS_RESULTS,
                success_criteria="Outliers identified with confidence intervals and timestamps",
                inputs=[{registry.context_types.ARCHIVER_DATA: "power_supply_voltage_data"}],
            ),
            scenario_description="Outlier detection in multiple time series to identify abnormal behavior",
            notes=f"Output stored under {registry.context_types.ANALYSIS_RESULTS} context type. Identifies data points that deviate significantly from normal patterns using statistical methods."
        )
        
        comprehensive_multi_source_analysis_example = OrchestratorExample(
            step=PlannedStep(
                context_key="comprehensive_beam_analysis_results",
                capability="data_analysis",
                task_objective="Perform comprehensive beam stability analysis combining current PV readings, historical trends, and operational parameters",
                expected_output=registry.context_types.ANALYSIS_RESULTS,
                success_criteria="Multi-dimensional analysis completed with correlations and stability metrics",
                inputs=[
                    {registry.context_types.PV_VALUES: "current_beam_parameters"},
                    {registry.context_types.ARCHIVER_DATA: "historical_beam_current_data"},
                    {registry.context_types.ARCHIVER_DATA: "historical_lifetime_data"},
                    {registry.context_types.OPERATION_RESULTS: "recent_operation_results"}
                ]
            ),
            scenario_description="Complex analysis combining multiple data sources and types",
            notes=f"Output stored under {registry.context_types.ANALYSIS_RESULTS} context type. Demonstrates multi-source analysis combining current readings, historical data, and operation results for comprehensive insights."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "data_analysis" steps:**
                - User requests analysis of numerical data (statistics, trends, patterns)
                - Need to process or analyze archiver data or PV values
                - User wants insights from time-series or control system data
                - Analysis is needed before visualization or decision-making
                - User asks for summaries, comparisons, or data-driven conclusions

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "trend_analysis_results", "statistical_summary")
                - inputs: List of input dictionaries from available context data:
                [
                  {{"{registry.context_types.ARCHIVER_DATA}": "historical_data_context_key"}},
                  {{"{registry.context_types.PV_VALUES}": "current_values_context_key"}},
                  {{"{registry.context_types.OPERATION_RESULTS}": "operation_data_context_key"}}
                ]
                **Include ALL relevant data sources for comprehensive analysis!**
                
                **Input Requirements by Analysis Type:**
                - Simple Analysis: Single data source (historical OR current data)
                - Comparative Analysis: Multiple data sources of same type (e.g., multiple historical datasets)
                - Comprehensive Analysis: Multiple data types (historical + current + operation results)
                - Cross-correlation Analysis: Multiple related data sources for relationship analysis
                
                **Output: {registry.context_types.ANALYSIS_RESULTS}**
                - Contains: Dynamic analysis results with flexible structure
                - Available to downstream steps via context system

                **Dependencies and sequencing:**
                - Works with any available data in context (flexible requirements)
                - Often used after data retrieval steps ({registry.capability_names.GET_ARCHIVER_DATA}, {registry.capability_names.PV_VALUE_RETRIEVAL})
                - Results can feed into {registry.capability_names.DATA_VISUALIZATION} or other analysis steps
                - Can analyze both historical and current data when both are available
                """),
            examples=[
                trend_analysis_example,
                statistical_analysis_example,
                outlier_detection_example,
                comprehensive_multi_source_analysis_example
                ],
            priority=30
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for data analysis capability."""
        return TaskClassifierGuide(
            instructions="Determine if the user query requires data analysis of numerical data from the control system.",
            examples=[
                ClassifierExample(
                    query="What tools do you have available?", 
                    result=False, 
                    reason="This is a question about AI capabilities, not a request for data analysis."
                ),
                ClassifierExample(
                    query="Analyze the beam lifetime data from yesterday", 
                    result=True, 
                    reason="This requires analysis of historical data."
                ),
                ClassifierExample(
                    query="Show me a plot of the beam current", 
                    result=False, 
                    reason="This is primarily a visualization request, not analysis."
                ),
                ClassifierExample(
                    query="What patterns do you see in the vacuum pressure data?", 
                    result=True, 
                    reason="This requires analysis to identify patterns in the data."
                ),
                ClassifierExample(
                    query="Calculate the average and standard deviation of the BPM readings", 
                    result=True, 
                    reason="This explicitly requests statistical analysis."
                ),
                ClassifierExample(
                    query="Set the ID gap to 25mm", 
                    result=False, 
                    reason="This is a machine control request, not data analysis."
                ),
                ClassifierExample(
                    query="Are there any anomalies in the power supply data?", 
                    result=True, 
                    reason="This requires analysis to detect anomalies."
                ),
                ClassifierExample(
                    query="Compare the stability before and after the maintenance", 
                    result=True, 
                    reason="This requires comparative analysis of different time periods."
                )
            ],
            actions_if_true=ClassifierActions()
        )