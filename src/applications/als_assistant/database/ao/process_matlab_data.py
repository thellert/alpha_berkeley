"""MATLAB Accelerator Object (AO) data processing and conversion utilities.

This module provides comprehensive functionality for processing MATLAB .mat files
containing Accelerator Object data from the ALS (Advanced Light Source) control
system. It handles the complete conversion pipeline from raw MATLAB structures
to standardized Python dictionaries suitable for MongoDB storage.

Key processing stages:
1. **MATLAB Structure Conversion**: Converts scipy.io structures to Python dictionaries
2. **Data Cleaning**: Handles NumPy types, NaN values, and function references
3. **System Filtering**: Applies whitelist/blacklist rules for each accelerator system
4. **Field Renaming**: Standardizes field names across different systems
5. **Data Restructuring**: Organizes data into standardized hierarchy
6. **System Splitting**: Separates GTB data into GTL, LN, and LTB subsystems
7. **Manual Imports**: Merges additional manually-defined data structures

The module supports multiple accelerator systems with system-specific configurations:
- **SR**: Storage Ring with extensive magnet and BPM systems
- **BR**: Booster Ring with specialized timing and control systems
- **GTB**: Gun-to-Booster line (split into GTL/LN/LTB subsystems)
- **BTS**: Booster-to-Storage Ring transport line

Processing features:
- Automatic NumPy type conversion to JSON-serializable Python types
- Function reference extraction and cataloging
- Hierarchical data validation and restructuring
- System-specific post-processing for data consistency
- Comprehensive error handling and logging

.. note::
   This module requires MATLAB .mat files with specific ALS control system
   structure. Source files should be generated from the MML (Middle Layer)
   accelerator physics toolbox.

.. warning::
   Processing modifies data structures extensively. Original MATLAB files
   are preserved, but intermediate processing steps may alter data organization.

Examples:
    Process a single accelerator system::
    
        >>> from applications.als_assistant.database.ao.process_matlab_data import main
        >>> main('SR')  # Process Storage Ring data
        # Generates: data/MML_ao_250413_SR.py
        
    Process all systems::
    
        >>> for system in ['SR', 'BR', 'GTB', 'BTS']:
        ...     main(system)
        # Generates processed data files for all systems
"""

import json
import numpy as np
from scipy.io import loadmat
import os
import pprint

# Import the local config module 
from applications.als_assistant.database.ao.ao_config import database_configs
from configs.logger import get_logger

# Initialize logger for this module
logger = get_logger("framework", "base")

# Import the manual imports from split files
from applications.als_assistant.database.ao.data.manual_imports_LN import manual_imports_LN
from applications.als_assistant.database.ao.data.manual_imports_LTB import manual_imports_LTB
from applications.als_assistant.database.ao.data.manual_imports_BR import manual_imports_BR
from applications.als_assistant.database.ao.data.manual_imports_BTS import manual_imports_BTS
from applications.als_assistant.database.ao.data.manual_imports_SR import manual_imports_SR

# Combine all manual imports into a single dictionary
manual_imports = {}
manual_imports.update(manual_imports_LN)
manual_imports.update(manual_imports_LTB)
manual_imports.update(manual_imports_BR)
manual_imports.update(manual_imports_BTS)
manual_imports.update(manual_imports_SR)
import copy


def mat_to_dict(obj):
    """Convert MATLAB/scipy objects to Python dictionaries recursively.
    
    Recursively processes MATLAB structures loaded via scipy.io.loadmat and converts
    them to native Python data structures. Handles various MATLAB data types including
    structured arrays, cell arrays, and scalar values.
    
    Conversion rules:
    - MATLAB structs → Python dictionaries
    - Structured numpy arrays → Python dictionaries  
    - Cell arrays → Python lists
    - Scalar arrays → Single values
    - NaN/Inf values → String representations for JSON compatibility
    
    :param obj: MATLAB object from scipy.io.loadmat to convert
    :type obj: Any
    :return: Converted Python data structure
    :rtype: dict | list | str | int | float | bool
    
    .. note::
       This function handles the complex nested structures typical in MATLAB
       accelerator physics data, including function handles and metadata.
    """
    # Handle dictionaries
    if isinstance(obj, dict):
        return {k: mat_to_dict(v) for k, v in obj.items()}
    
    # Handle numpy.void (structured arrays)
    if isinstance(obj, np.void):
        return {field: mat_to_dict(obj[field]) for field in obj.dtype.names}
    
    # Handle MATLAB struct objects
    if hasattr(obj, '_fieldnames'):
        return {field: mat_to_dict(getattr(obj, field)) for field in obj._fieldnames}
    
    # Handle numpy arrays
    if isinstance(obj, np.ndarray):
        if obj.dtype.names is not None:  # Structured array
            return mat_to_dict(obj[0]) if obj.size == 1 else [mat_to_dict(x) for x in obj]
        elif obj.size == 1:  # Single element array
            item = obj.item()
            return mat_to_dict(item) if item is not None else None
        else:  # Regular array
            return [mat_to_dict(x) for x in obj]
    
    # Handle numpy scalar types
    if isinstance(obj, (np.integer, np.bool_)):
        return int(obj) if isinstance(obj, np.integer) else bool(obj)
    if isinstance(obj, np.floating):
        # Represent NaN/Inf as strings for stable JSON serialization and cross-language portability
        if np.isnan(obj):
            return "NaN"
        elif np.isinf(obj):
            return "inf" if obj > 0 else "-inf"
        return float(obj)
    if np.isscalar(obj) and not isinstance(obj, (str, bytes, bool, int, float, complex)):
        return obj.item()
    
    # Handle Python float NaN and inf
    if isinstance(obj, float):
        if np.isnan(obj):
            return "NaN"
        elif np.isinf(obj):
            return "inf" if obj > 0 else "-inf"
    
    # Return other types unchanged
    return obj

def clean_matlab_data(data, path=""):
    """
    Clean and normalize MATLAB data structure for JSON serialization:
    1. Replace empty strings with empty lists in specific fields
    2. Convert single string MemberOf to arrays
    3. Handle function references
    4. Process special cases based on path
    5. Convert NumPy types to native Python types
    
    Returns cleaned data and list of function names found
    """
    # MML encodes function handles; capture function names for traceability and reproducibility
    function_fields = ["HW2PhysicsFcn", "Physics2HWFcn", "SpecialFunctionSet", 
                       "SpecialFunctionGet", "RunFlagFcn"]
    function_list = []
    
    # Handle NumPy scalar types first
    if isinstance(data, np.str_):
        return str(data), function_list
    elif isinstance(data, np.integer):
        return int(data), function_list
    elif isinstance(data, np.floating):
        if np.isnan(data):
            return "NaN", function_list
        elif np.isinf(data):
            return "inf" if data > 0 else "-inf", function_list
        return float(data), function_list
    # Handle Python float directly
    elif isinstance(data, float):
        if np.isnan(data):
            return "NaN", function_list
        elif np.isinf(data):
            return "inf" if data > 0 else "-inf", function_list
        return data, function_list
    
    # Handle dictionaries
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            curr_path = f"{path}.{k}" if path else k
            
            # Handle function fields
            if k in function_fields:
                if isinstance(v, str) and '/' in v:
                    # Extract function name from path string
                    fn_name = v.split('/')[-1].split('.')[0]
                    result[k] = fn_name
                    function_list.append(fn_name)
                elif isinstance(v, dict) and "function_handle" in v:
                    # Extract from function_handle structure
                    if isinstance(v["function_handle"], dict) and "function" in v["function_handle"]:
                        fn_name = v["function_handle"]["function"]
                        result[k] = fn_name
                        function_list.append(fn_name)
                    else:
                        # Process normally if we can't extract name
                        cleaned_v, fns = clean_matlab_data(v, curr_path)
                        result[k] = cleaned_v
                        function_list.extend(fns)
                else:
                    # Process normally for other types
                    cleaned_v, fns = clean_matlab_data(v, curr_path)
                    result[k] = cleaned_v
                    function_list.extend(fns)
            # Handle special fields
            elif k in ["HWUnits", "PhysicsUnits"] and v == "":
                result[k] = []
            elif k == "MemberOf" and isinstance(v, str):
                result[k] = [v]
            else:
                # Process normally
                cleaned_v, fns = clean_matlab_data(v, curr_path)
                result[k] = cleaned_v
                function_list.extend(fns)
                
        return result, list(set(function_list))
    
    # Handle lists and arrays
    elif isinstance(data, (list, np.ndarray)):
        result = []
        for i, item in enumerate(data):
            curr_path = f"{path}[{i}]"
            cleaned_item, fns = clean_matlab_data(item, curr_path)
            
            # Preserve array length/ordering; replace None in Golden/Monitor arrays to maintain shape
            if cleaned_item is None and ('Golden' in curr_path or 'Monitor' in curr_path):
                cleaned_item = "NaN"
                
            result.append(cleaned_item)
            function_list.extend(fns)
        return result, list(set(function_list))
    
    # Return other types unchanged
    return data, function_list

def apply_filters(ao_dict, database_config):
    """
    Apply blacklist and whitelist filters to the AO dictionary based on system configuration
    
    Args:
        ao_dict: The dictionary representation of the AO structure
        database_config: Configuration containing blacklists and whitelists
        
    Returns:
        Filtered dictionary with unwanted fields removed
    """
    # Remove unwanted top-level fields
    top_level_blacklist = database_config.get('top_level_blacklist', [])
    for family in top_level_blacklist:
        if family in ao_dict:
            del ao_dict[family]
    
    # Apply whitelists to each family
    for family in ao_dict.keys():
        whitelist = database_config.get(family,{}).get('whitelist', {})
        for field in list(ao_dict[family].keys()):
            # Keep only whitelisted fields
            if field not in whitelist:
                del ao_dict[family][field]

    # Rename families
    rename_families = database_config.get('rename_families', {})
    for old_name, new_name in rename_families.items():
        if old_name in ao_dict:
            ao_dict[new_name] = ao_dict.pop(old_name)
    
    # Apply field name mappings
    global_field_renames = database_config.get('rename_all_fields', {})

    renamed_ao_dict = {}
    for family, fields in ao_dict.items():
        # Rename fields within the family
        new_fields = {}
        family_config = database_config.get(family, {})
        family_renames = family_config.get('rename_family_fields', {})

        for field_name, field_value in fields.items():
            # Apply global field rename first
            renamed_field = global_field_renames.get(field_name, field_name)
            # Then apply family-specific rename
            renamed_field = family_renames.get(renamed_field, renamed_field)
            new_fields[renamed_field] = field_value

        renamed_ao_dict[family] = new_fields

    ao_dict.clear()
    ao_dict.update(renamed_ao_dict)

    # Only PV-bearing fields remain at the family top-level; move constants/config into 'setup'
    for family in ao_dict.keys():
        for field in list(ao_dict[family].keys()):
            # Leave pyAT fields alone
            if field.startswith('pyAT'):
                continue
            if not isinstance(ao_dict[family][field], dict) or 'ChannelNames' not in ao_dict[family][field]:
                # Make sure 'setup' exists
                if 'setup' not in ao_dict[family].keys():
                    ao_dict[family]['setup'] = {}
                ao_dict[family]['setup'][field] = ao_dict[family][field]
                del ao_dict[family][field]
    
    return ao_dict

def postprocessing_function(ao_cleaned, system='SR'):
    """System-specific post-processing of the cleaned AO structure"""
    ao_final={}
    if system == 'SR':
        # Fix specific known issue with TUNE.Monitor.Golden[2]
        if ('TUNE' in ao_cleaned and 'Monitor' in ao_cleaned['TUNE'] and 
                'Golden' in ao_cleaned['TUNE']['Monitor']):
            golden_array = ao_cleaned['TUNE']['Monitor']['Golden']
            if len(golden_array) > 2 and golden_array[2] is None:
                golden_array[2] = "NaN"    
        
        # Copy Gap nonitor and setpoint from IDs to EPU
        epu_devices = ao_cleaned['EPU']['setup']['DeviceList']
        id_devices = ao_cleaned['ID']['setup']['DeviceList']
        for id_dev in id_devices:
            if id_dev in epu_devices:
                epu_index = epu_devices.index(id_dev)
                id_index = id_devices.index(id_dev)
                # Check if field 'GapMonitor' exists, otherwise copy Monitor field and empty ChannelNames
                if 'GapMonitor' not in ao_cleaned['EPU']:
                    ao_cleaned['EPU']['GapMonitor'] = copy.deepcopy(ao_cleaned['EPU']['OffsetMonitor'])
                    ao_cleaned['EPU']['GapMonitor']['ChannelNames'] = [""]*len(epu_devices)
                if 'GapSetpoint' not in ao_cleaned['EPU']:
                    ao_cleaned['EPU']['GapSetpoint'] = copy.deepcopy(ao_cleaned['EPU']['OffsetSetpoint'])
                    ao_cleaned['EPU']['GapSetpoint']['ChannelNames'] = [""]*len(epu_devices)
                # Gap Monitor and Setpoints from ID to EPU
                ao_cleaned['EPU']['GapMonitor']['ChannelNames'][epu_index]  = ao_cleaned['ID']['GapMonitor']['ChannelNames'][id_index]
                ao_cleaned['EPU']['GapSetpoint']['ChannelNames'][epu_index] = ao_cleaned['ID']['GapSetpoint']['ChannelNames'][id_index]
        
        ao_final[f'{system}'] = ao_cleaned
    elif system == 'BR':
        ao_final[f'{system}'] = ao_cleaned
    elif system == 'BTS':
        ao_final[f'{system}'] = ao_cleaned
    elif system == 'GTB':
        # Split GTB AO into three systems: GTL, LN, and LTB
        subsystems = {'GTL': {}, 'LN': {}, 'LTB': {}}
        
        # Process each family in the AO structure
        for family_name, family_data in ao_cleaned.items():
            
            # Skip if not a dictionary
            if not isinstance(family_data, dict):
                continue

            # Check if DeviceList exists for this family
            if 'DeviceList' not in family_data['setup']:
                # Since there's no DeviceList to determine which subsystems contain this family,
                # add it to all subsystems as it's likely general configuration data
                for subsystem in subsystems:
                    subsystems[subsystem][family_name] = family_data
                continue
                
            device_list = family_data['setup']['DeviceList']
            # Ensure device_list is a nested list of lists
            device_list = device_list if isinstance(device_list[0], list) else [device_list]
                        
            # Determine which subsystems are present in the device_list
            present_subsystems = set()
            # Create subsystem device lists with local indices
            subsystem_device_lists = {'GTL': [], 'LN': [], 'LTB': []}
            subsystem_element_lists = {'GTL': [], 'LN': [], 'LTB': []}
            local_indices = {'GTL': 1, 'LN': 1, 'LTB': 1}
            
            for sys_id, dev_id in device_list:
                if sys_id == 1:
                    subsystem = 'GTL'
                    present_subsystems.add(subsystem)
                    subsystem_device_lists[subsystem].append([1, local_indices[subsystem]])
                    subsystem_element_lists[subsystem].append(local_indices[subsystem])
                    local_indices[subsystem] += 1
                elif sys_id == 2:
                    subsystem = 'LN'
                    present_subsystems.add(subsystem)
                    subsystem_device_lists[subsystem].append([1, local_indices[subsystem]])
                    subsystem_element_lists[subsystem].append(local_indices[subsystem])
                    local_indices[subsystem] += 1
                elif sys_id == 3:
                    subsystem = 'LTB'
                    present_subsystems.add(subsystem)
                    subsystem_device_lists[subsystem].append([1, local_indices[subsystem]])
                    subsystem_element_lists[subsystem].append(local_indices[subsystem])
                    local_indices[subsystem] += 1
            # Map MML 'system id' (1,2,3) to subsystems GTL/LN/LTB using local indices
            
            # Initialize subsystem-specific family data only for subsystems present in device_list
            for subsystem in present_subsystems:
                subsystems[subsystem][family_name] = {}
                # Copy entire setup field, but replace DeviceList and ElementList if available
                if subsystem_device_lists[subsystem]:
                    subsystems[subsystem][family_name]['setup'] = copy.deepcopy(family_data.get('setup', {}))
                    subsystems[subsystem][family_name]['setup']['DeviceList'] = subsystem_device_lists[subsystem]
                    # Only update ElementList if it exists in the original data
                    if 'ElementList' in family_data.get('setup', {}):
                        subsystems[subsystem][family_name]['setup']['ElementList'] = subsystem_element_lists[subsystem]
            
            # Process each field in the family
            for field_name, field_data in family_data.items():
                if isinstance(field_data, dict):
                    # Dictionary fields should have ChannelNames to be split
                    if 'ChannelNames' in field_data:
                        channel_names = field_data['ChannelNames']
                        
                        # Create subsystem-specific dictionary for each present subsystem
                        for subsystem in present_subsystems:
                            subsystems[subsystem][family_name][field_name] = {}
                            
                            # Copy all fields except ChannelNames
                            for subfield, subdata in field_data.items():
                                if subfield != 'ChannelNames':
                                    subsystems[subsystem][family_name][field_name][subfield] = subdata
                            
                            # Initialize empty ChannelNames for each subsystem
                            subsystems[subsystem][family_name][field_name]['ChannelNames'] = []
                        
                        # Distribute ChannelNames based on DeviceList
                        for idx, (sys_id, dev_id) in enumerate(device_list):
                            if idx < len(channel_names):
                                # Map system ID to subsystem name
                                if sys_id == 1:
                                    subsystem = 'GTL'
                                elif sys_id == 2:
                                    subsystem = 'LN'
                                elif sys_id == 3:
                                    subsystem = 'LTB'
                                else:
                                    continue  # Skip unknown system IDs
                                
                                # Add channel name to corresponding subsystem
                                subsystems[subsystem][family_name][field_name]['ChannelNames'].append(channel_names[idx])
                    else:
                        # Copy dictionary without ChannelNames to all present subsystems
                        for subsystem in present_subsystems:
                            if field_name != 'setup':  # Don't overwrite the setup we already created
                                subsystems[subsystem][family_name][field_name] = field_data
                else:
                    # For non-dictionary fields, split based on DeviceList if applicable
                    if isinstance(field_data, list) and len(field_data) == len(device_list):                        
                        # Distribute data based on DeviceList
                        for idx, (sys_id, dev_id) in enumerate(device_list):
                            if idx < len(field_data):
                                # Map system ID to subsystem name
                                if sys_id == 1:
                                    subsystem = 'GTL'
                                elif sys_id == 2:
                                    subsystem = 'LN'
                                elif sys_id == 3:
                                    subsystem = 'LTB'
                                else:
                                    continue  # Skip unknown system IDs
                                
                                # Add data to corresponding subsystem or initialise if empty
                                if field_name not in subsystems[subsystem][family_name]:
                                    subsystems[subsystem][family_name][field_name] = []
                                subsystems[subsystem][family_name][field_name].append(field_data[idx])
                    else:
                        # Copy other fields to all present subsystems
                        for subsystem in present_subsystems:
                            if field_name != 'setup':  # Don't overwrite the setup we already created
                                subsystems[subsystem][family_name][field_name] = field_data
        
        # TODO: find a better location for this
        # Known MML inconsistency: copy LN Quad PVs from GTL to LN to maintain coverage
        subsystems['LN']['Quad'] = copy.deepcopy(subsystems['GTL']['Quad'])
        
        # Return the three subsystems
        ao_final = subsystems
    # Add other system-specific post-processing as needed
    
    return ao_final

def add_manual_imports(ao_final, manual_imports):
    """Add manual imports to the AO structure
    
    This function adds entries from manual_imports to ao_final without replacing existing data.
    It recursively checks each level (system, family, field, subfield) and only adds what's missing.
    Only merges data for systems that exist in both dictionaries.
    
    Args:
        ao_final: The target AO dictionary with system.family.field.subfields structure
        manual_imports: The source dictionary with additional data to be added
        
    Returns:
        The updated AO dictionary with manual imports added
    """
    def recursive_merge(target_dict, source_dict):
        """Recursively merge source_dict into target_dict without overwriting existing keys."""
        for key, value in source_dict.items():
            if key not in target_dict:
                # If the key doesn't exist in target, simply add it
                target_dict[key] = value
            elif isinstance(value, dict) and isinstance(target_dict[key], dict):
                # If both are dictionaries, merge them recursively
                recursive_merge(target_dict[key], value)
            else:
                # Check if source and target are the same
                if value == target_dict[key]:
                    continue
                # Overwrite the target when values differ to apply manual corrections
                # TODO: figure out how the family name is passed to this function
                # FIXME: 'system' is not defined in this nested scope; warning context may be misleading
                logger.warning(f"Key '{key}' in system '{system}' already exists and will be overwritten by {value}")
                target_dict[key] = value
    
    # Only process systems that exist in both dictionaries
    for system in manual_imports:
        if system in ao_final:
            # Apply the recursive merge only for matching systems
            recursive_merge(ao_final[system], manual_imports[system])
    
    return ao_final

def main(system='SR'):
    """Process MATLAB AO data for specified accelerator system.
    
    Executes the complete processing pipeline for a single accelerator system,
    converting MATLAB .mat files to standardized Python dictionaries and saving
    the results as importable Python modules.
    
    Processing pipeline:
    1. Load MATLAB .mat file for the specified system
    2. Convert MATLAB structures to Python dictionaries
    3. Clean and normalize data (handle NaN, function references, etc.)
    4. Apply system-specific filtering (whitelist/blacklist rules)
    5. Perform system-specific post-processing
    6. Merge manual imports and corrections
    7. Generate Python data files for database import
    
    :param system: Accelerator system identifier to process
    :type system: str
    :raises ValueError: If system configuration not found
    :raises FileNotFoundError: If input .mat file doesn't exist
    :raises Exception: If processing pipeline fails
    
    .. note::
       Generated files are saved to the data/ subdirectory with standardized
       naming: MML_ao_250413_{system}.py
       
    .. warning::
       GTB system processing generates multiple output files (GTL, LN, LTB)
       due to the complex beamline structure.
    
    Examples:
        Process Storage Ring data::
        
            >>> main('SR')
            # Generates: data/MML_ao_250413_SR.py
            
        Process all systems in batch::
        
            >>> for sys in ['SR', 'BR', 'GTB', 'BTS']:
            ...     main(sys)
    """
    # File paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Use the local data directory
    data_dir = os.path.join(script_dir, 'data')
    input_file = os.path.join(data_dir, f'MML_ao_{system}_250410.mat')
    
    # Check if system config exists
    if system not in database_configs:
        raise ValueError(f"Configuration for system '{system}' not found")
    
    database_config = database_configs[system]
 
    # Load the MAT file
    # squeeze_me=True flattens singleton dimensions from MATLAB structs; struct_as_record=False yields simple objects
    mat_data = loadmat(input_file, squeeze_me=True, struct_as_record=False)
    
    # Get the AO data structure (with fallback)
    ao = mat_data.get('ao', mat_data)
    
    # Convert to Python dict structure
    ao_dict = mat_to_dict(ao)

    # Clean and normalize the data structure, including converting NumPy types to Python
    ao_cleaned, function_list = clean_matlab_data(ao_dict)
    
    # Apply blacklist and whitelist filters
    ao_cleaned = apply_filters(ao_cleaned, database_config)
    
   
    # Apply system-specific post-processing
    ao_final = postprocessing_function(ao_cleaned, system)
    
    # Add manual imports
    ao_final = add_manual_imports(ao_final, manual_imports)
        
    for system, ao in ao_final.items():    
        # Save output to the local data directory
        output_file = os.path.join(data_dir, f'MML_ao_250413_{system}.py')
        out_dict_name = f"MML_ao_{system}"
        
        with open(output_file, 'w') as f:
            # Pretty-print for human review; these files are later imported by the database loader
            f.write(f"# Auto-generated AO structure for {system}\n\n")
            f.write(f"{out_dict_name} = ")
            f.write(pprint.pformat(ao, indent=4, width=120))
            f.write("\n")
        
        logger.success(f"Python dictionary written to {output_file}")

if __name__ == "__main__":
    for system in ['SR', 'BTS', 'GTB','BR']:
        main(system)