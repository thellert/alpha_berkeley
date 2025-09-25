"""
Tool Examples - Storage Ring (SR) System
"""

from ..examples_loader import PVFinderToolExample

sr_examples = [
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['BPM'],
        query='Get horizontal position for the first and second BPMs in sector 1 and 4 of the storage ring',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BPM', 'field': 'X', 'sectors': [1, 4], 'devices': [1, 2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="misc",
        keywords=['families'],
        query='Get all available family names in the accelerator system',
        tool_name="list_families",
        tool_args={'system': 'SR'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['QF', 'setpoints'],
        query='Get current setpoints for all QF magnets',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'QF', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="pyAT",
        keywords=['BPM', 'positions', 's-positions'],
        query='Get the installed positions of all BPMs around the accelerator',
        tool_name="get_field_data",
        tool_args={'system': 'SR', 'family': 'BPM', 'field': 'setup', 'subfield': 'Position'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="misc",
        keywords=['RF', 'cavity', 'frequency range'],
        query='Get the range of the RF main cavity frequency',
        tool_name="get_field_data",
        tool_args={'system': 'SR', 'family': 'RF', 'field': 'Setpoint', 'subfield': 'Range'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="misc",
        keywords=['HCM', 'monitor data', 'hardware', 'units'],
        query='Get the hardware units for the SR horizontal corrector magnets monitor channels',
        tool_name="get_field_data",
        tool_args={'system': 'SR', 'family': 'HCM', 'field': 'Monitor', 'subfield': 'HWUnits'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['QF'],
        query='Examine the monitoring data structure for quadrupole magnets in the storage ring',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'QF', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="golden",
        keywords=['BPM', 'golden orbit'],
        query='Get golden reference orbit values for BPM X positions',
        tool_name="get_field_data",
        tool_args={'system': 'SR', 'family': 'BPM', 'field': 'X', 'subfield': 'Golden'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['BPM', '10kHz', 'noise'],
        query='Get channels for the first two BPMs X position RMS noise (10kHz sampling) in sectors 3, 6 and 9',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BPM', 'field': 'X_RMS_10k', 'sectors': [3, 6, 9], 'devices': [1, 2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="pyAT",
        keywords=['AT index', 'AT', 'pyAT', 'model', 'lattice', 'element indices', 'accelerator toolbox', 'toolbox', 'QF'],
        query='Get accelerator toolbox lattice elements for the SR QF magnets in sector 2.',
        tool_name="get_AT_index",
        tool_args={'system': 'SR', 'family': 'QF', 'sectors': [2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['BPM'],
        query='Get horizontal position channels for all BPMs in sector 1',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BPM', 'field': 'X', 'sectors': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['RF', 'cavity', 'temperature'],
        query='Get the first temperature monitoring PV for the main RF cavity',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'RF', 'field': 'CavityTemperature1'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['BEND', 'dipole'],
        query='Get all monitor PVs for the bending magnets',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BEND', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['BEND', 'dipole', 'fields'],
        query='Examine the field structure of the SR bending magnets',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'BEND'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['BEND'],
        query='Get setpoint channels for bending magnets in sectors 4 and 5',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BEND', 'field': 'Setpoint', 'sectors': [4, 5]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SF', 'sextupole'],
        query='Get all monitor channels for SF sextupole magnets',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SF', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="golden",
        keywords=['SF', 'sextupole', 'golden values'],
        query='Get golden reference values for SF sextupole magnets',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SF', 'field': 'SetpointGolden'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SF', 'sextupole'],
        query='Get SF setpoint PVs for the second device in all sectors',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SF', 'field': 'Setpoint', 'devices': [2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SHD', 'sextupole', 'harmonic sextupole', 'harmonic defocusing sextupole', 'defocusing', 'Monitor', 'RBV', 'readback'],
        query='Get monitor channels for defocusing harmonic sextupole magnets in sectors 3 and 6',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SHD', 'field': 'Monitor', 'sectors': [3, 6]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SHD', 'sextupole', 'harmonic sextupole', 'harmonic defocusing sextupole', 'defocusing', 'on/off'],
        query='Get on/off status for SHD device 1 in sector 2',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SHD', 'field': 'On', 'sectors': [2], 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SHD', 'sextupole', 'harmonic sextupole', 'harmonic defocusing sextupole', 'defocusing', 'ready', 'status'],
        query='Check if the harmonic defocusing sextupoles in sector 3 are ready',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SHD', 'field': 'Ready', 'sectors': [3]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['QFA', 'quadrupole', 'focusing quadrupole'],
        query='Get setpoints for QFA magnets in sectors 7, 8, and 9',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'QFA', 'field': 'Setpoint', 'sectors': [7, 8, 9]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['QFA', 'quadrupole', 'focusing quadrupole'],
        query='Examine all available fields for QFA magnets',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'QFA'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="pyAT",
        keywords=['AT index', 'AT', 'pyAT', 'model', 'lattice', 'element indices', 'accelerator toolbox', 'toolbox', 'QFA'],
        query='Get the element indices for the second QFA magnets of each sector in the accelerator toolbox model',
        tool_name="get_AT_index",
        tool_args={'system': 'SR', 'family': 'QFA', 'devices': [2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['QFA', 'on/off control', 'quadrupole', 'focusing quadrupole'],
        query='Get on/off control channels for QFA magnets in sector 3 for devices 1 and 2',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'QFA', 'field': 'OnControl', 'sectors': [3], 'devices': [1, 2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['ID', 'ID gap', 'Insertion device', 'gap'],
        query='Get the gap readback value for ID 11-2',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'ID', 'field': 'GapMonitor', 'sectors': [11], 'devices': [2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['EPU', 'EPU gap', 'Insertion device', 'gap'],
        query='Get the gap reading for EPU 11-1',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'EPU', 'field': 'GapMonitor', 'sectors': [11], 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['EPU', 'Insertion device', 'gap'],
        query='Get the gap SP for EPU4.2',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'EPU', 'field': 'GapSetpoint', 'sectors': [4], 'devices': [2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['EPU', 'Insertion device', 'gap'],
        query='Get the offset setpoint for EPU4.2',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'EPU', 'field': 'OffsetSetpoint', 'sectors': [4], 'devices': [2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['EPU', 'Insertion device', 'gap'],
        query='Whats the offset readback for EPU7-1',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'EPU', 'field': 'OffsetMonitor', 'sectors': [7], 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['EPU', 'insertion device', 'offset', 'RBV', 'readback', 'monitor'],
        query='What is the EPU 7-1 offset readback value?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'EPU', 'field': 'OffsetMonitor', 'sectors': [7], 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['ID', 'insertion device'],
        query='What fields are available for insertion devices?',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'ID'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['beam size', 'beamsize'],
        query='Whats the vertical beam size?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BeamSize', 'field': 'Y_10Hz_Beamline31'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['beam size', 'beamsize'],
        query='Give me the horizontal beam size?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BeamSize', 'field': 'X_10Hz_Beamline31'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['beam size', 'beamsize'],
        query='Whats the vertical beamsize at 7.2??',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BeamSize', 'field': 'Y_10Hz_Beamline72'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['beam size', 'beamsize'],
        query='Whats the 1Hz avg vertical beamsize at 3-1 ?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BeamSize', 'field': 'Y_1Hz_Beamline31'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['beam current', 'beamcurrent', 'DCCT', 'current'],
        query='Whats the beam current?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'DCCT', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['EPBI', 'thermocouple', 'temperature'],
        query='Get all lower EPBI thermocouple PVs',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'EPBI_TC_DOWN', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['EPBI', 'thermocouple', 'temperature', 'limit', 'overtemp'],
        query='Check if the temperature of the first devices of the lower thermocouples is over the limit',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'EPBI_TC_DOWN', 'field': 'Overtemp_flag', 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['harmonic cavity', 'interlock', 'thermal interlock', 'cavity', 'cavities', 'third harmonic', 'main tuner'],
        query='Whats the main tuner thermal interlock PV for third harmonic cavity 1?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'HarmonicCavity', 'field': 'MainTunerTempOk', 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['harmonic cavity', 'interlock', 'thermal interlock', 'cavity', 'cavities', 'third harmonic', 'HOM damper'],
        query='Whats the horizontal HOM damper thermal interlock PV for third harmonic cavity 2?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'HarmonicCavity', 'field': 'HorHOMDamperTempOk', 'devices': [2]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['harmonic cavity', 'interlock', 'thermal interlock', 'cavity', 'cavities', 'third harmonic', 'return temperature'],
        query='Whats the water return temperature interlock PVs for the third harmonic cavities?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'HarmonicCavity', 'field': 'RtnTempOk'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['Vacuum', 'vacuum pump', 'IonPump', 'Ion Pump', 'ion', 'pump', 'pressure'],
        query='Give me the pressure of the first ion pump in sector 3 and 6',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'IonPump', 'field': 'Monitor', 'sectors': [3, 6], 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['Vacuum', 'Vacuum Gauge', 'IonGauge', 'Ion Gauge', 'ion', 'gauge', 'pressure'],
        query='Get the ion gauge pressure for the entire storage ring.',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'IonGauge', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['pressure', 'Vacuum Gauge', 'vacuum', 'ion gauge', 'gauge'],
        query='What is the pressure in sector 7?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'IonGauge', 'field': 'Monitor', 'sectors': [7]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SHF', 'harmonic', 'harmonic focusing', 'harmonic focusing sextupole', 'sextupole', 'harmonic sextupole'],
        query='Check if the focusing harmonic sextupoles in sector 2 and 4 are ready?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SHF', 'field': 'Ready', 'sectors': [2, 4]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SDF', 'harmonic', 'harmonic defocusing', 'harmonic defocusing sextupole', 'sextupole', 'harmonic sextupole'],
        query='Get the setpoint for all first devices of the defocusing harmonic sextupoles',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SDF', 'field': 'Setpoint', 'devices': [1]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SHF', 'harmonic', 'harmonic focusing', 'harmonic focusing sextupole', 'sextupole', 'harmonic sextupole'],
        query='Get the readback for all focusing harmonic sextupoles',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SHF', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['QD', 'IP', 'IP address', 'ramprate'],
        query='Give me the QD ramprate IP address for sector 4 device 2.',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SHF', 'field': 'Monitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['PSS', 'frontend shutter', 'shutter', 'shutters', 'open', 'closed', 'status'],
        query='Whats the PSS frontend shutter status in sector 4?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'PSS', 'field': 'FrontEndShutterIsOpen', 'sectors': [4]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['injection', 'efficiency', 'beam injection', 'transfer efficiency'],
        query='What is the injection efficiency into the storage ring?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'Injection', 'field': 'Efficiency'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['injection', 'charge', 'beam injection', 'injected charge'],
        query='How much charge was injected into the storage ring?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'Injection', 'field': 'Charge'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['temperature', 'air handling unit', 'AHU', 'zone temperature', 'air', 'air temperature'],
        query='What is the temperature zone of air handling unit in sector 7?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'TunnelAirTemperature', 'field': 'Monitor', 'sectors': [7]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['chilled water', 'valve', 'CHW', 'air handler', 'AHU', 'air handling unit'],
        query='What is the setting of the chilled water valve of the air handler in sector 6?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'AirHandlingUnit', 'field': 'ChilledWaterValve', 'sectors': [6]}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['chilled water', 'temperature', 'building 34', 'CHWS'],
        query='What is the chilled water temperature as it leaves building 34?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BuildingUtilities', 'field': 'ChilledWaterSupplyB34'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['water flow', 'tower water', 'cooling tower', 'flow'],
        query='What is the water flow of tower water?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BuildingUtilities', 'field': 'TowerWaterFlow'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['building utilities', 'facilities', 'building systems', 'utilities', 'building', 'facility', 'chilled water', 'water flow'],
        query='What building utilities are available for monitoring?',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'BuildingUtilities'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SEN', 'SR-SEN', 'septum', 'setpoint', 'current', 'extraction', 'injection', 'injection septum'],
        query='What is the SEN septum setpoint?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SEN', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['SEK', 'SR-SEK', 'septum', 'setpoint', 'voltage', 'extraction', 'extraction septum'],
        query='What is the SR-SEK setpoint?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'SEK', 'field': 'Setpoint'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['BCM', 'bunch current monitor', 'bunch', 'current'],
        query='What fields are available for the bunch current monitor?',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'BunchCurrentMonitor'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['BCM', 'bunch current', 'individual bunch current', 'bunch', 'current', 'all bunches'],
        query='What is the individual bunch current in the storage-ring beam?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BunchCurrentMonitor', 'field': 'BunchCurrent'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['BCM', 'cam bunch', 'shaft bunch', 'cam', 'current', 'bunch current'],
        query='What is the current in the cam bunch?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'BunchCurrentMonitor', 'field': 'CamBunchCurrent'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['lifetime', 'beam lifetime', 'slow average', 'beam decay', 'topoff'],
        query='Slow average of the beam lifetime',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'Lifetime', 'field': 'SlowAverage'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['RF', 'klystron', 'klystron 2', 'forward power', 'output power'],
        query='Forward output power of klystron 2',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'RF', 'field': 'Klystron2ForwardPower'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['RF', 'phase', 'phase setpoint', 'klystron phase', 'master oscillator'],
        query='Phase setpoint for RF',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'RF', 'field': 'PhaseSetpoint'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['RF', 'radio frequency', 'cavity', 'klystron', 'frequency', 'phase', 'power'],
        query='What fields are available for the RF system?',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'RF'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['tune', 'feedback', 'delta', 'adjustment', 'tune feedback', 'dNu', 'horizontal tune'],
        query='How much has the tune feedback system adjusted the horizontal tune?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'TUNE', 'field': 'X_FeedbackDelta'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['tune', 'tune feedback', 'main tune'],
        query='What is the main horizontal tune PV?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'TUNE', 'field': 'X_TransverseFeedBack'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['user beam', 'beam available', 'operations', 'beam status', 'facility status'],
        query='Is user beam available?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'Operations', 'field': 'UserBeamAvailable'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="structure",
        keywords=['HOM', 'harmonic cavity', 'cavity', 'power', 'cavity power', 'harmonic', 'third harmonic'],
        query='What fields are available for the harmonic cavities?',
        tool_name="inspect_fields",
        tool_args={'system': 'SR', 'family': 'HarmonicCavity'}
    ),
    PVFinderToolExample(
        system="SR",
        query_type="PV",
        keywords=['HOM', 'harmonic cavity', 'cavity', 'loop', 'loop status', 'closed', 'harmonic', 'third harmonic', 'cavity loop'],
        query='Are the harmonic cavity loops closed?',
        tool_name="list_channel_names",
        tool_args={'system': 'SR', 'family': 'HarmonicCavity', 'field': 'LoopClosed'}
    ),
    
    ##############################
    # System Fallback Examples
    ##############################
    PVFinderToolExample(
        system="SR",
        query_type="fallback",
        keywords=['families', 'available', 'explore', 'help', 'list', 'what', 'show'],
        query='What families are available in the storage ring?',
        tool_name="list_families",
        tool_args={'system': 'SR'}
    ),
]
