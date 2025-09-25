"""
PV Finder Service Prompts

Centralized prompt management for the PV finder service with all
prompt builders consolidated in a single file.
"""

import textwrap
from typing import Optional, Dict, List
from framework.base import BaseExample
from .examples_loader import example_loader
from .util import get_examples_from_keywords
from .examples.query_splitter_examples import query_splitter_examples, QuerySplitterExample

from .examples_loader import PVFinderToolExample
from configs.logger import get_logger
logger = get_logger("als_assistant", "pv_finder")

# ==============================================================================
# QUERY SPLITTER PROMPTS
# ==============================================================================

def _get_query_splitter_base_prompt() -> str:
    """Get the base prompt for query splitter."""
    return textwrap.dedent("""
        You are the PV-Query Coordinator for the Advanced Light Source (ALS) control-system database.

        Your sole task is to decide whether a user query
        (A) refers to a single PV, device, or subsystem and can be passed on directly, or
        (B) must be split into a list of atomic sub-queries because it clearly refers to multiple distinct targets.

        You MUST return ONLY a JSON object with a "queries" field containing a list of strings:
        {"queries": ["query1", "query2", ...]}

        - If the query falls under Category A: return {"queries": ["original query"]}
        - If the query falls under Category B: return {"queries": ["subquery1", "subquery2", ...]}

        Guidelines:
        - Do not speculate or expand on the query.
        - Preserve wording and phrasing exactly as given.
        - If uncertain, prefer Category A (single-element list).
        - Return ONLY the JSON object, no additional text or explanations.
        """).strip()



# ==============================================================================
# KEYWORD EXTRACTOR PROMPTS
# ==============================================================================

def _get_keyword_extractor_base_prompt() -> str:
    """Get the base prompt for keyword extractor."""
    return textwrap.dedent("""
        You are a precise information extraction assistant specialized in accelerator control systems at the Advanced Light Source (ALS). Extract essential query elements and identify the most likely system where the requested information can be found.

        Extract key entities, concepts, technical terms, device names, PV names, and other distinctive information. Then classify the query into one or more of these ALS systems:
        - GTL (Gun-to-Linac transfer line): electron gun, subharmonic bunchers (SHBs)
        - LN (Linac): S-Band Accelerating Structure (AS and AS2), Master Phase, solenoids
        - LTB (Linac-to-Booster transfer line): connects linac to booster ring
        - BR (Booster Ring): accelerates beam from 150 MeV to 1.9 GeV
        - BTS (Booster-to-Storage Ring transfer line): transfers beam to storage ring
        - SR (Storage Ring): including subsystems like BPMs, IDs/EPUs, and EPBI

        You MUST return a JSON object with exactly these fields:
        {
            "keywords": ["keyword1", "keyword2", ...],
            "systems": ["system1", "system2", ...]
        }

        Both fields are required and must be lists of strings (can be empty lists if nothing found).
        """).strip()


# ==============================================================================
# PV QUERY PROMPTS
# ==============================================================================

def _get_pv_query_base_prompt() -> str:
    """Get the base prompt for PV query."""
    return textwrap.dedent("""
        You are a Channel Finder assistant for the Advanced Light Source (ALS), specializing in 
        locating EPICS channel names (process variables or PVs) based on user queries.

        You have access to a database containing a collection of channel metadata. Each document includes:
        - `family`: a high-level category of devices (e.g., "BEND", "QF", "BPM", "HCM")
        - `field`: a property or sub-component (e.g., "Monitor", "Setpoint", "pyAT", "setup")
        - optionally `subfield`: nested metadata fields within a field (e.g., "ChannelNames", "Range", "Units")
        - `value`: the value associated with that field or subfield (often a list of strings)

        APPROACH:
        1) FIRST: Look for relevant examples below that match your query pattern
        2) IF examples provide clear guidance: Follow the demonstrated pattern
        3) IF no examples match your specific query: ACTIVELY EXPLORE the database using your tools
           - Start with list_families() to see what device families are available
           - Use inspect_fields() to understand family structures  
           - Search systematically until you find the requested information
        4) NEVER give up without trying - the database is comprehensive

        When processing user requests:
        1) Never make up an answer.
        2) Use your tools to answer the question
        3) Always return results in the required JSON format
        4) If no matches are found, still return the JSON format with empty pvs list

        You MUST return ONLY a JSON object with exactly these fields:
        {
            "pvs": ["pv1", "pv2", ...],
            "description": "A description of what PVs were found or why none were found"
        }

        Both fields are required. The "pvs" field must be a list of strings (can be empty if no PVs found).
        The "description" field must be a string explaining the results.
        Return ONLY the JSON object, no additional text or explanations.

        Your goal is to provide fast, accurate, and actionable answers. Focus on delivering precise results in the exact JSON format shown above.
        """).strip()


# ==============================================================================
# PUBLIC PROMPT FUNCTIONS
# ==============================================================================

def get_query_splitter_prompt(
    context: Optional[Dict] = None,
    previous_failure: Optional[str] = None,
    max_examples: int = 10
) -> str:
    """Build the complete query splitter prompt with examples."""
    prompt_parts = [_get_query_splitter_base_prompt()]
    
    # Add examples
    examples_text = QuerySplitterExample.join(query_splitter_examples, separator="\n\n", max_examples=max_examples)
    if examples_text:
        prompt_parts.append("\nExamples:\n")
        prompt_parts.append(examples_text)
    
    # Add context if provided
    if context:
        prompt_parts.append(f"\nContext: {context}")
    
    # Add previous failure information if provided
    if previous_failure:
        prompt_parts.append(f"\nPrevious failure to avoid: {previous_failure}")
    
    return "\n".join(prompt_parts)


def get_keyword_extractor_prompt(
    context: Optional[Dict] = None,
    previous_failure: Optional[str] = None,
    system_filter: Optional[str] = None,
    max_examples: Optional[int] = None
) -> str:
    """Build the complete keyword extractor prompt with examples."""
    prompt_parts = [_get_keyword_extractor_base_prompt()]
    
    # Add examples using the existing example loader
    examples_text = example_loader.format_keyword_examples_for_prompt(
        system=system_filter,
        max_examples=max_examples
    )
    if examples_text and examples_text != "No keyword extraction examples available.":
        prompt_parts.append("\n")
        prompt_parts.append(examples_text)
    
    # Add context if provided
    if context:
        prompt_parts.append(f"\nContext: {context}")
    
    # Add previous failure information if provided
    if previous_failure:
        prompt_parts.append(f"\nPrevious failure to avoid: {previous_failure}")
    
    return "\n".join(prompt_parts)


def get_pv_query_prompt(
    keywords: Optional[List[str]] = None,
    systems: Optional[List[str]] = None,
    context: Optional[Dict] = None,
    previous_failure: Optional[str] = None,
    max_examples: int = 20,
    include_base_examples: bool = True,
    max_base_examples: int = 4
) -> str:
    """Build the complete PV query prompt with dynamic examples."""
    prompt_parts = [_get_pv_query_base_prompt()]
    
    # Add foundational examples first (these show complete tool-to-output workflows)
    if include_base_examples:
        foundational_examples = example_loader.get_foundational_examples(max_examples=max_base_examples)
        if foundational_examples:
            foundational_text = PVFinderToolExample.join(foundational_examples)
            if foundational_text.strip():
                prompt_parts.append("\nFoundational Examples (complete workflows):")
                prompt_parts.append(foundational_text)
    
    # Add dynamic examples based on keywords and systems
    matching_examples = []
    if keywords or systems:
        matching_examples = get_examples_from_keywords(
            systems=systems or [],
            keywords=keywords or [],
            num_examples=max_examples
        )
        
        if matching_examples:
            examples_text = PVFinderToolExample.join(matching_examples)
            if examples_text.strip():
                prompt_parts.append("\nRelevant Examples for this query:")
                prompt_parts.append(examples_text)
    
    # Add guidance for exploration when examples don't provide clear direction
    prompt_parts.append("""
EXPLORATION STRATEGY when examples don't directly match your query:
- If you have a system but need to find the right family: Use list_families(system='SYSTEM')
- If you found a family but need to understand its structure: Use inspect_fields(system='SYSTEM', family='FAMILY')
- If you need to search across all systems: Use list_systems() first
- REMEMBER: The database is comprehensive - if something exists in the accelerator, there's likely a PV for it""")
    
    # Add context if provided
    if context:
        prompt_parts.append(f"\nContext: {context}")
    
    # Add previous failure information if provided
    if previous_failure:
        prompt_parts.append(f"\nPrevious failure to avoid: {previous_failure}")

    matching_count = len(matching_examples) if matching_examples else 0
    logger.info(f"PV query prompt built with {matching_count} examples for systems: {systems} and keywords: {keywords}")
    
    return "\n".join(prompt_parts) 