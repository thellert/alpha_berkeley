"""
ALS Accelerator WIKI Tree-Building Algorithm

A typed, Pydantic-based pipeline for extracting durable knowledge from logbook entries
and organizing it into a compact, reviewable wiki tree structure.

Main components:
- schemas: Pydantic models for all data structures
- prompts: Schema-bound prompt builders for each pipeline step
- pipeline: Core logic, canonicalization index, and orchestrator

Usage:
    from ALS_wiki import run_pipeline_sync
    
    result = run_pipeline_sync(
        logbook_path="/path/to/logbook.jsonl",
        output_dir="./artifacts"
    )
"""

from .schemas import (
    BUCKETS, PAGE_TYPE, PRIORITY,
    TopicCandidate, TopicExtractionResult,
    CanonicalTopic, CanonicalizeDecision,
    TreeNode, TreeBuildResult,
    PrioritizeDecision, PruneResult
)

from .pipeline import (
    run_pipeline, run_pipeline_sync,
    CanonIndex, MAX_CHILDREN, TARGET_LEAVES,
    load_jsonl_stream, WIKI_MODELS
)

__version__ = "1.0.0"
__all__ = [
    # Main entry points
    "run_pipeline", "run_pipeline_sync",
    
    # Core classes and utilities
    "CanonIndex", "load_jsonl_stream",
    
    # Constants and configurations
    "MAX_CHILDREN", "TARGET_LEAVES", "WIKI_MODELS",
    
    # Type definitions
    "BUCKETS", "PAGE_TYPE", "PRIORITY",
    
    # Schema classes
    "TopicCandidate", "TopicExtractionResult",
    "CanonicalTopic", "CanonicalizeDecision", 
    "TreeNode", "TreeBuildResult",
    "PrioritizeDecision", "PruneResult"
]
