"""
Get Archiver Data Capability - LangGraph Convention-Based Implementation

This capability retrieves historical Process Variable data from the ALS archiver.
It provides access to time-series data for analysis, plotting, and trend monitoring.
"""

import asyncio
import logging
import pandas as pd
import textwrap
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Import from new clean architecture
from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.context.base import CapabilityContext
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.planning import PlannedStep
from framework.state import AgentState, StateManager
from framework.base.examples import OrchestratorGuide, TaskClassifierGuide, ClassifierExample, OrchestratorExample, ClassifierActions
from framework.registry import get_registry
from framework.context.context_manager import ContextManager

from applications.als_assistant.context_classes import ArchiverDataContext
from archivertools import ArchiverClient
from configs.config import get_model_config, get_config_value
from configs.streaming import get_streamer
from configs.logger import get_logger

logger = get_logger("als_assistant", "get_archiver_data")


registry = get_registry()

# === Archiver-Related Errors ===
class ArchiverError(Exception):
    """Base class for all archiver-related errors."""
    pass

class ArchiverTimeoutError(ArchiverError):
    """Raised when archiver requests time out."""
    pass

class ArchiverConnectionError(ArchiverError):
    """Raised when archiver connectivity issues."""
    pass

class ArchiverDataError(ArchiverError):
    """Raised when archiver returns unexpected data format."""
    pass

class ArchiverDependencyError(ArchiverError):
    """Raised when required dependencies (like PV addresses or time range) are missing."""
    pass

class ArchiverSystemError(ArchiverError):
    """Raised when there are system-level archiver issues that indicate configuration or installation problems."""
    pass

def download_archiver_data(
    pv_list: Union[str, List[str]],
    start_date: datetime,
    end_date: datetime,
    precision_ms: int = 1000,
    archiver_url: str = None,
    timeout: Optional[int] = None
) -> pd.DataFrame:
    """
    Retrieves historical data for PVs from the ALS archiver.
    This function is synchronous and can be used directly in Python scripts.

    Args:
        pv_list: A single PV address or a list of PV addresses to retrieve data for.
        start_date: The start date/time as datetime object.
        end_date: The end date/time as datetime object.
        precision_ms: Data precision in milliseconds (default: 1000, which is 1 second).

    Returns:
        A pandas DataFrame containing the retrieved data.
        
    Raises:
        ArchiverTimeoutError: If the archiver request times out
        ArchiverConnectionError: If there are connectivity issues with the archiver
        ArchiverDataError: For unexpected data formats
        ArchiverError: For other archiver-related errors
    """
    if ArchiverClient is None:
        raise ArchiverSystemError("ArchiverClient not available - please check installation")

    # Validate that inputs are datetime objects
    if not isinstance(start_date, datetime):
        raise TypeError(f"start_date must be a datetime object, got {type(start_date)}")
    if not isinstance(end_date, datetime):
        raise TypeError(f"end_date must be a datetime object, got {type(end_date)}")

    # Ensure pv_list is a list
    if isinstance(pv_list, str):
        pv_list = [pv_list]
      
    try:
        # Initialize the archiver client
        logger.debug(f"Initializing ArchiverClient with URL: {archiver_url!r} (type: {type(archiver_url)})")
        try:
            archiver = ArchiverClient(archiver_url=archiver_url)
        except Exception as init_error:
            # Convert any ArchiverClient initialization errors to our system error
            raise ArchiverSystemError(f"ArchiverClient initialization failed: {init_error}")
        
        def fetch_data():
            return archiver.match_data(
                pv_list=pv_list,
                precision=precision_ms,
                start=start_date,
                end=end_date,
                verbose=0
            )
        
        # Use ThreadPoolExecutor for timeout protection
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fetch_data)
            try:
                data = future.result(timeout=timeout)
                
                # Ensure the index is in datetime format if data is a DataFrame
                if isinstance(data, pd.DataFrame) and hasattr(data, 'index'):
                    data.index = pd.to_datetime(data.index)

                # Return the DataFrame directly
                if isinstance(data, pd.DataFrame):
                    return data
                else:
                    error_msg = f"Unexpected data format: {type(data)}"
                    raise ArchiverDataError(error_msg)
                    
            except TimeoutError:
                error_msg = "Request to archiver timed out. Please check if the archiver service is accessible."
                raise ArchiverTimeoutError(error_msg)
                
    except Exception as e:
        error_msg = str(e)
        
        # Check for connection refused errors which typically indicate SSH tunnel issues
        if "connection refused" in error_msg.lower() or "errno 61" in error_msg.lower():
            user_friendly_msg = "Cannot connect to the ALS archiver. Please make sure the SSH tunnel is open (port 8443). To open the tunnel, run: ssh -L 8443:pscaa02.pcds:8443 <username>@als.lbl.gov"
            raise ArchiverConnectionError(user_friendly_msg)
        
        # Check for other connectivity issues
        elif "connectionpool" in error_msg.lower() or "connection" in error_msg.lower():
            user_friendly_msg = "Network connectivity issue with the ALS archiver. This may be due to:\n1. SSH tunnel not being established\n2. VPN not being connected\n3. Network connectivity issues\nPlease check your connection and try again."
            raise ArchiverConnectionError(user_friendly_msg)
        
        # For other errors
        raise ArchiverError(f"Error accessing archiver data: {error_msg}")


def convert_dataframe_to_archiver_dict(df: pd.DataFrame, precision_ms: int) -> Dict[str, Any]:
    """
    Convert pandas DataFrame from archiver to simplified dictionary format.
    
    Args:
        df: pandas DataFrame with datetime index and PV columns
        precision_ms: The precision in milliseconds used for data retrieval
        
    Returns:
        Dictionary with timestamps as datetime objects, precision_ms, time_series_data, and available_pvs
    """
    try:
        if df.empty:
            return {
                "timestamps": [],
                "precision_ms": precision_ms,
                "time_series_data": {},
                "available_pvs": []
            }
        
        # Keep timestamps as datetime objects - no conversion to strings!
        timestamps = df.index.to_pydatetime().tolist()  # Convert pandas datetime index to Python datetime objects
        
        # Convert PV data to dictionary of lists, handling NaN values
        time_series_data = {}
        for col in df.columns:
            # Convert to list, replacing NaN with None (which will be serializable)
            values = df[col].fillna(0.0).tolist()  # Fill NaN with 0.0 for simplicity
            time_series_data[col] = values
        
        # Create list of available PV names for intuitive access
        available_pvs = list(df.columns)
        
        result = {
            "timestamps": timestamps,
            "precision_ms": precision_ms,
            "time_series_data": time_series_data,
            "available_pvs": available_pvs
        }
        
        return result
        
    except Exception as e:
        raise ArchiverDataError(f"Error converting DataFrame to archiver format: {str(e)}")


# ========================================================
# Convention-Based Capability Implementation
# ========================================================

@capability_node
class ArchiverDataCapability(BaseCapability):
    """
    Archiver Data Capability - LangGraph-Native with Full Business Logic
    
    - Complete archiver client integration with sophisticated error handling
    - Comprehensive validation and timeout protection  
    - Registry-based patterns for context types and capability names
    - Rich orchestrator examples and classifier configuration
    """
    
    # Required metadata (loaded through registry configuration)
    name = "get_archiver_data"
    description = "Retrieve historical Process Variable data from the ALS archiver"
    provides = ["ARCHIVER_DATA"]
    requires = ["PV_ADDRESSES", "TIME_RANGE"]
    
    @staticmethod
    async def execute(
        state: AgentState,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main archiver data retrieval logic.
        
        Pure business logic enhanced by @capability_node decorator for infrastructure.
        """
        
        # Extract current step from execution plan (single source of truth)
        step = StateManager.get_current_step(state)

        # Define streaming helper here for step awareness
        streamer = get_streamer("als_assistant", "get_archiver_data", state)
        
        # Initialize context manager
        context_manager = ContextManager(state)
        
        logger.info(f"Starting archiver data retrieval: {step.get('task_objective', 'unknown')}")
        streamer.status("Initializing archiver data retrieval...")
        
        try:
            try:
                contexts = context_manager.extract_from_step(
                    step, state,
                    constraints=[registry.context_types.PV_ADDRESSES, registry.context_types.TIME_RANGE],
                    constraint_mode="hard"
                )
                pv_finder_context = contexts[registry.context_types.PV_ADDRESSES]
                time_range_context = contexts[registry.context_types.TIME_RANGE]
                logger.info(f"Successfully extracted both required contexts: PV_ADDRESSES and TIME_RANGE")
            except ValueError as e:
                raise ArchiverDependencyError(str(e))
            
            # Validate that we have PV addresses to work with
            if not pv_finder_context.pvs or len(pv_finder_context.pvs) == 0:
                raise ArchiverDependencyError("No PV addresses available for archiver data retrieval. The PV address finding step may have failed to locate suitable PVs.")
            
            streamer.status(f"Found {len(pv_finder_context.pvs)} PVs and time range, retrieving data...")
            
            # Get precision from step parameters (with fallback to default)
            precision_ms = (step.get('parameters') or {}).get('precision_ms', 1000)
            
            # Get archiver URL from unified config system (matching old implementation path)
            archiver_url = get_config_value('applications.als_assistant.external_services.archiver.url')
            
            logger.debug(f"Retrieving archiver data for {len(pv_finder_context.pvs)} PVs from {time_range_context.start_date} to {time_range_context.end_date}")
            
            # Download the data asynchronously
            archiver_dataframe = await asyncio.to_thread(
                download_archiver_data,
                pv_list=pv_finder_context.pvs,
                start_date=time_range_context.start_date,
                end_date=time_range_context.end_date,
                precision_ms=precision_ms,
                archiver_url=archiver_url
            )
            
            streamer.status("Converting archiver data to structured format...")
            
            # Convert DataFrame to simplified dictionary format
            archiver_data = convert_dataframe_to_archiver_dict(archiver_dataframe, precision_ms)
            
            logger.debug(f"Retrieved archiver data with {len(archiver_data['timestamps'])} timestamps and {len(archiver_data['available_pvs'])} PVs")
            
            streamer.status("Creating archiver data context...")
            
            # Create rich context object
            archiver_context = ArchiverDataContext(
                timestamps=archiver_data["timestamps"],
                precision_ms=archiver_data["precision_ms"],
                time_series_data=archiver_data["time_series_data"],
                available_pvs=archiver_data["available_pvs"]
            )
            
            # Log archiver data info with safe timestamp access
            start_time = archiver_context.timestamps[0] if archiver_context.timestamps else 'N/A'
            end_time = archiver_context.timestamps[-1] if archiver_context.timestamps else 'N/A'
            logger.info(f"Retrieved archiver data: {len(archiver_context.timestamps)} points for {len(archiver_context.available_pvs)} PVs from {start_time} to {end_time}")
            
            # Store context using StateManager
            state_updates = StateManager.store_context(
                state, 
                registry.context_types.ARCHIVER_DATA, 
                step.get("context_key"), 
                archiver_context
            )
            
            
            # Return state updates (LangGraph will merge automatically)
            return state_updates
            
        except Exception as e:
            logger.error(f"Archiver data retrieval failed: {e}")
            streamer.error(f"Archiver data retrieval failed: {str(e)}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """
        Domain-specific error classification with detailed recovery suggestions.
        """
        
        if isinstance(exc, ArchiverTimeoutError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Archiver timeout error: {str(exc)}",
                metadata={
                    "technical_details": "Archiver requests timed out waiting for response from archivertools library",
                    "suggestions": [
                        "Reduce the time range of your query (try shorter periods like 1 hour instead of 1 day)",
                        "Request fewer PVs in a single query (limit to 5-10 PVs)",
                        "Increase precision_ms parameter to reduce data points (try 5000-10000ms)",
                        "Increase time out limit for large queries",
                        "Verify the archiver is reachable",
                        "Check network connectivity to ALS systems"
                    ]
                }
            )
        elif isinstance(exc, ArchiverConnectionError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Archiver connection error: {str(exc)}",
                metadata={
                    "technical_details": "Cannot establish connection to ALS archiver service - typically indicates missing SSH tunnel or network issues",
                    "suggestions": [
                        "Verify the archiver is reachable",
                        "Verify VPN connection to ALS network",
                        "Check if archiver service is running on pscaa02.pcds:8443",
                        "Confirm network access to ALS control room systems",
                        "Contact ALS operations if archiver service appears down"
                    ]
                }
            )
        elif isinstance(exc, ArchiverDataError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"Archiver data error: {str(exc)}",
                metadata={
                    "technical_details": "Archiver returned unexpected data format or empty dataset",
                    "replanning_reason": f"Archiver data format issue: {exc}",
                    "suggestions": [
                        "Verify that the requested PV names exist and are archived",
                        "Check if the time range contains actual data (avoid weekends/shutdowns)",
                        "Try a different time range when the accelerator was operational",
                        "Confirm PV naming convention matches archived data",
                        "Use PV finder capability to verify correct PV addresses"
                    ]
                }
            )
        elif isinstance(exc, ArchiverDependencyError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"Missing dependency: {str(exc)}",
                metadata={
                    "technical_details": "Required input context (PV_ADDRESSES or TIME_RANGE) not available for archiver data retrieval",
                    "replanning_reason": f"Missing required inputs: {exc}",
                    "suggestions": [
                        "Ensure PV addresses have been found using the pv_address_finding capability",
                        "Verify time range has been parsed using the time_range_parsing capability",
                        "Check that required input contexts are available from previous steps",
                        "Review execution plan to ensure proper step dependencies"
                    ]
                }
            )
        elif isinstance(exc, ArchiverSystemError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Archiver system error: {str(exc)}",
                metadata={
                    "technical_details": "System-level archiver configuration or installation issue",
                    "safety_abort_reason": f"Archiver system not properly configured: {exc}",
                    "suggestions": [
                        "Verify ArchiverClient library is properly installed",
                        "Check archiver URL configuration in external_services.archiver.url",
                        "Ensure system dependencies for archiver access are met",
                        "Contact system administrator to verify archiver configuration"
                    ]
                }
            )
        elif isinstance(exc, ArchiverError):
            # Generic archiver error for cases not covered by specific error types
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Archiver error: {str(exc)}",
                metadata={
                    "technical_details": "General archiver service error - may indicate temporary service issues",
                    "suggestions": [
                        "Retry the request as this may be a temporary service issue",
                        "Simplify the query by reducing time range or number of PVs",
                        "Verify the archiver is reachable"
                    ]
                }
            )
        else:
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"Archiver data retrieval failed: {exc}",
                metadata={"technical_details": str(exc)}
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create prompt snippet for archiver data capability."""
        
        # Define structured examples using simplified dict format
        standard_example = OrchestratorExample(
            step=PlannedStep(
                context_key="historical_beam_current_data",
                capability="get_archiver_data",
                task_objective="Retrieve historical beam current data from archiver for the last week",
                expected_output=registry.context_types.ARCHIVER_DATA,
                success_criteria="Data retrieved successfully",
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "beam_current_pvs"},
                    {registry.context_types.TIME_RANGE: "last_week_timerange"}
                ]
            ),
            scenario_description="Standard historical data retrieval for plotting or analysis",
            notes=f"Requires PV addresses and time range inputs. Output stored under {registry.context_types.ARCHIVER_DATA} context type."
        )
        
        high_resolution_example = OrchestratorExample(
            step=PlannedStep(
                context_key="high_res_magnet_data",
                capability="get_archiver_data",
                task_objective="Retrieve high-resolution historical magnet current data during maintenance period",
                expected_output=registry.context_types.ARCHIVER_DATA,
                success_criteria="High-resolution data retrieved successfully",
                parameters={"precision_ms": 100},
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "magnet_pvs"},
                    {registry.context_types.TIME_RANGE: "maintenance_timerange"}
                ]
            ),
            scenario_description="High-resolution data retrieval for detailed analysis of short term events",
            notes="Use precision_ms=100 for 0.1-second resolution, 1000 for standard 1-second, 10000 for 10-second averaging."
        )
        
        long_term_example = OrchestratorExample(
            step=PlannedStep(
                context_key="power_supply_trend_data",
                capability="get_archiver_data",
                task_objective="Retrieve long-term power supply trend data with reduced precision for monthly analysis",
                expected_output=registry.context_types.ARCHIVER_DATA,
                success_criteria="Long-term trend data retrieved successfully",
                parameters={"precision_ms": 10000},
                inputs=[
                    {registry.context_types.PV_ADDRESSES: "power_supply_pvs"},
                    {registry.context_types.TIME_RANGE: "monthly_timerange"}
                ]
            ),
            scenario_description="Long-term trend analysis over days/weeks with reduced data volume",
            notes="Use higher precision_ms values for long time ranges to reduce data volume and processing time."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "get_archiver_data" steps:**
                - When tasks require historical PV data
                - When retrieving past values from the ALS archiver
                - When time-series data is needed from archived sources

                **Step Structure:**
                - context_key: Unique identifier for output (e.g., "historical_data", "trend_data")
                - inputs: Specify required inputs:
                {{"{registry.context_types.PV_ADDRESSES}": "context_key_with_pv_data", "{registry.context_types.TIME_RANGE}": "context_key_with_time_range"}}
                
                **Required Inputs:**
                - {registry.context_types.PV_ADDRESSES} data: typically from a "{registry.capability_names.PV_ADDRESS_FINDING}" step
                - {registry.context_types.TIME_RANGE} data: typically from a "{registry.capability_names.TIME_RANGE_PARSING}" step
                
                **Optional Parameters (specify in step.parameters):**
                - precision_ms (int): Data sampling interval in milliseconds (default: 1000)
                * Use 1000 for 1-second precision (standard)
                * Use 100 for 0.1-second precision (high resolution)
                * Use 10000 for 10-second precision (long-term trends)
                
                **Input flow and sequencing:**
                1. "{registry.capability_names.PV_ADDRESS_FINDING}" step must precede this step (if {registry.context_types.PV_ADDRESSES} data is not present already)
                2. "{registry.capability_names.TIME_RANGE_PARSING}" step must precede this step (if {registry.context_types.TIME_RANGE} data is not present already)
                
                **Output: {registry.context_types.ARCHIVER_DATA}**
                - Contains: Structured historical data from the ALS archiver
                - Available to downstream steps via context system
                
                Do NOT plan this for current PV values; use "pv_value_retrieval" for real-time data.
                """),
            examples=[standard_example, high_resolution_example, long_term_example],
            priority=15
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for archiver data capability."""
        return TaskClassifierGuide(
            instructions="Determines if the task requires accessing the PV data archiver. This is relevant for requests involving historical data, trends from the control system.",
            examples=[
                ClassifierExample(
                    query="Which tools do you have?", 
                    result=False, 
                    reason="This is a question about the AI's capabilities."
                ),
                ClassifierExample(
                    query="Plot the historical data for vacuum pressure in Sector 4 for the last week.", 
                    result=True, 
                    reason="The query explicitly asks for historical data plotting, which requires archiver access."
                ),
                ClassifierExample(
                    query="What is the current beam energy?", 
                    result=False, 
                    reason="The query asks for a current value, not historical data."
                ),
                ClassifierExample(
                    query="Can you plot that over the last 4h?", 
                    result=True, 
                    reason="The query asks for historical data plotting."
                ),
                ClassifierExample(
                    query="What was that value yesterday?", 
                    result=True, 
                    reason="The query asks for historical data."
                ),
            ],
            actions_if_true=ClassifierActions()
        )