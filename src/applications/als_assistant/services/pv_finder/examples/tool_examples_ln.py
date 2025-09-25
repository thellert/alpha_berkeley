"""
PV Finder Examples - LN System
"""

from ..examples_loader import PVFinderToolExample

ln_examples = [
    PVFinderToolExample(
        system="LN",
        query_type="misc",
        keywords=['VVR', 'vacuum valve', 'positions'],
        query='Check the positions of all LN VVR valves',
        tool_name="get_field_data",
        tool_args={'system': 'LN', 'family': 'VVR', 'field': 'setup', 'subfield': 'Position'}
    ),
    PVFinderToolExample(
        system="LN",
        query_type="PV",
        keywords=['AS', 'AS2', 'Accelerating Structure'],
        query='What are the AS2 setpoints?',
        tool_name="list_channel_names",
        tool_args={'system': 'LN', 'family': 'AS', 'field': 'Setpoint', 'sectors': [1]}
    ),
    PVFinderToolExample(
        system="LN",
        query_type="PV",
        keywords=['AS', 'AS2', 'Accelerating Structure', 'phase'],
        query="What's the AS2 phase readback?",
        tool_name="list_channel_names",
        tool_args={'system': 'LN', 'family': 'AcceleratingStructure', 'field': 'Monitor', 'sectors': [1], 'devices': [1]}
    ),
    PVFinderToolExample(
        system="LN",
        query_type="misc",
        keywords=['AS', 'AS1', 'AS2', 'Accelerating Structure', 'phase', 'common names', 'names'],
        query='What are the common names for the accelerating structure?',
        tool_name="list_common_names",
        tool_args={'system': 'LN', 'family': 'AcceleratingStructure'}
    ),
    PVFinderToolExample(
        system="LN",
        query_type="PV",
        keywords=['Master', 'Master phase', 'phase'],
        query="What's the master phase setpoint?",
        tool_name="list_channel_names",
        tool_args={'system': 'LN', 'family': 'AcceleratingStructure', 'field': 'MasterPhase'}
    ),
    PVFinderToolExample(
        system="LN",
        query_type="PV",
        keywords=['Quad', 'quadrupole'],
        query="What's the linac Q1.1 quadrupole setpoint?",
        tool_name="list_channel_names",
        tool_args={'system': 'LN', 'family': 'Quad', 'field': 'Setpoint', 'devices': [1]}
    ),
    PVFinderToolExample(
        system="LN",
        query_type="PV",
        keywords=['SOL', 'solenoid', 'solenoid magnet'],
        query='Get all linac soleniod golden values',
        tool_name="list_channel_names",
        tool_args={'system': 'LN', 'family': 'SOL', 'field': 'SetpointGolden'}
    ),
    ##############################
    # System Fallback Examples
    ##############################
    PVFinderToolExample(
        system="LN",
        query_type="fallback",
        keywords=['families', 'available', 'explore', 'help', 'list', 'what', 'show'],
        query='What families are available in the linac?',
        tool_name="list_families",
        tool_args={'system': 'LN'}
    ),
]
