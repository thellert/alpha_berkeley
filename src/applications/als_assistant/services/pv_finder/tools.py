from applications.als_assistant.database.ao.ao_database import get_collection
from typing import List, Dict, Any, Optional
import json
import logging
from pydantic_ai.exceptions import ModelRetry
from applications.als_assistant.services.pv_finder.util import case_insensitive_eq, case_insensitive_in
import opentelemetry.trace

# Use global logger
from configs.logger import get_logger
logger = get_logger("als_assistant", "pv_finder")

def _get_system_doc(system: str) -> Dict[str, Any]:
    """Returns the system document for a given system name or raises an error if not found.
    """
    collection = get_collection()
    valid_systems = collection.distinct("system")

    # Check if system is in the collection
    if not case_insensitive_in(system, valid_systems):
        raise ModelRetry(
            f"Tool Error: The system '{system}' is invalid. Available systems: {valid_systems}"
        )
    
    # Find the system with case-insensitive matching
    for valid_system in valid_systems:
        if case_insensitive_eq(system, valid_system):
            return collection.find_one({"system": valid_system})
    
    # This should never happen if case_insensitive_in works correctly
    raise ModelRetry(f"Internal error: Could not find system '{system}' after validation")

def _get_family_doc(system: str, family: str) -> Dict[str, Any]:
    """Returns the family document for a given system and family name or raises an error if not found.
    """
    system_doc = _get_system_doc(system)  # This will raise ModelRetry if system not found
    
    families = [fam["name"] for fam in system_doc.get("families", [])]
    # Check family is in the system document
    if not case_insensitive_in(family, families):
        raise ModelRetry(f"Tool Error: The family '{family}' is invalid for system '{system}'. Available families: {families}")

    for family_doc in system_doc["families"]:
        if case_insensitive_eq(family_doc["name"], family):
            return family_doc
    
    # This should never happen if case_insensitive_in works correctly
    raise ModelRetry(f"Internal error: Could not find family '{family}' is invalid for system '{system}'")

def _filter_by_device_sectors(
    data_list: List[Any], 
    device_list: List[Any], 
    sectors: Optional[List[int]], 
    devices: Optional[List[int]]
) -> List[Any]:
    """Helper function to filter a list based on device and sector filters.
    
    Args:
        data_list: The list to filter (e.g., channel names).
        device_list: The DeviceList from the family document containing [sector, device] pairs.
        sectors: List of sectors to filter by (empty list means no sector filtering).
        devices: List of devices to filter by (empty list means no device filtering).
        
    Returns:
        A filtered list based on the specified sectors and devices.
        
    Raises:
        ValueError: If device_list structure is invalid.
    """
    # Convert None to empty lists for consistent handling
    sectors = sectors or []
    devices = devices or []
    
    # If no filtering needed, return the complete list
    if not sectors and not devices:
        return data_list
            
    # Validate device_list structure
    if not device_list or not isinstance(device_list, list):
        raise ValueError("Database error: DeviceList is missing or invalid in the family document")
    
    # Validate that data_list and device_list have matching lengths
    if len(data_list) != len(device_list):
        raise ValueError(
            f"Database error: Data list length ({len(data_list)}) does not match "
            f"DeviceList length ({len(device_list)})"
        )
    
    # Create filtered indices based on sector/device filters
    filtered_indices = []
    available_sectors = set()
    available_devices = set()
    
    for i, device_entry in enumerate(device_list):
        # Validate device entry structure
        if not isinstance(device_entry, list) or len(device_entry) != 2:
            raise ValueError(f"Invalid DeviceList entry at index {i}: {device_entry}")
        
        sector, device = device_entry
        available_sectors.add(sector)
        available_devices.add(device)
        
        # Check if this entry matches our filters
        sector_match = not sectors or sector in sectors
        device_match = not devices or device in devices
        
        if sector_match and device_match:
            filtered_indices.append(i)
    
    # If no matches found, provide helpful error message
    if not filtered_indices:
        error_parts = []
        if sectors:
            invalid_sectors = set(sectors) - available_sectors
            if invalid_sectors:
                error_parts.append(
                    f"Invalid sectors: {sorted(invalid_sectors)}. "
                    f"Available sectors: {sorted(available_sectors)}"
                )
        if devices:
            invalid_devices = set(devices) - available_devices
            if invalid_devices:
                error_parts.append(
                    f"Invalid devices: {sorted(invalid_devices)}. "
                    f"Available devices: {sorted(available_devices)}"
                )
        
        if error_parts:
            raise ModelRetry("; ".join(error_parts))
        else:
            # Filters are valid but no matches
            raise ModelRetry(
                f"No entries match the filter criteria. "
                f"Available sectors: {sorted(available_sectors)}, "
                f"Available devices: {sorted(available_devices)}"
            )
    
    # Return filtered items
    return [data_list[i] for i in filtered_indices]


# ----- Agent tools -----

def list_systems() -> List[str]:
    """Returns a list of all available system names.

    Returns:
        A list of strings containing all distinct system names.
    """
    logger.info("list_systems() called")
    collection = get_collection()
    result = collection.distinct("system")
    logger.info(f"list_systems returning {len(result)} systems")
    return result

def list_families(system: str) -> List[str]:
    """Returns a list of all available family names.

    Args:
        system: Optional system name to filter families by.

    Returns:
        A list of strings containing all distinct family names in the accelerator system.
    """  
    logger.info(f"list_families(system='{system}') called")
    system_doc = _get_system_doc(system)
    if "families" not in system_doc:
        collection = get_collection()
        raise ModelRetry(f"Tool Error: No families found for system '{system}'. Available systems: {collection.distinct('system')}")
    return [family["name"] for family in system_doc["families"]]


def list_common_names(
    system: str,
    family: str,
) -> List[str]:
    """Returns a list of common names for a given system and family.
    
    Args:
        system: Required system name.
        family: Required family name to inspect.

    Returns:
        A list of common names for the given family.
    """
    logger.info(f"list_common_names(system='{system}', family='{family}') called")
    family_doc = _get_family_doc(system, family)
    
    common_names = family_doc.get("setup", {}).get("CommonNames")
    if not common_names:
        raise ModelRetry(f"Common names are not defined for '{system}:{family}'.")
    
    return common_names

def inspect_fields(
    system: str,
    family: str, 
    field: Optional[str] = None, 
    subfield: Optional[str] = None
) -> Dict[str, str]:
    """Returns a dictionary of field names and their value types.
    
    Args:
        system: Required system name.
        family: Required family name to inspect.
        field: Optional field name to inspect within the family.
        subfield: Optional subfield name to inspect within the field.

    Returns:
        A dictionary mapping field names to their Python type names.
    """
    logger.info(f"inspect_fields(system='{system}', family='{family}', field='{field}', subfield='{subfield}') called")
    family_doc = _get_family_doc(system, family)
    
    # Initialize output dictionary
    field_info = {}
    
    # If a specific field is requested, get field names from the nested structure
    if field:
        # Find field with case-insensitive matching
        field_key = next((k for k in family_doc.keys() if case_insensitive_eq(k, field)), None)
        if not field_key:
            available_fields = [k for k in family_doc.keys() if k.lower() != "name"]
            raise ModelRetry(
                f"Tool Error: field '{field}' not found in '{system}:{family}'. "
                f"Available fields: {available_fields}"
            )
            
        nested_doc = family_doc[field_key]
        
        # If a subfield is requested and exists, get its fields
        if subfield and isinstance(nested_doc, dict):
            # Find subfield with case-insensitive matching
            subfield_key = next((k for k in nested_doc.keys() if case_insensitive_eq(k, subfield)), None)
            if not subfield_key:
                available_subfields = list(nested_doc.keys())
                raise ModelRetry(
                    f"Tool Error: subfield '{subfield}' not found in '{system}:{family}:{field}'. "
                    f"Available subfields: {available_subfields}"
                )
                
            sub_doc = nested_doc[subfield_key]
            if isinstance(sub_doc, dict):
                for key, value in sub_doc.items():
                    field_info[key] = type(value).__name__
            return field_info
        
        # Otherwise return fields from the first level of nesting
        if isinstance(nested_doc, dict):
            for key, value in nested_doc.items():
                field_info[key] = type(value).__name__
        return field_info
    
    # Otherwise return top-level fields (excluding name)
    for key, value in family_doc.items():
        if key.lower() != "name":
            field_info[key] = type(value).__name__
    return field_info

def get_field_data(
    system: str,
    family: str, 
    field: Optional[str] = None, 
    subfield: Optional[str] = None
) -> str:
    """Returns the values from a specified field or subfield as a JSON string.
    
    Args:
        system: Required system name.
        family: Required family name to retrieve data from.
        field: Optional field name to retrieve.
        subfield: Optional subfield name to retrieve.

    Returns:
        A JSON string representation of the requested data, which could be a dictionary, list, or primitive value.
    """
    logger.info(f"get_field_data(system='{system}', family='{family}', field='{field}', subfield='{subfield}') called")
    family_doc = _get_family_doc(system, family)

    # If a field is specified
    if field:
        # Get available fields
        fields = [f for f in family_doc.keys() if f.lower() != "name"]
        
        # Find field with case-insensitive matching
        field_key = next((f for f in fields if case_insensitive_eq(f, field)), None)
        if not field_key:
            raise ModelRetry(
                f"Tool Error: field '{field}' not found in '{system}:{family}'. "
                f"Available fields: {fields}"
            )
           
        field_doc = family_doc[field_key]
        
        # If a subfield is specified and field_doc is a dictionary 
        if subfield and isinstance(field_doc, dict):            
            # Get available subfields
            subfields = list(field_doc.keys())
            
            # Find subfield with case-insensitive matching
            subfield_key = next((f for f in subfields if case_insensitive_eq(f, subfield)), None)
            if not subfield_key:
                raise ModelRetry(
                    f"Tool Error: subfield '{subfield}' not found in '{system}:{family}:{field}'. "
                    f"Available subfields: {subfields}"
                )
            
            # Return the subfield document
            return json.dumps(field_doc[subfield_key])

        # Return the entire field document
        return json.dumps(field_doc)
        
    # Return the entire family document
    return json.dumps(family_doc)

def list_channel_names(
    system: str,
    family: str, 
    field: str, 
    sectors: Optional[List[int]] = None, 
    devices: Optional[List[int]] = None
) -> List[str]:
    """Returns the channel names list from a family and field.
    
    Args:
        system: Required system name.
        family: Required family name.
        field: Required field name.
        sectors: Optional list of sector numbers to filter by.
        devices: Optional list of device numbers to filter by.

    Returns:
        A list of channel names, filtered by sectors and devices if specified.
    """
    logger.info(f"list_channel_names(system='{system}', family='{family}', field='{field}', sectors={sectors}, devices={devices}) called")
    
    # Validate and fix parameter types
    if sectors is not None and not isinstance(sectors, list):
        if isinstance(sectors, int):
            sectors = [sectors]
        else:
            raise ModelRetry(f"Tool Error: 'sectors' must be a list of integers or None, got {type(sectors).__name__}: {sectors}")
    
    if devices is not None and not isinstance(devices, list):
        if isinstance(devices, int):
            devices = [devices]
        else:
            raise ModelRetry(f"Tool Error: 'devices' must be a list of integers or None, got {type(devices).__name__}: {devices}")
    
    # Get the current OpenTelemetry span
    span = opentelemetry.trace.get_current_span()
    span.set_attribute("input", f"System: {system}, Family: {family}, Field: {field}, Sectors: {sectors}, Devices: {devices}")
    
    family_doc = _get_family_doc(system, family)

    # Check if field is in the family document
    fields = [f for f in family_doc.keys() if f.lower() not in ["name", "setup"]]
    
    # Find field with case-insensitive matching
    field_key = next((f for f in fields if case_insensitive_eq(f, field)), None)
    if not field_key:
        raise ModelRetry(
            f"Tool Error: field '{field}' not found in '{system}:{family}'. "
            f"Available fields: {fields}"
        )

    # Get channel names from the field document
    field_doc = family_doc.get(field_key, {})
    channel_names = field_doc.get("ChannelNames", [])
    
    if not channel_names:
        raise ModelRetry(
            f"Tool Error: No channel names found for '{system}:{family}:{field}'. "
            f"The field exists but does not contain ChannelNames."
        )
    
    # Get device list from the setup section
    setup_doc = family_doc.get("setup", {})
    device_list = setup_doc.get("DeviceList", [])
    
    # If no filtering requested, return all channel names
    if not sectors and not devices:
        span.set_attribute("output", channel_names)
        return channel_names
    
    # If filtering is requested but DeviceList is missing, provide helpful error
    if not device_list:
        raise ModelRetry(
            f"Tool Error: Cannot filter by sectors/devices for '{system}:{family}' "
            f"because DeviceList is not defined in the database."
        )

    # Convert sectors and devices to lists if None
    sectors_list = sectors or []
    devices_list = devices or []
    
    try:
        # Apply filtering with the corrected parameter
        filtered_channel_names = _filter_by_device_sectors(
            channel_names, 
            device_list,  # Fixed: pass device_list instead of family_doc
            sectors_list, 
            devices_list
        )
        
        span.set_attribute("output", filtered_channel_names)
        return filtered_channel_names
        
    except ValueError as e:
        # Convert ValueError from filter function to ModelRetry with context
        raise ModelRetry(
            f"Tool Error: Failed to filter channel names for '{system}:{family}:{field}'. {str(e)}"
        )

def get_AT_index(
    system: str,
    family: str,
    sectors: Optional[List[int]] = None,
    devices: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Returns the AT index for a given system and family.
    
    Args:
        system: Required system name.
        family: Required family name.
        sectors: Optional list of sector numbers to filter by.
        devices: Optional list of device numbers to filter by.

    Returns:
        The AT index data as a Python dictionary, filtered by sectors and devices if specified.
    """
    logger.info(f"get_AT_index(system='{system}', family='{family}', sectors={sectors}, devices={devices}) called")
    
    # Validate and fix parameter types
    if sectors is not None and not isinstance(sectors, list):
        if isinstance(sectors, int):
            sectors = [sectors]
        else:
            raise ModelRetry(f"Tool Error: 'sectors' must be a list of integers or None, got {type(sectors).__name__}: {sectors}")
    
    if devices is not None and not isinstance(devices, list):
        if isinstance(devices, int):
            devices = [devices]
        else:
            raise ModelRetry(f"Tool Error: 'devices' must be a list of integers or None, got {type(devices).__name__}: {devices}")
    
    family_doc = _get_family_doc(system, family)

    # Check if pyAT field exists
    fields = [f for f in family_doc.keys() if f.lower() != "name"]
    field_key = next((f for f in fields if case_insensitive_eq(f, "pyAT")), None)
    if not field_key:
        raise ModelRetry(
            f"Tool Error: pyAT field not found in '{system}:{family}'. "
            f"Available fields: {fields}"
        )
    
    pyat_doc = family_doc[field_key]
    
    # Check if ATIndex exists within pyAT
    if not isinstance(pyat_doc, dict):
        raise ModelRetry(
            f"Tool Error: pyAT field in '{system}:{family}' is not a dictionary. "
            f"Type found: {type(pyat_doc).__name__}"
        )
        
    subfield_key = next((f for f in pyat_doc.keys() if case_insensitive_eq(f, "ATIndex")), None)
    if not subfield_key:
        raise ModelRetry(
            f"Tool Error: ATIndex subfield not found in '{system}:{family}:pyAT'. "
            f"Available subfields: {list(pyat_doc.keys())}"
        )
    
    at_index = pyat_doc[subfield_key]
    
    # If no filtering requested, return the AT index as is
    if not sectors and not devices:
        return at_index
    
    # If AT index is a list, apply filtering
    if isinstance(at_index, list):
        # Get device list from the setup section
        setup_doc = family_doc.get("setup", {})
        device_list = setup_doc.get("DeviceList", [])
        
        # If filtering is requested but DeviceList is missing, provide helpful error
        if not device_list:
            raise ModelRetry(
                f"Tool Error: Cannot filter AT index by sectors/devices for '{system}:{family}' "
                f"because DeviceList is not defined in the database."
            )
        
        # Convert sectors and devices to lists if None
        sectors_list = sectors or []
        devices_list = devices or []
        
        try:
            # Apply filtering with the correct device_list parameter
            filtered_at_index = _filter_by_device_sectors(
                at_index, 
                device_list,
                sectors_list, 
                devices_list
            )
            return filtered_at_index
            
        except ValueError as e:
            # Convert ValueError from filter function to ModelRetry with context
            raise ModelRetry(
                f"Tool Error: Failed to filter AT index for '{system}:{family}'. {str(e)}"
            )
    
    # If AT index is not a list and filtering was requested, inform the user
    if sectors or devices:
        raise ModelRetry(
            f"Tool Error: Cannot filter AT index by sectors/devices for '{system}:{family}' "
            f"because ATIndex is not a list. Type found: {type(at_index).__name__}"
        )
    
    return at_index
    