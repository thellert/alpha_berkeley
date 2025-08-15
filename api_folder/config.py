"""
Configuration file for tomography system
Contains motor and camera configurations that can be imported by other modules.
"""

# Motor Configuration
MOTOR_PV = 'DMC01:A'
MOTOR_NAME = 'motor'
MOTOR_RATIO = 2.8125  # Conversion ratio for motor angles

# Camera Configuration
CAMERA_PV = '13ARV1:'
CAMERA_NAME = 'camera'

# EPICS Signal PVs
CALLBACKS_SIGNAL_PV = '13ARV1:image1:EnableCallbacks'
ACQUIRE_SIGNAL_PV = '13ARV1:cam1:Acquire'

# Camera Configuration Settings
CAM_CONFIG = {
    'acquire': 0,
    'image_mode': 0,  # single, multiple, continuous
    'trigger_mode': 0  # internal, external
}

IMAGE_CONFIG = {
    'enable': 1,
    'queue_size': 2000
}

TIFF_CONFIG = {
    'enable': 1,
    'auto_save': 1,
    'file_write_mode': 0,
    'nd_array_port': 'SP1',
    'auto_increment': 1
}

PVA_CONFIG = {
    'enable': 1,
    'blocking_callbacks': 'No',
    'queue_size': 2000,
    'nd_array_port': 'SP1',
    'array_callbacks': 0
}

# File and Directory Settings
DEFAULT_SAVE_DIR = '/home/user/tmpData/AI_scan/measurements/'
FILE_TEMPLATE = '%s%s_%d.tiff'

# Acquisition Settings
NUM_IMAGES_PER_POS = 20
MAX_RETRIES = 50
FILE_WAIT_TIMEOUT = 5.0
POLL_INTERVAL = 0.1

# Motor Movement Settings
MOTOR_MAX_RETRIES = 5
MOTOR_POSITION_TOLERANCE = 0.01  # Tolerance for position verification (motor units)
MOTOR_RETRY_DELAY = 1.0  # Seconds to wait between retries
MOTOR_SETTLE_TIME = 0.5  # Seconds to wait for motor to settle after movement

# Image Processing Settings
CROP_BOX = (800, 800, 1600, 1500)  # (left, upper, right, lower)

# Tiled Server Configuration
TILED_SERVER_URL = "http://localhost:8000"
TILED_CONTAINER_PATH = "Measurements"

# Default scan parameters
DEFAULT_SCAN_PARAMS = {
    'start_angle': 0,
    'end_angle': 128,
    'num_projections': 10,
    'save_dir': 'default'
}

# EPICS Command Utilities
import subprocess
import shutil

def get_epics_command_path(command_name):
    """
    Dynamically find the path to an EPICS command using 'which'.
    Falls back to common locations if 'which' fails.
    
    Args:
        command_name (str): Name of the EPICS command (e.g., 'caget', 'caput')
    
    Returns:
        str: Full path to the command
    
    Raises:
        FileNotFoundError: If command cannot be found
    """
    # First try using 'which' command
    try:
        result = subprocess.run(['which', command_name], 
                              capture_output=True, text=True, check=True)
        path = result.stdout.strip()
        if path and shutil.which(path):
            return path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try using shutil.which as backup
    path = shutil.which(command_name)
    if path:
        return path
    
    # Fallback to common EPICS installation locations
    common_paths = [
        f"/opt/epics/base-7.0.4/bin/linux-x86_64/{command_name}",
        f"/usr/local/epics/base/bin/linux-x86_64/{command_name}",
        f"/epics/base/bin/linux-x86_64/{command_name}",
        f"/usr/bin/{command_name}",
        f"/usr/local/bin/{command_name}"
    ]
    
    for path in common_paths:
        if shutil.which(path):
            return path
    
    # If all else fails, raise an error
    raise FileNotFoundError(f"Could not find EPICS command '{command_name}'. "
                          f"Please ensure EPICS is installed and {command_name} is in your PATH.")

# Cache the command paths for performance
_EPICS_COMMANDS = {}

def get_caget_path():
    """Get the path to caget command"""
    if 'caget' not in _EPICS_COMMANDS:
        _EPICS_COMMANDS['caget'] = get_epics_command_path('caget')
    return _EPICS_COMMANDS['caget']

def get_caput_path():
    """Get the path to caput command"""
    if 'caput' not in _EPICS_COMMANDS:
        _EPICS_COMMANDS['caput'] = get_epics_command_path('caput')
    return _EPICS_COMMANDS['caput']
