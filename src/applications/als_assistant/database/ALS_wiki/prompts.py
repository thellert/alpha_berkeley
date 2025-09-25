"""
Prompt builders for the ALS Accelerator WIKI tree-building algorithm.
Each function builds a schema-bound prompt for the corresponding pipeline step.
"""

from typing import List, Dict, Any
from .schemas import TopicCandidate, CanonicalTopic, TreeBuildResult


def build_prompt_A(batch: List[Dict[str, Any]]) -> str:
    """
    Build prompt for Step A: Extract candidate topics from logbook entries.
    
    Args:
        batch: List of logbook entries, each with keys: id, subject, details, category, etc.
        
    Returns:
        Formatted prompt string for topic extraction
    """
    # Format the batch entries for the prompt
    entries_text = ""
    for entry in batch:
        entry_id = entry.get('id', 'unknown')
        subject = entry.get('subject', '')
        details = entry.get('details', '')
        category = entry.get('category', '')
        
        entries_text += f"Entry {entry_id}:\n"
        entries_text += f"Subject: {subject}\n"
        if details:
            entries_text += f"Details: {details}\n"
        if category:
            entries_text += f"Category: {category}\n"
        entries_text += "\n"
    
    prompt = f"""From the batch of logbook texts below, propose up to THREE durable topics per entry for the ALS WIKI.

INSTRUCTIONS:
- Focus on durable, reusable knowledge that remains valid beyond the specific incident
- Ignore ephemeral operational content (shift changes, tours, daily statuses, routine announcements)
- For each durable topic, extract: title, bucket, summary, page_type, durability, why_static, aliases
- Titles must be <60 characters and avoid dates or shift IDs
- Use concise, canonical phrasing

BUCKETS (choose exactly one):
Injector, Booster, BTS, Storage Ring, RF, Magnets, Power Supplies, Insertion Devices, Diagnostics, Vacuum, Timing, Controls, Safety, Operations, Procedures, Playbooks

PAGE_TYPES (choose one):
overview, concept, procedure, playbook, faq

Return a JSON object that validates against TopicExtractionResult schema.

LOGBOOK ENTRIES:
{entries_text}

Response (JSON only):"""

    return prompt


def build_prompt_B_incremental(candidate: TopicCandidate, shortlist: List[Dict[str, Any]]) -> str:
    """
    Build prompt for Step B1: Incremental canonicalization decision.
    
    Args:
        candidate: The new TopicCandidate to process
        shortlist: List of potential merge targets with keys: id, title, bucket, aliases
        
    Returns:
        Formatted prompt string for canonicalization decision
    """
    # Format the candidate
    candidate_text = f"""NEW CANDIDATE:
Title: {candidate.title}
Bucket: {candidate.bucket}
Summary: {candidate.summary}
Page Type: {candidate.page_type}
Aliases: {candidate.aliases}"""

    # Format the shortlist
    shortlist_text = ""
    if shortlist:
        shortlist_text = "POTENTIAL MERGE TARGETS:\n"
        for i, target in enumerate(shortlist, 1):
            shortlist_text += f"{i}. ID: {target['id']}\n"
            shortlist_text += f"   Title: {target['title']}\n"
            shortlist_text += f"   Bucket: {target['bucket']}\n"
            shortlist_text += f"   Aliases: {target.get('aliases', [])}\n\n"
    else:
        shortlist_text = "No potential merge targets found.\n"

    prompt = f"""Given ONE TopicCandidate and a shortlist of possible targets, decide whether to MERGE into one target or create a NEW canonical topic.

INSTRUCTIONS:
- If the candidate is sufficiently similar to an existing target, choose action="merge" and specify target_id
- If the candidate is unique enough, choose action="new"
- Ensure exactly one bucket assignment
- Prefer concise canonical phrasing; avoid dates or shift IDs
- Consider semantic similarity, not just string matching

{candidate_text}

{shortlist_text}

Return a JSON object that validates against CanonicalizeDecision schema.

Response (JSON only):"""

    return prompt


def build_prompt_B_global(canon_topics: List[CanonicalTopic]) -> str:
    """
    Build prompt for Step B2: Global canonicalization finalization.
    
    Args:
        canon_topics: Current list of canonical topics
        
    Returns:
        Formatted prompt string for global canonicalization
    """
    # Format the canonical topics (limit to prevent prompt overflow)
    topics_text = ""
    for i, topic in enumerate(canon_topics[:100]):  # Limit for prompt size
        topics_text += f"{i+1}. ID: {topic.id}\n"
        topics_text += f"   Title: {topic.title}\n"
        topics_text += f"   Bucket: {topic.bucket}\n"
        topics_text += f"   Aliases: {topic.aliases}\n"
        topics_text += f"   Summary: {topic.summary[:100]}...\n\n"
    
    if len(canon_topics) > 100:
        topics_text += f"... and {len(canon_topics) - 100} more topics\n"

    prompt = f"""Given the current list of CanonicalTopic objects, propose safe merges to remove near-duplicates and finalize titles, buckets, and aliases.

INSTRUCTIONS:
- Look for near-duplicate topics that should be merged
- Finalize canonical titles (max 60 chars, no dates/shift IDs)
- Ensure exactly one bucket per topic
- Preserve example_refs unions when merging
- Be conservative - only merge if clearly duplicates
- Return the complete final list with unique IDs

CURRENT CANONICAL TOPICS:
{topics_text}

Return a JSON list of CanonicalTopic objects (the final canonical set).

Response (JSON only):"""

    return prompt


def build_prompt_C(canon_topics: List[CanonicalTopic], max_children: int = 7) -> str:
    """
    Build prompt for Step C: Tree induction from canonical topics.
    
    Args:
        canon_topics: Finalized canonical topics
        max_children: Maximum children per node
        
    Returns:
        Formatted prompt string for tree building
    """
    # Group topics by bucket for the prompt
    buckets = {}
    for topic in canon_topics:
        if topic.bucket not in buckets:
            buckets[topic.bucket] = []
        buckets[topic.bucket].append(topic)
    
    topics_by_bucket_text = ""
    for bucket, topics in buckets.items():
        topics_by_bucket_text += f"\n{bucket} ({len(topics)} topics):\n"
        for topic in topics[:20]:  # Limit per bucket
            topics_by_bucket_text += f"  - {topic.title} ({topic.page_type})\n"
        if len(topics) > 20:
            topics_by_bucket_text += f"  ... and {len(topics) - 20} more\n"

    prompt = f"""Build a compact 2–3 level hierarchy from canonical topics.

INSTRUCTIONS:
- Create a tree structure grouped by bucket
- Max {max_children} children per node; overflow goes into "FAQ & Misc"
- Prefer merging thin/related topics into parent pages as sections (not separate pages)
- Build 2-3 levels: Bucket → Category → Specific Topic
- Use clear, descriptive node titles
- Set topic_refs to reference canonical topic IDs for leaf nodes

CONSTRAINTS:
- Max {max_children} children per node
- Group overflow into "FAQ & Misc" nodes
- Prefer sections over separate pages for small topics

CANONICAL TOPICS BY BUCKET:
{topics_by_bucket_text}

Return a JSON object that validates against TreeBuildResult schema.

Response (JSON only):"""

    return prompt


def build_prompt_D(tree_build_result: TreeBuildResult, target_leaves: int = 500) -> str:
    """
    Build prompt for Step D: Prioritize and prune the tree.
    
    Args:
        tree_build_result: Result from tree building step
        target_leaves: Target number of leaf pages
        
    Returns:
        Formatted prompt string for prioritization and pruning
    """
    # Count current leaves and format tree structure
    def count_leaves(nodes):
        count = 0
        for node in nodes:
            if not node.children:
                count += 1
            else:
                count += count_leaves(node.children)
        return count
    
    def format_tree(nodes, indent=0):
        text = ""
        for node in nodes:
            prefix = "  " * indent
            leaf_marker = " (LEAF)" if not node.children else ""
            text += f"{prefix}- {node.title}{leaf_marker}\n"
            if node.children:
                text += format_tree(node.children, indent + 1)
        return text
    
    current_leaves = count_leaves(tree_build_result.tree)
    tree_structure = format_tree(tree_build_result.tree)
    
    action_needed = ""
    if current_leaves > target_leaves:
        excess = current_leaves - target_leaves
        action_needed = f"\nACTION NEEDED: Current tree has {current_leaves} leaves, target is {target_leaves}. Please merge {excess} lowest-value 'could' leaves into nearest parent sections."

    prompt = f"""Assign each leaf page a priority: must | should | could.

CRITERIA for priority assignment:
- MUST: Critical for safety, frequently referenced, core operational knowledge
- SHOULD: Important for operators, useful troubleshooting, standard procedures  
- COULD: Nice to have, specialized knowledge, edge cases

EVALUATION FACTORS:
- Usefulness for operators 6–12 months later
- Reusability across different situations
- Safety relevance
- Frequency of reference (but don't over-weight this)

CURRENT TREE STRUCTURE ({current_leaves} leaves):
{tree_structure}
{action_needed}

If total leaves > {target_leaves}, merge lowest-value 'could' leaves into nearest parent sections and update the tree structure accordingly.

Return a JSON object that validates against PruneResult schema.

Response (JSON only):"""

    return prompt
