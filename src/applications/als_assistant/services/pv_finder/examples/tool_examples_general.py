"""
Tool Examples - General System

Type-safe PVFinderToolExample classes for general cross-system queries.
Contains 1 example for the general system showing tool usage patterns.
"""

from ..examples_loader import PVFinderToolExample

general_examples = [
    PVFinderToolExample(
        system="general",
        query_type="misc",
        keywords=['systems', 'ALS'],
        query='List all available systems in the accelerator',
        tool_name="list_systems",
        tool_args={}
    ),
]
