#!/usr/bin/env python3
"""Extract and catalog all Process Variables (PVs) from the AO database.

This script connects to the MongoDB AO database and systematically extracts all 
ChannelNames from all accelerator systems, families, and fields to create a 
comprehensive catalog of available Process Variables. The script handles different 
data structures and filters out invalid or empty PV entries.

The extraction process:
1. Connects to MongoDB AO database
2. Iterates through all systems (SR, BR, GTB, BTS, etc.)
3. Processes each family (BPM, HCM, VCM, etc.) within systems
4. Extracts ChannelNames from all fields except 'name' and 'setup'
5. Filters out empty, null, or 'NaN' entries
6. Generates a sorted, deduplicated list of unique PVs

Usage:
    Execute directly as a script::
    
        $ python get_all_pvs.py
        
    Or import and use the main function::
    
        >>> from applications.als_assistant.database.ao.get_all_pvs import main
        >>> result = main()
        >>> print(f"Extraction completed with exit code: {result}")

Output:
    Creates 'all_pvs.txt' containing:
    - Header with metadata and PV count
    - Sorted list of all unique PVs across all systems
    - One PV per line for easy processing

.. note::
   Requires active MongoDB connection and populated AO database.
   The script will fail if the database is empty or inaccessible.

.. warning::
   Output file 'all_pvs.txt' will be overwritten if it already exists.

Examples:
    Basic execution::
    
        $ python get_all_pvs.py
        INFO: Connecting to AO database and extracting PVs...
        INFO: Processing system: SR
        INFO: Processing system: BR
        SUCCESS: All unique PVs saved to: all_pvs.txt
"""

import sys
from applications.als_assistant.database.ao.ao_database import get_collection
from configs.logger import get_logger

# Initialize logger for this module
logger = get_logger("framework", "base")


def main():
    """Extract all Process Variables from AO database and save to text file.
    
    Connects to the MongoDB AO database, systematically extracts all ChannelNames 
    from all systems and families, filters out invalid entries, and saves a 
    comprehensive catalog of unique PVs to 'all_pvs.txt'.
    
    The function processes the hierarchical database structure:
    - Systems (SR, BR, GTB, BTS, etc.)
    - Families within systems (BPM, HCM, VCM, etc.)  
    - Fields within families (Monitor, Setpoint, etc.)
    - ChannelNames within fields (actual PV strings)
    
    :return: Exit code - 0 for success, 1 for failure
    :rtype: int
    :raises Exception: If database connection fails or data extraction encounters errors
    
    .. note::
       The output file 'all_pvs.txt' will be created in the current working directory
       and will overwrite any existing file with the same name.
    
    Examples:
        Direct function call::
        
            >>> exit_code = main()
            >>> if exit_code == 0:
            ...     print("PV extraction completed successfully")
            ... else:
            ...     print("PV extraction failed")
    """
    try:
        logger.info("Connecting to AO database and extracting PVs...")
        
        # Get the database collection
        collection = get_collection()
        
        all_pvs = []
        
        # Get all systems from the database
        systems = collection.find({})
        
        for system_doc in systems:
            system_name = system_doc.get("system", "Unknown")
            families = system_doc.get("families", [])
            
            logger.info(f"Processing system: {system_name}")
            
            for family in families:
                # Skip the 'name' field and process all other fields
                for field_name, field_value in family.items():
                    if field_name == "name":
                        continue
                        
                    # Check if this field has ChannelNames
                    if isinstance(field_value, dict) and "ChannelNames" in field_value:
                        channel_names = field_value["ChannelNames"]
                        
                        # Handle different types of ChannelNames data
                        if isinstance(channel_names, list):
                            for pv in channel_names:
                                if pv and pv != "" and pv != "NaN":  # Skip empty/invalid PVs
                                    all_pvs.append(pv)
                                    
                        elif isinstance(channel_names, str) and channel_names != "" and channel_names != "NaN":
                            all_pvs.append(channel_names)
        
        # Remove duplicates and sort
        unique_pvs = sorted(set(all_pvs))
        
        logger.info(f"Found {len(unique_pvs)} unique PVs across all systems")
        
        # Save to file
        output_file = "all_pvs.txt"
        with open(output_file, 'w') as f:
            f.write("# All PVs from AO Database\n")
            f.write(f"# Total unique PVs: {len(unique_pvs)}\n")
            f.write("# Generated by get_all_pvs.py\n\n")
            
            for pv in unique_pvs:
                f.write(f"{pv}\n")
        
        logger.success(f"All unique PVs saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())