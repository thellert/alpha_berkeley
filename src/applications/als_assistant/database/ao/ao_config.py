"""Configuration management for AO database connections and data processing.

This module provides configuration settings and utilities for managing MongoDB 
connections and system-specific data processing rules for the Accelerator Object (AO) 
database. It handles environment detection, connection parameter resolution, and 
comprehensive filtering configurations for different accelerator systems.

Key features:
- Automatic environment detection (container vs host execution)
- MongoDB connection parameter management
- System-specific data filtering configurations
- Field whitelisting and blacklisting rules
- Family and field renaming mappings

The module supports multiple accelerator systems including:
- SR (Storage Ring)
- BR (Booster Ring) 
- GTB (Gun-to-Booster transport line, split into GTL/LN/LTB)
- BTS (Booster-to-Storage Ring transport)

Configuration is loaded from the unified config system and can be overridden
using environment variables for local development.

.. note::
   MongoDB connection parameters are automatically detected based on runtime
   environment. Use MONGO_USE_LOCALHOST=true for local development.

.. warning::
   The database_configs dictionary contains critical filtering rules that
   determine which accelerator data is processed and stored. Modifications
   should be made carefully to avoid data loss.
"""

import os

# Load configuration using unified config
from configs.config import get_config_value
from configs.logger import get_logger

# Initialize logger for this module
logger = get_logger("framework", "base")

# Get service configuration for container details (host/port)
mongo_service_config = get_config_value("applications.als_assistant.services.mongo", {})
# Get app configuration for database details (database_name/collection_name)
db_app_config = get_config_value("applications.als_assistant.database.ao_db", {})

def _detect_mongo_connection():
    """Detect appropriate MongoDB connection parameters based on runtime environment.
    
    Automatically determines the correct MongoDB host and port by analyzing the 
    execution environment. The function checks for container execution indicators
    and environment variable overrides to select the appropriate connection settings.
    
    Detection logic:
    1. Check for MONGO_USE_LOCALHOST environment variable override
    2. Detect Podman container environment via /run/.containerenv file
    3. Default to localhost for host-based execution
    
    :return: MongoDB connection parameters as (host, port) tuple
    :rtype: tuple[str, int]
    
    .. note::
       Container detection is specific to Podman environments. Docker containers
       may require explicit MONGO_USE_LOCALHOST=false setting.
    
    Examples:
        Automatic detection in different environments::
        
            >>> host, port = _detect_mongo_connection()
            >>> print(f"Connecting to MongoDB at {host}:{port}")
            
        With environment override::
        
            >>> import os
            >>> os.environ['MONGO_USE_LOCALHOST'] = 'true'
            >>> host, port = _detect_mongo_connection()
            >>> # Returns localhost regardless of container state
    """
    # TODO: a bit hacky. 
    container_host = mongo_service_config.get("name", "mongo")  # Default to "mongo"
    local_host = "localhost"
    container_port = mongo_service_config.get("port_container", 27017)
    host_port = mongo_service_config.get("port_host", 27017)
    
    # Simple environment variable override for local development
    # Allow explicit localhost override for development and Docker-for-Desktop setups
    if os.environ.get("MONGO_USE_LOCALHOST", "").lower() in ("true", "1", "yes"):
        logger.debug(f"MONGO_USE_LOCALHOST set - using local environment '{local_host}:{host_port}'")
        return local_host, host_port
    
    # Check if we're running in a Podman container by looking for container indicators
    # For Podman containers, check for the .containerenv file
    # Podman exposes /run/.containerenv; prefer container networking defaults if present
    if os.path.exists("/run/.containerenv"):
        logger.debug(f"Detected Podman container environment - using '{container_host}:{container_port}'")
        return container_host, container_port
    
    # Default to localhost for host-based execution (like CLI)
    # Fallback for host execution (command line, unit tests, CI without containers)
    logger.debug(f"Detected host environment - using '{local_host}:{host_port}'")
    return local_host, host_port

# Database configuration combining service and app configs with environment detection
# Resolve connection parameters at import time to avoid per-call detection overhead
DB_HOST, DB_PORT = _detect_mongo_connection()
DB_NAME = db_app_config.get("database_name")
COLLECTION_NAME = db_app_config.get("collection_name")

# System-specific configurations
# Filtering and renaming rules mirror ALS MML semantics; edits change persisted schema.
database_configs = {
    'SR': {
        'top_level_blacklist': ['BPMx', 'BPMy', 'BPMTest', 'VCBSC', 'GeV', 'Kicker'],
        'rename_all_fields': {'On': 'OnMonitor', 'AT': 'pyAT'},
        #
        "BPM": {
            'whitelist': ['MemberOf', 'Status', 'ElementList', 'DeviceList', 'Cell', 'FOFB', 'IP', 'BaseName', 'X', 'Y', 'S', 'CommonNames', 'Position', 'XGolden', 'YGolden', 'XError', 'YError', 'FOFBIndex', 'SampleRate', 'X_RMS_10k', 'Y_RMS_10k', 'X_RMS_200', 'Y_RMS_200', 'XGoldenSetpoint', 'YGoldenSetpoint', 'AT'],
            'rename_family_fields': {"S": "SumSignal"},
        },
        "HCM": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'BaseName', 'DeviceType', 'Monitor', 'Setpoint', 'SetpointGolden', 'Trim', 'FF1', 'FF2', 'FFMultiplier', 'Sum', 'DAC', 'RampRate', 'TimeConstant', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Gain', 'Roll', 'CommonNames'],
        },
        "VCM": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'BaseName', 'DeviceType', 'Monitor', 'Setpoint', 'SetpointGolden', 'Trim', 'FF1', 'FF2', 'FFMultiplier', 'Sum', 'DAC', 'RampRate', 'TimeConstant', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Gain', 'Roll', 'CommonNames'],
        },
        ##########
        ##########
        "QF": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'FF', 'FFMultiplier', 'Sum', 'RampRate', 'TimeConstant', 'DAC', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Position'],
        },
        "QD": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'FF', 'FFMultiplier', 'Sum', 'RampRate', 'TimeConstant', 'DAC', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Position'],
        },
        "QFA": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'TimeConstant', 'OnControl', 'On', 'Reset', 'Ready', 'Shunt1Control', 'Shunt1', 'Shunt2Control', 'Shunt2', 'AT', 'Position'],
        },
        "QDA": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'TimeConstant', 'DAC', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Position'],
        },
        "BEND": {
            "whitelist": ['MemberOf', 'Status', 'DeviceList', 'ElementList', 'Monitor', 'Setpoint', 'SetpointGolden', 'DAC', 'RampRate', 'TimeConstant', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Position'],
        },
        "BSC": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'RampRate', 'Limit', 'AT', 'Position'],
        },
        ##########
        ##########
        "SF": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'TimeConstant', 'DAC', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Position'],
        },
        "SD": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'TimeConstant', 'DAC', 'OnControl', 'On', 'Reset', 'Ready', 'AT', 'Position'],
        },
        "SHF": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'BaseName', 'DeviceType', 'Setpoint', 'CommonNames', 'Monitor', 'Voltage', 'Resistance', 'SetpointGolden', 'RampRate', 'Fault', 'Ready', 'FaultStatus', 'OverVoltage', 'OverTemp', 'On', 'OnControl', 'Reset', 'AT'],
        },
        "SHD": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'BaseName', 'DeviceType', 'Setpoint', 'CommonNames', 'Monitor', 'Voltage', 'Resistance', 'SetpointGolden', 'RampRate', 'Fault', 'Ready', 'FaultStatus', 'OverVoltage', 'OverTemp', 'On', 'OnControl', 'Reset', 'AT'],
        },
        ##########
        ##########
        "SQSF": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Offset', 'AT'],
        },
        "SQSD": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Offset', 'AT'],
        },
        "SQSHF": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Ready'],
        },
        "SQEPU": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'BaseName', 'DeviceType', 'CommonNames', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'FF', 'FFMultiplier', 'Sum', 'DAC', 'Ready', 'Offset'],
        },      
        ##########
        ##########
        "DCCT": {
            'whitelist': ['Monitor', 'Avg', 'Fast', 'Keithley', 'LowPass'],
        },
        ##########
        ##########
        "HCMCHICANE": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'TimeConstant', 'OnControl', 'On', 'AT', 'Position'],
        },
        "VCMCHICANE": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'TimeConstant', 'OnControl', 'On', 'AT', 'Position'],
        },
        "HCMCHICANEM": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'Position'],
        },
        ##########
        ##########
        "HCMFOFB": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'BaseName', 'DeviceType', 'HostName', 'IP', 'CommonNames', 'Position', 'Monitor', 'Voltage', 'Setpoint', 'EnetSP', 'VoltageSetpoint', 'Leakage', 'Ramping', 'Remote', 'Regulation', 'Fault', 'On', 'Mode', 'ModeRBV', 'OnControl', 'OffControl', 'Reset', 'RemoteControl', 'Version', 'ID', 'PID_V', 'PID_I', 'Offset', 'FIR', 'FOFBSetpoint', 'Trim', 'FF1', 'FF2'],
        },
        "VCMFOFB": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'BaseName', 'DeviceType', 'HostName', 'IP', 'CommonNames', 'Position', 'Monitor', 'Voltage', 'Setpoint', 'EnetSP', 'VoltageSetpoint', 'Leakage', 'Ramping', 'Remote', 'Regulation', 'Fault', 'On', 'Mode', 'ModeRBV', 'OnControl', 'OffControl', 'Reset', 'RemoteControl', 'Version', 'ID', 'PID_V', 'PID_I', 'Offset', 'FIR', 'FOFBSetpoint', 'Trim', 'FF1', 'FF2'],
        },
        ##########
        ##########
        "EPU": {
            'whitelist': ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'OffsetA', 'OffsetAControl', 'OffsetB', 'OffsetBControl', 'ZMode', 'RunFlag', 'Velocity', 'VelocityControl', 'MoveCount', 'UserGap', 'FFTableHeader', 'Home', 'Amp', 'AmpReset', 'Position'],
            'rename_family_fields': {"Monitor": "OffsetMonitor", "Setpoint": "OffsetSetpoint", "Velocity": "OffsetVelocity"},
        },
        "ID": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'Velocity', 'VelocityControl', 'VelocityProfile', 'RunFlag', 'UserGap', 'GapEnableControl', 'GapEnable', 'FFEnableControl', 'FFEnable', 'FFReadTable', 'FFTableHeader', 'Home', 'MoveCount', 'Amp', 'AmpReset', 'Position'],
            'rename_family_fields': {"Monitor": "GapMonitor", "Setpoint": "GapSetpoint", "Velocity": "GapVelocity"},
        },
        ##########
        ##########
        "BOTTOMSCRAPER": {
            'whitelist': ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'Velocity', 'RunFlag', 'HomeControl', 'Home', 'PositiveLimit', 'NegativeLimit'],
        },
        "INSIDESCRAPER": {
            'whitelist': ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'Velocity', 'RunFlag', 'HomeControl', 'Home', 'PositiveLimit', 'NegativeLimit'],
        },
        "TOPSCRAPER": {
            'whitelist': ['Status', 'MemberOf', 'DeviceList', 'ElementList', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'Velocity', 'RunFlag', 'HomeControl', 'Home', 'PositiveLimit', 'NegativeLimit'],
        },
        ##########
        ##########
        "RF": {
            "whitelist": ['MemberOf', 'Status', 'DeviceList', 'ElementList', 'Monitor', 'Setpoint', 'CavityTemperature1', 'CavityTemperature2', 'AT', 'Position'],
            'rename_family_fields': {"Monitor": "FrequencyMonitor", "Setpoint": "FrequencySetpoint"},
        },
        "THC": {
            "whitelist": ['MemberOf', 'Status', 'DeviceList', 'ElementList', 'Monitor', 'Setpoint', 'Error'],
        },
        ##########
        ##########
        "IonGauge": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Position'],
        },
        "IonPump": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Position'],
            "blacklist": ["Torr"], # "Monitor" is just an alias of "Torr" but more consistent to use "Monitor"
        },       
    },
    ###############################
    ###############################
    ###############################
    'BR': {
        'top_level_blacklist': ['BPMx', 'BPMy'],
        'BPM': {
            'whitelist': ['MemberOf', 'Status', 'ElementList', 'DeviceList', 'Cell', 'FOFB', 'IP', 'BaseName', 'X', 'Y', 'S', 'CommonNames', 'Position', 'XGolden', 'YGolden', 'XError', 'YError', 'FOFBIndex', 'SampleRate', 'X_RMS_10k', 'Y_RMS_10k', 'X_RMS_200', 'Y_RMS_200', 'XGoldenSetpoint', 'YGoldenSetpoint', 'AT'],
            'rename_family_fields': {"S": "SumSignal"},
        },
        "HCM": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'BaseName', 'IRM', 'Monitor', 'Setpoint', 'RampRate', 'OnControl', 'On', 'Ready', 'AWGPattern', 'AWGTrigMode', 'AWGArm', 'AWGEnable', 'AWGActive', 'AWGTrigModeRBV', 'AWGArmRBV', 'AWGEnableRBV', 'AWGInt1Rise', 'AWGInt2Rise', 'AWGInt1Fall', 'AWGInt2Fall', 'AWGInt1RiseRBV', 'AWGInt2RiseRBV', 'AWGInt1FallRBV', 'AWGInt2FallRBV', 'AT', 'Position'],
        },
        "VCM": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'BaseName', 'IRM', 'Monitor', 'Setpoint', 'RampRate', 'OnControl', 'On', 'Ready', 'AWGPattern', 'AWGTrigMode', 'AWGArm', 'AWGEnable', 'AWGActive', 'AWGTrigModeRBV', 'AWGArmRBV', 'AWGEnableRBV', 'AWGInt1Rise', 'AWGInt2Rise', 'AWGInt1Fall', 'AWGInt2Fall', 'AWGInt1RiseRBV', 'AWGInt2RiseRBV', 'AWGInt1FallRBV', 'AWGInt2FallRBV', 'AT', 'Position'],
        },
        "QF": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'IDN', 'On', 'OnControl', 'EnableDAC', 'EnableRamp', 'Gain', 'Offset', 'Ready', 'RampTable', 'DVM', 'ILCTrim', 'AT', 'Position'],
        },
        "QD": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'On', 'OnControl', 'EnableDAC', 'EnableRamp', 'Gain', 'Offset', 'Ready', 'RampTable', 'DVM', 'ILCTrim', 'AT', 'Position'],
        },
        "SF": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'BaseName', 'IRM', 'Monitor', 'Setpoint', 'OnControl', 'On', 'Ready', 'AWGPattern', 'AWGTrigMode', 'AWGArm', 'AWGEnable', 'AWGActive', 'AWGTrigModeRBV', 'AWGArmRBV', 'AWGEnableRBV', 'AWGInt1Rise', 'AWGInt2Rise', 'AWGInt1Fall', 'AWGInt2Fall', 'AWGInt1RiseRBV', 'AWGInt2RiseRBV', 'AWGInt1FallRBV', 'AWGInt2FallRBV', 'RampRate', 'AT', 'Position'],
        },
        "SD": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'BaseName', 'IRM', 'Monitor', 'Setpoint', 'OnControl', 'On', 'Ready', 'AWGPattern', 'AWGTrigMode', 'AWGArm', 'AWGEnable', 'AWGActive', 'AWGTrigModeRBV', 'AWGArmRBV', 'AWGEnableRBV', 'AWGInt1Rise', 'AWGInt2Rise', 'AWGInt1Fall', 'AWGInt2Fall', 'AWGInt1RiseRBV', 'AWGInt2RiseRBV', 'AWGInt1FallRBV', 'AWGInt2FallRBV', 'RampRate', 'AT', 'Position'],
        },
        "BEND": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Monitor', 'Setpoint', 'DVM', 'On', 'OnControl', 'EnableDAC', 'EnableRamp', 'Gain', 'Offset', 'Ready', 'AT', 'Position'],
        },
        "RF": {
            "whitelist": ['MemberOf', 'Status', 'DeviceList', 'ElementList', 'Monitor', 'Setpoint', 'Mode', 'ModeControl', 'On', 'OnControl', 'EnableDAC', 'Gain', 'EnableRamp', 'PhaseControl', 'Phase', 'PhaseError', 'CircForwardPower', 'WaveGuideForwardPower', 'WaveGuideReversePower', 'TunerPosition', 'CavityTemperatureControl', 'CavityTemperature', 'LCWTemperature', 'CircTemperature', 'CircLoadTemperature', 'CircLoadFlow', 'CircFlow', 'SwitchLoadFlow', 'CavityFlow', 'WindowFlow', 'CavityTunerFlow', 'Position'],
        },
        "DCCT": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'Monitor'],
        },
    },
    ###############################
    ###############################
    ###############################
    'GTB': {
        'top_level_blacklist': ['BPMx', 'BPMy', 'ExtraMonitors', 'ExtraControls', 'ExtraMachineConfig', 'TUNE'],
        'rename_all_fields': {'AT': 'pyAT'},
        'rename_families': {'Q': 'Quad', 'AS': 'AcceleratingStructure', 'AT': 'pyAT', 'EG': 'GUN'}, #, 'SHB': 'SubHarmBuncher', 'MOD': 'Modulator'},
        'BPM': {
            'whitelist': ['MemberOf', 'Status', 'ElementList', 'DeviceList', 'Cell', 'FOFB', 'IP', 'BaseName', 'X', 'Y', 'S', 'CommonNames', 'Position', 'XGolden', 'YGolden', 'XError', 'YError', 'FOFBIndex', 'SampleRate', 'X_RMS_10k', 'Y_RMS_10k', 'X_RMS_200', 'Y_RMS_200', 'XGoldenSetpoint', 'YGoldenSetpoint', 'AT'],
            'rename_family_fields': {"S": "SumSignal"},
        },
        "HCM": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Ready', 'AT'],
        },
        "VCM": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Ready', 'AT'],
        },
        "Q": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Ready', 'AT'],
        },
        "BuckingCoil": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Ready'],
        },
        "BEND": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'BaseName', 'DeviceType', 'Monitor', 'Setpoint', 'SetpointGolden', 'Voltage', 'Shunt', 'RampRate', 'OnControl', 'On', 'Fault', 'Ready', 'CtrlPower', 'OverTemperature', 'AT'],
        },
        "SOL": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'BaseName', 'DeviceType', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'Voltage', 'OnControl', 'Ready', 'On'],
        },
        "DCCT": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'Monitor'],
        },
        "Trigger": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'EvtNumber', 'Crate', 'EVR', 'PG', 'Port', 'FD', 'EvtCounter', 'Evt', 'Enable', 'Prescaler', 'Delay', 'DelayRB', 'Width', 'WidthRB', 'Polarity', 'Pulser', 'FineDelay'],
        },
        "Delay": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Sync', 'Event', 'Group', 'FieldCounter', 'FieldCounterFiltered'],
        },
        "EG": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'OnControl'],
        },
        "SHB": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'BaseName', 'DeviceType', 'HVControl', 'HVGolden', 'HV', 'Ready', 'OnControl', 'On', 'PulsingControl', 'PulsingOn', 'PulsingReady', 'DriveAmp', 'Local', 'Computer', 'ExtInterlock1', 'ExtInterlock2', 'ExtInterlock3', 'FilamentTimeOut', 'PlugInterlock', 'Thermal', 'Intlk1', 'Intlk2', 'Intlk3', 'Air', 'AC_120V_OK', 'DC_24V_OK', 'PhaseControl', 'PhaseGolden', 'Phase', 'PulseWidth', 'PulseDelay', 'PulseAmp', 'PulsePermit', 'LocalPhase', 'RemotePhase'],
                'rename_family_fields': {"Phase": "PhaseMonitor"},
        },
        "MOD": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'State', 'Reset'],
        },
        "AS": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'LoopControl'],
        },
        "TV": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'InControl', 'In', 'Out', 'LampControl', 'Lamp', 'AT'],
        },
        "VVR": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'OpenControl', 'Open', 'Closed', 'UpStream', 'DownStream', 'Ready', 'Interlock', 'Local', 'DC_24V_OK', 'Air', 'Cathode'],
        },
    },
    ###############################
    ###############################
    ###############################
    'BTS': {
        'top_level_blacklist': ['BPMx', 'BPMy'],
        'BPM': {
            'whitelist': ['MemberOf', 'Status', 'ElementList', 'DeviceList', 'Cell', 'FOFB', 'IP', 'BaseName', 'X', 'Y', 'S', 'CommonNames', 'Position', 'XGolden', 'YGolden', 'XError', 'YError', 'FOFBIndex', 'SampleRate', 'X_RMS_10k', 'Y_RMS_10k', 'X_RMS_200', 'Y_RMS_200', 'XGoldenSetpoint', 'YGoldenSetpoint', 'AT'],
                'rename_family_fields': {"S": "SumSignal"},
        },
        "HCM": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Ready', 'AT'],
        },
        "VCM": {
            "whitelist": ['DeviceList', 'BaseName', 'DeviceType', 'MemberOf', 'Status', 'CommonNames', 'ElementList', 'Position', 'Monitor', 'Leakage', 'Voltage', 'BulkVoltage', 'RegulatorTemp', 'Setpoint', 'SetpointGolden', 'RampRate', 'Ramping', 'Fault', 'BulkOn', 'On', 'BulkControl', 'OnControl', 'Reset', 'Ready', 'AT'],
        },
        "Q": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'BaseName', 'DeviceType', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'Voltage', 'OnControl', 'On', 'Ready', 'Reset', 'AT'],
        },
        "BEND": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'BaseName', 'DeviceType', 'Monitor', 'Setpoint', 'SetpointGolden', 'RampRate', 'OnControl', 'On', 'Ready', 'Reset', 'AT'],
        },
        "BRBump": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint'],
        },
        "Kicker": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint'],
        },
        "Septum": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'AT'],
        },
        "SRBump": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'AT'],
        },
        "DCCT": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'Monitor'],
        },
        "TV": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Setpoint', 'InControl', 'In', 'Out', 'LampControl', 'Lamp', 'AT'],
        },
        "RightScraper": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'Velocity', 'RunFlag', 'HomeControl', 'Home', 'PositiveLimit', 'NegativeLimit'],
        },
        "LeftScraper": {
            "whitelist": ['MemberOf', 'DeviceList', 'ElementList', 'Status', 'Position', 'CommonNames', 'Monitor', 'Setpoint', 'Velocity', 'RunFlag', 'HomeControl', 'Home', 'PositiveLimit', 'NegativeLimit'],
        },
    },
}