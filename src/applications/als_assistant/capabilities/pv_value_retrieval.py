"""
PV Value Retrieval Capability - LangGraph Migration

This capability handles reading current values of Process Variables from the EPICS
control system. It provides real-time access to live PV data.

Migrated to LangGraph convention-based architecture with:
- Pure LangGraph streaming with get_stream_writer()
- New error classification system
- Unified configuration patterns
- Current context management system
"""

import os
import logging
import textwrap
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
import epics

# Import LangGraph-native patterns
from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.examples import OrchestratorGuide, OrchestratorExample, TaskClassifierGuide, ClassifierExample, ClassifierActions
from framework.base.planning import PlannedStep
from framework.state import AgentState
from configs.logger import get_logger
from configs.streaming import get_streamer
from configs.config import get_config_value
from framework.registry import get_registry
from framework.state import StateManager
from framework.context.context_manager import ContextManager

# Import context classes
from applications.als_assistant.context_classes import PVValues, PVValue, PVAddresses

if TYPE_CHECKING:
    pass

logger = get_logger("als_assistant", "pv_value_retrieval")


registry = get_registry()

# Import PV names list
try:
    from applications.als_assistant.database.PVs.pv_names_list import pv_names 
except ImportError:
    # Fallback for testing
    pv_names = []
    logger.warning("PV names list not available - PV validation will be performed by EPICS directly")



# ========================================================
# PV-Related Errors
# ========================================================

class PVError(Exception):
    """Base class for all PV-related errors."""
    pass

class PVNotFoundError(PVError):
    """Raised when a PV address doesn't exist in the system."""
    pass

class EPICSTimeoutError(PVError):
    """Raised when EPICS operations time out."""
    pass

class EPICSChannelAccessError(PVError):
    """Raised when there are EPICS channel access errors."""
    pass

class EPICSGatewayError(PVError):
    """Raised when there are EPICS gateway connectivity errors."""
    pass

class PVDependencyError(PVError):

    pass


# ========================================================
# Core PV Reading Function
# ========================================================

async def get_pv_value(pv_address: str, timeout: Optional[float] = None) -> Dict[str, Any]:
    """
    Reads a live EPICS Process Variable (PV) value and metadata from the ALS.

    Args:
        pv_address: The address of the Process Variable to read.
        timeout (optional): Timeout in seconds for each attempt. If None, uses config default.

    Returns:
        A dictionary containing:
            - 'value': String representation of the PV's current value
            - 'units': Engineering units (e.g., 'mA', 'mm', 'V') or empty string if not available
        
    Raises:
        PVNotFoundError: If the PV address doesn't exist in the system
        EPICSTimeoutError: If the read operation times out
        EPICSGatewayError: If there are gateway connectivity issues
        EPICSChannelAccessError: For other EPICS-related errors
    """
    
    # Use unified config pattern
    
    # Use config timeout if not provided
    if timeout is None:
        epics_config = get_config_value('epics_config', {})
        timeout = epics_config.get('timeout', 5.0)
    
    # Check if PV exists - handle whitespace issues
    if pv_names:
        # Strip whitespace from input PV and check against stripped PV names efficiently
        pv_address_clean = pv_address.strip()        
        if not any(pv.strip() == pv_address_clean for pv in pv_names):
            raise PVNotFoundError(f"PV {pv_address} does not exist. Ask the user or use get-pv-address tool to find the correct PV address.")
    
    logger.debug(f"Reading PV value for: {pv_address}")
    
    # Configure EPICS environment for container/gateway access (only once per process)
    if not hasattr(get_pv_value, '_epics_configured'):
        epics_config = get_config_value('epics_config', {})
        gateway_config = epics_config.get('gateways', {}).get('read_only', {})
        if gateway_config:
            # Use the old working EPICS environment variables
            address = gateway_config.get('address', '')
            port = gateway_config.get('port', 5064)
            os.environ['EPICS_CA_ADDR_LIST'] = address
            os.environ['EPICS_CA_SERVER_PORT'] = str(port)
            os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'
            
            # Clear EPICS cache to pick up new environment variables
            epics.ca.clear_cache()
            logger.debug(f"Configured EPICS gateway: {address}:{port}")
            get_pv_value._epics_configured = True
    
    try:
        # Create PV object to get both value and metadata (including units)
        pv = epics.PV(pv_address)
        pv.wait_for_connection(timeout=timeout)
        
        if pv.connected:
            value = pv.value
            units = getattr(pv, 'units', None) or ''  # Get units, default to empty string
            logger.debug(f"Retrieved PV {pv_address}: value={value}, units='{units}'")
            
            # Return structured result with value and units
            return {
                'value': str(value) if value is not None else 'None',
                'units': units,
            }
        else:
            # PV connection failed
            raise EPICSChannelAccessError(f"Failed to connect to PV '{pv_address}': Connection timeout after {timeout}s")
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Map different types of EPICS errors to our specific exception types
        if "timeout" in error_msg or "timed out" in error_msg:
            raise EPICSTimeoutError(f"Timeout reading PV {pv_address}: {str(e)}")
        elif "connection" in error_msg or "gateway" in error_msg or "host" in error_msg:
            raise EPICSGatewayError(f"Gateway/connection error reading PV '{pv_address}': {str(e)}")
        else:
            # For all other EPICS errors, use the general channel access error
            raise EPICSChannelAccessError(f"EPICS Channel Access error reading PV '{pv_address}': {str(e)}")


# ========================================================
# Capability Implementation
# ========================================================

@capability_node
class PVValueRetrievalCapability(BaseCapability):
    """PV value retrieval capability for reading current PV values."""
    
    name = "pv_value_retrieval"
    description = "Retrieve current values of Process Variables from EPICS"
    provides = ["PV_VALUES"]
    requires = ["PV_ADDRESSES"]
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute PV value retrieval with LangGraph-native patterns."""
        
        # Extract current step - this is provided by the decorator
        step = StateManager.get_current_step(state)
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("als_assistant", "pv_value_retrieval", state)
        streamer.status("Starting PV value retrieval...")
        
        # Extract required PV_ADDRESSES context using ContextManager
        
        try:
            context_manager = ContextManager(state)
            contexts = context_manager.extract_from_step(
                step, state,
                constraints=["PV_ADDRESSES"],
                constraint_mode="hard"
            )
            pv_addresses_context = contexts[registry.context_types.PV_ADDRESSES]
        except ValueError as e:
            raise PVDependencyError(str(e))
        
        streamer.status(f"Reading {len(pv_addresses_context.pvs)} PV values...")
        
        # Get all PV values
        pv_values = {}
        total_pvs = len(pv_addresses_context.pvs)
        
        for i, pv_address in enumerate(pv_addresses_context.pvs):
            streamer.status(f"Reading PV {i+1}/{total_pvs}: {pv_address}")
            
            pv_result = await get_pv_value(pv_address)
            pv_values[pv_address] = PVValue(
                value=pv_result['value'],
                timestamp=datetime.now(),
                units=pv_result['units']
            )
        
        # Create structured result
        result = PVValues(pv_values=pv_values)
        
        streamer.status(f"Successfully retrieved {result.pv_count} PV values")
        
        logger.info(f"PV value retrieval result: {result.pv_count} PVs retrieved")
        
        # Store context using StateManager
        context_updates = StateManager.store_context(
            state, 
            registry.context_types.PV_VALUES, 
            step.get('context_key'), 
            result
        )
        
        return context_updates
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """PV-specific error classification."""
        
        if isinstance(exc, EPICSTimeoutError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"EPICS timeout error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, EPICSChannelAccessError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"EPICS channel access error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, PVNotFoundError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"PV access failed: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, EPICSGatewayError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message=f"EPICS gateway error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, PVDependencyError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"Missing dependency: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        elif isinstance(exc, PVError):
            # Generic PV error
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"PV error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        else:
            # Not a PV-specific error, use default classification
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Unexpected error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Define retry policy for PV value retrieval."""
        return {
            "max_attempts": 3,
            "delay_seconds": 1.0,
            "backoff_factor": 2.0
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create prompt snippet for PV value retrieval."""
        
        # Define structured examples using simplified dict format
        current_values_example = OrchestratorExample(
            step=PlannedStep(
                context_key="read_BPM_pv_values",
                capability="pv_value_retrieval",
                task_objective="Read current horizontal BPM position values for orbit analysis",
                expected_output="PV_VALUES",
                success_criteria="Horizontal BPM PV values successfully retrieved",
                inputs=[{"PV_ADDRESSES": "BPM_pv_addresses"}]
            ),
            scenario_description="Reading horizontal BPM PV values for real-time monitoring",
            notes="Output stored under PV_VALUES context type. Requires PV_ADDRESSES input from previous step."
        )
        
        status_check_example = OrchestratorExample(
            step=PlannedStep(
                context_key="system_status_values",
                capability="pv_value_retrieval",
                task_objective="Check current values of critical power supply and magnet parameters for system health assessment",
                expected_output="PV_VALUES",
                success_criteria="Status values retrieved and within expected ranges",
                inputs=[{"PV_ADDRESSES": "critical_system_pvs"}]
            ),
            scenario_description="Status checking for critical system parameters",
            notes="Output stored under PV_VALUES context type. Used for system health checks and operational status queries"
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent("""
            **When to plan "pv_value_retrieval" steps:**
            - When the user requests current status, readings, or values of specific Process Variables
            - For real-time monitoring of control system parameters
            - When current PV values are needed as inputs for subsequent steps

            **Step Structure:**
            - context_key: Unique identifier for output (e.g., "current_beam_values", "status_readings")
            - inputs: Specify required inputs using simplified format:
              {"PV_ADDRESSES": "context_key_with_pv_addresses"}
            
            **Required Inputs:**
            - PV_ADDRESSES data: typically from a "pv_address_finding" step
            
            **Output: PV_VALUES**
            - Contains: Dictionary mapping PV addresses to their current values and timestamps
            - Available to downstream steps via context system

            **Dependencies and sequencing:**
            1. PV address finding step must precede this step if PV_ADDRESSES data is not present already
            2. PV values can serve as inputs for analysis or visualization steps
            3. Returns current values with timestamps for real-time monitoring
            
            Do NOT plan this for historical PV data; use "get_archiver_data" for historical data.
            
            **NEVER** plan steps that would require making up PV addresses - always ensure addresses are obtained from previous steps.
            """).strip(),
            examples=[current_values_example, status_check_example],
            priority=10
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for PV value retrieval."""
        try:
            return TaskClassifierGuide(
                instructions="Determine if the task requires fetching a Process Variable (PV) value. Look for requests about current values, statuses, or readings of specific PVs.",
                examples=[
                    ClassifierExample(
                        query="Which tools do you have?", 
                        result=False, 
                        reason="This is a question about the AI's capabilities."
                    ),
                    ClassifierExample(
                        query="What is the value of SR01S___BM1_X____AC00?", 
                        result=True, 
                        reason="The query explicitly asks for the value of a specific PV address."
                    ),
                    ClassifierExample(
                        query="Can you launch the orbit display application?", 
                        result=False, 
                        reason="The query is about launching an application, not retrieving a PV value."
                    ),
                    ClassifierExample(
                        query="Read the current for 'SOME:PV:NAME'.", 
                        result=True, 
                        reason="The query asks to read the current value of a specific PV."
                    ),
                    ClassifierExample(
                        query="What's the beam current right now?", 
                        result=True, 
                        reason="The query asks for a current value, which requires PV value retrieval after finding the address."
                    ),
                    ClassifierExample(
                        query="Show me historical beam current data.", 
                        result=False, 
                        reason="This is asking for historical data, not current PV values."
                    )
                ],
                actions_if_true=ClassifierActions()
            )
        except Exception as e:
            logger.warning(f"Failed to create classifier config due to import issues: {e}")
            return None


# Create a singleton instance of the capability
pv_value_retrieval = PVValueRetrievalCapability()
