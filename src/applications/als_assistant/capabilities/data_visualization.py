"""
Data Visualization Capability

This capability serves as a specialized prompt engineering and formatting layer 
for data visualization tasks. It prepares domain-specific prompts and structured 
data contexts that guide the Python Executor Agent to generate publication-quality 
plots and interactive displays tailored for accelerator physics applications.
"""

# Standard library imports
import asyncio
import json
import logging
import textwrap
from typing import List, Dict, Any, Optional

# Third-party imports
from pydantic import BaseModel, Field
from langgraph.types import Command

# Local imports - framework
from framework.approval import create_approval_type
from framework.approval.approval_system import (
    get_approval_resume_data,
    clear_approval_state,
    handle_service_with_interrupts
)
from framework.base.capability import BaseCapability
from framework.base.decorators import capability_node
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.examples import (
    OrchestratorGuide, OrchestratorExample,
    ClassifierExample, TaskClassifierGuide, ClassifierActions
)
from framework.base.planning import PlannedStep
from framework.context.context_manager import ContextManager
from framework.models import get_chat_completion
from framework.registry import get_registry
from framework.services.python_executor import (
    PythonExecutionRequest,
    PythonExecutionSuccess,
    CodeRuntimeError,
    PythonServiceResult
)
from framework.state import AgentState, StateManager
from framework.state.state_manager import get_execution_steps_summary

# Local imports - configs
from configs.logger import get_logger
from configs.streaming import get_streamer
from configs.config import get_model_config, get_full_configuration

# Local imports - application
from applications.als_assistant.context_classes import VisualizationResultsContext
logger = get_logger("als_assistant", "data_visualization")


registry = get_registry()


# === Capability-Specific Error Classes ===

class DataVisualizationError(Exception):
    """Base class for all data visualization capability errors."""
    pass

class PromptGenerationError(DataVisualizationError):
    """Raised when prompt generation fails."""
    pass

class VisualizationDataError(DataVisualizationError):
    """Raised when visualization data validation fails."""
    pass

class ExecutorCommunicationError(DataVisualizationError):
    """Raised when communication with Python Executor fails."""
    pass

class ResultProcessingError(DataVisualizationError):
    """Raised when processing executor results fails."""
    pass

# === Hierarchical Visualization Plan ===

class VisualizationPhase(BaseModel):
    """Individual phase in the visualization plan with detailed subtasks."""
    phase: str = Field(description="Name of the major visualization phase (e.g., 'Data Preparation', 'Plot Creation')")
    subtasks: List[str] = Field(description="List of specific visualization/plotting tasks within this phase")
    output_state: str = Field(description="What this phase accomplishes or produces as input for subsequent phases")

class VisualizationPlan(BaseModel):
    """Wrapper for a list of visualization phases."""
    phases: List[VisualizationPhase] = Field(description="List of visualization phases for the data visualization plan")

async def create_visualization_plan(current_step: Dict[str, Any], task_objective: str, state: AgentState) -> List[VisualizationPhase]:
    """Use a LLM to create a hierarchical visualization plan from the high level task_objective."""
    
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
        You are an expert in data visualization for the Advanced Light Source (ALS) accelerator facility.
        You are given a specific visualization task that is part of a larger execution plan.
        
        EXECUTION CONTEXT:
        The full execution plan includes these steps:
        {chr(10).join(execution_steps)}
        
        CURRENT TASK FOCUS:
        You are planning for: "{task_objective}"
        
        AVAILABLE INPUTS:
        {input_context}
        
        IMPORTANT CONSTRAINTS:
        - ONLY plan the visualization/plotting aspects of the current task
        - Required data inputs are already handled by previous steps and will be available
        - Focus ONLY on plot creation, formatting, styling, and visual presentation
        - **MATCH VISUALIZATION COMPLEXITY TO THE REQUEST**: Simple requests should get simple, focused plans
        
        COMPLEXITY ASSESSMENT:
        - Simple requests (e.g., "plot beam current", "show status"): Use 1 focused phase
        - Moderate requests (e.g., "create dashboard", "compare trends"): Use 1-2 phases  
        - Complex requests (e.g., "comprehensive visualization", "multi-panel analysis"): Use 2-3+ phases
        
        Create a hierarchical visualization plan organized into phases. Each phase should represent a major visualization step with detailed subtasks.
        
        Structure each phase with:
        - phase: Name of the major visualization phase
        - subtasks: List of specific visualization/plotting tasks within this phase
        - output_state: What this phase accomplishes or produces

        **Keep it focused and proportional to what the user actually requested.**
        
        """)

    logging.debug(f"\n\nSystem prompt for visualization plan: {system_prompt}\n\n")
    
    try:
        # Use unified model configuration
        data_visualization_config = get_model_config("als_assistant", "data_visualization")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=data_visualization_config,
            message=f"{system_prompt}\n\nCreate the hierarchical visualization plan based on the given context.",
            output_model=VisualizationPlan,
        )
        
        if isinstance(response_data, VisualizationPlan):
            return response_data.phases
        else:
            raise PromptGenerationError(f"Expected VisualizationPlan, got {type(response_data)}")
        
    except Exception as e:
        raise PromptGenerationError(f"Failed to generate visualization plan: {e}")

def _format_visualization_plan(visualization_plan: List[VisualizationPhase]) -> str:
    """Format the hierarchical plan for the prompt"""
    plan_text = ""
    for i, phase in enumerate(visualization_plan, 1):
        plan_text += f"Phase {i}: {phase.phase}\n"
        if phase.subtasks:
            for subtask in phase.subtasks:
                plan_text += f"  • {subtask}\n"
        if phase.output_state:
            plan_text += f"  → Output: {phase.output_state}\n"
        plan_text += "\n"
    return plan_text

# === Results Dictionary ===

class VisualizationResultsDictionary(BaseModel):
    """Dictionary of results for the data visualization."""
    results: Dict[str, Any] = Field(description="Nested dictionary structure template with placeholder values indicating expected data types for visualization results")

async def create_visualization_results_dictionary(visualization_plan: List[VisualizationPhase]) -> Dict[str, Any]:
    """Use a LLM to create a results dictionary structure template from the hierarchical visualization plan."""
    
    plan_text = _format_visualization_plan(visualization_plan)
  
    system_prompt = textwrap.dedent(f"""
        You are an expert in data visualization for the Advanced Light Source (ALS) accelerator facility.
        You are given a hierarchical visualization plan and you need to create a results dictionary STRUCTURE TEMPLATE.
        
        This is NOT actual results data, but a template showing what the output structure should look like.
        Use placeholder values that clearly indicate the expected data types and content.
        
        **CRITICAL**: Keep the structure MINIMAL and FOCUSED - only include what's directly needed for the visualization phases.
        Do NOT add extensive metadata, summaries, or auxiliary information unless specifically required by the plan. 
        
        Use these placeholder patterns:
        - "<list>" for lists of file paths
        - "<string>" for text descriptions  
        - "<dict>" for nested dictionaries
        - "<int>" for counts
        
        Example structure (adjust to the visualization plan!):
        results = {{
            "plot_files": ["<list>"],
            "plot_metadata": {{
                "plot_types": ["<list>"],
                "summary": "<string>",
                "file_formats": ["<list>"]
            }}
        }}
        
        **Your structure should match the complexity and scope of the visualization plan - don't over-engineer simple requests.**
        Be descriptive with key names so downstream tasks can easily access the right data.
        
        Return the structured template directly - do not wrap in markdown or code blocks. The system will enforce the correct structure automatically.
        
        This is the visualization plan:
        {plan_text}
        """)
    logging.debug(f"\n\nSystem prompt for visualization results dictionary: {system_prompt}\n\n")
    
    try:
        data_visualization_config = get_model_config("als_assistant", "data_visualization")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=data_visualization_config,
            message=f"{system_prompt}\n\nCreate the results dictionary structure template based on the visualization plan.",
            output_model=VisualizationResultsDictionary,
        )
        
        if isinstance(response_data, VisualizationResultsDictionary):
            return response_data.results
        else:
            raise PromptGenerationError(f"Expected VisualizationResultsDictionary, got {type(response_data)}")
        
    except Exception as e:
        raise PromptGenerationError(f"Failed to generate visualization results dictionary: {e}")

def _get_visualization_system_prompts(visualization_plan: List[VisualizationPhase], expected_results: Dict[str, Any], context_description: str) -> List[str]:
    """Prepare minimalistic capability-specific system prompts for the Python Executor"""
    prompts = []
    
    # Pass structured visualization plan
    prompts.append(textwrap.dedent(f"""
        **STRUCTURED VISUALIZATION PLAN:**
        {_format_visualization_plan(visualization_plan)}
        """))

    # Create output format based on expected results structure
    results_structure = json.dumps(expected_results, indent=2)
    prompts.append(textwrap.dedent(f"""
        **REQUIRED OUTPUT FORMAT:**
        Your code must create a results dictionary matching this exact structure template:
        
        {results_structure}
        
        IMPORTANT: 
        - Replace all placeholder values (like "<list>", "<string>", "<dict>") with actual computed values
        - The dictionary keys and nested structure must match exactly
        - Store the final results in a variable called 'results'
        - Downstream tasks depend on this specific structure for accessing your visualization results
        """))
    
    # Add detailed context description
    prompts.append(textwrap.dedent(f"""
        **AVAILABLE CONTEXT DATA:**
        {context_description}
        """))
    
    # Add figure handling instructions
    prompts.append(textwrap.dedent("""
        **FIGURE HANDLING REQUIREMENTS:**
        - Save all generated figures with descriptive filenames (e.g., 'beam_current_trends.png', 'sector_comparison.png')
        - Use meaningful names that describe the plot content, not generic names like 'plot.png'
        - After saving each figure, immediately call plt.close() or plt.close(fig) to free memory and prevent duplicate saves
        - Example pattern:
          ```python
          plt.figure(figsize=(12, 6))
          # ... create your plot ...
          plt.savefig('descriptive_filename.png', dpi=300, bbox_inches='tight')
          plt.close()  # Important: Close the figure after saving
          ```
        """))

    return prompts

# --- Capability Definition ---

def _validate_context_data(state: AgentState, step: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and extract required context data for data visualization.
    
    Args:
        state: Current agent state
        step: Current execution step with input requirements
        
    Returns:
        Dict of extracted contexts as specified in step inputs
        
    Raises:
        DataVisualizationError: If required contexts cannot be extracted or step has no inputs
    """
    
    # Require explicit context specifications from orchestrator
    if not step.get('inputs'):
        raise DataVisualizationError(
            "Data visualization requires explicit context inputs from the orchestrator. "
            "Step must specify which contexts to visualize (e.g., PV_DATA, ANALYSIS_RESULTS)."
        )
    
    try:
        context_manager = ContextManager(state)
        contexts = context_manager.extract_from_step(step, state)
        if not contexts:
            raise DataVisualizationError("No contexts could be extracted from specified step inputs.")
        return contexts
    except ValueError as e:
        raise DataVisualizationError(f"Failed to extract required contexts: {str(e)}")


def _create_visualization_context(service_result: PythonServiceResult) -> VisualizationResultsContext:
    """
    Create VisualizationResultsContext from structured service result.
    
    No validation needed - service guarantees structure and raises exceptions on failure.
    Still performs visualization-specific logic for result extraction.
    
    Args:
        service_result: Structured result from Python executor service
        
    Returns:
        VisualizationResultsContext: Ready-to-store context object
        
    Raises:
        RuntimeError: If visualization results are empty (visualization-specific requirement)
    """
    # Service guarantees execution_result is valid
    execution_result = service_result.execution_result
    visualization_results = execution_result.results
    expected_results = getattr(execution_result, 'expected_results', {})
    
    # Visualization-specific validation: require non-empty results
    if not visualization_results:
        raise RuntimeError(
            "Python executor returned no results. This indicates the generated Python code "
            "did not create a 'results' variable or the variable was not structured correctly."
        )
    
    # Create visualization context with results in the standardized container
    return VisualizationResultsContext(
        results=visualization_results,  # Pass all results in the standardized results field
        expected_schema=expected_results
    )



@capability_node
class DataVisualizationCapability(BaseCapability):
    """Data visualization capability that prepares prompts for generating publication-quality plots."""
    
    name = "data_visualization"
    description = "Data visualization capability that prepares prompts and context for generating publication-quality plots and displays"
    provides = ["VISUALIZATION_RESULTS"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute data visualization by preparing prompts for the Python Executor."""
                
        # Define streaming helper here for step awareness
        streamer = get_streamer("als_assistant", "data_visualization", state)
        streamer.status("Preparing data visualization...")
        
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
                "thread_id": f"data_visualization_{step.get('context_key', 'default')}",
                "checkpoint_ns": "python_executor"
            }
        }
        
        # =====================================================================
        # PHASE 1: CHECK FOR APPROVED CODE EXECUTION
        # =====================================================================
        
        # Check if this is a resume from approval using centralized function
        has_approval_resume, approved_payload = get_approval_resume_data(state, create_approval_type("data_visualization"))
        
        if has_approval_resume:
            if approved_payload:
                logger.success("Using approved code execution from previous approval")
                
                streamer.status("Executing approved code...")
                
                # Resume execution with approval response
                resume_response = {"approved": True}
                resume_response.update(approved_payload)
            else:
                # Explicitly rejected
                logger.info("Data visualization was rejected by user")
                resume_response = {"approved": False}
            
            # Resume the service with Command pattern
            service_result = await python_service.ainvoke(
                Command(resume=resume_response),
                config=service_config
            )
            
            logger.success("✅ Data visualization completed successfully after approval")
            
            # Both approval and normal paths converge to single processing below
            approval_cleanup = clear_approval_state()
        else:
            # =====================================================================  
            # PHASE 2: NORMAL DATA VISUALIZATION FLOW
            # =====================================================================
            
            # 1. Validate and extract context data
            extracted_contexts = _validate_context_data(state, step)
        
            # 2. Generate detailed plan and expected results structure using LLMs
            streamer.status("Generating visualization plan...")
            
            visualization_plan = await create_visualization_plan(
                current_step=step, 
                task_objective=step.get('task_objective', 'Create appropriate visualizations for the available data'),
                state=state,
            )
            logger.info(f"Generated hierarchical plan with {len(visualization_plan)} phases: {[p.phase for p in visualization_plan]}")
            
            streamer.status("Creating results structure template...")
            
            expected_results = await create_visualization_results_dictionary(visualization_plan)
            logger.info(f"Generated expected results structure with keys: {list(expected_results.keys()) if expected_results else 'None'}")
            
            # 3. Get context description for available data
            context_manager = ContextManager(state)
            context_description = context_manager.get_context_access_description(step.get('inputs', []))

            # 4. Create adaptive prompts with detailed plan and expected results
            prompts = _get_visualization_system_prompts(visualization_plan, expected_results, context_description)
            
            # 5. Create type-safe execution request (matching framework Python capability pattern)
            user_query = state.get("input_output", {}).get("user_query", "")
            task_objective = step.get("task_objective", "Create appropriate visualizations for the available data")
            python_config = get_model_config("framework", "python_code_generator")
            
            # Get raw context data
            capability_contexts = state.get('capability_context_data', {})
            
            execution_request = PythonExecutionRequest(
                user_query=user_query,
                task_objective=task_objective,
                capability_prompts=prompts,
                expected_results=expected_results,
                execution_folder_name="data_visualization",
                capability_context_data=capability_contexts,
                config=kwargs.get("config", {}),
                retries=python_config.get("retries", 3)
            )
            
            streamer.status("Generating python code for data visualization...")
            
            logger.info("Calling Python Agent for data visualization")
            await asyncio.sleep(0.01)  # Give event loop time to process observer message
            
            # Use centralized service interrupt handler
            service_result = await handle_service_with_interrupts(
                service=python_service,
                request=execution_request,
                config=service_config,
                logger=logger,
                capability_name="DataVisualization"
            )
            
            logger.success("Data visualization completed successfully")
            
            # Normal flow doesn't need approval cleanup
            approval_cleanup = None
        
        # ====================================================================
        # CONVERGENCE POINT: Both approval and normal paths meet here
        # ====================================================================
        
        # Process results - single path for both approval and normal execution
        streamer.status("Processing visualization results...")
        
        # Create context using private helper function (handles all complexity)
        visualization_context = _create_visualization_context(service_result)
        
        # Store context using StateManager
        step = StateManager.get_current_step(state)
        context_updates = StateManager.store_context(
            state, 
            registry.context_types.VISUALIZATION_RESULTS, 
            step.get("context_key"), 
            visualization_context
        )
        
        # Register figures in centralized UI registry
        figure_updates = {}
        if hasattr(service_result, 'execution_result') and service_result.execution_result.figure_paths:
            # Register figures using StateManager with proper accumulation
            accumulating_figures = None  # Start with None for first registration
            
            for figure_path in service_result.execution_result.figure_paths:
                figure_update = StateManager.register_figure(
                    state,
                    capability="data_visualization",
                    figure_path=str(figure_path),
                    display_name="Data Visualization Plot",
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
                capability="data_visualization",
                notebook_path=str(service_result.execution_result.notebook_path),
                notebook_link=service_result.execution_result.notebook_link,
                display_name="Data Visualization Notebook",
                metadata={
                    "execution_folder": service_result.execution_result.folder_path,
                    "execution_time": service_result.execution_result.execution_time,
                    "context_key": step.get("context_key"),
                }
            )
        
        streamer.status("Data visualization completed successfully")
        
        logger.info(f"Stored VisualizationResultsContext to context under {registry.context_types.VISUALIZATION_RESULTS}.{step.get('context_key')}")
        
        # Return results with conditional approval cleanup, figure updates, and notebook updates
        if approval_cleanup:
            return {**context_updates, **approval_cleanup, **figure_updates, **notebook_updates}
        else:
            return {**context_updates, **figure_updates, **notebook_updates}
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Data visualization error classification."""
        
        if isinstance(exc, VisualizationDataError):
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
        elif isinstance(exc, DataVisualizationError):
            # Generic data visualization error
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Data visualization error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        else:
            # Unknown errors should be classified as RETRIABLE by default
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Unexpected data visualization error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """
        Create prompt snippet that teaches the orchestrator when and how to use this capability.
        """
        # Define structured examples
        time_series_plot_example = OrchestratorExample(
            step=PlannedStep(
                context_key="beam_current_plots",
                capability="data_visualization",
                task_objective="Create time series plots of beam current data showing trends and anomalies",
                expected_output=registry.context_types.VISUALIZATION_RESULTS,
                success_criteria="Publication-quality time series plots generated",
                inputs=[
                    {registry.context_types.ARCHIVER_DATA: "historical_beam_current_data"},
                    {registry.context_types.PV_ADDRESSES: "beam_current_pv_addresses"}
                ]
            ),
            scenario_description="Time series visualization of historical data",
            notes=f"Output stored under {registry.context_types.VISUALIZATION_RESULTS} context type. Creates professional time series plots with proper axis labels and styling."
        )
        
        analysis_visualization_example = OrchestratorExample(
            step=PlannedStep(
                context_key="statistical_plots",
                capability="data_visualization",
                task_objective="Create statistical plots and correlation matrices from analysis results",
                expected_output=registry.context_types.VISUALIZATION_RESULTS,
                success_criteria="Statistical plots and correlation visualizations created",
                inputs=[{registry.context_types.ANALYSIS_RESULTS: "statistical_analysis_results"}]
            ),
            scenario_description="Statistical analysis result visualization",
            notes=f"Output stored under {registry.context_types.VISUALIZATION_RESULTS} context type. Creates statistical plots, histograms, correlation matrices from analysis results."
        )
        
        scan_results_example = OrchestratorExample(
            step=PlannedStep(
                context_key="optimization_plots",
                capability="data_visualization",
                task_objective="Plot parameter sweep results showing flux vs gap relationship with hysteresis",
                expected_output=registry.context_types.VISUALIZATION_RESULTS,
                success_criteria="Scan results and optimization trajectories visualized",
                inputs=[{registry.context_types.OPERATION_RESULTS: "flux_vs_gap_sweep_results"}]
            ),
            scenario_description="Machine operation and scan result visualization",
            notes=f"Output stored under {registry.context_types.VISUALIZATION_RESULTS} context type. Visualizes parameter scans, optimization results, and machine operation data."
        )
        
        comprehensive_dashboard_example = OrchestratorExample(
            step=PlannedStep(
                context_key="system_dashboard",
                capability="data_visualization",
                task_objective="Create multi-panel dashboard combining current status, historical trends, and analysis results",
                expected_output=registry.context_types.VISUALIZATION_RESULTS,
                success_criteria="Multi-panel dashboard with integrated data visualization",
                inputs=[
                    {registry.context_types.ARCHIVER_DATA: "historical_beam_current_data"},
                    {registry.context_types.ANALYSIS_RESULTS: "statistical_analysis_results"}, 
                    {registry.context_types.PV_VALUES: "current_pv_values"}
                ]
            ),
            scenario_description="Comprehensive dashboard combining multiple data sources",
            notes=f"Output stored under {registry.context_types.VISUALIZATION_RESULTS} context type. Creates integrated dashboards when multiple data sources are available."
        )
        
        complex_operation_visualization_example = OrchestratorExample(
            step=PlannedStep(
                context_key="operation_analysis_plots",
                capability="data_visualization",
                task_objective="Create comprehensive visualization of EPU gap sweep results including hysteresis plots, beam size trends, and statistical analysis",
                expected_output=registry.context_types.VISUALIZATION_RESULTS,
                success_criteria="Multi-faceted visualization of operation results with analysis integration",
                inputs=[
                    {registry.context_types.OPERATION_RESULTS: "epu_gap_sweep_results"},          # Operation data
                    {registry.context_types.ANALYSIS_RESULTS: "epu_gap_min_max_analysis"},        # Pre-operation analysis
                    {registry.context_types.ANALYSIS_RESULTS: "sweep_statistical_analysis"},     # Post-operation analysis
                    {registry.context_types.ARCHIVER_DATA: "baseline_beam_size_data"}            # Baseline comparison data
                ]
            ),
            scenario_description="Complex visualization combining operation results, multiple analysis results, and baseline data",
            notes=f"Output stored under {registry.context_types.VISUALIZATION_RESULTS} context type. Demonstrates comprehensive visualization requiring operation results, multiple analysis contexts, and historical baseline data for complete characterization plots."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "data_visualization" steps:**
                - User requests plots, charts, graphs, or visual displays of data
                - User wants to "see", "show", "plot", "visualize", or "display" data
                - After data analysis when results need visual presentation
                - After machine operations when scan/optimization results need plotting
                - User requests dashboards, status displays, or comprehensive visualizations
                - User asks for publication-quality or professional plots

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "beam_current_plots", "statistical_dashboard")
                - inputs: List of input dictionaries from available context data:
                [
                  {{"{registry.context_types.ARCHIVER_DATA}": "historical_data_context_key"}},
                  {{"{registry.context_types.ANALYSIS_RESULTS}": "analysis_results_context_key"}},
                  {{"{registry.context_types.OPERATION_RESULTS}": "operation_results_context_key"}}
                ]
                **Include ALL data sources needed for comprehensive visualization!**

                **Input Requirements by Visualization Type:**
                - Simple Plots: Single data source (historical OR analysis results)
                - Comparative Plots: Multiple data sources for before/after or correlation plots
                - Comprehensive Dashboards: Multiple data types (historical + analysis + current status)
                - Operation Visualization: Operation results + analysis results + baseline data for complete characterization

                **Output: {registry.context_types.VISUALIZATION_RESULTS}**
                - Contains: Plot files, metadata, and descriptions
                - Available to downstream steps via context system

                **Dependencies and sequencing:**
                - Works with any visualizable data in context (flexible requirements)
                - Often used after data retrieval ({registry.capability_names.GET_ARCHIVER_DATA}, {registry.capability_names.PV_VALUE_RETRIEVAL}), analysis ({registry.capability_names.DATA_ANALYSIS}), or operation steps ({registry.capability_names.MACHINE_OPERATIONS})
                - Can combine multiple data sources when available
                - Produces plot files and metadata for reference or further use
                """),
            examples=[time_series_plot_example, analysis_visualization_example, scan_results_example, comprehensive_dashboard_example, complex_operation_visualization_example],
            priority=40
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for data visualization capability."""
        return TaskClassifierGuide(
            instructions="Determine if the user query requires creating plots, charts, graphs, or visual displays of accelerator data.",
            examples=[
                ClassifierExample(
                    query="What tools do you have available?", 
                    result=False, 
                    reason="This is a question about AI capabilities, not a request for data visualization."
                ),
                ClassifierExample(
                    query="Show me a plot of the beam current", 
                    result=True, 
                    reason="This explicitly requests a plot/visualization."
                ),
                ClassifierExample(
                    query="Analyze the beam lifetime data from yesterday", 
                    result=False, 
                    reason="This is primarily a data analysis request, not visualization."
                ),
                ClassifierExample(
                    query="Create a graph showing the ID gap vs photon flux", 
                    result=True, 
                    reason="This explicitly requests creating a graph/visualization."
                ),
                ClassifierExample(
                    query="Visualize the correlation between vacuum pressure and beam loss", 
                    result=True, 
                    reason="This explicitly requests data visualization."
                ),
                ClassifierExample(
                    query="Set the ID gap to 25mm", 
                    result=False, 
                    reason="This is a machine control request, not visualization."
                ),
                ClassifierExample(
                    query="Display the current machine status", 
                    result=True, 
                    reason="This requests a visual display of status information."
                ),
                ClassifierExample(
                    query="I want to see the trends in the power supply data", 
                    result=True, 
                    reason="This requests visual representation (seeing trends) of data."
                ),
                ClassifierExample(
                    query="Plot the optimization results from the scan", 
                    result=True, 
                    reason="This explicitly requests plotting optimization results."
                ),
                ClassifierExample(
                    query="Create a dashboard showing beam lifetime and related parameters", 
                    result=True, 
                    reason="This requests creating a visual dashboard."
                ),
                ClassifierExample(
                    query="Show me the distribution of BPM readings", 
                    result=True, 
                    reason="This requests showing (visualizing) data distribution."
                ),
                ClassifierExample(
                    query="Get the archiver data for beam current", 
                    result=False, 
                    reason="This is a data retrieval request, not visualization."
                )
            ],
            actions_if_true=ClassifierActions()
        )