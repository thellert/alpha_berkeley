"""
PV Finder Service

A service for finding EPICS process variables (PVs) at the Advanced Light Source
using natural language queries and intelligent keyword extraction.

Public API:
    - PVFinderService class for dependency injection
"""

from .service import (
    PVFinderService,
)

from .core import (
    PVSearchResult,
    PVQueryOutput,
    KeywordExtractorOutput,
    QuerySplitterOutput,
    IPVFinderService,
    PVFinderError,
    ValidationError,
    SystemNotFoundError,
    FamilyNotFoundError,
    FieldNotFoundError,
    ServiceUnavailableError
)

# Version information
__version__ = "2.0.0"
__author__ = "ALS Controls Team"

# Public API
__all__ = [
    # Service classes
    "PVFinderService",
    
    # Response types
    "PVSearchResult",
    "PVQueryOutput",
    "KeywordExtractorOutput", 
    "QuerySplitterOutput",
    
    # Exceptions
    "PVFinderError",
    "ValidationError",
    "SystemNotFoundError",
    "FamilyNotFoundError",
    "FieldNotFoundError",
    "ServiceUnavailableError",
    
    # Interfaces (for DI and testing)
    "IPVFinderService",
    
    # Metadata
    "__version__",
    "__author__"
] 