"""
Weather Data Retrieval Capability

This capability retrieves historical weather data from the mock weather API.
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
from applications.wind_turbine.context_classes import WeatherDataContext
from applications.wind_turbine.mock_apis import weather_api
from configs.logger import get_logger

logger = get_logger("wind_turbine", "weather_data_retrieval")


registry = get_registry()

# === Weather Data Errors ===
class WeatherDataError(Exception):
    """Base class for weather data related errors."""
    pass

class WeatherDataRetrievalError(WeatherDataError):
    """Raised when weather data retrieval fails."""
    pass

class MissingTimeRangeError(WeatherDataError):
    """Raised when required time range context is missing."""
    pass

@capability_node
class WeatherDataRetrievalCapability(BaseCapability):
    """Capability for retrieving historical weather data."""
    
    name = "weather_data_retrieval"
    description = "Retrieve historical weather data including wind speed and direction"
    provides = [registry.context_types.WEATHER_DATA]
    requires = [registry.context_types.TIME_RANGE]
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Retrieve historical weather data for the specified time range."""
        
        # Extract current step from execution plan
        step = StateManager.get_current_step(state)
        
        # Define streaming helper here for step awareness
        from configs.streaming import get_streamer
        streamer = get_streamer("wind_turbine", "weather_data_retrieval", state)
        streamer.status("Retrieving historical weather data...")
        
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
        
        logger.debug(f"Retrieving weather data from {time_range_input.start_date} to {time_range_input.end_date}")
        
        try:
            # Use the mock API to get historical weather data
            wind_readings = await weather_api.get_weather_history(
                start_time=time_range_input.start_date,
                end_time=time_range_input.end_date
            )
            
            # Convert to separate lists
            timestamps = [reading["timestamp"] for reading in wind_readings]
            wind_speeds = [reading["wind_speed"] for reading in wind_readings]
            
            # Create weather data context
            weather_data = WeatherDataContext(
                timestamps=timestamps,
                wind_speeds=wind_speeds,
                time_range=f"{time_range_input.start_date} to {time_range_input.end_date}"
            )
            
            logger.info(f"Retrieved {len(wind_readings)} weather readings for time range")
            
            # Streaming completion
            streamer.status("Weather data retrieved")
            
            # Store context using StateManager
            return StateManager.store_context(
                state, 
                registry.context_types.WEATHER_DATA, 
                step.get("context_key"), 
                weather_data
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve weather data: {e}")
            raise WeatherDataRetrievalError(f"Failed to retrieve weather data: {str(e)}")
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Weather data specific error classification."""
        
        if isinstance(exc, MissingTimeRangeError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"Missing time range dependency: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, WeatherDataRetrievalError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Weather data retrieval failed: {str(exc)}",
                technical_details=str(exc)
            )
        elif isinstance(exc, WeatherDataError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Weather data error: {str(exc)}",
                technical_details=str(exc)
            )
        else:
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Unknown error: {str(exc)}",
                technical_details=str(exc)
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create prompt snippet for weather data retrieval."""
        
        weather_data_example = OrchestratorExample(
            step=PlannedStep(
                context_key="historical_weather_data",
                capability="weather_data_retrieval",
                task_objective="Retrieve 3-day historical weather data to correlate wind conditions with reported performance issues",
                expected_output=registry.context_types.WEATHER_DATA,
                success_criteria="Historical wind speed and direction data retrieved for performance correlation",
                inputs=[{registry.context_types.TIME_RANGE: "past_3_days_timerange"}]
            ),
            scenario_description="Retrieving historical weather data for turbine performance correlation",
            notes=f"Output stored under {registry.context_types.WEATHER_DATA} context type with wind speed and direction readings."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "weather_data_retrieval" steps:**
                - When tasks require weather data for turbine performance correlation
                - For analyzing impact of wind conditions on turbine operation
                - When investigating performance issues that may be weather-related
                - As supporting data for turbine performance analysis

                **Required Dependencies:**
                - {registry.context_types.TIME_RANGE}: Must have time range context from time_range_parsing step

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "historical_weather_data")
                - task_objective: Specific weather data retrieval task
                - inputs: [{{"{registry.context_types.TIME_RANGE}": "time_range_context_key"}}]
                
                **Output: {registry.context_types.WEATHER_DATA}**
                - Contains: timestamps, wind_speeds as separate lists
                - Available fields: timestamps, wind_speeds
                - Available to downstream analysis steps
                - Provides environmental context for turbine performance analysis

                **Dependencies and sequencing:**
                1. Requires {registry.context_types.TIME_RANGE} context from time_range_parsing step
                2. Provides data for {registry.capability_names.TURBINE_ANALYSIS} capability (wind correlation)
                3. Can be combined with turbine data for comprehensive analysis
                
                **Data structure:** Separate lists for timestamps and wind_speeds (m/s).
                """),
            examples=[weather_data_example],
            order=11
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for weather data retrieval."""
        return TaskClassifierGuide(
            instructions="Determine if the task requires historical weather data retrieval for turbine analysis.",
            examples=[
                ClassifierExample(
                    query="Analyze wind patterns from yesterday", 
                    result=True, 
                    reason="Request requires historical weather data for wind pattern analysis."
                ),
                ClassifierExample(
                    query="Correlate turbine performance with wind conditions", 
                    result=True, 
                    reason="Correlation analysis requires weather data to compare with turbine performance."
                ),
                ClassifierExample(
                    query="Show turbine power output trends", 
                    result=False, 
                    reason="Request is for turbine data only, no weather correlation mentioned."
                ),
                ClassifierExample(
                    query="Check if high winds caused performance issues", 
                    result=True, 
                    reason="Investigation requires weather data to check wind conditions."
                ),
                ClassifierExample(
                    query="Set up turbine maintenance schedule", 
                    result=False, 
                    reason="Maintenance scheduling task, doesn't require weather data retrieval."
                ),
                ClassifierExample(
                    query="How do wind conditions affect turbine efficiency?", 
                    result=True, 
                    reason="Analysis question that would benefit from historical weather data."
                ),
            ],
            actions_if_true=ClassifierActions()
        ) 