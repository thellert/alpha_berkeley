"""
Live Monitoring Capability - Simplified Version

This capability launches the Phoebus Data Browser for real-time monitoring of Process Variables.
The primary purpose is LIVE monitoring of current machine status and real-time data streams.

SIMPLIFIED APPROACH: No context storage - just generate launch URI and return to user.
"""

import logging
import textwrap
from typing import Dict, Any, Optional
import asyncio

# Framework imports
from framework.base.decorators import capability_node
from framework.base.capability import BaseCapability
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.base.examples import (
    OrchestratorGuide, OrchestratorExample,
    ClassifierExample, TaskClassifierGuide, ClassifierActions
)
from framework.base.planning import PlannedStep
from framework.state import AgentState, StateManager
from framework.registry import get_registry
from framework.context.context_manager import ContextManager

# Application imports
from applications.als_assistant.services.launcher.service import LauncherService
from applications.als_assistant.services.launcher.models import LauncherServiceRequest

# Configuration and logging
from configs.config import get_full_configuration
from configs.streaming import get_streamer
from configs.logger import get_logger

logger = get_logger("als_assistant", "live_monitoring")

registry = get_registry()

# === Capability-Specific Error Classes ===

class LiveMonitoringError(Exception):
    """Base class for all live monitoring capability errors."""
    pass

class LauncherServiceError(LiveMonitoringError):
    """Raised when the launcher service fails."""
    pass

class PVDependencyError(LiveMonitoringError):
    """Raised when required PV addresses are not available."""
    pass

# === Core Implementation ===

@capability_node
class LiveMonitoringCapability(BaseCapability):
    """Live monitoring capability for launching Phoebus Data Browser for real-time PV monitoring."""
    
    name = "live_monitoring"
    description = "Launch Phoebus Data Browser for real-time monitoring of Process Variables"
    provides = []
    requires = ["PV_ADDRESSES"]
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute live monitoring by launching Phoebus Data Browser."""
        
        # Extract current step from execution plan
        step = StateManager.get_current_step(state)
        
        # Define streaming helper for step awareness
        streamer = get_streamer("als_assistant", "live_monitoring", state)
        streamer.status("Preparing live monitoring setup...")
        
        logger.info(f"Starting live monitoring for task: {step.get('task_objective', 'unknown')}")
        
        try:
            # 1. Extract required PV addresses context
            context_manager = ContextManager(state)
            contexts = context_manager.extract_from_step(
                step, state,
                constraints=[registry.context_types.PV_ADDRESSES],
                constraint_mode="hard"
            )
            pv_addresses_context = contexts[registry.context_types.PV_ADDRESSES]
            
            if not pv_addresses_context.pvs or len(pv_addresses_context.pvs) == 0:
                raise PVDependencyError(
                    "No PV addresses available for live monitoring. The PV address finding step "
                    "may have failed to locate suitable PVs for monitoring."
                )
            
            streamer.status(f"Setting up live monitoring for {len(pv_addresses_context.pvs)} PVs...")
            logger.info(f"Configuring live monitoring for PVs: {pv_addresses_context.pvs}")
            
            # 2. Prepare launcher service request
            task_objective = step.get('task_objective', 'Launch live monitoring for selected PVs')
            runtime_config = get_full_configuration()
            
            launcher_request = LauncherServiceRequest(
                query=task_objective,
                pv_addresses=pv_addresses_context.pvs,
                runtime_config=runtime_config
            )
            
            streamer.status("Generating Data Browser configuration...")
            
            # 3. Execute launcher service
            launcher_service = LauncherService()
            service_result = await launcher_service.execute(launcher_request)
            
            if not service_result.success:
                raise LauncherServiceError(
                    f"Launcher service failed: {service_result.error_message}"
                )
            
            streamer.status("Data Browser launch configuration ready")
            logger.success(f"Live monitoring setup complete: {service_result.command_name}")
            
            # 4. Register command in centralized UI registry
            command_updates = StateManager.register_command(
                state=state,
                capability="live_monitoring",
                launch_uri=service_result.launch_uri,
                display_name=service_result.command_name or "Launch Data Browser",
                command_type="data_browser",
                metadata={
                    "pv_count": len(pv_addresses_context.pvs),
                    "pvs_monitored": pv_addresses_context.pvs,
                    "monitoring_type": "live_data_browser",
                    "task_objective": task_objective,
                    "description": service_result.command_description or "Launch Phoebus Data Browser for live monitoring"
                }
            )
            
            streamer.status("Live monitoring command registered successfully")
            logger.info(f"Registered live monitoring command: {service_result.command_name or 'Launch Data Browser'}")
            
            return command_updates
            
        except Exception as e:
            logger.error(f"Live monitoring setup failed: {e}")
            streamer.error(f"Live monitoring setup failed: {str(e)}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Live monitoring error classification."""
        
        if isinstance(exc, PVDependencyError):
            return ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message=f"Missing PV addresses: {str(exc)}",
                metadata={
                    "technical_details": str(exc),
                    "replanning_reason": f"PV addresses not available: {exc}",
                    "suggestions": [
                        "Ensure PV addresses have been found using the pv_address_finding capability",
                        "Check that the PV address finding step completed successfully",
                        "Verify that the requested PVs exist in the system"
                    ]
                }
            )
        elif isinstance(exc, LauncherServiceError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Launcher service error: {str(exc)}",
                metadata={
                    "technical_details": str(exc),
                    "suggestions": [
                        "Verify Phoebus executable is properly configured",
                        "Check if the launcher service is accessible",
                        "Ensure proper network connectivity for application launching"
                    ]
                }
            )
        elif isinstance(exc, LiveMonitoringError):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Live monitoring error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
        else:
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message=f"Unexpected live monitoring error: {str(exc)}",
                metadata={"technical_details": str(exc)}
            )
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Create orchestrator guide for simplified live monitoring."""
        
        # Define structured examples - no context output needed
        real_time_monitoring_example = OrchestratorExample(
            step=PlannedStep(
                context_key="beam_current_live_monitor",  # Still need unique key for step tracking
                capability="live_monitoring",
                task_objective="Launch live monitoring of beam current for real-time operator display",
                expected_output="Direct response with launch URI",  # No context type
                success_criteria="Data Browser launch URI generated successfully",
                inputs=[{registry.context_types.PV_ADDRESSES: "beam_current_pvs"}]
            ),
            scenario_description="Real-time monitoring of machine parameters",
            notes="Returns launch URI directly in response."
        )
        
        return OrchestratorGuide(
            instructions=textwrap.dedent(f"""
                **When to plan "live_monitoring" steps:**
                - User requests real-time monitoring, live displays, or continuous observation of PV values
                - User wants to "monitor", "watch", "observe", or "track" current machine parameters
                - User asks for operator displays, dashboards, or live status screens
                - User requests Data Browser or Phoebus interface for live data

                **CRITICAL DISTINCTION - Live Monitoring vs Historical Analysis:**
                - **Use live_monitoring for**: Real-time displays, current status, live updating plots, operator interfaces
                - **Use {registry.capability_names.GET_ARCHIVER_DATA} + {registry.capability_names.DATA_ANALYSIS} for**: Historical trends, past data analysis, statistical studies

                **Step Structure:**
                - context_key: Unique identifier for step tracking
                - inputs: Specify required inputs using simplified format:
                  {{{registry.context_types.PV_ADDRESSES}: "context_key_with_pv_addresses"}}
                
                **Required Inputs:**
                - PV_ADDRESSES data: typically from a "{registry.capability_names.PV_ADDRESS_FINDING}" step
                
                **Output: Launchable Command**
                - Registers a command that users can click to launch external monitoring applications
                - No persistent context data created - this is a terminal UI operation
                - Command provides immediate access to live monitoring tools

                **Dependencies and sequencing:**
                1. "{registry.capability_names.PV_ADDRESS_FINDING}" step must precede this step to provide PV_ADDRESSES data
                2. This is typically a final step in the execution plan for monitoring workflows
                3. Users launch the monitoring application outside the agent system
                
                **NEVER** plan this for data analysis or historical studies - use {registry.capability_names.GET_ARCHIVER_DATA} and {registry.capability_names.DATA_ANALYSIS} capabilities instead.
                """),
            examples=[real_time_monitoring_example],
            priority=25
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Create classifier for live monitoring capability."""
        return TaskClassifierGuide(
            instructions="Determine if the user query requires real-time monitoring or live display of control system parameters. Focus on requests for current, live, or continuously updating information rather than historical analysis.",
            examples=[
                ClassifierExample(
                    query="Monitor the beam current in real time",
                    result=True,
                    reason="Explicitly requests real-time monitoring of beam current."
                ),
                ClassifierExample(
                    query="Analyze the beam current data from yesterday",
                    result=False,
                    reason="This requests historical data analysis, not live monitoring."
                ),
                ClassifierExample(
                    query="Open Phoebus to watch the BPM readings",
                    result=True,
                    reason="Requests launching Phoebus for live monitoring of BPM readings."
                ),
                ClassifierExample(
                    query="Show me a dashboard of the current machine status",
                    result=True,
                    reason="Requests a live dashboard display of current machine parameters."
                ),
                ClassifierExample(
                    query="Calculate the statistics for power supply voltages over the last week",
                    result=False,
                    reason="This requests statistical analysis of historical data, not live monitoring."
                ),
            ],
            actions_if_true=ClassifierActions()
        )
