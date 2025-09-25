"""Database connection and management utilities for Accelerator Object (AO) data.

This module provides comprehensive database management functionality for storing
and retrieving Accelerator Object data in MongoDB. It handles automatic database
initialization, data validation, and provides utilities for managing accelerator
control system data across multiple beamlines.

Key features:
- Automatic MongoDB connection management with environment detection
- Database initialization and population from MATLAB data files
- Comprehensive data validation and structure verification
- Support for multiple accelerator systems (SR, BR, GTB, BTS, etc.)
- Automatic data loading when database is empty
- Hard reset capabilities for database maintenance

The module manages hierarchical accelerator data with the following structure:
- Systems: Top-level accelerator systems (SR, BR, GTB, BTS)
- Families: Device families within systems (BPM, HCM, VCM, etc.)
- Fields: Data fields within families (Monitor, Setpoint, etc.)
- ChannelNames: EPICS PV names for actual device communication

Data validation ensures:
- All family fields (except 'setup' and 'pyAT') contain 'ChannelNames'
- Setup fields contain required 'DeviceList' information
- PyAT fields contain 'ATIndex' for accelerator physics calculations

.. note::
   The database is automatically populated from MATLAB .mat files if empty.
   This behavior can be controlled via the auto_load parameter.

.. warning::
   Hard reset operations will completely drop and recreate the database.
   Use with caution in production environments.

Examples:
    Basic database connection::
    
        >>> collection = get_collection()
        >>> doc_count = collection.count_documents({})
        >>> print(f"Database contains {doc_count} documents")
        
    Database reset and validation::
    
        >>> collection = get_collection(hard_reset=True, validate=True)
        >>> # Database is dropped, reloaded, and validated
"""
# Standard library imports
from pymongo import MongoClient
from applications.als_assistant.database.ao import ao_config
from configs.logger import get_logger

# Initialize logger for this module
logger = get_logger("framework", "base")


def get_collection(auto_load=True, hard_reset=False, validate=False):
    """Connect to MongoDB and return AO data collection with optional initialization.
    
    Establishes connection to MongoDB using environment-detected parameters and 
    returns the AO data collection. Provides options for automatic data loading,
    hard database reset, and structure validation.
    
    The function handles the complete database lifecycle:
    - Establishes MongoDB connection using detected host/port
    - Optionally drops and recreates the collection (hard_reset=True)
    - Automatically populates empty database with reference data (auto_load=True)
    - Validates database structure integrity (validate=True)
    
    :param auto_load: Automatically load AO data when database is empty
    :type auto_load: bool
    :param hard_reset: Drop collection and reload all data from source files
    :type hard_reset: bool  
    :param validate: Validate database structure after loading operations
    :type validate: bool
    :return: MongoDB collection object for AO data operations
    :rtype: pymongo.collection.Collection
    :raises ConnectionError: If MongoDB connection fails
    :raises ValueError: If database configuration is invalid
    
    .. note::
       auto_load should be set to False in production environments to avoid
       unexpected database modifications during routine operations.
       
    .. warning::
       hard_reset=True will permanently delete all existing data in the collection.
       This operation cannot be undone.
    
    Examples:
        Basic connection with auto-loading::
        
            >>> collection = get_collection()
            >>> systems = collection.find({})
            >>> print(f"Found {collection.count_documents({})} systems")
            
        Production connection without auto-loading::
        
            >>> collection = get_collection(auto_load=False)
            >>> # Safe for production - won't modify existing data
            
        Database maintenance with full reset::
        
            >>> collection = get_collection(hard_reset=True, validate=True)
            >>> # Database is completely rebuilt and validated
    """
    logger.debug(f"Connecting to MongoDB at host: {ao_config.DB_HOST}, port: {ao_config.DB_PORT}")
    client = MongoClient(
        host=ao_config.DB_HOST,
        port=ao_config.DB_PORT
    )
    db = client[ao_config.DB_NAME]
    collection = db[ao_config.COLLECTION_NAME]

    if hard_reset:
        logger.info("Hard resetting database...")
        collection.drop()
        collection = db[ao_config.COLLECTION_NAME]  # Reconnect to the collection
        auto_load = True  # Force reload after destructive reset to ensure collection is repopulated

    if auto_load:
        _ensure_db_loaded(collection, validate)

    return collection


def _ensure_db_loaded(collection, validate=False):
    """Ensure database is populated with AO data, loading if empty.
    
    Checks if the MongoDB collection contains any documents and automatically
    loads reference AO data from MATLAB files if the collection is empty.
    Optionally validates the database structure after loading.
    
    :param collection: MongoDB collection to check and potentially populate
    :type collection: pymongo.collection.Collection
    :param validate: Validate database structure after loading data
    :type validate: bool
    :raises Exception: If data loading or validation fails
    
    .. note::
       This function is called automatically by get_collection() when auto_load=True.
       It ensures the database always contains the reference AO data structure.
    """
    # Cheap emptiness check; avoids reading or iterating the entire dataset
    doc_count = collection.count_documents({})
    if doc_count == 0:
        logger.info("Database is empty. Loading default AO data...")
        # Load JSON
        ao_data = _load_ao_from_files()
        
        # Insert into DB
        _insert_ao_into_db(collection, ao_data)
        logger.success("AO data inserted.")
    
    # Validate database structure
    if validate:
        validate_database_structure(collection)


def validate_database_structure(collection):
    """Validate AO database structure and data integrity.
    
    Performs comprehensive validation of the database structure to ensure data
    integrity and consistency across all systems and families. Checks for required
    fields, proper data organization, and validates the hierarchical structure.
    
    Validation checks:
    - All family fields (except 'setup' and 'pyAT') contain 'ChannelNames' subfield
    - Setup fields contain required 'DeviceList' information
    - PyAT fields contain 'ATIndex' for accelerator physics calculations
    - Field structures are properly formatted as dictionaries
    - No missing or malformed critical data elements
    
    :param collection: MongoDB collection containing AO data to validate
    :type collection: pymongo.collection.Collection
    :return: True if all validation checks pass, False if issues found
    :rtype: bool
    
    .. note::
       Validation warnings are logged but don't prevent database operation.
       Critical errors are logged as errors and cause validation to fail.
       
    .. warning::
       This function performs read-only validation and will not modify data.
       Issues must be resolved by reprocessing source data files.
    
    Examples:
        Validate existing database::
        
            >>> collection = get_collection(auto_load=False)
            >>> is_valid = validate_database_structure(collection)
            >>> if not is_valid:
            ...     print("Database validation failed - check logs")
            
        Validate after database reset::
        
            >>> collection = get_collection(hard_reset=True)
            >>> is_valid = validate_database_structure(collection)
            >>> assert is_valid, "Fresh database should always validate"
    """
    logger.info("Validating database structure...")
    issues_found = 0
    
    # Get all systems
    systems = collection.find({})
    
    for system_doc in systems:
        system_name = system_doc.get("system", "Unknown")
        families = system_doc.get("families", [])
        
        for family in families:
            family_name = family.get("name", "Unknown")
            
            # Check setup field if it exists
            if "setup" in family:
                setup = family["setup"]
                if not isinstance(setup, dict):
                    logger.warning(f"'setup' in '{system_name}:{family_name}' is not a dictionary")
                    issues_found += 1
                elif "DeviceList" not in setup:
                    logger.warning(f"Missing 'DeviceList' in '{system_name}:{family_name}:setup'")
                    issues_found += 1
            
            # Check all fields except 'name', 'setup', and handle 'pyAT' specially
            for field_name, field_value in family.items():
                if field_name.lower() in ["name", "setup"]:
                    continue
                
                # Verify field is a dictionary
                if not isinstance(field_value, dict):
                    logger.warning(f"Field '{field_name}' in '{system_name}:{family_name}' is not a dictionary")
                    issues_found += 1
                    continue
                
                # Special check for pyAT field
                if field_name.lower() == "pyat":
                    # pyAT fields carry lattice indices and metadata, not PV channel lists
                    if "ATIndex" not in field_value:
                        logger.warning(f"Missing 'ATIndex' in '{system_name}:{family_name}:pyAT'")
                        issues_found += 1
                    continue  # Skip ChannelNames check for pyAT fields
                
                # Check for ChannelNames in all fields except setup and pyAT
                if "ChannelNames" not in field_value:
                    logger.error(f"Missing 'ChannelNames' in '{system_name}:{family_name}:{field_name}'")
                    issues_found += 1
    
    if issues_found > 0:
        logger.warning(f"Database validation completed with {issues_found} issues found.")
        return False
    else:
        logger.success("Database validation completed successfully.")
        return True


def _insert_ao_into_db(collection, ao_data):
    """Insert processed AO data into MongoDB collection.
    
    Transforms the hierarchical AO data structure into MongoDB documents and
    inserts them into the specified collection. Each accelerator system becomes
    a separate document containing all its families as nested arrays.
    
    Document structure:
    - system: System identifier (SR, BR, GTB, BTS)
    - families: Array of family objects, each containing device data
    
    :param collection: Target MongoDB collection for data insertion
    :type collection: pymongo.collection.Collection
    :param ao_data: Hierarchical dictionary of processed AO data
    :type ao_data: dict
    :raises Exception: If database insertion fails
    
    .. warning::
       This function drops the existing collection before inserting new data.
       All existing data will be permanently lost.
    """
    # Clear existing data to guarantee idempotent load and eliminate stale documents
    collection.drop()
    
    # Track entries for reporting
    entries = []
    
    # For each system (SR, BR, etc)
    for system, system_data in ao_data.items():
        # Create a system document with families as nested array
        system_doc = {
            "system": system,
            "families": []
        }
        
        # Check if system_data contains families (BPM, HCM, etc)
        if isinstance(system_data, dict):
            # Add each family as an entry in the families array
            for family_name, family_data in system_data.items():
                if isinstance(family_data, dict):
                    family_entry = {
                        "name": family_name
                    }
                    family_entry.update(family_data)
                    system_doc["families"].append(family_entry)
        
        # Insert the complete system document with all its families
        collection.insert_one(system_doc)
        entries.append(system_doc)
    
    logger.info(f"Inserted {len(entries)} documents into the database.")
    
    # Sanity check: verify the number of documents in the collection
    doc_count = collection.count_documents({})
    if doc_count != len(entries):
        logger.warning(f"Expected {len(entries)} documents, but found {doc_count} in the collection.")
    
    
def _load_ao_from_files():
    """Load reference AO data from processed Python data files.
    
    Imports and combines AO data from all processed accelerator systems. The data
    files are generated by the MATLAB processing pipeline and contain the complete
    accelerator object structures for each system.
    
    Loaded systems:
    - SR: Storage Ring accelerator data
    - BR: Booster Ring accelerator data  
    - GTL: Gun-to-Linac transport line data
    - LN: Linac accelerator data
    - LTB: Linac-to-Booster transport line data
    - BTS: Booster-to-Storage Ring transport data
    
    :return: Dictionary mapping system names to their AO data structures
    :rtype: dict
    :raises ImportError: If required data files are missing or corrupted
    
    .. note::
       Data files are automatically generated by process_matlab_data.py and
       should not be manually edited. Regenerate files if source data changes.
    """
    # Generated modules; an ImportError here indicates preprocessing has not been executed yet
    from applications.als_assistant.database.ao.data.MML_ao_250413_SR import MML_ao_SR
    from applications.als_assistant.database.ao.data.MML_ao_250413_BR import MML_ao_BR
    from applications.als_assistant.database.ao.data.MML_ao_250413_GTL import MML_ao_GTL
    from applications.als_assistant.database.ao.data.MML_ao_250413_LN import MML_ao_LN
    from applications.als_assistant.database.ao.data.MML_ao_250413_LTB import MML_ao_LTB
    from applications.als_assistant.database.ao.data.MML_ao_250413_BTS import MML_ao_BTS

    # Initialize the ao_data dictionary
    ao_data = {}
    
    # Assign the imported module variables to the dictionary
    ao_data['SR'] = MML_ao_SR
    ao_data['BR'] = MML_ao_BR
    ao_data['GTL'] = MML_ao_GTL
    ao_data['LN'] = MML_ao_LN
    ao_data['LTB'] = MML_ao_LTB
    ao_data['BTS'] = MML_ao_BTS
    
    return ao_data  