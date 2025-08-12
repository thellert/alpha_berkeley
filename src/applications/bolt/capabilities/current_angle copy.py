"""
Current Weather Capability for Hello World Weather Tutorial.
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

logger = get_logger("bolt", "current_angle")
registry = get_registry()

@capability_node
class CurrentAngleCapability(BaseCapability):
    """Motor angle data retrieval capability for current conditions."""
    
    # Required class attributes for registry configuration
    name = "current_angle"
    description = "Get current angle conditions for a location"
    provides = ["CURRENT_ANGLE"]
    requires = []
    
    @staticmethod
    async def execute(state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute complete get angle retrieval workflow."""

        step = StateManager.get_current_step(state)
        streamer = get_streamer("bolt", "current_angle", state)
        
        try:
            streamer.status("Extracting data from query...")
            
            query = StateManager.get_current_task(state).lower()
            
            # Simple location detection
            motor = "DMC01:A"
            
            streamer.status(f"Getting angle for {motor}...")
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
                registry.context_types.CURRENT_ANGLE, 
                step.get("context_key"), 
                context
            )
            
            streamer.status(f"Motor angle retrieved: {angle_data.motor} - {angle_data.angle}°")
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
        """Define retry policy configuration for get angle service operations."""

        return {
            "max_attempts": 3,
            "delay_seconds": 0.5,
            "backoff_factor": 1.5
        }
    
    def _create_orchestrator_guide(self) -> Optional[OrchestratorGuide]:
        """Provide orchestration guidance for intelligent get angle capability planning."""

        example = OrchestratorExample(
            step=PlannedStep(
                context_key="current_angle",
                capability="current_angle",
                task_objective="Get current angle of motor",
                expected_output=registry.context_types.CURRENT_ANGLE,
                success_criteria="Current angle data retrieved with angle and motor position",
                inputs=[]
            ),
            scenario_description="Getting current angle for a motor",
            notes=f"Output stored as {registry.context_types.CURRENT_ANGLE} with angle data."
        )
        
        return OrchestratorGuide(
            instructions=f"""**When to plan "current_angle" steps:**
- When users ask for current angle position
- For real-time angle information requests
- When motor-specific current conditions are needed

**Output: {registry.context_types.CURRENT_ANGLE}**
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
                    query="What is the current angle?",
                    result=True,
                    reason="Request is for historical angle data, not current conditions."
                ),
                ClassifierExample(
                    query="What was the previous angle?",
                    result=False,
                    reason="Request is for historical angle data, not current conditions."
                ),
                ClassifierExample(
                    query="What tools do you have?",
                    result=False,
                    reason="Request is for tool information, not current angle."
                ),
            ],
            actions_if_true=ClassifierActions()
        )