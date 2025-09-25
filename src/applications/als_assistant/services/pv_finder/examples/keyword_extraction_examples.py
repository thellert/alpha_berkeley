"""
Keyword Extraction Examples

Migrated from raw dictionary format to type-safe KeywordExtractionExample classes.
Contains 20 examples for keyword extraction training.
"""

from ..examples_loader import KeywordExtractionExample

keyword_examples = [
    KeywordExtractionExample(
        query='What are the current values of BPMs in the Booster Ring?',
        expected_keywords=['BPM', 'monitor'],
        expected_systems=['BR']
    ),
    KeywordExtractionExample(
        query='Show me the Gun bias voltage setting',
        expected_keywords=['Gun', 'bias', 'voltage', 'setting'],
        expected_systems=['GTL']
    ),
    KeywordExtractionExample(
        query='What is the gap value for EPU11?',
        expected_keywords=['EPU', 'gap', 'EPU11'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='What are the current ID gaps in the storage ring?',
        expected_keywords=['ID', 'gap', 'gaps'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='Show me the phase setpoint for the second subharmonic buncher',
        expected_keywords=['SHB', 'SHB2', 'phase', 'setpoint'],
        expected_systems=['GTL']
    ),
    KeywordExtractionExample(
        query='What is the status of TV2 in the LTB?',
        expected_keywords=['TV2', 'status'],
        expected_systems=['LTB']
    ),
    KeywordExtractionExample(
        query='Check the horizontal position of beam at BPM3 in sector 5 of storage ring',
        expected_keywords=['BPM', 'BPM3', 'horizontal', 'position', 'sector 5', 'device 3'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='What are the temperature readings from the EPBI thermocouples in SR sector 4?',
        expected_keywords=['EPBI', 'temperature', 'thermocouples', 'sector 4'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='Whats the beam current?',
        expected_keywords=['beam current'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='What is the vertical beam size?',
        expected_keywords=['vertical', 'beam size'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='What is the thermal interlock status of the Third Harmonic Cavity?',
        expected_keywords=['thermal interlock', 'third harmonic cavity'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='What is the temperature in the tunnel?',
        expected_keywords=['tunnel temperature'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='What is AS2 phase setpoint?',
        expected_keywords=['AS2', 'phase', 'setpoint'],
        expected_systems=['LN']
    ),
    KeywordExtractionExample(
        query='What are the horizontal and vertical tune PVs?',
        expected_keywords=['horizontal', 'vertical', 'tune'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='Give me BPM 6-2',
        expected_keywords=['BPM'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='Whats the first linac solenoid RBV?',
        expected_keywords=['solenoid', 'readback'],
        expected_systems=['LN']
    ),
    KeywordExtractionExample(
        query='Whats the RBV for the second SHD in sector 4?',
        expected_keywords=['SHD', 'RBV'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query="What's the mod's values?",
        expected_keywords=['MOD'],
        expected_systems=['GTL']
    ),
    KeywordExtractionExample(
        query="What's the linac modulator state value?",
        expected_keywords=['modulator', 'state'],
        expected_systems=['GTL']
    ),
    KeywordExtractionExample(
        query='What is the PV address for the storage ring beam current?',
        expected_keywords=['beam current'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='Return the phase control setpoint for the gun',
        expected_keywords=['gun', 'phase', 'phase control', 'setpoint'],
        expected_systems=['GTL']
    ),
    KeywordExtractionExample(
        query='What is the main RF setpoint?',
        expected_keywords=['RF', 'setpoint'],
        expected_systems=['SR']
    ),
    KeywordExtractionExample(
        query='Forward output power of klystron 2',
        expected_keywords=['klystron', 'forward', 'power'],
        expected_systems=['SR']
    ),
]
