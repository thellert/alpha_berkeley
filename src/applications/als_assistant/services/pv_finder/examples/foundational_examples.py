"""
Foundational Examples - Core PV Finder Workflows

These examples demonstrate the fundamental patterns that every PV Finder agent should know:
1. System exploration when starting from scratch
2. Family exploration to understand available devices  
3. Successful PV finding workflow
4. Proper handling of failed queries

These replace the old PVResponseExample system with complete tool-to-output workflows.
"""

from ..examples_loader import PVFinderToolExample


foundational_examples = [
    # 1. System Exploration - When you don't know where to start
    PVFinderToolExample(
        system="general",
        query_type="misc", 
        keywords=['systems', 'help', 'available', 'start', 'explore'],
        query="What systems are available? I don't know where to start",
        tool_name="list_systems",
        tool_args={},
        expected_output={
            "pvs": [],
            "description": "Available systems: GTL, LN, LTB, BR, BTS, SR. Use list_families(system='SYSTEM') to explore device families in a specific system."
        }
    ),
    
    # 2. Family Exploration - Learning about a system  
    PVFinderToolExample(
        system="SR",
        query_type="misc",
        keywords=['families', 'devices', 'explore', 'available', 'storage ring'],
        query="What device families are available in the storage ring?",
        tool_name="list_families", 
        tool_args={"system": "SR"},
        expected_output={
            "pvs": [],
            "description": "Available families in SR: BPM, QF, QD, BEND, HCM, VCM, RF, DCCT, etc. Use inspect_fields(system='SR', family='FAMILY') to see available fields for a specific family."
        }
    ),
    
    # 3. Successful PV Query - Complete workflow that finds actual PVs
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['beam', 'current', 'DCCT', 'monitor'],
        query="What's the beam current PV?",
        tool_name="list_channel_names",
        tool_args={"system": "SR", "family": "DCCT", "field": "Monitor"},
        expected_output={
            "pvs": ["SR:DCCT"],
            "description": "Found beam current monitor PV for the storage ring"
        }
    ),
    
    # 4. No Results Found - Proper failure handling with guidance
    PVFinderToolExample(
        system="general",
        query_type="misc",
        keywords=['nonexistent', 'unknown', 'not found', 'error'],
        query="Find PVs for nonexistent device xyz",
        tool_name="list_channel_names",
        tool_args={"system": "SR", "family": "xyz"},
        expected_output={
            "pvs": [],
            "description": "No PVs found matching 'nonexistent device xyz'. Try list_families(system='SR') to see available device families."
        }
    )
]
