"""
PV Finder Service Core Definitions

Centralized core definitions including type definitions, Pydantic models,
dataclasses, response types, and abstract interfaces for the PV finder service.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass, field


# ==============================================================================
# RESPONSE MODELS
# ==============================================================================

class QuerySplitterOutput(BaseModel):
    """Output from the query splitter agent."""
    queries: List[str] = Field(..., description="A list of queries that are atomic and can be answered by the pv_query_agent.")


class KeywordExtractorOutput(BaseModel):
    """Output from the keyword extractor agent."""
    keywords: List[str] = Field(..., description="A list of keywords extracted from the user query.")
    systems: List[str] = Field(..., description="A list of systems relevant to the user query.")


class PVQueryOutput(BaseModel):
    """Output from the PV query agent."""
    pvs: List[str] = Field(..., description="A list of PVs that are relevant to the user query.")
    description: str = Field(..., description="A description of the PVs that are relevant to the user query.")


class PVSearchResult(BaseModel):
    """
    Service layer response from PV finder operations.
    
    This is a simple data transfer object used by the pv_finder service layer.
    It represents the raw search results before framework context processing.
    
    This class maintains architectural separation from the framework's PVAddresses
    context class, enabling service layer independence and clean testing boundaries.
    """
    pvs: List[str] = Field(..., description="A list of PVs that are relevant to the user query.")
    description: str = Field(..., description="A description of the PVs that are relevant to the user query.")


# ==============================================================================
# AGENT DEPENDENCIES
# ==============================================================================

@dataclass(init=False)
class QueryAgentDeps:
    """Dependencies for the PV query agent."""
    initial_query: str
    systems: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    def __init__(self, 
                 initial_query: str,
                 systems: Optional[List[str]] = None, 
                 keywords: Optional[List[str]] = None):
        self.initial_query = initial_query
        self.systems = systems if systems is not None else []
        self.keywords = keywords if keywords is not None else []


# ==============================================================================
# GRAPH STATE
# ==============================================================================

class PVFinderGraphState(BaseModel):
    """State object for the PV finder graph workflow."""
    model_config = {"arbitrary_types_allowed": True}
    
    initial_query: str
    split_queries: Optional[List[str]] = None
    pv_results: Optional[List[PVQueryOutput]] = None
    
    # Langfuse observability fields
    langfuse_trace_id: str | None = None
    langfuse_parent_span_id: str | None = None
    langfuse_user_id: str | None = None
    langfuse_session_id: str | None = None
    
    # Status emitter for real-time updates
    status_emitter: Optional[Callable[[Dict[str, Any]], None]] = None


# ==============================================================================
# ABSTRACT INTERFACES
# ==============================================================================

class IPVFinderService(ABC):
    """Main service interface for PV finding operations."""
    
    @abstractmethod
    async def find_pvs(self, query: str) -> PVSearchResult:
        """Find PVs based on natural language query."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health and dependencies."""
        pass


# ==============================================================================
# EXCEPTIONS
# ==============================================================================

class PVFinderError(Exception):
    """Base exception for all PV finder errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class ValidationError(PVFinderError):
    """Raised when input validation fails."""
    pass


class SystemNotFoundError(PVFinderError):
    """Raised when a requested system is not found."""
    
    def __init__(self, system: str, available_systems: List[str]):
        message = f"System '{system}' not found"
        details = {
            "requested_system": system,
            "available_systems": available_systems
        }
        super().__init__(message, details)


class FamilyNotFoundError(PVFinderError):
    """Raised when a requested family is not found in a system."""
    
    def __init__(self, family: str, system: str, available_families: List[str]):
        message = f"Family '{family}' not found in system '{system}'"
        details = {
            "requested_family": family,
            "system": system,
            "available_families": available_families
        }
        super().__init__(message, details)


class FieldNotFoundError(PVFinderError):
    """Raised when a requested field is not found in a family."""
    
    def __init__(self, field: str, family: str, system: str, available_fields: List[str]):
        message = f"Field '{field}' not found in '{system}:{family}'"
        details = {
            "requested_field": field,
            "family": family,
            "system": system,
            "available_fields": available_fields
        }
        super().__init__(message, details)


class ServiceUnavailableError(PVFinderError):
    """Raised when the service or its dependencies are unavailable."""
    pass


def handle_pv_finder_error(error: Exception) -> PVFinderError:
    """
    Convert various exceptions to appropriate PVFinderError instances.
    
    Args:
        error: The original exception
        
    Returns:
        An appropriate PVFinderError instance
    """
    if isinstance(error, PVFinderError):
        return error
    
    # Convert common exceptions
    if isinstance(error, ValueError):
        return ValidationError(str(error))
    elif isinstance(error, KeyError):
        return ValidationError(f"Missing required field: {str(error)}")
    elif isinstance(error, ConnectionError):
        return ServiceUnavailableError(f"Connection failed: {str(error)}")
    elif isinstance(error, TimeoutError):
        return ServiceUnavailableError(f"Operation timed out: {str(error)}")
    else:
        # Generic fallback
        return PVFinderError(f"Unexpected error: {str(error)}", {"original_type": type(error).__name__}) 