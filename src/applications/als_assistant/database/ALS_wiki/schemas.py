"""
Pydantic schemas for the ALS Accelerator WIKI tree-building algorithm.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# Type definitions
BUCKETS = Literal[
    "Injector", "Booster", "BTS", "Storage Ring", "RF", "Magnets", "Power Supplies",
    "Insertion Devices", "Diagnostics", "Vacuum", "Timing", "Controls", "Safety",
    "Operations", "Procedures", "Playbooks"
]

PAGE_TYPE = Literal["overview", "concept", "procedure", "playbook", "faq"]

PRIORITY = Literal["must", "should", "could"]


# Step A: Topic extraction schemas
class TopicCandidate(BaseModel):
    """A candidate topic extracted from logbook entries."""
    title: str = Field(..., max_length=60, description="Topic title, max 60 chars")
    bucket: BUCKETS = Field(..., description="Which system bucket this topic belongs to")
    summary: str = Field(..., description="Brief summary of the topic")
    page_type: PAGE_TYPE = Field(..., description="Type of page this would be")
    durability: Literal["durable", "ephemeral"] = Field(..., description="Whether topic is durable or ephemeral")
    why_static: Optional[str] = Field(None, description="Why this topic is durable/static")
    example_refs: List[str] = Field(default_factory=list, description="Reference logbook entry IDs")
    aliases: List[str] = Field(default_factory=list, description="Alternative names for this topic")


class TopicExtractionResult(BaseModel):
    """Result of topic extraction from a batch of logbook entries."""
    topics: List[TopicCandidate] = Field(..., description="List of extracted topics")


# Step B: Canonicalization schemas
class CanonicalTopic(BaseModel):
    """A canonical topic after deduplication and normalization."""
    id: str = Field(..., description="Stable unique identifier (slug)")
    title: str = Field(..., max_length=60, description="Canonical title, max 60 chars")
    bucket: BUCKETS = Field(..., description="Assigned system bucket")
    summary: str = Field(..., description="Canonical summary")
    page_type: PAGE_TYPE = Field(..., description="Type of page")
    aliases: List[str] = Field(default_factory=list, description="All known aliases")
    example_refs: List[str] = Field(default_factory=list, description="All supporting logbook entry IDs")


class CanonicalizeDecision(BaseModel):
    """Decision for canonicalization: merge with existing or create new."""
    action: Literal["merge", "new"] = Field(..., description="Whether to merge or create new")
    target_id: Optional[str] = Field(None, description="ID of target to merge into (if action=merge)")
    canonical_title: Optional[str] = Field(None, description="Improved canonical title")
    bucket: Optional[BUCKETS] = Field(None, description="Bucket assignment")
    aliases_to_add: List[str] = Field(default_factory=list, description="Additional aliases to add")


# Step C: Tree building schemas
class TreeNode(BaseModel):
    """A node in the wiki tree structure."""
    id: str = Field(..., description="Unique node identifier")
    title: str = Field(..., description="Node title")
    page_type: Optional[PAGE_TYPE] = Field(None, description="Page type (for leaf nodes)")
    children: List["TreeNode"] = Field(default_factory=list, description="Child nodes")
    topic_refs: List[str] = Field(default_factory=list, description="Referenced canonical topic IDs")


# Enable forward references
TreeNode.model_rebuild()


class TreeBuildResult(BaseModel):
    """Result of tree building process."""
    tree: List[TreeNode] = Field(..., description="Root nodes of the tree")
    merges: List[str] = Field(default_factory=list, description="Notes about topic merges into sections")


# Step D: Prioritization and pruning schemas
class PrioritizeDecision(BaseModel):
    """Priority assignment for a tree node."""
    node_id: str = Field(..., description="Node ID")
    priority: PRIORITY = Field(..., description="Assigned priority level")


class PruneResult(BaseModel):
    """Final result after prioritization and pruning."""
    tree: List[TreeNode] = Field(..., description="Final pruned tree structure")
    priorities: List[PrioritizeDecision] = Field(..., description="Priority assignments for all nodes")
