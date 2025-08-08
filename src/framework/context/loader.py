"""
Context Loading Utilities

Utilities for loading context data from various sources (JSON files, etc.)
for use with the ContextManager system.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .context_manager import ContextManager

logger = logging.getLogger(__name__)


def load_context(context_file: str = "context.json") -> Optional[ContextManager]:
    """
    Load agent execution context from a JSON file in the current directory.
    
    This function provides the same interface as the old load_context function
    but uses the new Pydantic-based ContextManager system. It maintains exact
    compatibility with existing access patterns.
    
    Args:
        context_file: Name of the context file (default: "context.json")
        
    Returns:
        ContextManager instance with dot notation access, or None if loading fails
        
    Usage:
        >>> from framework.context import load_context
        >>> context = load_context()
        >>> data = context.ARCHIVER_DATA.beam_current_historical_data
        >>> pv_values = context.PV_ADDRESSES.step_1.pv_values
    """
    try:
        # Look for context file in current working directory
        context_path = Path.cwd() / context_file
        
        if not context_path.exists():
            logger.warning(f"Context file not found: {context_path}")
            print(f"⚠️  Context file not found: {context_path}")
            print("Make sure you're running this from a directory with a context.json file")
            return None
        
        # Load JSON data
        with open(context_path, 'r', encoding='utf-8') as f:
            context_data = json.load(f)
        
        # Create ContextManager with the loaded data
        # The data structure should be: {context_type: {context_key: {field: value}}}
        # ContextManager expects an AgentState with capability_context_data key
        fake_state = {'capability_context_data': context_data}
        context_manager = ContextManager(fake_state)
        
        # Validate that we have properly structured data
        if context_data:
            logger.info("✓ Agent context loaded successfully!")
            print("✓ Agent context loaded successfully!")
            print(f"Context available with {len(context_data)} context categories")
            print(f"Available context types: {list(context_data.keys())}")
            return context_manager
        else:
            logger.warning("Context loaded but no data found")
            print("⚠️  Context loaded but no data found")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in context file: {e}")
        print(f"⚠️  Invalid JSON in context file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading context: {e}")
        print(f"⚠️  Error loading context: {e}")
        return None