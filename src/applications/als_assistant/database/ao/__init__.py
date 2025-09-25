"""Accelerator Object (AO) database subpackage.

This subpackage provides comprehensive functionality for managing Adaptive Optics (AO) 
accelerator data structures in MongoDB. It handles the conversion, storage, and retrieval 
of accelerator control system data including beam position monitors, corrector magnets, 
quadrupoles, and other accelerator components across multiple beamlines (SR, BR, GTB, BTS).

The subpackage includes:
- Database connection and configuration management
- MATLAB .mat file processing and conversion to Python dictionaries
- Data validation and structure verification
- Automated database population and updates
- PV (Process Variable) extraction and cataloging

Key modules:
    ao_database: Core database connection and data management functions
    ao_config: Configuration settings and system-specific filtering rules
    process_matlab_data: MATLAB file processing and data transformation
    get_all_pvs: PV extraction utilities for comprehensive system cataloging
    update_ao_database: Database update scripts and maintenance tools

.. note::
   This subpackage requires MongoDB connection and assumes specific MATLAB data
   structures from the ALS (Advanced Light Source) control system.

.. seealso::
   :mod:`applications.als_assistant.database.ao.ao_database` : Core database functions
   :mod:`applications.als_assistant.database.ao.ao_config` : Configuration management
"""
