"""
Pydantic-based Context Base Classes

Clean, production-ready context system using Pydantic for automatic serialization,
validation, and type safety. Eliminates complex custom serialization logic.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CapabilityContext(BaseModel):
    """
    Base class for all capability context objects. Uses Pydantic for automatic
    serialization/deserialization and type validation.
    
    This class provides:
    - Automatic JSON serialization via .model_dump()
    - Automatic deserialization via .model_validate()
    - Type validation on field assignment
    - Consistent interface for all context types
    """
    
    model_config = {
        # Enforce JSON-compatible types only (no complex Python objects)
        "arbitrary_types_allowed": False,
        
        # Allow field names for compatibility
        "populate_by_name": True,
        
        # Use enum values for serialization
        "use_enum_values": True,
        
        # JSON encoders for specific types (Pydantic v2 syntax)
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        }
    }

    # Class constants - using ClassVar to exclude from model fields
    CONTEXT_TYPE: ClassVar[str] = ""
    CONTEXT_CATEGORY: ClassVar[str] = ""

    @property
    def context_type(self) -> str:
        """Return the context type identifier"""
        return self.CONTEXT_TYPE

    @abstractmethod
    def get_access_details(self, key: str) -> dict:
        """
        Get detailed access information for this context data.
        
        Args:
            key: The context key this data is stored under
            
        Returns:
            Dictionary with access details including summary, capabilities, etc.
        """
        pass

    @abstractmethod
    def get_human_summary(self, key: str) -> dict:
        """
        Get a human-readable summary of this context data.
        
        Args:
            key: The context key this data is stored under
            
        Returns:
            Dictionary with human-readable information about the context
        """
        pass 