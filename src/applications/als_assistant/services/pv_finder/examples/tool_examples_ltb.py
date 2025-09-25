"""
PV Finder Examples - LTB System
"""

from ..examples_loader import PVFinderToolExample

ltb_examples = [
    PVFinderToolExample(
        system="LTB",
        query_type="misc",
        keywords=['LTB', 'expert', 'fields'],
        query='List all available setup fields for the LTB BPMs.',
        tool_name="inspect_fields",
        tool_args={'system': 'LTB', 'family': 'BPM', 'field': 'setup'}
    ),
    PVFinderToolExample(
        system="LTB",
        query_type="misc",
        keywords=['VVR', 'vacuum valve', 'positions'],
        query='Check the positions of all LTB VVR valves',
        tool_name="get_field_data",
        tool_args={'system': 'LTB', 'family': 'VVR', 'field': 'setup', 'subfield': 'Position'}
    ),
    PVFinderToolExample(
        system="LTB",
        query_type="PV",
        keywords=['dipole', 'BEND', 'ready'],
        query='Check if the last LTB dipole is ready',
        tool_name="list_channel_names",
        tool_args={'system': 'LTB', 'family': 'BEND', 'field': 'Ready', 'devices': [4]}
    ),
    PVFinderToolExample(
        system="LTB",
        query_type="PV",
        keywords=['TV', 'screen', 'move in', 'insert', 'beam viewer', 'last screen'],
        query='How do I insert the last TV screen in the LTB beamline?',
        tool_name="list_channel_names",
        tool_args={'system': 'LTB', 'family': 'TV', 'field': 'InControl', 'devices': [5]}
    ),
    
    ##############################
    # System Fallback Examples
    ##############################
    PVFinderToolExample(
        system="LTB",
        query_type="fallback",
        keywords=['families', 'available', 'explore', 'help', 'list', 'what', 'show'],
        query='What families are available in the linac-to-booster transfer line?',
        tool_name="list_families",
        tool_args={'system': 'LTB'}
    ),
]
