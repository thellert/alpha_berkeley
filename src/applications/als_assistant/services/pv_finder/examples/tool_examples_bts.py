"""
PV Finder Examples - BTS System
"""

from ..examples_loader import PVFinderToolExample

bts_examples = [
    PVFinderToolExample(
        system="BTS",
        query_type="PV",
        keywords=['transfer', 'efficiency', 'BTS transfer', 'injection efficiency', 'beam transfer'],
        query='What is the BTS injection efficiency?',
        tool_name="list_channel_names",
        tool_args={'system': 'BTS', 'family': 'Transfer', 'field': 'Efficiency'}
    ),
    PVFinderToolExample(
        system="BTS",
        query_type="PV",
        keywords=['BPM', 'horizontal', 'X', 'beam position monitor'],
        query='Give me the last horizontal BPM reading in the BTS?',
        tool_name="list_channel_names",
        tool_args={'system': 'BTS', 'family': 'BPM', 'field': 'X', 'devices': [6]}
    ),
    PVFinderToolExample(
        system="BTS",
        query_type="PV",
        keywords=['TV', 'TV3', 'screen', 'move in', 'insert', 'beam viewer'],
        query='How do I insert the fifth TV screen in the beamline?',
        tool_name="list_channel_names",
        tool_args={'system': 'BTS', 'family': 'TV', 'field': 'InControl', 'devices': [5]}
    ),
    PVFinderToolExample(
        system="BTS",
        query_type="structure",
        keywords=['TV', 'screen', 'beam viewer', 'monitor screen'],
        query='What fields are available for the BTS TV screens?',
        tool_name="inspect_fields",
        tool_args={'system': 'BTS', 'family': 'TV'}
    ),
    PVFinderToolExample(
        system="BTS",
        query_type="PV",
        keywords=['BEND', 'bending magnet', 'dipole', 'power supply', 'RBV', 'readback', 'current', 'monitor'],
        query='Get the power supply readback current for the last bending magnet',
        tool_name="list_channel_names",
        tool_args={'system': 'BTS', 'family': 'BEND', 'field': 'Monitor', 'devices': [4]}
    ),
    
    ##############################
    # System Fallback Examples
    ##############################
    PVFinderToolExample(
        system="BTS",
        query_type="fallback",
        keywords=['families', 'available', 'explore', 'help', 'list', 'what', 'show'],
        query='What families are available in the BTS transfer line?',
        tool_name="list_families",
        tool_args={'system': 'BTS'}
    ),
]
