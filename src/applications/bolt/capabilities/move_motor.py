"""
Move motor capability
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

logger = get_logger("bolt", "move_motor")
registry = get_registry()

@capability_node
class CurrentMoveMotorCapability(BaseCapability):
    """Motor angle data retrieval capability for current conditions."""
    
    # Required class attributes for registry configuration
    name = "move_motor"
    description = "Move motor by certain amount"
    provides = ["MOVE_MOTOR"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute complete move motor workflow. """

        step = StateManager.get_current_step(state)
        streamer = get_streamer("bolt", "move_motor", state)

        query = StateManager.get_current_task(state).lower()
        
        try:
            streamer.status("Extracting motor from query...")
            
            query = StateManager.get_current_task(state).lower()
            import re
            match = re.search(r"-?\d+", query)

            by_flag = 0
            if "by" in query:
                by_flag = 1
            # Simple location detection
            motor = "DMC01:A"
            
            streamer.status(f"Moving {motor}...")
            move_data = bolt_api.move_motor(motor, str(match.group()), by_flag)  #NEXT


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
                registry.context_types.MOVE_MOTOR, 
                step.get("context_key"), 
                context
            )
            
            streamer.status(f"Motor moved: {move_data.motor} to {move_data.angle}°")
            return context_updates
            
        except Exception as e:
            logger.error(f"Weather retrieval error: {e}")
            raise
    
    @staticmethod
    def classify_error(exc: Exception, context: dict) -> ErrorClassification:
        """Classify get angle service errors for intelligent retry coordination."""

        if isinstance(exc, (ConnectionError, TimeoutError)):
            return ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message="Motor service timeout, retrying...",
                technical_details=str(exc)
            )
        
        return ErrorClassification(
            severity=ErrorSeverity.CRITICAL,
            user_message=f"Motor service error: {str(exc)}",
            technical_details=f"Error: {type(exc).__name__}"
        )
    
    @staticmethod
    def get_retry_policy() -> Dict[str, Any]:
        """Define retry policy configuration for weather service operations.
        """
        return {
            "max_attempts": 3,
            "delay_seconds": 0.5,
            "backoff_factor": 1.5
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Provide orchestration guidance for intelligent weather capability planning.
        """
        example = OrchestratorExample(
            step=PlannedStep(
                context_key="current_angle",
                capability="current_angle",
                task_objective="Get current angle of motor",
                expected_output=registry.context_types.MOVE_MOTOR,
                success_criteria="Current angle data retrieved with angle and motor position",
                inputs=[]
            ),
            scenario_description="Getting current weather for a location",
            notes=f"Output stored as {registry.context_types.MOVE_MOTOR} with move motor data."
        )
        
        return OrchestratorGuide(
            instructions=f"""**When to plan "move_motor" steps:**
- When users ask to move a motor to a position/angle
- For move motor requests
- When motor-specific current conditions are needed

**Output: {registry.context_types.MOVE_MOTOR}**
- Contains: motor, angle, and timestamp
- Available for immediate display or further analysis

**Motor Support:**
- Supports: DMC01:A
- Defaults to DMC01:A if location not specified""",
            examples=[example],
            order=5
        )
    
    def _create_classifier_guide(self) -> Optional[TaskClassifierGuide]:
        """Provide task classification guidance for intelligent capability selection."""
        return TaskClassifierGuide(
            instructions="Determine if the task requires current angle information",
            examples=[
                ClassifierExample(
                    query="Move motor to 45 degrees",
                    result=True,
                    reason="Request is to move motor to some angle/position"
                ),
                ClassifierExample(
                    query="What was the preivous motor position",
                    result=False,
                    reason="Request is for historical motor data, not current conditions."
                ),
                ClassifierExample(
                    query="What tools do you have?",
                    result=False,
                    reason="Request is for tool information, not current angle."
                ),
            ],
            actions_if_true=ClassifierActions()
        )