"""
Machine Operations Capability

This capability handles comprehensive machine control and experimental procedures
covering simple parameter control, coordinated sequences, experimental sweeps,
and optimization loops. It integrates control and measurement operations for
efficient accelerator operations and characterization studies.
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
import numpy as np
import textwrap
import json
from pydantic import BaseModel, Field

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
    PythonExecutionSuccess,
    CodeRuntimeError,
    PythonServiceResult
)
from framework.models import get_chat_completion
from framework.approval.approval_system import (
    get_approval_resume_data,
    clear_approval_state,
    handle_service_with_interrupts
)
from configs.config import get_model_config, get_full_configuration
from configs.streaming import get_streamer
from applications.als_assistant.context_classes import OperationResultsContext
from framework.context.context_manager import ContextManager
from framework.approval import create_approval_type

# Third-party imports
from langgraph.types import Command

from configs.logger import get_logger
logger = get_logger("als_assistant", "machine_operations")


registry = get_registry()


# === Capability-Specific Error Classes ===

class MachineOperationsError(Exception):
    """Base class for all machine operations capability errors."""
    pass

class PromptGenerationError(MachineOperationsError):
    """Raised when prompt generation fails."""
    pass

class OperationParameterError(MachineOperationsError):
    """Raised when operation parameters are invalid or missing."""
    pass

class ExecutorCommunicationError(MachineOperationsError):
    """Raised when communication with Python Executor fails."""
    pass

class SafetyValidationError(MachineOperationsError):
    """Raised when safety validation checks fail."""
    pass

class ResultProcessingError(MachineOperationsError):
    """Raised when processing executor results fails."""
    pass

# === Simple Operation Plan ===

class SimpleOperationPlan(BaseModel):
    """Simple operation plan without complex phases - just the essentials."""
    steps_needed: List[str] = Field(description="Simple list of the actual steps needed to complete the operation (e.g., ['Set PV to target value', 'Read back to verify'])")
    inputs_required: List[str] = Field(description="List of context data access patterns needed (e.g., ['context.PV_ADDRESSES.setpoint_pvs.pvs', 'context.PV_ADDRESSES.readback_pvs.pvs'])")
    data_to_save: List[str] = Field(description="List of what data should be saved in results (e.g., ['final_setpoint_value', 'final_readback_value', 'success_status'])")
    operation_type: str = Field(description="Simple description of what this operation does (e.g., 'Parameter Setting', 'Parameter Scan', 'Simple Measurement')")

# === Code Examples for Different Operation Types ===

def _get_operation_examples(task_objective: str) -> str:
    """Get relevant code examples based on keywords in the task objective."""
    
    task_lower = task_objective.lower()
    examples = []
    
    # Parameter scan/sweep examples
    if any(keyword in task_lower for keyword in ['scan', 'sweep', 'vary', 'range']):
        examples.append("""
# Example: Parameter Scan
scan_values = np.linspace(start_value, end_value, num_points)
results = []
for device in devices:
    for value in scan_values:
        # Set parameter
        epics.caput(setpoint_pv, value)
        time.sleep(settle_time)  # Allow settling
        
        # Read measurements
        measurement = epics.caget(measurement_pv)
        readback = epics.caget(readback_pv)
        results.append({'device': device, 'setpoint': value, 'measurement': measurement, 'readback': readback})
""")
    
    # Simple parameter setting examples
    if any(keyword in task_lower for keyword in ['set', 'adjust', 'change', 'control']):
        examples.append("""
# Example: Simple Parameter Setting (keep it minimal!)
# Set parameter value
epics.caput(setpoint_pv, target_value)
time.sleep(settle_time)

# Verify setting
readback_value = epics.caget(readback_pv)  
success = abs(readback_value - target_value) < tolerance

# That's it - don't add more complexity unless requested
""")
    
    # Optimization examples
    if any(keyword in task_lower for keyword in ['optimize', 'maximize', 'minimize', 'find optimal']):
        examples.append("""
# Example: Simple Optimization
from scipy.optimize import minimize_scalar

def objective_function(parameter_value):
    epics.caput(setpoint_pv, parameter_value)
    time.sleep(settle_time)
    return -epics.caget(measurement_pv)  # Negative for maximization

result = minimize_scalar(objective_function, bounds=(min_val, max_val), method='bounded')
optimal_value = result.x
""")
    
    # Coordinated control examples  
    if any(keyword in task_lower for keyword in ['coordinated', 'synchronized', 'simultaneous', 'multiple']):
        examples.append("""
# Example: Coordinated Control
setpoint_pvs = [pv1, pv2, pv3]
target_values = [val1, val2, val3]

# Set all parameters simultaneously
for pv, value in zip(setpoint_pvs, target_values):
    epics.caput(pv, value, wait=False)  # Non-blocking

# Wait for all to settle
time.sleep(settle_time)

# Verify all settings
readbacks = [epics.caget(f"{pv}_RBV") for pv in setpoint_pvs]
""")
    
    if not examples:
        # Default minimal example
        examples.append("""
# Example: Basic Operation
# Use context data: context.CONTEXT_TYPE.context_key.attribute
# Set parameters: epics.caput(pv_name, value)  
# Read measurements: epics.caget(pv_name)
# Keep it simple - only do what's explicitly requested
""")
    
    return "\n".join(examples)

async def create_operation_plan(current_step: Dict[str, Any], task_objective: str, state: AgentState) -> SimpleOperationPlan:
    """Use a LLM to create a simple operation plan from the high level task_objective."""
    
    # Use state utility function for execution context information
    execution_steps = get_execution_steps_summary(state)
    
    # Get context description for available data
    context_manager = ContextManager(state)
    context_description = context_manager.get_context_access_description(current_step.get('inputs', []))
    
    # Get relevant code examples
    code_examples = _get_operation_examples(task_objective)
    
    system_prompt = textwrap.dedent(f"""
        You are an expert in machine operations for the Advanced Light Source (ALS) accelerator facility.
        You are planning a simple operation to accomplish: "{task_objective}"
        
        AVAILABLE CONTEXT DATA:
        {context_description}
        
        **YOUR TASK: Create a simple plan with just the basics:**
        1. **steps_needed**: What are the actual steps needed? Keep it simple and direct.
        2. **inputs_required**: What context data access patterns are needed? Use only what's available.
        3. **data_to_save**: What should the results contain? Only the essential outputs.
        4. **operation_type**: Simple one-phrase description of what this does.
        
        **CRITICAL RULES:**
        - **THINK SIMPLE**: Most requests need only 2-4 basic steps
        - **USE REAL DATA**: Only specify context access patterns that exist in the available data above
        - **ESSENTIAL OUTPUTS**: Only save data that's actually needed or requested
        - **NO OVER-PLANNING**: Don't add infrastructure, error handling, or complexity unless explicitly requested
        
        **EXAMPLE FOR "Set ID gap to 25mm":**
        - steps_needed: ["Set ID gap PV to 25mm", "Read back gap value to verify"]
        - inputs_required: ["context.PV_ADDRESSES.id_gap_setpoint_pvs.pvs", "context.PV_ADDRESSES.id_gap_readback_pvs.pvs"]
        - data_to_save: ["target_value", "final_readback", "success"]
        - operation_type: "Parameter Setting"
        
        **EXAMPLE FOR "Scan corrector from 95 to 105 amps":**
        - steps_needed: ["Create scan values from 95 to 105", "Loop: set corrector, wait, measure BPM", "Collect all measurements"]
        - inputs_required: ["context.PV_ADDRESSES.corrector_setpoint_pvs.pvs", "context.PV_ADDRESSES.bpm_measurement_pvs.pvs"]
        - data_to_save: ["scan_values", "measurements", "summary"]
        - operation_type: "Parameter Scan"
        
        **KEEP IT SIMPLE. Don't overthink it. Most operations are simpler than they seem.**
        
        RELEVANT CODE PATTERNS:
        {code_examples}
        """)

    logging.debug(f"\n\nSystem prompt for operation plan: {system_prompt}\n\n")
       
    try:
        # Use unified model configuration
        machine_operations_config = get_model_config("als_assistant", "machine_operations")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=machine_operations_config,
            message=f"{system_prompt}\n\nCreate a simple operation plan based on the given context.",
            output_model=SimpleOperationPlan,
        )
        
        if isinstance(response_data, SimpleOperationPlan):
            return response_data
        else:
            raise PromptGenerationError(f"Expected SimpleOperationPlan, got {type(response_data)}")
        
    except Exception as e:
        raise PromptGenerationError(f"Failed to generate operation plan: {e}")

def _format_operation_plan(operation_plan: SimpleOperationPlan) -> str:
    """Format the simple operation plan for the prompt"""
    plan_text = f"Operation Type: {operation_plan.operation_type}\n\n"
    
    plan_text += "Steps Needed:\n"
    for i, step in enumerate(operation_plan.steps_needed, 1):
        plan_text += f"  {i}. {step}\n"
    
    plan_text += "\nInputs Required:\n"
    for input_pattern in operation_plan.inputs_required:
        plan_text += f"  - {input_pattern}\n"
    
    plan_text += "\nData to Save:\n"
    for data_item in operation_plan.data_to_save:
        plan_text += f"  - {data_item}\n"
    
    return plan_text

# === Results Dictionary ===

class OperationResultsDictionary(BaseModel):
    """Dictionary of results for the machine operations."""
    results: Dict[str, Any] = Field(description="Nested dictionary structure template with placeholder values indicating expected data types for operation results")

async def create_operation_results_dictionary(operation_plan: SimpleOperationPlan) -> Dict[str, Any]:
    """Use a LLM to create a results dictionary structure template from the simple operation plan."""
    
    plan_text = _format_operation_plan(operation_plan)
  
    system_prompt = textwrap.dedent(f"""
        You are an expert in machine operations for the Advanced Light Source (ALS) accelerator facility.
        You are given a simple operation plan and you need to create a results dictionary STRUCTURE TEMPLATE.
        
        This is NOT actual results data, but a template showing what the output structure should look like.
        Use placeholder values that clearly indicate the expected data types and content.
        
        **CRITICAL**: Keep the structure MINIMAL and FOCUSED - only include the data items listed in "Data to Save".
        Do NOT add extensive metadata, summaries, or auxiliary information unless specifically listed.
        
        **SIMPLE STRUCTURES ONLY**: Create a flat dictionary structure. Avoid complex nesting unless truly necessary.
        
        Use these placeholder patterns:
        - "<bool>" for success/failure flags
        - "<string>" for operation descriptions  
        - "<list>" for lists of actions or measurements
        - "<float>" for numerical measurements
        
        **Base your structure ONLY on the "Data to Save" list from the operation plan.**
        
        Example for "Data to Save: ['target_value', 'final_readback', 'success']":
        results = {{
            "target_value": "<float>",
            "final_readback": "<float>",
            "success": "<bool>"
        }}
        
        **Keep it simple. Only include what's listed in "Data to Save". No extra complexity.**
        
        Simple operation plan:
        {plan_text}
        """)
    logging.debug(f"\n\nSystem prompt for operation results dictionary: {system_prompt}\n\n")
   
    try:
        machine_operations_config = get_model_config("als_assistant", "machine_operations")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=machine_operations_config,
            message=f"{system_prompt}\n\nCreate the results dictionary structure template based on the operation plan.",
            output_model=OperationResultsDictionary,
        )
        
        if isinstance(response_data, OperationResultsDictionary):
            return response_data.results
        else:
            raise PromptGenerationError(f"Expected OperationResultsDictionary, got {type(response_data)}")
        
    except Exception as e:
        raise PromptGenerationError(f"Failed to generate operation results dictionary: {e}")

def _get_machine_operations_system_prompts(operation_plan: SimpleOperationPlan, expected_results: Dict[str, Any], task_objective: str, context_description: str) -> List[str]:
    """Prepare minimalistic capability-specific system prompts for the Python Executor"""
    prompts = []
    
    # Add code examples and anti-hallucination guidelines
    code_examples = _get_operation_examples(task_objective) 
    prompts.append(textwrap.dedent(f"""     

        **MANDATORY REQUIREMENTS:**
        - NEVER make up PV names - only use PVs from the specified context access patterns
        - NEVER simulate/fake measurements - use real EPICS calls with the specified PV names
        - NEVER create dummy loops or artificial data generation
        
        **KEEP CODE MINIMAL:**
        - Only implement what the user explicitly requested - nothing more
        - Don't add extra features, logging, or complexity
        - Use simple, direct approaches - avoid nested loops unless truly necessary
        - Focus on the core operation, not elaborate infrastructure
        - **PREFER DIRECT SOLUTIONS**: Use the most straightforward approach that solves the problem
        - **AVOID OVER-ENGINEERING**: Don't add error handling, retries, or elaborate validation unless explicitly requested
        - **ONE SIMPLE TASK**: If the request is simple, the code should be simple too
        
        **RELEVANT CODE PATTERNS:**
        {code_examples}
        
        **STRICT RULE: Only access context data using the patterns specified in your operation plan above.**
        **If a required access pattern is not in your plan, raise an error rather than guessing.**
        
        **ANTI-PATTERN WARNING: Don't write elaborate wrapper functions, extensive try-catch blocks, 
        progress tracking, detailed logging, or complex data structures unless explicitly requested.**
        """))
  
    # Pass simple operation plan
    prompts.append(textwrap.dedent(f"""
        **SIMPLE OPERATION PLAN:**
        {_format_operation_plan(operation_plan)}
        """))
        
    # Create output format based on expected results structure
    results_structure = json.dumps(expected_results, indent=2)
    prompts.append(textwrap.dedent(f"""
        **REQUIRED OUTPUT FORMAT:**
        Your code must create a results dictionary matching this exact structure template:
        
        {results_structure}
        
        IMPORTANT: 
        - Replace all placeholder values (like "<bool>", "<string>", "<list>") with actual computed values
        - The dictionary keys and nested structure must match exactly
        - Store the final results in a variable called 'results'
        - Downstream tasks depend on this specific structure for accessing your operation results
        """))
    
    # Add detailed context description (using the same temp_context approach)
    prompts.append(textwrap.dedent(f"""
        **AVAILABLE CONTEXT DATA:**
        {context_description}
        """))

    return prompts

# --- Capability Definition ---

def _validate_context_data(state: AgentState, step: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and extract required context data for machine operations.
    
    Args:
        state: Current agent state
        step: Current execution step with input requirements
        
    Returns:
        Dict of extracted contexts as specified in step inputs
        
    Raises:
        MachineOperationsError: If required contexts cannot be extracted or step has no inputs
    """
    
    # Require explicit context specifications from orchestrator
    if not step.get('inputs'):
        raise MachineOperationsError(
            "Machine operations require explicit context inputs from the orchestrator. "
            "Step must specify which contexts to operate on (e.g., PV_ADDRESSES, MACHINE_CONFIG)."
        )
    
    try:
        context_manager = ContextManager(state)
        contexts = context_manager.extract_from_step(step, state)
        if not contexts:
            raise MachineOperationsError("No contexts could be extracted from specified step inputs.")
        return contexts
    except ValueError as e:
        raise MachineOperationsError(f"Failed to extract required contexts: {str(e)}")


def _create_operation_context(service_result: PythonServiceResult) -> OperationResultsContext:
    """
    Create OperationResultsContext from structured service result.
    
    No validation needed - service guarantees structure and raises exceptions on failure.
    Still performs operation-specific logic for result extraction.
    
    Args:
        service_result: Structured result from Python executor service
        
    Returns:
        OperationResultsContext: Ready-to-store context object
        
    Raises:
        RuntimeError: If operation results are empty (operation-specific requirement)
    """
    # Service guarantees execution_result is valid
    execution_result = service_result.execution_result
    operation_results = execution_result.results
    expected_results = getattr(execution_result, 'expected_results', {})
    
    # Operation-specific validation: require non-empty results
    if not operation_results:
        raise RuntimeError(
            "Python executor returned no results. This indicates the generated Python code "
            "did not create a 'results' variable or the variable was not structured correctly."
        )
    
    # Create operation context with results in the standardized container
    return OperationResultsContext(
        results=operation_results,  # Pass all results in the standardized results field
        expected_schema=expected_results
    )



@capability_node
class MachineOperationsCapability(BaseCapability):
    """Machine operations capability for accelerator control, experimental procedures, and optimization."""
    
    name = "machine_operations"
    description = "Comprehensive machine operations capability for accelerator control, experimental procedures, and optimization"
    provides = ["OPERATION_RESULTS"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute machine operations by preparing prompts for the Python Executor."""
                
        # Define streaming helper here for step awareness
        streamer = get_streamer("als_assistant", "machine_operations", state)
        streamer.status("Preparing machine operations...")
        
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
                "thread_id": f"machine_operations_{step.get('context_key', 'default')}",
                "checkpoint_ns": "python_executor"
            }
        }
        
        # =====================================================================
        # PHASE 1: CHECK FOR APPROVED CODE EXECUTION
        # =====================================================================
        
        # Check if this is a resume from approval using centralized function
        has_approval_resume, approved_payload = get_approval_resume_data(state, create_approval_type("machine_operations"))
        
        if has_approval_resume:
            if approved_payload:
                logger.success("Using approved code execution from previous approval")
                
                streamer.status("Executing approved code...")
                
                # Resume execution with approval response
                resume_response = {"approved": True}
                resume_response.update(approved_payload)
            else:
                # Explicitly rejected
                logger.info("Machine operations was rejected by user")
                resume_response = {"approved": False}
            
            # Resume the service with Command pattern
            service_result = await python_service.ainvoke(
                Command(resume=resume_response),
                config=service_config
            )
            
            logger.success("✅ Machine operations completed successfully after approval")
            
            # Both approval and normal paths converge to single processing below
            approval_cleanup = clear_approval_state()
        else:
            # =====================================================================  
            # PHASE 2: NORMAL MACHINE OPERATIONS FLOW
            # =====================================================================
            
            # 1. Validate and extract context data
            extracted_contexts = _validate_context_data(state, step)
        
            # 2. Generate detailed plan and expected results structure using LLMs
            streamer.status("Generating operation plan...")
            
            operation_plan = await create_operation_plan(
                current_step=step, 
                task_objective=step.get('task_objective', 'Execute machine operations'),
                state=state,
            )
            logger.info(f"Generated simple plan '{operation_plan.operation_type}' with {len(operation_plan.steps_needed)} steps: {operation_plan.steps_needed}")
            
            streamer.status("Creating results structure template...")
            
            expected_results = await create_operation_results_dictionary(operation_plan)
            logger.info(f"Generated expected results structure with keys: {list(expected_results.keys()) if expected_results else 'None'}")
            
            # 3. Get context description for available data
            context_manager = ContextManager(state)
            context_description = context_manager.get_context_access_description(step.get('inputs', []))

            # 4. Create adaptive prompts with detailed plan and expected results
            prompts = _get_machine_operations_system_prompts(operation_plan, expected_results, step.get('task_objective', 'Execute machine operations'), context_description)
            
            # 5. Create type-safe execution request (matching framework Python capability pattern)
            user_query = state.get("input_output", {}).get("user_query", "")
            task_objective = step.get("task_objective", "Execute machine operations")
            python_config = get_model_config("framework", "python_code_generator")
            
            # Get raw context data
            capability_contexts = state.get('capability_context_data', {})
            
            execution_request = PythonExecutionRequest(
                user_query=user_query,
                task_objective=task_objective,
                capability_prompts=prompts,
                expected_results=expected_results,
                execution_folder_name="machine_operations",
                capability_context_data=capability_contexts,
                config=kwargs.get("config", {}),
                retries=python_config.get("retries", 3)
            )
            
            streamer.status("Generating python code for machine operations...")
            
            logger.info("Calling Python Agent for machine operations")
            await asyncio.sleep(0.01)  # Give event loop time to process observer message
            
            # Use centralized service interrupt handler
            service_result = await handle_service_with_interrupts(
                service=python_service,
                request=execution_request,
                config=service_config,
                logger=logger,
                capability_name="MachineOperations"
            )
            
            logger.success("Machine operations completed successfully")
            
            # Normal flow doesn't need approval cleanup
            approval_cleanup = None
        
        # ====================================================================
        # CONVERGENCE POINT: Both approval and normal paths meet here
        # ====================================================================
        
        # Process results - single path for both approval and normal execution
        streamer.status("Processing operation results...")
        
        # Create context using private helper function (handles all complexity)
        operation_context = _create_operation_context(service_result)
        
        # Store context using StateManager
        step = StateManager.get_current_step(state)
        context_updates = StateManager.store_context(
            state, 
            registry.context_types.OPERATION_RESULTS, 
            step.get("context_key"), 
            operation_context
        )
        
        # Register generated figures in centralized UI registry
        figure_updates = {}
        if hasattr(service_result, 'execution_result') and service_result.execution_result.figure_paths:
            # Register figures using StateManager with proper accumulation
            accumulating_figures = None  # Start with None for first registration
            
            for figure_path in service_result.execution_result.figure_paths:
                figure_update = StateManager.register_figure(
                    state,
                    capability="machine_operations",
                    figure_path=str(figure_path),
                    display_name="Machine Operations Plot",
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
                capability="machine_operations",
                notebook_path=str(service_result.execution_result.notebook_path),
                notebook_link=service_result.execution_result.notebook_link,
                display_name="Machine Operations Notebook",
                metadata={
                    "execution_folder": service_result.execution_result.folder_path,
                    "execution_time": service_result.execution_result.execution_time,
                    "context_key": step.get("context_key"),
                }
            )
        
        streamer.status("Machine operations completed successfully")
        
        logger.info(f"Stored OperationResultsContext to context under {registry.context_types.OPERATION_RESULTS}.{step.get('context_key')}")
        
        # Return results with conditional approval cleanup, figure updates, and notebook updates
        if approval_cleanup:
            return {**context_updates, **approval_cleanup, **figure_updates, **notebook_updates}
        else:
            return {**context_updates, **figure_updates, **notebook_updates}
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Machine operations error classification."""
        
        if isinstance(exc, OperationParameterError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,  # Need different parameters or user clarification
                user_message=f"Operation parameter validation failed: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, SafetyValidationError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,  # Safety issues require immediate attention
                user_message=f"Safety validation failed: {str(exc)}",
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
        elif isinstance(exc, MachineOperationsError):
            # Generic machine operations error
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Machine operations error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        else:
            # Unknown errors should be classified as RETRIABLE by default
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Unexpected machine operations error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """
        Create prompt snippet that teaches the orchestrator when and how to use this capability.
        """
        # Define structured examples
        simple_control_example = OrchestratorExample(
            step=PlannedStep(
                context_key="id_gap_control_results",
                capability="machine_operations",
                task_objective="Set insertion device gap to 25mm with safety verification",
                expected_output=registry.context_types.OPERATION_RESULTS,
                success_criteria="Parameter set successfully with verification",
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "id_gap_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "id_gap_readback_pv_addresses"}
                ]
            ),
            scenario_description="Simple parameter setting with verification",
            notes=f"Output stored under {registry.context_types.OPERATION_RESULTS} context type. Direct control of single parameters like ID gaps, magnet currents, etc."
        )
        
        experimental_sweep_example = OrchestratorExample(
            step=PlannedStep(
                context_key="cm_vs_BPM_reading_sweep_results",
                capability="machine_operations",
                task_objective="Scan corrector magnet strength from 95 to 105 amps while measuring BPM response",
                expected_output=registry.context_types.OPERATION_RESULTS,
                success_criteria="Sweep completed with synchronized measurements",
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "cm_setpoint_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "cm_readback_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "BPM_reading_pv_addresses"}
                ]
            ),
            scenario_description="Parameter scans with synchronized measurement",
            notes=f"Output stored under {registry.context_types.OPERATION_RESULTS} context type. Used for machine characterization, optimization studies, and beam physics experiments."
        )
        
        optimization_example = OrchestratorExample(
            step=PlannedStep(
                context_key="lifetime_optimization_results",
                capability="machine_operations",
                task_objective="Optimize sextupole magnet settings to maximize beam lifetime above 10 hours",
                expected_output=registry.context_types.OPERATION_RESULTS,
                success_criteria="Optimal settings found and applied",
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "lifetime_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "sextupole_setpoint_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "sextupole_readback_pv_addresses"}
                ]
            ),
            scenario_description="Iterative optimization to find optimal machine settings",
            notes=f"Output stored under {registry.context_types.OPERATION_RESULTS} context type. Automated optimization loops for beam lifetime, flux, stability, etc."
        )
        
        coordinated_procedure_example = OrchestratorExample(
            step=PlannedStep(
                context_key="ramping_procedure_results",
                capability="machine_operations",
                task_objective="Execute coordinated quadrupole and sextupole ramping sequence with 30-second intervals",
                expected_output=registry.context_types.OPERATION_RESULTS,
                success_criteria="Coordinated procedure completed safely",
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "quadrupole_setpoint_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "quadrupole_readback_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "sextupole_setpoint_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "sextupole_readback_pv_addresses"}  
                ],
                parameters={
                    "operation_type": "coordinated_procedure",
                    "timeout_settings": {"step_timeout": 30, "total_timeout": 300}
                }
            ),
            scenario_description="Multi-parameter sequences with timing and dependencies",
            notes=f"Output stored under {registry.context_types.OPERATION_RESULTS} context type. Complex procedures requiring coordination between multiple systems."
        )

        
        multi_system_characterization_example = OrchestratorExample(
            step=PlannedStep(
                context_key="insertion_device_characterization_results",
                capability="machine_operations",
                task_objective="Characterize all insertion devices by scanning gaps and measuring flux, lifetime, and orbit distortion",
                expected_output=registry.context_types.OPERATION_RESULTS,
                success_criteria="Multi-system characterization completed with comprehensive measurements",
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "id_gap_setpoint_pvs"},
                    {registry.context_types.PV_ADDRESSES: "flux_measurement_pvs"},
                    {registry.context_types.PV_ADDRESSES: "beam_lifetime_measurement_pvs"},
                    {registry.context_types.PV_ADDRESSES: "orbit_measurement_pvs"},
                    {registry.context_types.TIME_RANGE: "characterization_timerange"}
                ]
            ),
            scenario_description="Multi-system characterization requiring many different PV sources and context data",
            notes=f"Output stored under {registry.context_types.OPERATION_RESULTS} context type. Shows orchestrator how to handle operations requiring MANY different context sources - multiple PV types plus other context data."
        )
        
        optimization_with_constraints_example = OrchestratorExample(
            step=PlannedStep(
                context_key="constrained_optimization_results", 
                capability="machine_operations",
                task_objective="Optimize sextupole settings for maximum lifetime while maintaining orbit stability within analyzed bounds",
                expected_output=registry.context_types.OPERATION_RESULTS,
                success_criteria="Optimization completed with constraint satisfaction verified",
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "sextupole_setpoint_pvs"},
                    {registry.context_types.PV_ADDRESSES: "sextupole_readback_pv_addresses"},
                    {registry.context_types.PV_ADDRESSES: "beam_lifetime_measurement_pvs"},
                    {registry.context_types.PV_ADDRESSES: "orbit_measurement_pvs"},
                    {registry.context_types.ANALYSIS_RESULTS: "orbit_stability_analysis"},
                    {registry.context_types.ANALYSIS_RESULTS: "baseline_lifetime_analysis"}
                ]
            ),
            scenario_description="Constrained optimization using multiple measurement systems and analysis-derived constraints",
            notes=f"Output stored under {registry.context_types.OPERATION_RESULTS} context type. Complex optimization requiring multiple PV sources AND multiple analysis results to define objectives and constraints."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "machine_operations" steps:**
                - Simple Control: User requests setting PV values or changing single machine parameters
                - Coordinated Procedures: Multi-parameter sequences, ramping procedures, synchronized changes
                - Experimental Sweeps: Parameter scans while measuring machine response (e.g., "scan ID gap and measure flux")
                - Optimization Loops: Finding optimal settings through iterative control and measurement

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "id_gap_control_results", "optimization_sweep_results")
                - inputs: List of input dictionaries from available context data:
                [
                  {{"{registry.context_types.PV_ADDRESSES}": "control_pvs_context_key"}},
                  {{"{registry.context_types.PV_ADDRESSES}": "measurement_pvs_context_key"}},
                  {{"{registry.context_types.ANALYSIS_RESULTS}": "analysis_context_key"}}
                ]
                
                **CRITICAL: For complex operations, include ALL required context sources!**
                - Control PVs: PV addresses for parameters to be controlled/changed
                - Readback PVs: PV addresses for parameters to be read back after control is applied
                - Measurement PVs: PV addresses for quantities to be measured during operation
                - Analysis Results: Data from previous analysis steps (min/max values, constraints, etc.)
                - Time Ranges: Time specifications for time-dependent operations

                **Input Requirements by Operation Type:**
                - Simple Control: Usually just control PV addresses and readback PV addresses
                - Sweeps/Scans: Control&Readback PVs + Measurement PVs + (optionally) Analysis Results for ranges
                - Optimization: Control PVs + Objective Measurement PVs + (optionally) Constraint Analysis
                - Complex Procedures: Multiple PV sources + Analysis Results + Other context as needed

                **Output: {registry.context_types.OPERATION_RESULTS}**
                - Contains: Operation results, control actions, measurements, final state
                - Available to downstream steps via context system

                **Core Operation Types:**
                - Simple Control: Direct parameter setting with verification
                - Coordinated Procedures: Multi-step sequences with timing and dependencies
                - Experimental Sweeps: Scan parameters while measuring response variables
                - Optimization Loops: Iterative procedures to find optimal machine settings

                **Dependencies and sequencing:**
                - Optional: {registry.context_types.PV_ADDRESSES} data for specific PV operations
                - Can work independently or after PV address lookup steps
                - Integrates control and measurement - produces comprehensive results
                - Can discover additional PVs during complex procedures
                """),
            examples=[
                simple_control_example, 
                experimental_sweep_example, 
                optimization_example, 
                coordinated_procedure_example,
                multi_system_characterization_example, 
                optimization_with_constraints_example
            ],
            priority=20
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for machine operations capability."""
        return TaskClassifierGuide(
            instructions="Determine if the user query requires any form of machine control, experimental procedure, or optimization in the accelerator control system.",
            examples=[
            # ---------- POSITIVE EXAMPLES ----------
            #
            ClassifierExample(
                query="Set the ID gap to 25mm", 
                result=True, 
                reason="Simple control operation - setting a single parameter."
            ),
            ClassifierExample(
                query="Scan the ID gap from 10 to 30mm and measure the photon flux", 
                result=True, 
                reason="Experimental sweep - scanning parameter while measuring response."
            ),
            ClassifierExample(
                query="Optimize the beam lifetime by adjusting the RF parameters", 
                result=True, 
                reason="Optimization loop - iterative control to find optimal settings."
            ),
            ClassifierExample(
                query="Scan the quadrupole current from 95 to 105 amps", 
                result=True, 
                reason="Experimental sweep - parameter scan operation."
            ),
            ClassifierExample(
                query="Ramp up the sextupole current slowly while monitoring beam losses", 
                result=True, 
                reason="Coordinated procedure - controlled ramping with integrated monitoring."
            ),
            ClassifierExample(
                query="Find the optimal gap for maximum flux at 8 keV", 
                result=True, 
                reason="Optimization loop - finding optimal parameter settings."
            ),
            ClassifierExample(
                query="Adjust three quadrupole magnets simultaneously", 
                result=True, 
                reason="Coordinated procedure - multi-parameter synchronized control."
            ),
            ClassifierExample(
                query="Characterize the nonlinear dynamics by varying chromaticity", 
                result=True, 
                reason="Experimental sweep - machine characterization study."
            ),
            ClassifierExample(
                query="Study the beam-beam effects versus bunch current", 
                result=True, 
                reason="Experimental sweep - systematic study requiring parameter variation."
            ),
            ClassifierExample(
                query="Increase the sextupole strength by 2%", 
                result=True, 
                reason="Simple control - direct parameter modification."
            ),      
            # ---------- NEGATIVE EXAMPLES ----------
            #
            ClassifierExample(
                query="What tools do you have available?", 
                result=False, 
                reason="This is a question about AI capabilities, not a request for machine operations."
            ),
            ClassifierExample(
                query="Show me the current beam lifetime", 
                result=False, 
                reason="This is requesting data display only, not machine operations."
            ),
            ClassifierExample(
                query="Plot the BPM readings over the last hour", 
                result=False, 
                reason="This is historical data visualization, not machine operations."
            ),
            ClassifierExample(
                query="Get the minimum and maximum value of all power supply values in the last 2 days.",
                result=False,
                reason="This is a historical data analysis request, not a machine operations request."
            ),
            ClassifierExample(
                query="Explain how insertion device gap affects photon flux",
                result=False,
                reason="This is an educational/explanatory request, not a request to control or operate the machine."
            ),
            ClassifierExample(
                query="Show me the current status of all beamlines",
                result=False,
                reason="This is a status display request for monitoring purposes, not machine operations."
            ),
            ClassifierExample(
                query="What caused the beam dump yesterday at 2pm?",
                result=False,
                reason="This is a historical analysis question about past events, not a request for machine control."
            )
            ],
            actions_if_true=ClassifierActions()
        )