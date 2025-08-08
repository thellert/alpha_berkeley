"""
ContextManager - Simplified LangGraph-Native Context Management

Ultra-simplified context manager using Pydantic for automatic serialization.
This eliminates 90% of the complexity from the previous implementation while
maintaining full LangGraph compatibility for checkpointing and serialization.

Key simplifications:
- Uses Pydantic's .model_dump() and .model_validate() for serialization
- No custom reflection-based serialization logic
- No complex type conversion or property detection
- No DotDict utilities needed
- Direct registry lookup without extensive validation
"""

import json
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from datetime import datetime
from pathlib import Path
from configs.logger import get_logger

if TYPE_CHECKING:
    from framework.context.base import CapabilityContext
    from framework.state.state import AgentState

logger = get_logger("framework", "base")



class ContextManager:
    """Simplified LangGraph-native context manager using Pydantic serialization.
    
    This class provides sophisticated functionality over dictionary data while storing
    everything in LangGraph-compatible dictionary format. It uses Pydantic's built-in
    serialization capabilities to eliminate complex custom logic.
    
    The data is stored as: {context_type: {context_key: {field: value}}}
    """
    
    def __init__(self, state: 'AgentState'):
        """Initialize ContextManager with agent state.
        
        Args:
            state: Full AgentState containing capability_context_data
            
        Raises:
            TypeError: If state is not an AgentState dictionary
            ValueError: If state doesn't contain capability_context_data key
        """
        if not isinstance(state, dict):
            raise TypeError(f"ContextManager expects AgentState dictionary, got {type(state)}")
        
        if 'capability_context_data' not in state:
            raise ValueError("AgentState must contain 'capability_context_data' key")
            
        self._data = state['capability_context_data']
        self._object_cache: Dict[str, Dict[str, 'CapabilityContext']] = {}
    
    def __getattr__(self, context_type: str):
        """Enable dot notation access to context data with lazy namespace creation."""
        if context_type.startswith('_'):
            # For private attributes, use normal attribute access
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{context_type}'")
        
        if context_type in self._data:
            # Create a namespace for this context type with lazy object reconstruction
            namespace = ContextNamespace(self, context_type)
            return namespace
        
        # If not found in _data, raise AttributeError to maintain normal Python behavior
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{context_type}'")
    
    def set_context(self, context_type: str, key: str, value: 'CapabilityContext', skip_validation: bool = False) -> None:
        """Store context using Pydantic's built-in serialization.
        
        Args:
            context_type: Type of context (e.g., "PV_ADDRESSES")
            key: Unique key for this context instance
            value: CapabilityContext object to store
            skip_validation: Skip registry validation (useful for testing)
        """
        # Validate using registry (unless skipped for testing)
        if not skip_validation:
            try:
                # Import registry here to avoid circular imports
                from framework.registry import get_registry
                registry = get_registry()
                # Check if registry is initialized before validation
                if hasattr(registry, '_registries') and registry._registries:
                    # Validate context type is recognized
                    if not registry.is_valid_context_type(context_type):
                        raise ValueError(f"Unknown context type: {context_type}. Valid types: {registry.get_all_context_types()}")
                    
                    # Validate value is correct type for context type
                    expected_type = registry.get_context_class(context_type)
                    if expected_type is not None and not isinstance(value, expected_type):
                        raise ValueError(f"Context type {context_type} expects {expected_type}, got {type(value)}")
                else:
                    # Registry not initialized - just log a warning and continue
                    logger.warning(f"Registry not initialized, skipping validation for {context_type}")
                    
            except ImportError:
                # If registry is not available yet, skip validation
                logger.debug(f"Registry not available, skipping validation for {context_type}")
        
        # Use Pydantic's built-in .model_dump() method for serialization
        if context_type not in self._data:
            self._data[context_type] = {}
        self._data[context_type][key] = value.model_dump()
        
        # Update cache
        if context_type not in self._object_cache:
            self._object_cache[context_type] = {}
        self._object_cache[context_type][key] = value
        
        logger.debug(f"Stored context: {context_type}.{key} = {type(value).__name__}")
    
    def get_context(self, context_type: str, key: str) -> Optional['CapabilityContext']:
        """Retrieve using Pydantic's .model_validate() for reconstruction.
        
        Args:
            context_type: Type of context to retrieve
            key: Key of the context instance
            
        Returns:
            Reconstructed CapabilityContext object or None if not found
        """
        # Check cache first
        if (context_type in self._object_cache and 
            key in self._object_cache[context_type]):
            cached_obj = self._object_cache[context_type][key]
            logger.debug(f"Retrieved cached context: {context_type}.{key} = {type(cached_obj).__name__}")
            return cached_obj
        
        # Get raw dictionary data
        raw_data = self._data.get(context_type, {}).get(key)
        if raw_data is None:
            return None
        
        # Get context class from registry
        context_class = self._get_context_class(context_type)
        if context_class is None:
            logger.warning(f"Unknown context type: {context_type}")
            return None
        
        # Use Pydantic's model_validate for reconstruction
        try:
            reconstructed_obj = context_class.model_validate(raw_data)
            
            # Cache the reconstructed object
            if context_type not in self._object_cache:
                self._object_cache[context_type] = {}
            self._object_cache[context_type][key] = reconstructed_obj
            
            logger.debug(f"Retrieved and cached context: {context_type}.{key} = {type(reconstructed_obj).__name__}")
            return reconstructed_obj
        except Exception as e:
            logger.error(f"Failed to reconstruct {context_type}: {e}")
            return None
    
    def get_all_of_type(self, context_type: str) -> Dict[str, 'CapabilityContext']:
        """Get all contexts of a specific type as reconstructed objects.
        
        Args:
            context_type: Type of context to retrieve
            
        Returns:
            Dictionary of key -> CapabilityContext objects
        """
        result = {}
        context_keys = self._data.get(context_type, {}).keys()
        
        for key in context_keys:
            context_obj = self.get_context(context_type, key)
            if context_obj:
                result[key] = context_obj
        
        return result
    
    def get_all(self) -> Dict[str, Any]:
        """Get all context data in flattened format for reporting/summary purposes.
        
        Returns:
            Dictionary with flattened keys in format "context_type.key" -> context object
        """
        flattened = {}
        for context_type in self._data.keys():
            contexts_dict = self.get_all_of_type(context_type)
            for key, context in contexts_dict.items():
                flattened_key = f"{context_type}.{key}"
                flattened[flattened_key] = context
        return flattened
    
    def get_context_access_description(self, context_filter: Optional[List[Dict[str, str]]] = None) -> str:
        """Create detailed description of available context data for use in prompts.
        
        Args:
            context_filter: Optional list of context filter dictionaries
            
        Returns:
            Formatted string description of available context data
        """
        if not self._data:
            return "No context data available."
        
        description_parts = []
        description_parts.append("The agent context is available via the 'context' object with dot notation access:")
        description_parts.append("")
        
        # Determine which contexts to show based on context_filter
        contexts_to_show = {}
        
        if context_filter and isinstance(context_filter, list) and context_filter:
            # Filter to only show contexts referenced in context_filter
            for filter_dict in context_filter:
                for context_type, context_key in filter_dict.items():
                    if context_type in self._data and context_key in self._data[context_type]:
                        if context_type not in contexts_to_show:
                            contexts_to_show[context_type] = {}
                        # Reconstruct the object for access details
                        context_obj = self.get_context(context_type, context_key)
                        if context_obj:
                            contexts_to_show[context_type][context_key] = context_obj
        else:
            # Show all contexts (reconstruct all objects)
            for context_type in self._data.keys():
                contexts_to_show[context_type] = self.get_all_of_type(context_type)
        
        if not contexts_to_show:
            return "No relevant context data available for the specified context filter."
        
        for context_type, contexts_dict in contexts_to_show.items():
            if isinstance(contexts_dict, dict):
                description_parts.append(f"• context.{context_type}:")
                
                for key, context_obj in contexts_dict.items():
                    # Use the get_access_details method with the actual key name
                    if hasattr(context_obj, 'get_access_details'):
                        try:
                            details = context_obj.get_access_details(key_name=key)
                            if isinstance(details, dict):
                                description_parts.append(f"  └── {key}")
                                
                                details_str = json.dumps(details, indent=6, default=str)
                                description_parts.append(f"      └── Details: {details_str}")
                            else:
                                description_parts.append(f"  └── {key}: {str(details)}")
                        except Exception as e:
                            description_parts.append(f"  └── {key}: {type(context_obj).__name__} object (get_access_details error: {e})")
                    else:
                        description_parts.append(f"  └── {key}: {type(context_obj).__name__} object (no get_access_details method available)")
                
                description_parts.append("")
        
        return "\n".join(description_parts)

    
    def get_human_summaries(self, step: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get human summaries for specific step contexts or all contexts.
        
        Args:
            step: Optional step dict. If provided, extract contexts from step.inputs.
                  If None, get human summaries for all available contexts.
        
        Returns:
            Dict with flattened keys "context_type.key" -> human_summary_data
        """
        # Step 1: Get contexts (filtered by step or all)
        if step is not None:
            # Get specific step contexts and convert to flattened format
            try:
                step_contexts = self.extract_from_step(step, {})
                contexts_dict = {}
                
                # Convert to flattened format like get_all() returns
                for input_spec in step.get('inputs', []):
                    if isinstance(input_spec, dict):
                        for context_type, key_name in input_spec.items():
                            if context_type in step_contexts:
                                flattened_key = f"{context_type}.{key_name}"
                                contexts_dict[flattened_key] = step_contexts[context_type]
                                
            except Exception as e:
                logger.error(f"Error extracting step contexts: {e}")
                contexts_dict = self.get_all()  # Fallback to all contexts
        else:
            # Get all contexts in flattened format
            contexts_dict = self.get_all()
        
        # Step 2: Convert contexts to human summaries (single consolidated logic)
        return self._contexts_to_human_summaries(contexts_dict)
    
    def _contexts_to_human_summaries(self, contexts_dict: Dict[str, 'CapabilityContext']) -> Dict[str, Any]:
        """Convert flattened contexts dict to human summaries dict.
        
        Args:
            contexts_dict: Dict with "context_type.key" -> context_object format
            
        Returns:
            Dict with "context_type.key" -> human_summary_data format
        """
        summaries = {}
        
        for flattened_key, context_object in contexts_dict.items():
            # Extract key name from flattened key
            if '.' in flattened_key:
                context_type, key_name = flattened_key.split('.', 1)
            else:
                context_type, key_name = flattened_key, flattened_key
            
            if hasattr(context_object, 'get_human_summary'):
                summaries[flattened_key] = context_object.get_human_summary(key_name)
            else:
                # Fallback for context objects without human summary
                summaries[flattened_key] = {
                    "type": context_type,
                    "raw_data": str(context_object)[:200] + "..." if len(str(context_object)) > 200 else str(context_object)
                }
        
        return summaries
    
    def get_raw_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get the raw dictionary data for state updates.
        
        Returns:
            The raw dictionary data for LangGraph state updates
        """
        return self._data
    
    def save_context_to_file(self, folder_path: Path, filename: str = "context.json") -> Path:
        """Save capability context data to a JSON file in the specified folder.
        
        This method always saves the current context data to ensure it reflects
        the latest state. It uses the same serialization format as the state system.
        
        Args:
            folder_path: Path to the folder where the context file should be saved
            filename: Name of the context file (default: "context.json")
            
        Returns:
            Path to the saved context file
            
        Raises:
            OSError: If file cannot be written
            TypeError: If context data cannot be serialized
            ValueError: If filename is empty or contains invalid characters
        """
        if not isinstance(folder_path, Path):
            folder_path = Path(folder_path)
            
        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty")
            
        # Ensure filename has .json extension if not provided
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
            
        # Ensure folder exists
        folder_path.mkdir(parents=True, exist_ok=True)
        
        context_file = folder_path / filename
        
        try:
            # Save using standard JSON (data is already JSON-serializable via Pydantic)
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Saved context data to: {context_file}")
            return context_file
            
        except Exception as e:
            logger.error(f"Failed to save context to {context_file}: {e}")
            raise
    
    def _get_context_class(self, context_type: str) -> Optional[type]:
        """Get context class from registry or direct mapping.
        
        Args:
            context_type: The context type string
            
        Returns:
            Context class or None if not found
        """
        try:
            # Import registry here to avoid circular imports
            from framework.registry import get_registry
            registry = get_registry()
            return registry.get_context_class(context_type)
        except Exception as e:
            logger.error(f"Failed to get context class for {context_type}: {e}")
            raise ValueError(f"Registry not available, cannot get context class for {context_type}")
    
    def extract_from_step(
        self,
        step: Dict[str, Any],
        state: Dict[str, Any],
        constraints: Optional[List[str]] = None,
        constraint_mode: str = "hard"
    ) -> Dict[str, 'CapabilityContext']:
        """Extract all contexts specified in step.inputs with optional type constraints.
        
        This method consolidates the common pattern of extracting context data from
        step inputs and validating against expected types. It replaces repetitive
        validation logic across capabilities.
        
        Args:
            step: Execution step with inputs list like ``[{"PV_ADDRESSES": "key1"}, {"TIME_RANGE": "key2"}]``
            state: Current agent state (for error checking)
            constraints: Optional list of required context types (e.g., ``["PV_ADDRESSES", "TIME_RANGE"]``)
            constraint_mode: ``"hard"`` (all constraints required) or ``"soft"`` (at least one constraint required)
        
        Returns:
            Dict mapping context_type to context object
            
        Raises:
            ValueError: If contexts not found or constraints not met (capability converts to specific error)
            
        Example:
        
        .. code-block:: python
        
            # Simple extraction without constraints
            contexts = context_manager.extract_from_step(step, state)
            
            # With hard constraints (all required)
            try:
                contexts = context_manager.extract_from_step(
                    step, state, 
                    constraints=["PV_ADDRESSES", "TIME_RANGE"]
                )
                pv_context = contexts["PV_ADDRESSES"]
                time_context = contexts["TIME_RANGE"]
            except ValueError as e:
                raise ArchiverDependencyError(str(e))
                
            # With soft constraints (at least one required)
            try:
                contexts = context_manager.extract_from_step(
                    step, state,
                    constraints=["PV_VALUES", "ARCHIVER_DATA"], 
                    constraint_mode="soft"
                )
            except ValueError as e:
                raise DataValidationError(str(e))
        """
        results = {}
        
        # Extract all contexts from step.inputs
        step_inputs = step.get('inputs', [])
        if not step_inputs:
            # Check if we need any data at all
            if constraints:
                capability_context_data = state.get('capability_context_data', {})
                if not capability_context_data:
                    raise ValueError("No context data available and no step inputs specified")
            return results
        
        # Process each input dictionary
        for input_dict in step_inputs:
            for context_type, context_key in input_dict.items():
                context_obj = self.get_context(context_type, context_key)
                if context_obj:
                    results[context_type] = context_obj
                else:
                    raise ValueError(f"Context {context_type}.{context_key} not found")
        
        # Apply constraints if specified
        if constraints:
            found_types = set(results.keys())
            required_types = set(constraints)
            
            if constraint_mode == "hard":
                # All constraints must be satisfied
                missing_types = required_types - found_types
                if missing_types:
                    raise ValueError(f"Missing required context types: {list(missing_types)}")
            elif constraint_mode == "soft":
                # At least one constraint must be satisfied
                if not (required_types & found_types):
                    raise ValueError(f"None of the required context types found: {list(required_types)}")
            else:
                raise ValueError(f"Invalid constraint_mode: {constraint_mode}. Use 'hard' or 'soft'")
        
        return results


class ContextNamespace:
    """Namespace object that provides dot notation access to context objects."""
    
    def __init__(self, context_manager: ContextManager, context_type: str):
        self._context_manager = context_manager
        self._context_type = context_type
    
    def __getattr__(self, key: str):
        """Get context object by key with lazy reconstruction."""
        context_obj = self._context_manager.get_context(self._context_type, key)
        if context_obj is not None:
            return context_obj
        raise AttributeError(f"Context '{self._context_type}' has no key '{key}'")
    
    def __setattr__(self, key: str, value):
        """Set context object by key."""
        if key.startswith('_'):
            # Set private attributes normally
            super().__setattr__(key, value)
        else:
            # This would require the value to be a CapabilityContext object
            # For now, raise an error as direct assignment should go through set_context
            raise AttributeError(f"Cannot directly assign to context key '{key}'. Use context_manager.set_context() instead.") 