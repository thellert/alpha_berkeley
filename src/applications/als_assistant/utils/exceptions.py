"""
ALS Assistant Agent - Custom Exceptions

This module contains all custom exception classes for the ALS Assistant Agent system.
"""

from typing import Dict


class ReclassificationRequired(Exception):
    """Exception to trigger complete reclassification and graph rebuild."""
    
    def __init__(self, reason: str, context: Dict, current_task: str):
        self.reason = reason
        self.context = context  
        self.current_task = current_task
        super().__init__(f"Reclassification required: {reason}") 