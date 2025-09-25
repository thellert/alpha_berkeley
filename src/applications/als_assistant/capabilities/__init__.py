"""
ALS Assistant Agent Capabilities

This module provides the capability system for the ALS Assistant Agent.
All capabilities are managed through the registry system.
"""

from typing import List
from framework.base import BaseCapability
from framework.registry import get_registry

def get_all_context_types() -> List[str]:
    """Get all available context types."""
    return get_registry().get_all_context_types()

def get_capability_instances() -> List[BaseCapability]:
    """Get all capability instances using the registry."""
    return get_registry().get_all_capabilities()

def get_all_capabilities():
    """Get all capabilities."""
    return get_capability_instances()

# Export what's actually used
__all__ = [
    'get_capability_instances', 
    'get_all_capabilities',
    'get_all_context_types'
] 