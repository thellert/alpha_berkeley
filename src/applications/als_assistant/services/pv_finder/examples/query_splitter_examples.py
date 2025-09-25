"""
Query Splitter Examples

Type-safe examples for the query splitter agent that determines whether to split
complex queries into atomic sub-queries.
"""

from framework.base import BaseExample
from typing import List
from dataclasses import dataclass
import json


@dataclass
class QuerySplitterExample(BaseExample):
    """
    Type-safe example for query splitter functionality.
    
    Maps from user query to expected splitting decision (single query vs multiple).
    """
    query: str  # Input query
    expected_queries: List[str]  # Expected output queries
    reasoning: str  # Why this splitting decision was made
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.query.strip():
            raise ValueError("Query cannot be empty")
        if not self.expected_queries:
            raise ValueError("Expected queries list cannot be empty")
        if not self.reasoning.strip():
            raise ValueError("Reasoning cannot be empty")
    
    def format_for_prompt(self) -> str:
        """
        Format this example for inclusion in LLM prompts.
        
        Returns JSON format with query -> expected output mapping.
        """
        return json.dumps({
            "query": self.query,
            "expected_output": {"queries": self.expected_queries},
            "reasoning": self.reasoning
        }, indent=2)
    
    def format_compact(self) -> str:
        """Format in compact single-line format."""
        return f"'{self.query}' -> {self.expected_queries} | {self.reasoning}"
    
    def is_split_query(self) -> bool:
        """Check if this example represents a split query (multiple outputs)."""
        return len(self.expected_queries) > 1
    
    


# Query Splitter Examples
query_splitter_examples = [
    QuerySplitterExample(
        query="beam current PV",
        expected_queries=["beam current PV"],
        reasoning="Single device request - no splitting needed"
    ),
    
    QuerySplitterExample(
        query="Get the beam current and all vacuum pumps in sector 12",
        expected_queries=["beam current", "vacuum pumps in sector 12"],
        reasoning="Two distinct requests: beam current (global) and vacuum pumps (specific sector)"
    ),
    
    QuerySplitterExample(
        query="Show injection efficiency trend over 24 h",
        expected_queries=["injection efficiency trend over 24 h"],
        reasoning="Single metric with time qualifier - atomic request"
    ),
    
    QuerySplitterExample(
        query="List all corrector and quadrupole magnet setpoints in the booster",
        expected_queries=["booster corrector magnet setpoints", "booster quadrupole magnet setpoints"],
        reasoning="Two different magnet types - should be split for better tool selection"
    ),
    
    QuerySplitterExample(
        query="what are the 5 last GTL quadrupole setpoints",
        expected_queries=["5 last GTL quadrupole setpoints"],
        reasoning="Single device type with quantity qualifier - atomic request"
    ),
    
    QuerySplitterExample(
        query="horizontal and vertical BPM readings for sector 1",
        expected_queries=["horizontal BPM readings for sector 1", "vertical BPM readings for sector 1"],
        reasoning="Two different measurement types (X/Y) for same devices"
    ),
    
    QuerySplitterExample(
        query="storage ring lifetime",
        expected_queries=["storage ring lifetime"],
        reasoning="Single metric request - no splitting needed"
    ),
    
    QuerySplitterExample(
        query="get me the horizontal corrector setpoints and the quadrupole strengths for the storage ring",
        expected_queries=["horizontal corrector setpoints for the storage ring", "quadrupole strengths for the storage ring"],
        reasoning="Two different device families with different properties"
    ),
    
    QuerySplitterExample(
        query="What are the BPM positions in sectors 1, 2, and 3?",
        expected_queries=["What are the BPM positions in sectors 1, 2, and 3?"],
        reasoning="Single request for same measurement type across multiple sectors - can be handled atomically"
    )
] 