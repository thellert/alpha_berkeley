"""
PV Finder Agent Examples

Type-safe example classes for the PV Finder agent, providing structured
examples for tool selection and keyword extraction with multiple formatting
options for different use cases.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from framework.base import BaseExample


class AcceleratorSystem(Enum):
    """Enumeration of accelerator systems."""
    SR = "SR"  # Storage Ring
    BR = "BR"  # Booster Ring  
    BTS = "BTS"  # Booster to Storage Ring Transfer Line
    GTL = "GTL"  # Gun to Linac
    LN = "LN"  # Linac
    LTB = "LTB"  # Linac to Booster Transfer Line
    GENERAL = "general"  # General/cross-system


class QueryType(Enum):
    """Enumeration of query types."""
    PV = "PV"  # Process Variable queries
    MISC = "misc"  # Miscellaneous queries
    STRUCTURE = "structure"  # Structure inspection queries
    PYAT = "pyAT"  # PyAT model queries
    GOLDEN = "golden"  # Golden data queries
    FALLBACK = "fallback"  # System fallback queries (always shown for matching system)


class ToolName(Enum):
    """Enumeration of available tools."""
    LIST_CHANNEL_NAMES = "list_channel_names"
    LIST_COMMON_NAMES = "list_common_names"
    GET_FIELD_DATA = "get_field_data"
    GET_AT_INDEX = "get_AT_index"
    INSPECT_FIELDS = "inspect_fields"
    LIST_FAMILIES = "list_families"
    LIST_SYSTEMS = "list_systems"


@dataclass
class PVFinderToolExample(BaseExample):
    """
    Type-safe example for PV Finder tool selection.
    
    Represents a mapping from natural language query to specific tool
    invocation with arguments. Used for few-shot learning in tool selection.
    """
    system: str  # AcceleratorSystem value
    query_type: str  # QueryType value  
    keywords: List[str]  # Keywords for matching
    query: str  # Natural language query
    tool_name: str  # ToolName value
    tool_args: Dict[str, Any]  # Tool arguments
    expected_output: Optional[Dict[str, Any]] = None  # Optional expected result
    
    def __post_init__(self):
        """Validate enum values and required fields."""
        # Validate system
        valid_systems = [s.value for s in AcceleratorSystem]
        if self.system not in valid_systems:
            raise ValueError(f"Invalid system '{self.system}'. Must be one of: {valid_systems}")
        
        # Validate query_type
        valid_query_types = [q.value for q in QueryType]
        if self.query_type not in valid_query_types:
            raise ValueError(f"Invalid query_type '{self.query_type}'. Must be one of: {valid_query_types}")
        
        # Validate tool_name
        valid_tool_names = [t.value for t in ToolName]
        if self.tool_name not in valid_tool_names:
            raise ValueError(f"Invalid tool_name '{self.tool_name}'. Must be one of: {valid_tool_names}")
        
        # Validate required fields
        if not self.query.strip():
            raise ValueError("Query cannot be empty")
        if not self.keywords:
            raise ValueError("Keywords list cannot be empty")
        if not isinstance(self.tool_args, dict):
            raise ValueError("Tool args must be a dictionary")
    
    def matches_system(self, system: str) -> bool:
        """Check if this example matches the specified system."""
        return self.system == system or self.system == AcceleratorSystem.GENERAL.value
    
    def matches_query_type(self, query_type: str) -> bool:
        """Check if this example matches the specified query type."""
        return self.query_type == query_type
    
    def has_keyword(self, keyword: str) -> bool:
        """Check if this example contains the specified keyword."""
        keyword_lower = keyword.lower()
        result = any(keyword_lower in kw.lower() for kw in self.keywords)
        return result
    
    def format_for_prompt(self) -> str:
        """Format this example for inclusion in LLM prompts.
        
        Returns User Query/Assistant Action format for individual tool examples.
        This implements the required BaseExample interface.
        """
        tool_args_json = json.dumps(self.tool_args, indent=2)
        response = f'User Query: "{self.query}"\n'
        response += f"Assistant Action:\n"
        response += f"  Tool Call: {self.tool_name}\n"
        response += f"  Tool Arguments: {tool_args_json}\n"
        if self.expected_output:
            final_answer = json.dumps(self.expected_output, indent=2)
            response += f"Final Answer:\n{final_answer}\n"
        return response
    


@dataclass
class KeywordExtractionExample(BaseExample):
    """
    Type-safe example for keyword extraction and system identification.
    
    Represents a mapping from user query to expected keywords and target
    accelerator systems. Used for training keyword extraction models.
    """
    query: str  # User query
    expected_keywords: List[str]  # Expected keywords to extract
    expected_systems: List[str]  # Expected target systems
    
    def __post_init__(self):
        """Validate required fields and system values."""
        if not self.query.strip():
            raise ValueError("Query cannot be empty")
        if not self.expected_keywords:
            raise ValueError("Expected keywords list cannot be empty")
        if not self.expected_systems:
            raise ValueError("Expected systems list cannot be empty")
        
        # Validate system values
        valid_systems = [s.value for s in AcceleratorSystem if s != AcceleratorSystem.GENERAL]
        for system in self.expected_systems:
            if system not in valid_systems:
                raise ValueError(f"Invalid system '{system}'. Must be one of: {valid_systems}")
    
    def format_for_prompt(self) -> str:
        """
        Format this example for inclusion in LLM prompts.
        
        Returns JSON format with query -> expected output mapping suitable
        for training keyword extraction models.
        
        Returns:
            Formatted string representation of the example
        """
        return json.dumps({
            "query": self.query,
            "expected_output": {
                "keywords": self.expected_keywords,
                "systems": self.expected_systems
            }
        }, indent=2)
    
    def has_system(self, system: str) -> bool:
        """Check if this example targets the specified system."""
        return system in self.expected_systems
    
    def has_keyword(self, keyword: str) -> bool:
        """Check if this example expects the specified keyword."""
        keyword_lower = keyword.lower()
        return any(keyword_lower in kw.lower() for kw in self.expected_keywords)
    
    



# Utility functions for working with the example classes

# ==============================================================================
# EXAMPLE LOADER - Centralized management and loading of examples
# ==============================================================================

class PVFinderExampleLoader:
    """Centralized loader for PV Finder examples with filtering capabilities."""
    
    def __init__(self):
        self._pv_examples: Optional[Dict[str, List[PVFinderToolExample]]] = None
        self._keyword_examples: Optional[List[KeywordExtractionExample]] = None
    
    def _load_pv_examples(self) -> Dict[str, List[PVFinderToolExample]]:
        """Load all PV Finder examples grouped by system."""
        if self._pv_examples is not None:
            return self._pv_examples
        
        # Use global logger
        from configs.logger import get_logger
        logger = get_logger("als_assistant", "pv_finder")
        
        examples_by_system = {}
        
        try:
            # Load SR examples
            from .examples.tool_examples_sr import sr_examples
            examples_by_system['SR'] = sr_examples
            logger.info(f"Loaded {len(sr_examples)} SR examples")
        except ImportError as e:
            examples_by_system['SR'] = []
            logger.warning(f"Failed to load SR examples: {e}")
        
        try:
            # Load BR examples
            from .examples.tool_examples_br import br_examples
            examples_by_system['BR'] = br_examples
            logger.info(f"Loaded {len(br_examples)} BR examples")
        except ImportError as e:
            examples_by_system['BR'] = []
            logger.warning(f"Failed to load BR examples: {e}")
        
        try:
            # Load GTL examples
            from .examples.tool_examples_gtl import gtl_examples
            examples_by_system['GTL'] = gtl_examples
            logger.info(f"Loaded {len(gtl_examples)} GTL examples")
        except ImportError as e:
            examples_by_system['GTL'] = []
            logger.warning(f"Failed to load GTL examples: {e}")
        
        try:
            # Load LN examples
            from .examples.tool_examples_ln import ln_examples
            examples_by_system['LN'] = ln_examples
            logger.info(f"Loaded {len(ln_examples)} LN examples")
        except ImportError as e:
            examples_by_system['LN'] = []
            logger.warning(f"Failed to load LN examples: {e}")
        
        try:
            # Load LTB examples
            from .examples.tool_examples_ltb import ltb_examples
            examples_by_system['LTB'] = ltb_examples
            logger.info(f"Loaded {len(ltb_examples)} LTB examples")
        except ImportError as e:
            examples_by_system['LTB'] = []
            logger.warning(f"Failed to load LTB examples: {e}")
        
        try:
            # Load BTS examples
            from .examples.tool_examples_bts import bts_examples
            examples_by_system['BTS'] = bts_examples
            logger.info(f"Loaded {len(bts_examples)} BTS examples")
        except ImportError as e:
            examples_by_system['BTS'] = []
            logger.warning(f"Failed to load BTS examples: {e}")
        

        
        self._pv_examples = examples_by_system
        return self._pv_examples
    
    def _load_keyword_examples(self) -> List[KeywordExtractionExample]:
        """Load keyword extraction examples."""
        if self._keyword_examples is not None:
            return self._keyword_examples
        
        try:
            from .examples.keyword_extraction_examples import keyword_examples
            self._keyword_examples = keyword_examples
        except ImportError:
            self._keyword_examples = []
        
        return self._keyword_examples
    
    def get_query_splitter_examples(self) -> List:
        """Get query splitter examples."""
        try:
            from .examples.query_splitter_examples import query_splitter_examples
            return query_splitter_examples
        except ImportError:
            return []
    

    
    def get_foundational_examples(self, max_examples: int = None) -> List[PVFinderToolExample]:
        """Get foundational examples that demonstrate core PV Finder workflows."""
        try:
            from .examples.foundational_examples import foundational_examples
            
            if max_examples and len(foundational_examples) > max_examples:
                return foundational_examples[:max_examples]
            
            return foundational_examples
        except ImportError:
            return []
    
    def get_all_pv_examples(self) -> List[PVFinderToolExample]:
        """Get all PV Finder examples across all systems."""
        examples_by_system = self._load_pv_examples()
        all_examples = []
        for examples in examples_by_system.values():
            all_examples.extend(examples)
        return all_examples
    
    def get_pv_examples_by_system(self, system: str) -> List[PVFinderToolExample]:
        """
        Get PV Finder examples for a specific system.
        
        Args:
            system: System name (SR, BR, GTL, LN, LTB, general)
            
        Returns:
            List of examples for the specified system
        """
        examples_by_system = self._load_pv_examples()
        return examples_by_system.get(system, [])
    
    def get_pv_examples_by_query_type(self, query_type: str, 
                                     system: Optional[str] = None) -> List[PVFinderToolExample]:
        """
        Get PV Finder examples by query type, optionally filtered by system.
        
        Args:
            query_type: Query type (PV, misc, structure, pyAT, golden)
            system: Optional system filter
            
        Returns:
            List of examples matching the criteria
        """
        if system:
            examples = self.get_pv_examples_by_system(system)
        else:
            examples = self.get_all_pv_examples()
        
        return [ex for ex in examples if ex.matches_query_type(query_type)]
    

    
    def get_keyword_examples(self) -> List[KeywordExtractionExample]:
        """Get all keyword extraction examples."""
        return self._load_keyword_examples()
    
    def get_keyword_examples_by_system(self, system: str) -> List[KeywordExtractionExample]:
        """
        Get keyword extraction examples that target a specific system.
        
        Args:
            system: System name to filter by
            
        Returns:
            List of keyword examples targeting the specified system
        """
        examples = self.get_keyword_examples()
        return [ex for ex in examples if ex.has_system(system)]
    
    def format_pv_examples_for_prompt(self, system: Optional[str] = None,
                                     query_type: Optional[str] = None,
                                     max_examples: Optional[int] = None) -> str:
        """
        Format PV Finder examples for inclusion in prompts with optional filtering.
        
        Args:
            system: Optional system filter
            query_type: Optional query type filter  
            max_examples: Optional limit on number of examples
            
        Returns:
            Formatted string suitable for LLM prompts
        """
        if system and query_type:
            examples = self.get_pv_examples_by_query_type(query_type, system)
        elif system:
            examples = self.get_pv_examples_by_system(system)
        elif query_type:
            examples = self.get_pv_examples_by_query_type(query_type)
        else:
            examples = self.get_all_pv_examples()
        
        if max_examples and len(examples) > max_examples:
            examples = examples[:max_examples]
        
        return PVFinderToolExample.join(examples)
    
    def format_keyword_examples_for_prompt(self, system: Optional[str] = None,
                                         max_examples: Optional[int] = None) -> str:
        """
        Format keyword extraction examples for inclusion in prompts.
        
        Args:
            system: Optional system filter
            max_examples: Optional limit on number of examples
            
        Returns:
            Formatted string suitable for LLM prompts
        """
        if system:
            examples = self.get_keyword_examples_by_system(system)
        else:
            examples = self.get_keyword_examples()
        
        if max_examples and len(examples) > max_examples:
            examples = examples[:max_examples]
        
        return KeywordExtractionExample.join(examples)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the loaded examples."""
        pv_examples = self._load_pv_examples()
        keyword_examples = self._load_keyword_examples()
        
        stats = {
            'total_pv_examples': sum(len(examples) for examples in pv_examples.values()),
            'total_keyword_examples': len(keyword_examples),
            'systems': len([sys for sys, examples in pv_examples.items() if examples])
        }
        
        # Add per-system counts
        for system, examples in pv_examples.items():
            if examples:
                stats[f'{system}_examples'] = len(examples)
        
        return stats


# Global instance for easy access
example_loader = PVFinderExampleLoader()