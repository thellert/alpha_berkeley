"""
Helper utilities for the ALS Assistant Agent.

This module contains miscellaneous utility functions that don't belong
in other specific modules but are used across the agent components.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length with an optional suffix.
    
    Args:
        text: The string to truncate
        max_length: Maximum length of the result
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_dict_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with type hints.
    
    Args:
        dictionary: The dictionary to query
        key: The key to look for
        default: Default value if key not found
        
    Returns:
        The value or default
    """
    return dictionary.get(key, default)


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        The path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format an error message with optional context.
    
    Args:
        error: The exception to format
        context: Optional context string
        
    Returns:
        Formatted error message
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{context}: {error_msg}"
    return error_msg


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present in a dictionary.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        List of missing field names
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    return missing_fields 