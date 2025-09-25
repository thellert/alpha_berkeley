"""
PV Finder Examples - GTL System
"""

from ..examples_loader import PVFinderToolExample

gtl_examples = [
    PVFinderToolExample(
        system="GTL",
        query_type="pyAT",
        keywords=['quadrupole', 'model', 'pyAT', 'ATIndex'],
        query='Get the GTL quadrupole indices from the accelerator toolbox model',
        tool_name="get_field_data",
        tool_args={'system': 'GTL', 'family': 'Quad', 'field': 'setup', 'subfield': 'AT.ATIndex'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="misc",
        keywords=['families', 'GTL'],
        query='Get a list of all GTL families available',
        tool_name="list_families",
        tool_args={'system': 'GTL'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['HCM', 'corrector', 'setpoints'],
        query='Get the setpoint PV channels for all horizontal GTL corrector magnets',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'HCM', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['HCM', 'monitor', 'readback', 'RBV', 'device 2'],
        query='Get the second HCM readback channel in the gun.',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'HCM', 'field': 'Monitor', 'devices': [2]}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="structure",
        keywords=['VCM', 'vertical corrector', 'on/off', 'switch'],
        query='Examine the on/off control structure for VCM magnets',
        tool_name="inspect_fields",
        tool_args={'system': 'GTL', 'family': 'VCM', 'field': 'OnControl'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="misc",
        keywords=['quad', 'quadrupole', 'setup', 'device list'],
        query='Get the GTL quadrupole device list.',
        tool_name="get_field_data",
        tool_args={'system': 'GTL', 'family': 'Quad', 'field': 'setup', 'subfield': 'DeviceList'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="misc",
        keywords=['BPM', 'hardware units'],
        query='Get the hardware units for the GTL horizontal BPM channels',
        tool_name="get_field_data",
        tool_args={'system': 'GTL', 'family': 'BPM', 'field': 'X', 'subfield': 'HWUnits'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['BuckingCoil', 'on/off'],
        query='Get the OnControl channels for the bucking coils',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'BuckingCoil', 'field': 'OnControl'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="structure",
        keywords=['DCCT', 'bunch charge', 'charge', 'injection efficiency'],
        query='Inspect the DCCT monitor data structure',
        tool_name="inspect_fields",
        tool_args={'system': 'GTL', 'family': 'DCCT', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['SHB', 'cavity', 'high voltage'],
        query='Get the SHB high-voltage control channels',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'SHB', 'field': 'HVControl'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['SHB', 'SHB2', 'buncher', 'subharmonic'],
        query='Get the SHB 2 Phase RBV value',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'SHB', 'field': 'PhaseMonitor', 'devices': [2]}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['SHB', 'SHB1', 'buncher', 'subharmonic'],
        query='Whats the value of the SHB 1 Phase monitor',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'SHB', 'field': 'PhaseMonitor', 'devices': [1]}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="misc",
        keywords=['BEND', 'ramp rate'],
        query='Get the ramp rate for the BEND setpoints',
        tool_name="get_field_data",
        tool_args={'system': 'GTL', 'family': 'BEND', 'field': 'Setpoint', 'subfield': 'RampRate'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="structure",
        keywords=['Trigger', 'event counter', 'structure'],
        query='Examine the Trigger EvtCounter field structure',
        tool_name="inspect_fields",
        tool_args={'system': 'GTL', 'family': 'Trigger', 'field': 'EvtCounter'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['SOL', 'solenoid', 'solenoid magnet'],
        query='Get the setpoint PVs for the GTL soleniod magnets',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'SOL', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['SOL', 'solenoid', 'RBV', 'readback'],
        query='Whats the third solenoid readback?',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'SOL', 'field': 'Monitor', 'devices': [3]}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['TV', 'lamp', 'control'],
        query='Get the GTL TV4 lamp control channels',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'TV', 'field': 'LampControl', 'devices': [4]}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['gun', 'e gun', 'e-gun', 'names'],
        query='What are the common names of the e-guns channels?',
        tool_name="list_common_names",
        tool_args={'system': 'GTL', 'family': 'GUN'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['gun', 'e gun', 'e-gun'],
        query='Whats the E gun phase setpoint?',
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'GUN', 'field': 'Setpoint', 'devices': [3]}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['AS', 'AS2', 'accelerating structure', 'names'],
        query='What are the names of the GTL accelerating structures?',
        tool_name="list_common_names",
        tool_args={'system': 'GTL', 'family': 'AcceleratingStructure'}
    ),
    PVFinderToolExample(
        system="GTL",
        query_type="PV",
        keywords=['MOD', 'mods', 'modulator'],
        query="What's the modulator state PVs?",
        tool_name="list_channel_names",
        tool_args={'system': 'GTL', 'family': 'MOD', 'field': 'State'}
    ),
    
    ##############################
    # System Fallback Examples
    ##############################
    PVFinderToolExample(
        system="GTL",
        query_type="fallback",
        keywords=['families', 'available', 'explore', 'help', 'list', 'what', 'show'],
        query='What families are available in the gun-to-linac system?',
        tool_name="list_families",
        tool_args={'system': 'GTL'}
    ),
]
