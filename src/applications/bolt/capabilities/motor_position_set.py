"""
Motor Position Set Capability for BOLT Beamline System.

This capability moves the sample rotation motor to a specified angular position
in the BOLT imaging beamline. It's essential for sample positioning,
experimental setup, and scan preparation.
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

from applications.bolt.context_classes import CurrentMoveMotorContext
from applications.bolt.bolt_api import bolt_api

logger = get_logger("bolt", "motor_position_set")
registry = get_registry()

@capability_node
class MotorPositionSetCapability(BaseCapability):
    """Move sample rotation motor to specified angular position in BOLT beamline."""
    
    # Required class attributes for registry configuration
    name = "motor_position_set"
    description = "Move sample rotation motor to specified angular position"
    provides = ["MOTOR_MOVEMENT"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute motor position movement workflow."""

        step = StateManager.get_current_step(state)
        streamer = get_streamer("bolt", "motor_position_set", state)
        
        try:
            streamer.status("Parsing target position from query...")
            
            query = StateManager.get_current_task(state).lower()
            import re
            
            # Extract numerical value from query (looking for angles/positions)
            # Use findall to get all numbers, then take the most likely angle value
            numbers = re.findall(r"-?\d+(?:\.\d+)?", query)
            if not numbers:
                raise ValueError("No target angle specified in query")
            
            # Take the last number found (most likely to be the target angle)
            # or the largest number if multiple found (angles are typically larger than motor IDs)
            if len(numbers) == 1:
                target_angle = numbers[0]
            else:
                # If multiple numbers, take the largest one (likely the angle, not motor ID)
                target_angle = max(numbers, key=lambda x: abs(float(x)))

            motor = "DMC01:A"
            
            streamer.status(f"Moving {motor} to {target_angle}°...")
            
            move_data = bolt_api.move_motor(motor, target_angle)

            # Create context object
            context = CurrentMoveMotorContext(
                motor=move_data.motor,
                angle=move_data.angle,
                condition=move_data.condition,
                timestamp=move_data.timestamp
            )
            
            # Store context in framework state
            context_updates = StateManager.store_context(
                state, 
                registry.context_types.MOTOR_MOVEMENT, 
                step.get("context_key"), 
                context
            )
            
            streamer.status(f"Motor positioned: {move_data.motor} at {move_data.angle}°")
            return context_updates
            
        except Exception as e:
            logger.error(f"Motor movement error: {e}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Classify motor movement errors for intelligent retry coordination."""

        if isinstance(exc, (ConnectionError, TimeoutError)):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                metadata={
                    "user_message": "Motor communication timeout, retrying...",
                    "technical_details": str(exc)
                }
            )
        elif isinstance(exc, ValueError):
            return ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                metadata={
                    "user_message": f"Invalid motor position: {str(exc)}",
                    "technical_details": str(exc)
                }
            )
        
        return ErrorClassification(
            severity=ErrorSeverity.CRITICAL,
            metadata={
                "user_message": f"Motor movement error: {str(exc)}",
                "technical_details": f"Error: {type(exc).__name__}"
            }
        )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Define retry policy configuration for motor movement operations."""
        return {
            "max_attempts": 3,
            "delay_seconds": 0.5,
            "backoff_factor": 1.5
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Provide orchestration guidance for motor position setting in BOLT beamline."""
        
        example = OrchestratorExample(
            step=PlannedStep(
                context_key="motor_positioning",
                capability="motor_position_set",
                task_objective="Move sample rotation motor to specified angular position",
                expected_output=registry.context_types.MOTOR_MOVEMENT,
                success_criteria="Motor successfully positioned at target angle",
                inputs=[]
            ),
            scenario_description="Moving sample rotation motor to desired position for experimental setup",
            notes=f"Output stored as {registry.context_types.MOTOR_MOVEMENT}. Use for sample positioning and experimental setup."
        )
        
        return OrchestratorGuide(
            instructions=f"""**When to plan "motor_position_set" steps:**
- User asks to move motor to specific angle (e.g., "move to 45 degrees")
- User requests relative movement (e.g., "rotate by 30 degrees")
- For sample positioning before scans or measurements
- When setting up experimental configurations

**BOLT Beamline Context:**
- Controls sample rotation motor for photogrammetry
- Essential for sample alignment and positioning
- Required before photogrammetry scans at specific angles

**Movement Types:**
- Absolute: "move to 45 degrees" (sets absolute position)
- Relative: "rotate by 30 degrees" (moves relative to current)

**Output: {registry.context_types.MOTOR_MOVEMENT}**
- Contains: motor_id, final_angle, movement_type, timestamp
- Available for position confirmation and further movements

**Typical Workflow Position:**
- After reading current position
- Before imaging or scanning operations
- For experimental setup and sample alignment""",
            examples=[example],
            order=2  # After position read, before imaging
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Provide task classification guidance for motor position setting."""
        return TaskClassifierGuide(
            instructions="""Determine if the user wants to MOVE/SET the angular position of the sample rotation motor in the BOLT beamline system.

BOLT CONTEXT: This is an beamline testbed where samples are rotated for photogrammetry experiments. Users may request:
- Moving motor to specific angles
- Relative motor movements  
- Sample positioning for experiments
- Motor adjustments for alignment""",
            examples=[
                ClassifierExample(
                    query="Move motor to 45 degrees",
                    result=True,
                    reason="Direct command to move motor to specific angle."
                ),
                ClassifierExample(
                    query="Rotate the sample by 30 degrees",
                    result=True,
                    reason="Request for relative motor movement."
                ),
                ClassifierExample(
                    query="Set motor position to 90",
                    result=True,
                    reason="Command to set motor to specific position."
                ),
                ClassifierExample(
                    query="Position the sample at 0 degrees",
                    result=True,
                    reason="Request to position sample at specific angle."
                ),
                ClassifierExample(
                    query="Turn the motor clockwise 15 degrees",
                    result=True,
                    reason="Relative motor movement command."
                ),
                ClassifierExample(
                    query="Adjust sample orientation to 60 degrees",
                    result=True,
                    reason="Request to adjust motor position for sample orientation."
                ),
                ClassifierExample(
                    query="What is the current motor angle?",
                    result=False,
                    reason="This is a position reading request, not a movement command."
                ),
                ClassifierExample(
                    query="Start a photogrammetry scan",
                    result=False,
                    reason="This is a scan execution request, not motor positioning."
                ),
                ClassifierExample(
                    query="Take an image",
                    result=False,
                    reason="This is an imaging request, not motor movement."
                ),
                ClassifierExample(
                    query="Check sample position",
                    result=False,
                    reason="This is a status check, not a movement command."
                ),
                ClassifierExample(
                    query="What tools do you have?",
                    result=False,
                    reason="Request is for tool information, not motor control."
                ),
            ],
            actions_if_true=ClassifierActions()
        )