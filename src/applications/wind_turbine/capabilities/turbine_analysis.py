"""
Turbine Analysis Capability

This capability performs performance analysis and baseline calculations using Python execution.
Simplified for educational purposes - demonstrates basic statistical analysis of wind turbine data.
"""

import asyncio
import json
import logging
import textwrap
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, Field
from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.examples import OrchestratorGuide, OrchestratorExample, ClassifierActions, ClassifierExample, TaskClassifierGuide
from framework.base.planning import PlannedStep
from framework.state import AgentState, StateManager
from framework.registry import get_registry
from framework.context.context_manager import ContextManager
from applications.wind_turbine.context_classes import AnalysisResultsContext, TurbineDataContext, WeatherDataContext, TurbineKnowledgeContext
from framework.services.python_executor.models import PythonExecutionRequest
from framework.services.python_executor import PythonServiceResult
from framework.approval import (
    create_approval_type,
    get_approval_resume_data,
    clear_approval_state,
    handle_service_with_interrupts
)
from configs.streaming import get_streamer
from configs.unified_config import get_full_configuration, get_model_config
from langgraph.types import Command
from configs.logger import get_logger
from framework.models import get_chat_completion

logger = get_logger("wind_turbine", "turbine_analysis")


registry = get_registry()

# === Analysis Errors ===
class AnalysisError(Exception):
    """Base class for analysis related errors."""
    pass

class DataValidationError(AnalysisError):
    """Raised when input data validation fails."""
    pass

class ExecutorCommunicationError(AnalysisError):
    """Raised when communication with Python Executor fails."""
    pass

class ResultProcessingError(AnalysisError):
    """Raised when processing executor results fails."""
    pass

# === Analysis Plan Models ===

class AnalysisPhase(BaseModel):
    """Individual phase in the analysis plan with detailed subtasks."""
    phase: str = Field(description="Name of the major analytical phase (e.g., 'Data Correlation', 'Efficiency Calculation')")
    subtasks: List[str] = Field(description="List of specific computational/analytical tasks within this phase")
    output_state: str = Field(description="What this phase accomplishes or produces as input for subsequent phases")

class AnalysisPlan(BaseModel):
    """Wrapper for a list of analysis phases."""
    phases: List[AnalysisPhase] = Field(description="List of analysis phases for the turbine performance analysis plan")

class ResultsDictionary(BaseModel):
    """Dictionary structure template for turbine analysis results."""
    results: Dict[str, Any] = Field(description="Nested dictionary structure template with placeholder values indicating expected data types for turbine analysis results")

async def create_turbine_analysis_plan(current_step: Dict[str, Any], task_objective: str, state: AgentState) -> List[AnalysisPhase]:
    """Use LLM to create a hierarchical analysis plan for turbine performance analysis."""
    
    # Build input context information
    input_info = []
    if current_step.get('inputs'):
        for input_dict in current_step['inputs']:
            for input_type, context_key in input_dict.items():
                input_info.append(f"- {input_type} data will be available from context key '{context_key}'")
    
    input_context = "\n".join(input_info) if input_info else "No specific input context defined."
    
    system_prompt = textwrap.dedent(f"""
        You are an expert in wind turbine performance analysis and wind energy engineering.
        You are given a specific turbine analysis task that requires calculating efficiency metrics
        and comparing performance against industry standards.
        
        CURRENT TASK FOCUS:
        You are planning for: "{task_objective}"
        
        AVAILABLE INPUTS:
        {input_context}
        
        DOMAIN KNOWLEDGE - CRITICAL CONCEPTS:
        - Wind turbine efficiency should be calculated relative to available wind conditions, not just rated capacity
        - True efficiency compares actual performance to what's possible given the wind resource
        - Capacity factor measures total energy production vs maximum theoretical over time
        - Industry benchmarks classify turbines by actual vs expected performance for given conditions
        
        ANALYSIS CONSTRAINTS:
        - Focus ONLY on computational/analytical aspects of turbine performance evaluation
        - Data inputs are already handled by previous steps and will be available
        - Must correlate turbine data with weather data by timestamp
        - Must use knowledge base thresholds for performance classification
        - KEEP IT SIMPLE: Create exactly 3-4 phases maximum to ensure manageable Python code generation
        
        Create a hierarchical analysis plan organized into phases. Each phase should represent 
        a major analytical step with 2-3 focused subtasks (not more).
        
        Structure each phase with:
        - phase: Name of the major analytical phase
        - subtasks: List of 2-3 specific computational tasks within this phase
        - output_state: What this phase accomplishes or produces
        
        REQUIRED PHASES (adapt to the specific task):
        Phase 1: Data Preparation and Correlation
        Phase 2: Performance Metrics Calculation
        Phase 3: Industry Benchmark Comparison
        """)

    try:
        # Use wind turbine application model configuration
        model_config = get_model_config("wind_turbine", "turbine_analysis")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=model_config,
            message=f"{system_prompt}\n\nCreate the hierarchical analysis plan for turbine performance analysis.",
            output_model=AnalysisPlan,
        )
        
        if isinstance(response_data, AnalysisPlan):
            return response_data.phases
        else:
            raise RuntimeError(f"Expected AnalysisPlan, got {type(response_data)}")
        
    except Exception as e:
        logger.error(f"Failed to generate analysis plan: {e}")
        # Fallback to default plan
        return [
            AnalysisPhase(
                phase="Data Preparation and Correlation",
                subtasks=[
                    "Merge turbine power data with weather data by timestamp",
                    "Calculate theoretical power for each wind speed condition"
                ],
                output_state="Correlated turbine and weather dataset with theoretical power calculations"
            ),
            AnalysisPhase(
                phase="Performance Metrics Calculation",
                subtasks=[
                    "Calculate actual vs theoretical efficiency for each turbine",
                    "Compute capacity factors relative to rated capacity"
                ],
                output_state="Efficiency metrics and capacity factors for each turbine"
            ),
            AnalysisPhase(
                phase="Industry Benchmark Comparison",
                subtasks=[
                    "Apply knowledge base thresholds for performance classification",
                    "Rank turbines by performance metrics"
                ],
                output_state="Performance classifications and rankings"
            )
        ]

async def create_turbine_results_dictionary(analysis_plan: List[AnalysisPhase]) -> Dict[str, Any]:
    """Use LLM to create a results dictionary structure template from the analysis plan."""
    
    def _format_analysis_plan(plan: List[AnalysisPhase]) -> str:
        """Format the hierarchical plan for the prompt"""
        plan_text = ""
        for i, phase in enumerate(plan, 1):
            plan_text += f"Phase {i}: {phase.phase}\n"
            if phase.subtasks:
                for subtask in phase.subtasks:
                    plan_text += f"  • {subtask}\n"
            if phase.output_state:
                plan_text += f"  → Output: {phase.output_state}\n"
            plan_text += "\n"
        return plan_text
    
    plan_text = _format_analysis_plan(analysis_plan)
  
    system_prompt = textwrap.dedent(f"""
        You are an expert in wind turbine performance analysis.
        You are given a hierarchical analysis plan and need to create a results dictionary STRUCTURE TEMPLATE.
        
        This is NOT actual results data, but a template showing what the output structure should look like.
        Use placeholder values that clearly indicate the expected data types and content.
        
        CRITICAL CONSTRAINTS:
        - KEEP IT SIMPLE: Create exactly 3-4 top-level keys maximum
        - Avoid deeply nested structures that complicate Python code generation
        - Focus on the essential outputs: turbine metrics, performance analysis, and summary
        
        TURBINE ANALYSIS CONTEXT:
        - Results should include per-turbine metrics (efficiency, capacity factor, performance class)
        - Should provide performance rankings and summary statistics
        - Use turbine IDs like "T-001", "T-002", etc.
        
        Use these placeholder patterns:
        - "<float>" for numerical values (efficiency percentages, capacity factors)
        - "<int>" for integer counts
        - "<string>" for text descriptions (performance classes)
        - "<list>" for lists of turbine IDs
        
        EXAMPLE STRUCTURE (adapt to the analysis plan):
        results = {{
            "turbine_performance": {{
                "<turbine_id>": {{
                    "efficiency_percent": "<float>",
                    "capacity_factor_percent": "<float>",
                    "performance_class": "<string>"
                }}
            }},
            "performance_rankings": ["<turbine_ids_ranked_by_performance>"],
            "performance_summary": {{
                "farm_average_efficiency": "<float>",
                "total_turbines_analyzed": "<int>"
            }}
        }}
        
        Keep the structure FOCUSED on what the analysis plan actually produces.
        Be descriptive with key names so downstream tasks can easily access the right data.
        
        Hierarchical analysis plan:
        {plan_text}
        """)
    
    try:
        model_config = get_model_config("wind_turbine", "turbine_analysis")
        
        response_data = await asyncio.to_thread(
            get_chat_completion,
            model_config=model_config,
            message=f"{system_prompt}\n\nCreate the results dictionary structure template based on the analysis plan.",
            output_model=ResultsDictionary,
        )
        
        if isinstance(response_data, ResultsDictionary):
            return response_data.results
        else:
            raise RuntimeError(f"Expected ResultsDictionary, got {type(response_data)}")
        
    except Exception as e:
        logger.error(f"Failed to generate results dictionary: {e}")
        # Fallback to default structure
        return {
            "turbine_performance": {
                "<turbine_id>": {
                    "efficiency_percent": "<float>",
                    "capacity_factor_percent": "<float>",
                    "performance_class": "<string>"
                }
            },
            "performance_rankings": ["<turbine_ids_ranked_by_performance>"],
            "performance_summary": {
                "farm_average_efficiency": "<float>",
                "total_turbines_analyzed": "<int>"
            }
        }

def _create_structured_analysis_prompts(analysis_plan: List[AnalysisPhase], expected_results: Dict[str, Any], context_description: str) -> List[str]:
    """Create prompts using the analysis plan and results template."""
    prompts = []
    
    # Format analysis plan for prompt
    def _format_plan_for_prompt(plan: List[AnalysisPhase]) -> str:
        plan_text = ""
        for i, phase in enumerate(plan, 1):
            plan_text += f"Phase {i}: {phase.phase}\n"
            for subtask in phase.subtasks:
                plan_text += f"  • {subtask}\n"
            plan_text += f"  → {phase.output_state}\n\n"
        return plan_text
    
    # Execution plan summary (simplified)
    prompts.append(textwrap.dedent(f"""
        **STRUCTURED EXECUTION PLAN:**
        {_format_plan_for_prompt(analysis_plan)}
        
        **KEY REQUIREMENTS:**
        - Merge turbine and weather data by timestamp
        - Calculate efficiency relative to wind conditions (not just rated capacity)
        - Use knowledge base thresholds for performance classification
        """))

    # Required output format (simplified)
    results_structure = json.dumps(expected_results, indent=2)
    prompts.append(textwrap.dedent(f"""
        **REQUIRED OUTPUT:**
        Create a results dictionary matching this structure:
        
        {results_structure}
        
        Replace placeholders with actual computed values. Store in variable 'results'.
        """))
    
    # Available context data (simplified)
    prompts.append(f"**AVAILABLE DATA:** {context_description}")

    return prompts

def _create_simple_turbine_prompt(context_description: str = "") -> str:
    """Create a focused prompt for turbine performance benchmarking analysis.
    
    Args:
        context_description: Optional context access description for available data
    """
    base_prompt = textwrap.dedent("""
        **TURBINE PERFORMANCE BENCHMARKING ANALYSIS:**
        Analyze wind turbine performance against industry standards and identify underperformers.
        
        **DATA AVAILABLE:**
        - Turbine data: turbine_id, timestamp, power_output (MW)
        - Weather data: timestamp, wind_speed (m/s)  
        - Knowledge base: Performance thresholds and industry standards
        
        **CRITICAL UNITS NOTE:**
        - DO NOT convert units - keep everything in MW for calculations
        
        **ANALYSIS OBJECTIVES:**
        1. Calculate efficiency for each turbine against theoretical maximum
        2. Calculate capacity factors and compare to industry benchmarks
        3. Classify turbine performance against industry standards
        4. Rank turbines by overall performance
        
        **ANALYSIS OBJECTIVE:**
        Perform comprehensive wind farm performance benchmarking to identify underperforming turbines.
        Use the extracted industry standards and performance thresholds from the knowledge base to 
        classify performance and rank turbines.
        
        **AVAILABLE DATA:**
        - Historical turbine power output data with timestamps (multiple turbines per timestamp)
        - Weather data (wind speeds) with timestamps (one reading per timestamp)
        - Industry performance benchmarks and thresholds from knowledge base
        
        **DATA RELATIONSHIPS:**
        Turbine and weather data share timestamps but have different structures - weather data
        needs to be joined with turbine data by timestamp to correlate performance with wind conditions.
        
        **EXPECTED INSIGHTS:**
        - Which turbines are excellent performers vs poor performers
        - How each turbine compares to industry standards
        - Performance trends and consistency metrics
        - Turbine performance rankings
        
        **DOMAIN CONTEXT:**
        Wind turbines convert wind energy to electrical power. Performance should be evaluated
        relative to available wind resource (wind speed), not just absolute power output. 
        True efficiency compares actual power generation to what's theoretically possible 
        given the wind conditions.
        
        **CAPACITY FACTOR CALCULATION:**
        Capacity Factor = (Actual Energy Output) / (Maximum Theoretical Output) * 100
        - Use actual power_output values in MW (do NOT convert to kW)
        - Use rated_capacity_mw from knowledge base (already in MW)
        - Typical wind farm capacity factors range from 25-45%
    
        
        **USE KNOWLEDGE BASE THRESHOLDS:**
        Access extracted numerical thresholds from knowledge base to classify performance:
        - Excellent vs good vs poor efficiency ratings
        - Industry benchmark comparisons
        - Performance classification standards
        
        **OUTPUT:** Store results with turbine performance metrics, rankings, and classifications.
        """)
    
    # Add context description if available
    if context_description:
        return f"{base_prompt}\n\n**CONTEXT ACCESS DESCRIPTION:**\n{context_description}"
    
    return base_prompt

def _create_turbine_analysis_context(service_result: PythonServiceResult, expected_schema: Dict[str, Any]) -> AnalysisResultsContext:
    """
    Create AnalysisResultsContext from structured service result.
    
    No validation needed - service guarantees structure and raises exceptions on failure.
    
    Args:
        service_result: Structured result from Python executor service
        expected_schema: The dynamically generated expected results structure
        
    Returns:
        AnalysisResultsContext: Ready-to-store context object
        
    Raises:
        RuntimeError: If analysis results are empty
    """
    # Service guarantees execution_result is valid
    execution_result = service_result.execution_result
    
    if not execution_result or not execution_result.results:
        raise RuntimeError(
            "Python executor returned no results. The generated Python code "
            "did not create a 'results' variable or the variable was empty."
        )
    
    # Create structured context
    return AnalysisResultsContext(
        results=execution_result.results,
        expected_schema=expected_schema
    )

@capability_node
class TurbineAnalysisCapability(BaseCapability):
    """Simplified turbine analysis capability using Python execution."""
    
    name = "turbine_analysis"
    description = "Analyze wind turbine performance against industry benchmarks to identify underperformers and rank performance"
    provides = [registry.context_types.ANALYSIS_RESULTS]
    requires = [registry.context_types.TURBINE_DATA, registry.context_types.WEATHER_DATA, registry.context_types.TURBINE_KNOWLEDGE]
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute turbine analysis using Python service."""
        
        # Extract current step from execution plan
        step = StateManager.get_current_step(state)
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("wind_turbine", "turbine_analysis", state)
        streamer.status("Analyzing turbine performance using Python...")
        
        # Get context manager
        context_manager = ContextManager(state)
        
        # Get Python executor service from registry
        python_service = registry.get_service("python_executor")
        if not python_service:
            raise RuntimeError("Python executor service not available in registry")
        
        # Get the full configurable from main graph
        main_configurable = get_full_configuration()
        
        # Create service config by extending main graph's configurable
        service_config = {
            "configurable": {
                **main_configurable,
                "thread_id": f"python_service_{step.get('context_key', 'default')}",
                "checkpoint_ns": "python_executor"
            }
        }
        
        # =====================================================================
        # PHASE 1: CHECK FOR APPROVED CODE EXECUTION
        # =====================================================================
        
        # Check if this is a resume from approval using centralized function
        has_approval_resume, approved_payload = get_approval_resume_data(state, create_approval_type("turbine_analysis"))
        
        if has_approval_resume:
            if approved_payload:
                logger.success("Using approved code execution from previous approval")
                
                streamer.status("Executing approved code...")
                
                # Resume execution with approval response
                resume_response = {"approved": True}
                resume_response.update(approved_payload)
            else:
                # Explicitly rejected
                logger.info("Turbine analysis was rejected by user")
                resume_response = {"approved": False}
            
            # Resume the service with Command pattern
            service_result = await python_service.ainvoke(
                Command(resume=resume_response),
                config=service_config
            )
            
            logger.success("✅ Python executor service completed successfully after approval")
            
            # Both approval and normal paths converge to single processing below
            approval_cleanup = clear_approval_state()
        else:
            # =====================================================================  
            # PHASE 2: STRUCTURED TURBINE ANALYSIS FLOW
            # =====================================================================
            # Extract required contexts using ContextManager
            try:
                contexts = context_manager.extract_from_step(
                    step, state,
                    constraints=["TURBINE_DATA", "WEATHER_DATA", "TURBINE_KNOWLEDGE"],
                    constraint_mode="hard"
                )
                turbine_data = contexts[registry.context_types.TURBINE_DATA]
                weather_data = contexts[registry.context_types.WEATHER_DATA]
                knowledge_data = contexts[registry.context_types.TURBINE_KNOWLEDGE]
            except ValueError as e:
                raise DataValidationError(str(e))
            
            if not isinstance(turbine_data, TurbineDataContext):
                raise DataValidationError(f"Expected TurbineDataContext, got {type(turbine_data)}")
            if not isinstance(weather_data, WeatherDataContext):
                raise DataValidationError(f"Expected WeatherDataContext, got {type(weather_data)}")
            # Note: knowledge_data validation is handled by context manager
            
            # Create execution request parameters
            user_query = state.get("input_output", {}).get("user_query", "")
            task_objective = step.get("task_objective", "")
            
            # =============================
            # STEP 1: Create Analysis Plan
            # =============================
            streamer.status("Creating analysis plan...")
            
            analysis_plan = await create_turbine_analysis_plan(
                current_step=step,
                task_objective=task_objective,
                state=state
            )
            logger.info(f"Generated analysis plan with {len(analysis_plan)} phases: {[p.phase for p in analysis_plan]}")
            
            # ===================================
            # STEP 2: Create Results Template
            # ===================================
            streamer.status("Creating results structure template...")
            
            expected_results = await create_turbine_results_dictionary(analysis_plan)
            logger.info(f"Generated results template with keys: {list(expected_results.keys()) if expected_results else 'None'}")
            
            # ===================================
            # STEP 3: Create Structured Prompts
            # ===================================
            # Get context description for available data
            context_description = context_manager.get_context_access_description(step.get('inputs', []))
            
            # Create structured prompts using analysis plan and results template
            capability_prompts = _create_structured_analysis_prompts(
                analysis_plan, expected_results, context_description
            )
            
            # Add task context
            if task_objective:
                capability_prompts.insert(0, f"TASK: {task_objective}")
            if user_query and user_query != task_objective:
                capability_prompts.insert(1, f"USER REQUEST: {user_query}")
            
            logger.info(f"Created {len(capability_prompts)} structured prompts for Python generation")
            
            # Get main graph's context data
            capability_contexts = state.get('capability_context_data', {})
            
            # ===============================
            # STEP 4: Execute with Structure
            # ===============================
            execution_request = PythonExecutionRequest(
                user_query=user_query,
                task_objective=task_objective,
                expected_results=expected_results,  # Use generated structure
                capability_prompts=capability_prompts,  # Use structured prompts
                execution_folder_name="turbine_analysis",
                capability_context_data=capability_contexts,
                config=state.get("config"),
                retries=3
            )
            
            streamer.status("Generating and executing Python code...")
            
            # Use centralized service interrupt handler
            service_result = await handle_service_with_interrupts(
                service=python_service,
                request=execution_request,
                config=service_config,
                logger=logger,
                capability_name="TurbineAnalysis"
            )
            
            logger.success("Structured turbine analysis completed successfully")
            
            # Normal flow doesn't need approval cleanup
            approval_cleanup = None
    
        
        # ====================================================================
        # CONVERGENCE POINT: Both approval and normal paths meet here
        # ====================================================================
        
        # Process results using structured approach - ultra-clean!
        analysis_context = _create_turbine_analysis_context(service_result, expected_results)
        
        logger.info("Turbine analysis completed successfully")
        
        # Streaming completion
        streamer.status("Analysis complete")
        
        # Store context using StateManager
        context_updates = StateManager.store_context(
            state, 
            registry.context_types.ANALYSIS_RESULTS, 
            step.get("context_key"), 
            analysis_context
        )
        
        # Return results with conditional approval cleanup
        if approval_cleanup:
            return {**context_updates, **approval_cleanup}
        else:
            return context_updates
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Turbine analysis error classification."""
        
        if isinstance(exc, DataValidationError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"Data validation failed: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, ExecutorCommunicationError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Python Executor communication failed: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, ResultProcessingError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Result processing failed: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, AnalysisError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Analysis error: {str(exc)}",
                technical_details=str(exc)
            )
        else:
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Unknown error: {str(exc)}",
                technical_details=str(exc)
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create prompt snippet for turbine analysis."""
        
        analysis_example = OrchestratorExample(
            step={
                "context_key": "turbine_performance_benchmarking",
                "capability": "turbine_analysis",
                "task_objective": "Analyze turbine performance against industry standards and rank performance",
                "expected_output": registry.context_types.ANALYSIS_RESULTS,
                "success_criteria": "Performance benchmarking completed with performance rankings",
                "inputs": [
                    {registry.context_types.TURBINE_DATA: "historical_turbine_data"},
                    {registry.context_types.WEATHER_DATA: "historical_weather_data"},
                    {registry.context_types.TURBINE_KNOWLEDGE: "performance_standards"}
                ]
            },
            scenario_description="Performance benchmarking analysis using Python with knowledge base thresholds",
            notes=f"Uses Python execution with industry standards from knowledge base. Output stored under {registry.context_types.ANALYSIS_RESULTS} context type."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "turbine_analysis" steps:**
                - When tasks require performance benchmarking against industry standards
                - For identifying underperforming turbines and ranking performance
                - When comparing turbine efficiency and capacity factors
                - For analyzing turbine performance against specifications

                **Required Dependencies:**
                - {registry.context_types.TURBINE_DATA}: Historical turbine performance data
                - {registry.context_types.WEATHER_DATA}: Historical weather data
                - {registry.context_types.TURBINE_KNOWLEDGE}: Industry standards and thresholds

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "performance_benchmarking")
                - task_objective: Specific benchmarking task to perform
                - inputs: [{{"{registry.context_types.TURBINE_DATA}": "data_key"}}, {{"{registry.context_types.WEATHER_DATA}": "weather_key"}}, {{"{registry.context_types.TURBINE_KNOWLEDGE}": "standards_key"}}]
                
                **Output: {registry.context_types.ANALYSIS_RESULTS}**
                - Contains: turbine_performance, performance_rankings, performance_summary
                - Available fields: efficiency metrics, capacity factors, performance status, rankings
                - Generated using Python execution with knowledge base thresholds

                **Analysis capabilities:**
                - Efficiency calculations against theoretical maximum
                - Capacity factor analysis and industry comparisons
                - Performance categorization using knowledge base thresholds
                - Performance rankings and classifications
                """),
            examples=[analysis_example],
            order=15
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for turbine analysis."""
        return TaskClassifierGuide(
            instructions="Determine if the task requires statistical analysis of turbine performance data.",
            examples=[
                ClassifierExample(
                    query="Calculate performance baselines for each turbine", 
                    result=True, 
                    reason="Request explicitly asks for baseline calculations."
                ),
                ClassifierExample(
                    query="Analyze turbine performance patterns", 
                    result=True, 
                    reason="Performance pattern analysis requires statistical analysis."
                ),
                ClassifierExample(
                    query="Show raw turbine data", 
                    result=False, 
                    reason="Request is for raw data display, not analysis."
                ),
                ClassifierExample(
                    query="Find performance issues and establish proper baselines", 
                    result=True, 
                    reason="Finding issues and establishing baselines requires performance analysis."
                ),
                ClassifierExample(
                    query="Configure monitoring thresholds", 
                    result=False, 
                    reason="Monitoring configuration is a different capability."
                ),
                ClassifierExample(
                    query="Detect anomalies in turbine behavior", 
                    result=True, 
                    reason="Anomaly detection requires statistical analysis of performance data."
                ),
            ],
            actions_if_true=ClassifierActions()
        ) 