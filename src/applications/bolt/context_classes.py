"""
Hello World Weather Context Classes.
"""

from datetime import datetime
from typing import Dict, Any, Optional, ClassVar
from pydantic import Field
from framework.context.base import CapabilityContext

class CurrentAngleContext(CapabilityContext):
    """Structured context for current weather condition data.
    """

    CONTEXT_TYPE: ClassVar[str] = "CURRENT_ANGLE"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
    
    # Basic weather data
    motor: str = Field(description="Motor name")
    angle: float = Field(description="Angle in degrees")
    condition: str = Field(description="Curent get_angle condition description")
    timestamp: datetime = Field(description="Timestamp of current angle data")
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating.
        """
        key_ref = key_name if key_name else "key_name"
        
        return {
            "motor": self.motor,
            "current_temp": f"{self.angle}°",
            "conditions": self.condition,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.angle, context.{self.CONTEXT_TYPE}.{key_ref}.condition",
            "example_usage": f"The angle of motor {self.motor} is {{context.{self.CONTEXT_TYPE}.{key_ref}.angle}}°",
            "available_fields": ["motor", "angle", "timestamp"]
        }
    
    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of weather context data.
        """
        return {
            "summary": f"Motor angle of {self.motor} on {self.timestamp.strftime('%Y-%m-%d')} at {self.timestamp.strftime('%I-%M')}: {self.angle}°, Motor Position: {self.angle / 2.8125}"
        }
    
class CurrentMoveMotorContext(CapabilityContext):
    """Structured context for current weather condition data.
    """

    CONTEXT_TYPE: ClassVar[str] = "MOVE_MOTOR"
    CONTEXT_CATEGORY: ClassVar[str] = "LIVE_DATA"
    
    # Basic weather data
    motor: str = Field(description="Motor name")
    angle: float = Field(description="Angle in degrees")
    condition: str = Field(description="Curent get_angle condition description")
    timestamp: datetime = Field(description="Timestamp of current angle data")
    
    def get_access_details(self, key_name: Optional[str] = None) -> Dict[str, Any]:
        """Provide structured access information for LLM consumption and templating."""

        key_ref = key_name if key_name else "key_name"
        
        return {
            "motor": self.motor,
            "current_temp": f"{self.angle}°",
            "conditions": self.condition,
            "access_pattern": f"context.{self.CONTEXT_TYPE}.{key_ref}.angle, context.{self.CONTEXT_TYPE}.{key_ref}.condition",
            "example_usage": f"Moved motor {self.motor} to {{context.{self.CONTEXT_TYPE}.{key_ref}.angle}}°",
            "available_fields": ["motor", "angle", "timestamp"]
        }
    
    def get_human_summary(self, key: str) -> dict:
        """Generate human-readable summary of weather context data.
        """
        return {
            "summary": f"Moved motor {self.motor} at {self.timestamp.strftime('%Y-%m-%d')} and {self.timestamp.strftime('%I-%M')} to: {self.angle}°, Motor Position: {self.angle / 2.8125}"
        }
    