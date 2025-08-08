"""
Turbine Data Archiver Capability

This capability retrieves historical turbine performance data from the mock turbine sensor API.
"""

import asyncio
import logging
import textwrap
from typing import Dict, Any, Optional

from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.examples import OrchestratorGuide, OrchestratorExample, ClassifierActions, ClassifierExample, TaskClassifierGuide
from framework.base.planning import PlannedStep
from framework.state import AgentState, StateManager
from framework.registry import get_registry
from framework.context.context_manager import ContextManager
from applications.wind_turbine.context_classes import TurbineDataContext
from applications.wind_turbine.mock_apis import turbine_api
from configs.streaming import get_streamer
from configs.logger import get_logger

logger = get_logger("wind_turbine", "turbine_data_archiver")


registry = get_registry()

# === Turbine Data Errors ===
class TurbineDataError(Exception):
    """Base class for turbine data related errors."""
    pass

class TurbineDataRetrievalError(TurbineDataError):
    """Raised when turbine data retrieval fails."""
    pass

class MissingTimeRangeError(TurbineDataError):
    """Raised when required time range context is missing."""
    pass

@capability_node
class TurbineDataArchiverCapability(BaseCapability):
    """Capability for retrieving historical turbine performance data."""
    
    name = "turbine_data_archiver"
    description = "Retrieve historical turbine performance data from sensor archives"
    provides = [registry.context_types.TURBINE_DATA]
    requires = [registry.context_types.TIME_RANGE]
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Retrieve historical turbine data for the specified time range."""
        
        # Extract current step from execution plan
        step = StateManager.get_current_step(state)
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("wind_turbine", "turbine_data_archiver", state)
        streamer.status("Retrieving historical turbine data...")
        
        # Extract required TIME_RANGE context using ContextManager
        
        try:
            context_manager = ContextManager(state)
            contexts = context_manager.extract_from_step(
                step, state,
                constraints=["TIME_RANGE"],
                constraint_mode="hard"
            )
            time_range_input = contexts[registry.context_types.TIME_RANGE]
        except ValueError as e:
            raise MissingTimeRangeError(str(e))
        
        # Validate time range context
        if not hasattr(time_range_input, 'start_date') or not hasattr(time_range_input, 'end_date'):
            raise MissingTimeRangeError(f"{registry.context_types.TIME_RANGE} context missing required start_date/end_date attributes")
        
        logger.debug(f"Retrieving turbine data from {time_range_input.start_date} to {time_range_input.end_date}")
        
        try:
            # Use the mock API to get historical data
            turbine_readings = await turbine_api.get_historical_data(
                start_time=time_range_input.start_date,
                end_time=time_range_input.end_date
            )
            
            # Convert to separate lists (makes subsequent pd-dataframe conversion easier)
            timestamps = [reading["timestamp"] for reading in turbine_readings]
            turbine_ids = [reading["turbine_id"] for reading in turbine_readings]
            power_outputs = [reading["power_output"] for reading in turbine_readings]
            
            # Create turbine data context
            turbine_data = TurbineDataContext(
                timestamps=timestamps,
                turbine_ids=turbine_ids,
                power_outputs=power_outputs,
                time_range=f"{time_range_input.start_date} to {time_range_input.end_date}",
                total_records=len(turbine_readings)
            )
            
            logger.info(f"Retrieved {len(turbine_readings)} turbine readings for time range")
            
            # Streaming completion
            streamer.status("Turbine data retrieved")
            
            # Store context using StateManager
            return StateManager.store_context(
                state, 
                registry.context_types.TURBINE_DATA, 
                step.get("context_key"), 
                turbine_data
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve turbine data: {e}")
            raise TurbineDataRetrievalError(f"Failed to retrieve turbine data: {str(e)}")
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Turbine data specific error classification."""
        
        if isinstance(exc, MissingTimeRangeError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"Missing time range dependency: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, TurbineDataRetrievalError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Turbine data retrieval failed: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, TurbineDataError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Turbine data error: {str(exc)}",
                technical_details=str(exc)
            )
        else:
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Unknown error: {str(exc)}",
                technical_details=str(exc)
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create prompt snippet for turbine data archiver."""
        
        turbine_data_example = OrchestratorExample(
            step=PlannedStep(
                context_key="historical_turbine_data",
                capability="turbine_data_archiver",
                task_objective="Retrieve historical turbine performance data from the past 3 days for baseline calculation and trend analysis",
                expected_output=registry.context_types.TURBINE_DATA,
                success_criteria="Historical turbine performance data retrieved with power output over the time period",
                inputs=[{registry.context_types.TIME_RANGE: "past_3_days_timerange"}]
            ),
            scenario_description="Retrieving historical turbine performance data for analysis",
            notes=f"Output stored under {registry.context_types.TURBINE_DATA} context type with individual turbine readings."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "turbine_data_archiver" steps:**
                - When tasks require historical turbine performance data for analysis
                - For baseline calculations and trend analysis
                - When investigating performance issues over time
                - As a data source for turbine-specific analysis

                **Required Dependencies:**
                - {registry.context_types.TIME_RANGE}: Must have time range context from time_range_parsing step

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "historical_turbine_data")
                - task_objective: Specific data retrieval task
                - inputs: [{{"{registry.context_types.TIME_RANGE}": "time_range_context_key"}}]
                
                **Output: {registry.context_types.TURBINE_DATA}**
                - Contains: timestamps, turbine_ids, power_outputs as separate lists
                - Available fields: timestamps, turbine_ids, power_outputs  
                - Available to downstream analysis steps
                - Provides raw data for performance analysis and baseline calculations

                **Dependencies and sequencing:**
                1. Requires {registry.context_types.TIME_RANGE} context from time_range_parsing step
                2. Provides data for {registry.capability_names.TURBINE_ANALYSIS} capability
                3. Can be combined with weather data for correlation analysis
                
                **Data structure:** Separate lists for timestamps, turbine_ids, and power_outputs (MW).
                """),
            examples=[turbine_data_example],
            order=10
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for turbine data archiver."""
        return TaskClassifierGuide(
            instructions="Determine if the task requires historical turbine performance data retrieval.",
            examples=[
                ClassifierExample(
                    query="Show turbine performance for the past 3 days", 
                    result=True, 
                    reason="Request requires historical turbine performance data."
                ),
                ClassifierExample(
                    query="Analyze recent turbine trends", 
                    result=True, 
                    reason="Analysis requires historical turbine data for trends."
                ),
                ClassifierExample(
                    query="What is the current wind speed?", 
                    result=False, 
                    reason="Request is for current weather data, not turbine performance history."
                ),
                ClassifierExample(
                    query="Configure monitoring thresholds for turbines", 
                    result=False, 
                    reason="Monitoring configuration task, doesn't require historical data retrieval directly."
                ),
                ClassifierExample(
                    query="Compare turbine performance to baselines", 
                    result=True, 
                    reason="Comparison requires historical turbine performance data."
                ),
                ClassifierExample(
                    query="How do wind turbines generate power?", 
                    result=False, 
                    reason="General question about turbine operation, not data retrieval."
                ),
            ],
            actions_if_true=ClassifierActions()
        ) 