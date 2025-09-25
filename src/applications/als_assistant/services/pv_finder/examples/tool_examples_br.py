"""
PV Finder Examples - BR System
"""

from ..examples_loader import PVFinderToolExample

br_examples = [
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['BPM', 'monitor'],
        query='What are the vertical booster BPMs?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'BPM', 'field': 'Y'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['radiation', 'gamma', 'gamma detector', 'gamma monitor', 'dose rate', '1 hour average'],
        query='What is the avergae 1 hour dose rate of the L2 booster gamma monitor?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'GammaRad', 'field': 'DoseRateAvg1Hour', 'sectors': [2]}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['radiation', 'gamma', 'gamma detector', 'gamma monitor', 'dose rate'],
        query='What is the current gamma radiation level in the booster in sector 1 and 6?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'GammaRad', 'field': 'DoseRateInstantaneous', 'sectors': [1, 6]}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['radiation', 'gamma', 'gamma detector', 'gamma monitor', 'dose', '1 hour'],
        query='What is the 1 hour gamma dose in the L7 booster?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'GammaRad', 'field': 'Dose1Hour', 'sectors': [7]}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['extraction kicker', 'extraction', 'kicker'],
        query='What is the booster ring extraction kicker SP?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'ExtractionKicker', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['QF', 'setpoints', 'quad', 'quadrupole', 'focusing', 'magnet'],
        query='Get current setpoints for all booster ring QF magnets',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'QF', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['QD', 'monitor', 'quad', 'quadrupole', 'defocusing', 'magnet'],
        query='Get current monitor values for all QD magnets in sector 2 of the booster ring',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'QD', 'field': 'Monitor', 'sectors': [2]}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['bend', 'offset', 'setpoint', 'magnet', 'ramp'],
        query='What is the offset setpoint for the booster bend magnets?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'BEND', 'field': 'Offset'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['QD', 'offset', 'setpoint', 'quad', 'quadrupole', 'defocusing', 'magnet', 'ramp'],
        query='What are the offset setpoints for the booster QD quadrupole magnets?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'QD', 'field': 'Offset'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['QD', 'gain', 'value', 'setpoint', 'quad', 'quadrupole', 'defocusing', 'magnet', 'ramp'],
        query='What are the gain setpoints for the booster QD quadrupole magnets?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'QD', 'field': 'Gain'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['SEK', 'BR-SEK', 'septum', 'setpoint', 'voltage', 'extraction', 'extraction septum', 'thick'],
        query='What is the booster SEK septum setpoint?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'SEK', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['SEN', 'BR-SEN', 'septum', 'setpoint', 'current', 'extraction', 'extraction septum', 'thin'],
        query='What is the booster SEN septum setpoint?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'SEN', 'field': 'Setpoint'}
    ),
        PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['charge', 'booster charge', 'ICT', 'ramp', 'booster ramp', 'ramp stages'],
        query='What charge measurements are available for different parts of the booster ramp?',
        tool_name="inspect_fields",
        tool_args={'system': 'BR', 'family': 'ICT'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['extraction', 'efficiency', 'booster extraction', 'extraction efficiency'],
        query='What is the booster extraction efficiency?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'Extraction', 'field': 'Efficiency'}
    ),
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['injection', 'efficiency', 'booster injection', 'injection efficiency'],
        query='What is the booster injection efficiency?',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'Injection', 'field': 'Efficiency'}
    ),
    
    PVFinderToolExample(
        system="BR",
        query_type="PV",
        keywords=['VCM', 'vertical corrector', 'corrector magnets', 'corrector', 'CM', 'setpoint', 'vertical'],
        query='Set points of the vertical corrector magnets in sector 4 of the booster.',
        tool_name="list_channel_names",
        tool_args={'system': 'BR', 'family': 'VCM', 'field': 'Setpoint', 'sectors': [4]}
    ),
    
    ##############################
    # System Fallback Examples
    ##############################
    PVFinderToolExample(
        system="BR",
        query_type="fallback",
        keywords=['families', 'available', 'explore', 'help', 'list', 'what', 'show'],
        query='What families are available in the booster ring?',
        tool_name="list_families",
        tool_args={'system': 'BR'}
    ),
]
