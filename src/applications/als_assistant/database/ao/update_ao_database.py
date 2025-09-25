#!/usr/bin/env python3
"""AO Database update and maintenance script.

This script provides a complete database refresh workflow for the Accelerator Object
(AO) database. It processes all MATLAB source files through the conversion pipeline
and performs a hard reset of the MongoDB database with fresh data.

The script executes the following operations:
1. **MATLAB Processing**: Processes all .mat files for supported systems
2. **Database Reset**: Drops existing database and recreates collection
3. **Data Import**: Loads processed data into MongoDB
4. **Validation**: Verifies database structure integrity

Supported accelerator systems:
- SR: Storage Ring
- BTS: Booster-to-Storage Ring transport  
- GTB: Gun-to-Booster line (generates GTL, LN, LTB subsystems)
- BR: Booster Ring

This script is designed for:
- Initial database setup
- Periodic database refreshes with updated source data
- Database recovery after corruption
- Development environment initialization

.. warning::
   This script performs destructive database operations. All existing data
   will be permanently lost and replaced with freshly processed data.

.. note::
   The script requires:
   - Valid MATLAB .mat files in the data directory
   - MongoDB connection (configured via environment detection)
   - Proper environment setup with PROJECT_ROOT variable

Usage:
    Execute directly for complete database refresh::
    
        $ python update_ao_database.py
        
    Or run from project root::
    
        $ cd /path/to/project
        $ python src/applications/als_assistant/database/ao/update_ao_database.py

Examples:
    Typical usage for database refresh::
    
        $ python update_ao_database.py
        INFO: Processing MATLAB files for all systems...
        SUCCESS: Python dictionary written to data/MML_ao_250413_SR.py
        SUCCESS: Python dictionary written to data/MML_ao_250413_BR.py
        INFO: Hard resetting database...
        SUCCESS: AO data inserted.
        SUCCESS: Database validation completed successfully.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path using environment variable
project_root = os.getenv('PROJECT_ROOT')
src_dir = Path(project_root) / 'src'
sys.path.insert(0, str(src_dir))

# Import required modules
from applications.als_assistant.database.ao.process_matlab_data import main as process_matlab_ao
from applications.als_assistant.database.ao.ao_database import get_collection

if __name__ == "__main__":
    # Process MATLAB files first so that fresh Python data modules exist before database reset
    for system in ['SR', 'BTS', 'GTB', 'BR']:
        process_matlab_ao(system)
    
    # Update database with hard reset
    # Drops and repopulates the collection, then validates structure integrity
    get_collection(hard_reset=True, validate=True)
