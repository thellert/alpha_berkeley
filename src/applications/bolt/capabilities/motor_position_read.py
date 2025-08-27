"""
Motor Position Read Capability for BOLT Beamline System.

This capability reads the current angular position of the sample rotation motor
in the BOLT imaging beamline. It's essential for experimental setup,
status verification, and scan planning.
"""

from typing import Dict, Any, Optional

from framework.base import (
    BaseCapability, capability_node,
    OrchestratorGuide, OrchestratorExample, PlannedStep,
    ClassifierActions, ClassifierExample, TaskClassifierGuide
)
from framework.base.errors import ErrorClassification, ErrorSeverity
from framework.registry import get_registry
from framework.state import AgentState, StateManager
from configs.logger import get_logger
from configs.streaming import get_streamer

from applications.bolt.context_classes import CurrentAngleContext
from applications.bolt.bolt_api import bolt_api

logger = get_logger("bolt", "motor_position_read")
registry = get_registry()

@capability_node
class MotorPositionReadCapability(BaseCapability):
    """Read current angular position of sample rotation motor in BOLT beamline."""
    
    # Required class attributes for registry configuration
    name = "motor_position_read"
    description = "Read current angular position of sample rotation motor"
    provides = ["MOTOR_POSITION"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute motor position reading workflow."""

        step = StateManager.get_current_step(state)
        streamer = get_streamer("bolt", "motor_position_read", state)
        
        try:
            streamer.status("Reading motor position...")
            
            # BOLT beamline sample rotation motor
            motor = "DMC01:A"
            
            streamer.status(f"Reading position from {motor}...")
            angle_data = bolt_api.get_current_angle(motor)
            
            # Create context object
            context = CurrentAngleContext(
                motor=angle_data.motor,
                angle=angle_data.angle,
                condition=angle_data.condition,
                timestamp=angle_data.timestamp
            )
            
            # Store context in framework state
            context_updates = StateManager.store_context(
                state, 
                registry.context_types.MOTOR_POSITION, 
                step.get("context_key"), 
                context
            )
            
            streamer.status(f"Motor position read: {angle_data.motor} at {angle_data.angle}°")
            return context_updates
            
        except Exception as e:
            logger.error(f"Motor position read error: {e}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Classify motor position read errors for intelligent retry coordination."""

        if isinstance(exc, (ConnectionError, TimeoutError)):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                metadata={
                    "user_message": "Motor communication timeout, retrying...",
                    "technical_details": str(exc)
                }
            )
        
        return ErrorClassification(
            severity=ErrorSeverity.CRITICAL,
            metadata={
                "user_message": f"Motor position read error: {str(exc)}",
                "technical_details": f"Error: {type(exc).__name__}"
            }
        )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Define retry policy configuration for motor position read operations."""

        return {
            "max_attempts": 3,
            "delay_seconds": 0.5,
            "backoff_factor": 1.5
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Provide orchestration guidance for motor position reading in BOLT beamline."""

        example = OrchestratorExample(
            step=PlannedStep(
                context_key="current_motor_position",
                capability="motor_position_read",
                task_objective="Read current angular position of sample rotation motor",
                expected_output=registry.context_types.MOTOR_POSITION, 
                success_criteria="Current motor angle retrieved in degrees from Tiled data source",
                inputs=[]
            ),
            scenario_description="Reading current sample rotation motor position for status check or before movement",
            notes=f"Data retrieved from {registry.context_types.MOTOR_POSITION}, generated from Tiled. Use before motor movements or for status checks."
        )
        
        return OrchestratorGuide(
            instructions=f"""**When to plan "motor_position_read" steps:**
- User asks "what is the current angle/position?"
- Before planning motor movements (to know starting position)
- For experimental setup and status verification
- When troubleshooting sample positioning issues

**BOLT Beamline Context:**
- Essential for photogrammetry scan preparation
- Required before motor position changes
- Used for sample alignment verification

**Output:
- Contains: motor_id, angle_degrees, timestamp  
- Available for motor movement planning and status reporting
- Live data acquired via queue server execution and extracted from Tiled metadata

**Typical Workflow Position:**
- Often first step before motor movements
- Used for status reporting to user
- Prerequisites for photogrammetry scan planning""",
            examples=[example],
            order=1  # High priority since often needed first
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Provide task classification guidance for motor position reading."""
        return TaskClassifierGuide(
            instructions="""Determine if the user wants to READ/CHECK the current angular position of the sample rotation motor in the BOLT beamline system.

BOLT CONTEXT: This is a beamline where samples are rotated for photogrammetry experiments. Users may ask about:
- Sample orientation/rotation angle
- Motor position before movements  
- Current angle for scan planning
- Status checks of sample positioning""",
            examples=[
                ClassifierExample(
                    query="What is the current motor angle?",
                    result=True,
                    reason="User explicitly asks for current motor position information."
                ),
                ClassifierExample(
                    query="Check the sample rotation position",
                    result=True,
                    reason="User wants to check/read the current sample orientation."
                ),
                ClassifierExample(
                    query="Where is the motor positioned right now?",
                    result=True,
                    reason="Request for current motor position status."
                ),
                ClassifierExample(
                    query="What's the current rotation angle of the sample?",
                    result=True,
                    reason="Direct request for current sample rotation position."
                ),
                ClassifierExample(
                    query="Check sample position before starting the scan",
                    result=True,
                    reason="User wants motor position status before experimental procedure."
                ),
                ClassifierExample(
                    query="Move the motor to 45 degrees",
                    result=False,
                    reason="This is a movement command, not a position read request."
                ),
                ClassifierExample(
                    query="Start a photogrammetry scan",
                    result=False,
                    reason="This is a scan execution request, not motor position reading."
                ),
                ClassifierExample(
                    query="Take an image",
                    result=False,
                    reason="This is an imaging request, not motor position reading."
                ),
                ClassifierExample(
                    query="What was the previous motor position?",
                    result=False,
                    reason="Request is for historical position data, not current status."
                ),
                ClassifierExample(
                    query="What tools do you have?",
                    result=False,
                    reason="Request is for tool information, not motor position."
                ),
            ],
            actions_if_true=ClassifierActions()
        )