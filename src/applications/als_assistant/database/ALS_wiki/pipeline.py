"""
Main pipeline for the ALS Accelerator WIKI tree-building algorithm.
Contains constants, IO helpers, CanonIndex, typed LLM calls, and orchestrator.
"""

import json
import asyncio
import re
import sys
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Iterator
from pathlib import Path
import unicodedata
from itertools import islice
from tqdm import tqdm

# Framework imports (path should be set by calling script)

from framework.models import get_chat_completion


from .schemas import (
    TopicCandidate, TopicExtractionResult, CanonicalTopic, CanonicalizeDecision,
    TreeNode, TreeBuildResult, PruneResult, BUCKETS
)
from .prompts import (
    build_prompt_A, build_prompt_B_incremental, build_prompt_B_global,
    build_prompt_C, build_prompt_D
)


# Constants and thresholds
MAX_CHILDREN = 7
TARGET_LEAVES = 500
BATCH_SIZE = 50

# Merge thresholds for canonicalization
TITLE_JACCARD = 0.80
BIGRAM_OVERLAP = 0.60
EMBED_COSINE = 0.86  # If using embeddings

# Time window for logbook entries (3 years back)
TIME_WINDOW_YEARS = 3

# ALS WIKI Model Configurations
WIKI_MODELS = {
    "extract": {
        "provider": "cborg",
        "model_id": "google/gemini-flash",  # Complex: multi-entry processing, technical understanding
        "max_tokens": 30000,
        "temperature": 0.1
    },
    "canon_incremental": {
        "provider": "cborg", 
        "model_id": "google/gemini-flash",   # Simple: binary decision with small context
        "max_tokens": 30000,
        "temperature": 0.1
    },
    "canon_global": {
        "provider": "cborg",
        "model_id": "google/gemini-flash",  # Complex: large-scale deduplication, semantic analysis
        "max_tokens": 30000,
        "temperature": 0.1
    },
    "tree": {
        "provider": "cborg",
        "model_id": "google/gemini-flash",  # Complex: hierarchical reasoning, structural constraints
        "max_tokens": 30000,
        "temperature": 0.1
    },
    "prune": {
        "provider": "cborg",
        "model_id": "google/gemini-flash",   # Simple: priority assignment with clear criteria
        "max_tokens": 30000,
        "temperature": 0.1
    }
}


def batched(iterable, n):
    """Batch an iterable into chunks of size n."""
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


def load_jsonl_stream(path: str, since: Optional[datetime] = None, until: Optional[datetime] = None, newest_first: bool = True) -> Iterator[Dict[str, Any]]:
    """
    Stream JSONL entries from logbook file.
    
    Args:
        path: Path to JSONL logbook file
        since: Only return entries after this timestamp (optional)
        until: Only return entries before this timestamp (optional)
        newest_first: If True, return newest entries first
        
    Yields:
        Logbook entry dictionaries
    """
    entries = []
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                
                # Filter by timestamp if specified
                if since or until:
                    timestamp = int(entry.get('timestamp', 0))
                    entry_time = datetime.fromtimestamp(timestamp)
                    
                    # Skip if before start date
                    if since and entry_time < since:
                        continue
                    
                    # Skip if after end date
                    if until and entry_time > until:
                        continue
                
                entries.append(entry)
            except json.JSONDecodeError:
                continue
    
    # Sort by timestamp if requested
    if newest_first:
        entries.sort(key=lambda x: int(x.get('timestamp', 0)), reverse=True)
    
    yield from entries


def save_json(path: str, obj: Any) -> None:
    """Save object as JSON to file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def render_tree_markdown(canonical_topics: List[CanonicalTopic], tree_result: Optional[TreeBuildResult] = None, 
                        prune_result: Optional[PruneResult] = None, output_path: str = None) -> str:
    """Render canonical topics and tree structure as Markdown."""
    
    md_lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Header
    md_lines.extend([
        "# ALS Accelerator WIKI Tree Structure",
        f"*Generated: {timestamp}*",
        "",
        "## Overview",
        f"- **Total Topics**: {len(canonical_topics)}",
    ])
    
    if tree_result:
        leaf_count = count_tree_leaves(tree_result.tree)
        md_lines.append(f"- **Tree Leaves**: {leaf_count}")
    
    if prune_result:
        priorities = {}
        for decision in prune_result.priorities:
            priorities[decision.priority] = priorities.get(decision.priority, 0) + 1
        priority_str = ", ".join([f"{p}: {c}" for p, c in priorities.items()])
        md_lines.append(f"- **Priorities**: {priority_str}")
    
    md_lines.extend(["", "---", ""])
    
    # Group topics by bucket
    topics_by_bucket = {}
    for topic in canonical_topics:
        if topic.bucket not in topics_by_bucket:
            topics_by_bucket[topic.bucket] = []
        topics_by_bucket[topic.bucket].append(topic)
    
    # Render topics by bucket
    md_lines.append("## Topics by System Bucket")
    md_lines.append("")
    
    for bucket in sorted(topics_by_bucket.keys()):
        topics = topics_by_bucket[bucket]
        md_lines.extend([
            f"### {bucket} ({len(topics)} topics)",
            ""
        ])
        
        for topic in sorted(topics, key=lambda t: t.title):
            # Basic topic info
            md_lines.append(f"#### {topic.title}")
            md_lines.append(f"- **Type**: {topic.page_type}")
            md_lines.append(f"- **Summary**: {topic.summary}")
            
            if topic.aliases:
                aliases_str = ", ".join(f"`{alias}`" for alias in topic.aliases)
                md_lines.append(f"- **Aliases**: {aliases_str}")
            
            if topic.example_refs:
                refs_str = ", ".join(f"`{ref}`" for ref in topic.example_refs[:5])  # Limit to first 5
                if len(topic.example_refs) > 5:
                    refs_str += f" (and {len(topic.example_refs) - 5} more)"
                md_lines.append(f"- **References**: {refs_str}")
            
            md_lines.append("")
    
    # Render tree structure if available
    if tree_result:
        md_lines.extend([
            "---",
            "",
            "## Tree Structure",
            ""
        ])
        
        def render_tree_node(node: TreeNode, level: int = 0) -> List[str]:
            lines = []
            indent = "  " * level
            
            # Node title with priority if available
            title = node.title
            if prune_result:
                priority_decision = next((p for p in prune_result.priorities if p.node_id == node.id), None)
                if priority_decision:
                    priority_emoji = {"must": "🔴", "should": "🟡", "could": "🟢"}.get(priority_decision.priority, "⚪")
                    title = f"{priority_emoji} {title}"
            
            if not node.children:  # Leaf node
                lines.append(f"{indent}- **{title}** *(leaf)*")
                if node.topic_refs:
                    refs_str = ", ".join(node.topic_refs[:3])  # Show first 3
                    if len(node.topic_refs) > 3:
                        refs_str += f" (+{len(node.topic_refs) - 3} more)"
                    lines.append(f"{indent}  - *Topics: {refs_str}*")
            else:  # Parent node
                lines.append(f"{indent}- **{title}** ({len(node.children)} children)")
                for child in node.children:
                    lines.extend(render_tree_node(child, level + 1))
            
            return lines
        
        for root_node in tree_result.tree:
            md_lines.extend(render_tree_node(root_node))
            md_lines.append("")
        
        # Show merge notes if available
        if tree_result.merges:
            md_lines.extend([
                "### Tree Building Notes",
                ""
            ])
            for merge_note in tree_result.merges:
                md_lines.append(f"- {merge_note}")
            md_lines.append("")
    
    # Priority breakdown if available
    if prune_result:
        md_lines.extend([
            "---",
            "",
            "## Priority Breakdown",
            ""
        ])
        
        priority_groups = {"must": [], "should": [], "could": []}
        for decision in prune_result.priorities:
            priority_groups[decision.priority].append(decision.node_id)
        
        for priority, nodes in priority_groups.items():
            if nodes:
                emoji = {"must": "🔴", "should": "🟡", "could": "🟢"}[priority]
                md_lines.extend([
                    f"### {emoji} {priority.upper()} ({len(nodes)} items)",
                    ""
                ])
                for node_id in sorted(nodes):
                    md_lines.append(f"- `{node_id}`")
                md_lines.append("")
    
    # Footer
    md_lines.extend([
        "---",
        f"*Last updated: {timestamp}*"
    ])
    
    markdown_content = "\n".join(md_lines)
    
    # Save to file if path provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        tqdm.write(f"📝 Updated markdown: {output_path}")
    
    return markdown_content


def count_tree_leaves(nodes: List[TreeNode]) -> int:
    """Count total leaf nodes in tree."""
    count = 0
    for node in nodes:
        if not node.children:
            count += 1
        else:
            count += count_tree_leaves(node.children)
    return count


def load_json(path: str) -> Any:
    """Load JSON from file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


class PipelineState:
    """Manages pipeline state for checkpointing and resuming."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.checkpoint_dir = self.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # State tracking
        self.completed_batches = set()
        self.canon_index = None
        self.step_completed = {
            "extraction": False,
            "canonicalization": False,
            "tree_building": False,
            "pruning": False
        }
        self.metadata = {
            "start_time": None,
            "last_checkpoint": None,
            "total_entries": 0,
            "total_batches": 0,
            "batch_size": 0,
            "date_range": {},
            "config": {}
        }
    
    def save_checkpoint(self, step: str, data: Any = None):
        """Save checkpoint for current step."""
        checkpoint_file = self.checkpoint_dir / f"{step}_checkpoint.pkl"
        
        checkpoint_data = {
            "timestamp": datetime.now().isoformat(),
            "completed_batches": self.completed_batches,
            "step_completed": self.step_completed.copy(),
            "metadata": self.metadata.copy(),
            "canon_index": self.canon_index,
            "step_data": data
        }
        
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        # Also save as JSON for human readability (excluding binary data)
        json_data = {
            "timestamp": checkpoint_data["timestamp"],
            "completed_batches": list(self.completed_batches),
            "step_completed": self.step_completed,
            "metadata": self.metadata
        }
        json_file = self.checkpoint_dir / f"{step}_checkpoint.json"
        save_json(str(json_file), json_data)
        
        self.metadata["last_checkpoint"] = datetime.now().isoformat()
        tqdm.write(f"💾 Checkpoint saved: {checkpoint_file}")
    
    def load_checkpoint(self, step: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint for specified step."""
        checkpoint_file = self.checkpoint_dir / f"{step}_checkpoint.pkl"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            # Restore state
            self.completed_batches = checkpoint_data.get("completed_batches", set())
            self.step_completed = checkpoint_data.get("step_completed", {})
            self.metadata = checkpoint_data.get("metadata", {})
            self.canon_index = checkpoint_data.get("canon_index")
            
            print(f"📂 Loaded checkpoint: {checkpoint_file}")
            print(f"   Completed batches: {len(self.completed_batches)}")
            print(f"   Last checkpoint: {self.metadata.get('last_checkpoint')}")
            
            return checkpoint_data.get("step_data")
            
        except Exception as e:
            print(f"❌ Failed to load checkpoint {checkpoint_file}: {e}")
            return None
    
    def get_resume_point(self) -> str:
        """Determine where to resume the pipeline."""
        if self.step_completed.get("pruning"):
            return "completed"
        elif self.step_completed.get("tree_building"):
            return "pruning"
        elif self.step_completed.get("canonicalization"):
            return "tree_building"
        elif self.step_completed.get("extraction"):
            return "canonicalization"
        else:
            return "extraction"
    
    def is_batch_completed(self, batch_num: int) -> bool:
        """Check if a batch has been completed."""
        return batch_num in self.completed_batches
    
    def mark_batch_completed(self, batch_num: int, checkpoint_frequency: int = 10):
        """Mark a batch as completed."""
        self.completed_batches.add(batch_num)
        
        # Save progress checkpoint every N batches
        if len(self.completed_batches) % checkpoint_frequency == 0:
            self.save_checkpoint("progress")
    
    def mark_step_completed(self, step: str):
        """Mark a pipeline step as completed."""
        self.step_completed[step] = True
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get human-readable progress summary."""
        return {
            "total_batches": self.metadata.get("total_batches", 0),
            "completed_batches": len(self.completed_batches),
            "completion_percentage": (len(self.completed_batches) / max(1, self.metadata.get("total_batches", 1))) * 100,
            "steps_completed": [k for k, v in self.step_completed.items() if v],
            "current_step": self.get_resume_point(),
            "last_checkpoint": self.metadata.get("last_checkpoint"),
            "runtime": self._calculate_runtime()
        }
    
    def _calculate_runtime(self) -> Optional[str]:
        """Calculate total runtime so far."""
        if not self.metadata.get("start_time"):
            return None
        
        start = datetime.fromisoformat(self.metadata["start_time"])
        now = datetime.now()
        duration = now - start
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"


class CanonIndex:
    """
    Canonicalization index for managing and deduplicating topics.
    Maintains normalized title maps, aliases, and provides fuzzy matching.
    """
    
    def __init__(self):
        self.topics: Dict[str, CanonicalTopic] = {}  # id -> CanonicalTopic
        self.title_map: Dict[str, str] = {}  # normalized_title -> topic_id
        self.alias_map: Dict[str, str] = {}  # normalized_alias -> topic_id
        self._id_counter = 0
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for matching: lowercase, remove punctuation, etc."""
        # Remove accents and normalize unicode
        title = unicodedata.normalize('NFD', title)
        title = ''.join(c for c in title if unicodedata.category(c) != 'Mn')
        
        # Lowercase and remove punctuation/whitespace
        title = re.sub(r'[^\w\s]', '', title.lower())
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def _generate_id(self, candidate: TopicCandidate) -> str:
        """Generate a stable ID for a topic."""
        self._id_counter += 1
        # Create slug from bucket and title
        title_slug = re.sub(r'[^\w\s-]', '', candidate.title.lower())
        title_slug = re.sub(r'[-\s]+', '_', title_slug)
        return f"{candidate.bucket}/{title_slug}_{self._id_counter}"
    
    def add_new(self, candidate: TopicCandidate) -> str:
        """Add a new canonical topic from candidate."""
        topic_id = self._generate_id(candidate)
        
        canonical = CanonicalTopic(
            id=topic_id,
            title=candidate.title,
            bucket=candidate.bucket,
            summary=candidate.summary,
            page_type=candidate.page_type,
            aliases=candidate.aliases.copy(),
            example_refs=candidate.example_refs.copy()
        )
        
        self.topics[topic_id] = canonical
        
        # Update indexes
        norm_title = self.normalize_title(candidate.title)
        self.title_map[norm_title] = topic_id
        
        for alias in candidate.aliases:
            norm_alias = self.normalize_title(alias)
            self.alias_map[norm_alias] = topic_id
        
        return topic_id
    
    def merge(self, target_id: str, candidate: TopicCandidate) -> None:
        """Merge candidate into existing canonical topic."""
        if target_id not in self.topics:
            raise ValueError(f"Target topic {target_id} not found")
        
        target = self.topics[target_id]
        
        # Union aliases
        new_aliases = set(target.aliases) | set(candidate.aliases)
        target.aliases = list(new_aliases)
        
        # Union example refs
        new_refs = set(target.example_refs) | set(candidate.example_refs)
        target.example_refs = list(new_refs)
        
        # Update alias map
        for alias in candidate.aliases:
            norm_alias = self.normalize_title(alias)
            self.alias_map[norm_alias] = target_id
    
    def find_match(self, candidate: TopicCandidate) -> Optional[str]:
        """Find potential match for candidate. Returns topic_id if found."""
        norm_title = self.normalize_title(candidate.title)
        
        # Exact title match
        if norm_title in self.title_map:
            return self.title_map[norm_title]
        
        # Alias match
        if norm_title in self.alias_map:
            return self.alias_map[norm_title]
        
        # Check candidate aliases against existing
        for alias in candidate.aliases:
            norm_alias = self.normalize_title(alias)
            if norm_alias in self.title_map:
                return self.title_map[norm_alias]
            if norm_alias in self.alias_map:
                return self.alias_map[norm_alias]
        
        return None
    
    def propose_merge_targets(self, candidate: TopicCandidate, k: int = 5) -> List[Dict[str, Any]]:
        """Propose k best merge targets for candidate using fuzzy matching."""
        norm_candidate = self.normalize_title(candidate.title)
        candidate_tokens = set(norm_candidate.split())
        
        scores = []
        
        for topic_id, topic in self.topics.items():
            # Skip if different bucket (usually not mergeable)
            if topic.bucket != candidate.bucket:
                continue
            
            # Calculate token Jaccard similarity
            norm_topic = self.normalize_title(topic.title)
            topic_tokens = set(norm_topic.split())
            
            if not topic_tokens:
                continue
            
            jaccard = len(candidate_tokens & topic_tokens) / len(candidate_tokens | topic_tokens)
            
            # Boost score if candidate title appears in topic aliases
            alias_boost = 0
            for alias in topic.aliases:
                norm_alias = self.normalize_title(alias)
                alias_tokens = set(norm_alias.split())
                if alias_tokens:
                    alias_jaccard = len(candidate_tokens & alias_tokens) / len(candidate_tokens | alias_tokens)
                    alias_boost = max(alias_boost, alias_jaccard)
            
            final_score = max(jaccard, alias_boost)
            
            if final_score > 0.3:  # Minimum threshold
                scores.append((final_score, topic_id, topic))
        
        # Sort by score and return top k
        scores.sort(reverse=True)
        
        targets = []
        for score, topic_id, topic in scores[:k]:
            targets.append({
                'id': topic_id,
                'title': topic.title,
                'bucket': topic.bucket,
                'aliases': topic.aliases,
                'score': score
            })
        
        return targets
    
    def materialize(self) -> List[CanonicalTopic]:
        """Return all canonical topics as a list."""
        return list(self.topics.values())


# Typed LLM wrappers
async def llm_typed_call_A(batch: List[Dict[str, Any]], output_model) -> TopicExtractionResult:
    """Step A: Extract topics from logbook batch."""
    prompt = build_prompt_A(batch)
    
    model_config = WIKI_MODELS["extract"]
    
    response = await asyncio.to_thread(
        get_chat_completion,
        model_config=model_config,
        message=prompt,
        output_model=output_model,
    )
    
    return response


async def llm_typed_call_B_incremental(candidate: TopicCandidate, shortlist: List[Dict[str, Any]], output_model) -> CanonicalizeDecision:
    """Step B1: Incremental canonicalization decision."""
    prompt = build_prompt_B_incremental(candidate, shortlist)
    
    model_config = WIKI_MODELS["canon_incremental"]
    
    response = await asyncio.to_thread(
        get_chat_completion,
        model_config=model_config,
        message=prompt,
        output_model=output_model,
    )
    
    return response


async def llm_typed_call_B_global(canon_topics: List[CanonicalTopic]) -> List[CanonicalTopic]:
    """Step B2: Global canonicalization finalization."""
    prompt = build_prompt_B_global(canon_topics)
    
    model_config = WIKI_MODELS["canon_global"]
    
    response = await asyncio.to_thread(
        get_chat_completion,
        model_config=model_config,
        message=prompt,
        output_model=List[CanonicalTopic],
    )
    
    return response


async def llm_typed_call_C(canon_topics: List[CanonicalTopic], max_children: int = MAX_CHILDREN) -> TreeBuildResult:
    """Step C: Build tree structure."""
    prompt = build_prompt_C(canon_topics, max_children)
    
    model_config = WIKI_MODELS["tree"]
    
    response = await asyncio.to_thread(
        get_chat_completion,
        model_config=model_config,
        message=prompt,
        output_model=TreeBuildResult,
    )
    
    return response


async def llm_typed_call_D(tree_build_result: TreeBuildResult, target_leaves: int = TARGET_LEAVES) -> PruneResult:
    """Step D: Prioritize and prune tree."""
    prompt = build_prompt_D(tree_build_result, target_leaves)
    
    model_config = WIKI_MODELS["prune"]
    
    response = await asyncio.to_thread(
        get_chat_completion,
        model_config=model_config,
        message=prompt,
        output_model=PruneResult,
    )
    
    return response


def apply_decision(decision: CanonicalizeDecision, candidate: TopicCandidate, canon_index: CanonIndex) -> str:
    """Apply canonicalization decision to the index."""
    if decision.action == "merge":
        if not decision.target_id:
            raise ValueError("Merge decision must specify target_id")
        canon_index.merge(decision.target_id, candidate)
        return decision.target_id
    else:  # action == "new"
        # Update candidate with any improvements from decision
        if decision.canonical_title:
            candidate.title = decision.canonical_title
        if decision.bucket:
            candidate.bucket = decision.bucket
        if decision.aliases_to_add:
            candidate.aliases.extend(decision.aliases_to_add)
        
        return canon_index.add_new(candidate)


async def run_pipeline(logbook_path: str, output_dir: str, since: Optional[datetime] = None, until: Optional[datetime] = None, batch_size: int = BATCH_SIZE, resume: bool = True, fresh_start: bool = False, checkpoint_frequency: int = 10) -> Dict[str, str]:
    """
    Run the complete WIKI tree-building pipeline.
    
    Args:
        logbook_path: Path to logbook JSONL file
        output_dir: Directory to save output artifacts
        since: Only process entries after this date (defaults to 3 years ago)
        until: Only process entries before this date (optional)
        batch_size: Number of logbook entries to process per batch (default: 50)
        resume: Whether to resume from checkpoints (default: True)
        fresh_start: Whether to start fresh, ignoring checkpoints (default: False)
        checkpoint_frequency: Save checkpoints and update Markdown every N batches (default: 10)
        
    Returns:
        Dict with paths to generated artifacts
    """
    if since is None:
        since = datetime.now() - timedelta(days=365 * TIME_WINDOW_YEARS)
    
    # Initialize state management
    state = PipelineState(output_dir)
    
    # Handle fresh start vs resume
    if fresh_start:
        print("🔄 Starting fresh - ignoring any existing checkpoints")
        # Clear checkpoint directory
        import shutil
        if state.checkpoint_dir.exists():
            shutil.rmtree(state.checkpoint_dir)
        state.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    elif resume:
        # Try to load existing checkpoint
        checkpoint_data = state.load_checkpoint("progress")
        if checkpoint_data:
            print("📂 Resuming from checkpoint...")
            progress = state.get_progress_summary()
            print(f"   Progress: {progress['completed_batches']}/{progress['total_batches']} batches ({progress['completion_percentage']:.1f}%)")
            print(f"   Runtime so far: {progress['runtime']}")
            print(f"   Current step: {progress['current_step']}")
    
    print(f"Starting WIKI pipeline...")
    print(f"Logbook: {logbook_path}")
    print(f"Output: {output_dir}")
    print(f"Batch size: {batch_size}")
    print(f"Processing entries since: {since}")
    if until:
        print(f"Processing entries until: {until}")
    
    # First pass: collect all entries to get total count for progress bar
    entries_list = list(load_jsonl_stream(logbook_path, since=since, until=until, newest_first=True))
    total_entries = len(entries_list)
    total_batches = (total_entries + batch_size - 1) // batch_size  # Ceiling division
    
    # Update state metadata
    if not state.metadata.get("start_time"):
        state.metadata["start_time"] = datetime.now().isoformat()
    state.metadata.update({
        "total_entries": total_entries,
        "total_batches": total_batches,
        "batch_size": batch_size,
        "date_range": {
            "since": since.isoformat(),
            "until": until.isoformat() if until else None
        },
        "config": {
            "logbook_path": logbook_path,
            "models": WIKI_MODELS
        }
    })
    
    print(f"Found {total_entries} entries, processing in {total_batches} batches...")
    
    # Initialize or restore canonicalization index
    if state.canon_index is None:
        canon_index = CanonIndex()
        state.canon_index = canon_index
    else:
        canon_index = state.canon_index
        print(f"📂 Restored canonicalization index with {len(canon_index.topics)} topics")
    
    total_candidates = 0
    total_canonical = len(canon_index.topics)
    
    # Step A + B1: Extraction and canonicalization with checkpoints
    resume_point = state.get_resume_point()
    if resume_point not in ["extraction", "completed"]:
        print(f"⏭️  Skipping extraction - resuming from {resume_point}")
        batch_pbar = tqdm(total=total_batches, desc="Skipping batches", unit="batch")
        batch_pbar.update(total_batches)
        batch_pbar.close()
    else:
        print("\n🔄 Step A + B1: Extracting and canonicalizing topics...")
        
        # Create progress bar for batches
        completed_count = len(state.completed_batches)
        batch_pbar = tqdm(total=total_batches, initial=completed_count, desc="Processing batches", unit="batch")
        
        for batch_num, batch in enumerate(batched(entries_list, batch_size), 1):
            # Skip already completed batches
            if state.is_batch_completed(batch_num):
                continue
                
            batch_pbar.set_description(f"Batch {batch_num}/{total_batches} ({len(batch)} entries)")
            
            try:
                # Step A: Extract topics
                extraction = await llm_typed_call_A(batch, TopicExtractionResult)
                
                # Process each durable candidate with progress
                durable_candidates = [c for c in extraction.topics if c.durability == "durable"]
                
                if durable_candidates:
                    candidate_pbar = tqdm(durable_candidates, desc=f"  Canonicalizing topics", leave=False, unit="topic")
                    
                    for candidate in candidate_pbar:
                        total_candidates += 1
                        candidate_pbar.set_description(f"  Processing: {candidate.title[:40]}...")
                        
                        # Step B1: Incremental canonicalization
                        shortlist = canon_index.propose_merge_targets(candidate, k=5)
                        decision = await llm_typed_call_B_incremental(candidate, shortlist, CanonicalizeDecision)
                        
                        topic_id = apply_decision(decision, candidate, canon_index)
                        
                        if decision.action == "new":
                            total_canonical += 1
                            tqdm.write(f"  ✓ New topic: {candidate.title}")
                        else:
                            tqdm.write(f"  ↗ Merged: {candidate.title} -> {decision.target_id}")
                    
                    candidate_pbar.close()
                
                # Mark batch as completed and update state
                state.mark_batch_completed(batch_num, checkpoint_frequency)
                state.canon_index = canon_index  # Update state with current index
                
                # Update live Markdown at same frequency as checkpoints
                if len(state.completed_batches) % checkpoint_frequency == 0:
                    current_topics = canon_index.materialize()
                    if current_topics:  # Only update if we have topics
                        markdown_path = f"{output_dir}/wiki_tree_live.md"
                        render_tree_markdown(current_topics, output_path=markdown_path)
                
            except Exception as e:
                tqdm.write(f"❌ Error processing batch {batch_num}: {e}")
                continue
            
            batch_pbar.update(1)
            batch_pbar.set_postfix({
                "candidates": total_candidates,
                "canonical": total_canonical
            })
        
        batch_pbar.close()
        
        # Mark extraction step as completed
        state.mark_step_completed("extraction")
        state.save_checkpoint("extraction_complete")
    
    print(f"Extracted {total_candidates} durable candidates, canonicalized to {total_canonical} topics")
    
    # Step B2: Global canonicalization finalization
    resume_point = state.get_resume_point()
    if resume_point in ["tree_building", "pruning", "completed"]:
        print("⏭️  Skipping global canonicalization - loading from checkpoint")
        checkpoint_data = state.load_checkpoint("canonicalization_complete")
        final_canon = checkpoint_data.get("final_canon") if checkpoint_data else canon_index.materialize()
    else:
        print("\n🔄 Step B2: Global canonicalization finalization...")
        canon_topics = canon_index.materialize()
        
        with tqdm(total=1, desc="Global canonicalization", unit="step") as pbar:
            try:
                pbar.set_description(f"Processing {len(canon_topics)} canonical topics...")
                final_canon = await llm_typed_call_B_global(canon_topics)
                pbar.update(1)
                tqdm.write(f"✓ Final canonical topics: {len(final_canon)}")
            except Exception as e:
                tqdm.write(f"❌ Error in global canonicalization: {e}")
                final_canon = canon_topics  # Fall back to incremental result
                pbar.update(1)
        
        # Mark canonicalization step as completed and save checkpoint
        state.mark_step_completed("canonicalization")
        state.save_checkpoint("canonicalization_complete", {"final_canon": final_canon})
    
    # Save canonical topics
    canon_path = f"{output_dir}/canonical_topics.json"
    save_json(canon_path, [topic.model_dump() for topic in final_canon])
    print(f"Saved canonical topics: {canon_path}")
    
    # Generate live Markdown for topics (Step 1)
    markdown_path = f"{output_dir}/wiki_tree_live.md"
    render_tree_markdown(final_canon, output_path=markdown_path)
    
    # Step C: Build tree
    print("\nStep C: Building tree structure...")
    
    with tqdm(total=1, desc="Tree building", unit="step") as pbar:
        try:
            pbar.set_description(f"Building tree from {len(final_canon)} topics...")
            tree_result = await llm_typed_call_C(final_canon, max_children=MAX_CHILDREN)
            pbar.update(1)
            tqdm.write(f"✓ Built tree with {len(tree_result.tree)} root nodes")
            
            tree_path = f"{output_dir}/tree.json"
            save_json(tree_path, tree_result.model_dump())
            tqdm.write(f"✓ Saved tree: {tree_path}")
            
            # Update live Markdown with tree structure (Step 2)
            render_tree_markdown(final_canon, tree_result, output_path=markdown_path)
            
        except Exception as e:
            tqdm.write(f"❌ Error building tree: {e}")
            return {"error": f"Tree building failed: {e}"}
    
    # Step D: Prioritize and prune
    print("\nStep D: Prioritizing and pruning...")
    
    with tqdm(total=1, desc="Prioritizing & pruning", unit="step") as pbar:
        try:
            pbar.set_description(f"Prioritizing tree (target: {TARGET_LEAVES} leaves)...")
            prune_result = await llm_typed_call_D(tree_result, target_leaves=TARGET_LEAVES)
            pbar.update(1)
            tqdm.write(f"✓ Final tree with priorities assigned")
            
            final_path = f"{output_dir}/pruned_tree.json"
            save_json(final_path, prune_result.model_dump())
            tqdm.write(f"✓ Saved final tree: {final_path}")
            
            # Final live Markdown with complete tree and priorities (Step 3)
            render_tree_markdown(final_canon, tree_result, prune_result, output_path=markdown_path)
            
        except Exception as e:
            tqdm.write(f"❌ Error in pruning: {e}")
            return {"error": f"Pruning failed: {e}"}
    
    print("\nPipeline completed successfully!")
    
    return {
        "canonical_topics": canon_path,
        "tree": tree_path,
        "final_tree": final_path,
        "markdown": markdown_path
    }


# Convenience function for external usage
def run_pipeline_sync(logbook_path: str, output_dir: str, since: Optional[datetime] = None, until: Optional[datetime] = None, batch_size: int = BATCH_SIZE, resume: bool = True, fresh_start: bool = False, checkpoint_frequency: int = 10) -> Dict[str, str]:
    """Synchronous wrapper for run_pipeline."""
    return asyncio.run(run_pipeline(logbook_path, output_dir, since, until, batch_size, resume, fresh_start, checkpoint_frequency))
