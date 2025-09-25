# Accelerator Database Module

This directory contains code related to accessing, processing, and storing accelerator data.

## Structure

The database module is organized as follows:

```
database/
├── __init__.py            # Package initialization
├── README.md              # This file
└── ao/                    # Accelerator Objects subpackage
    ├── __init__.py        # AO subpackage initialization
    ├── config.py          # Database configuration and field mappings
    ├── database_connection.py # MongoDB connection utilities
    ├── process_matlab_ao.py # MATLAB .mat to Python dictionary converter
    ├── test_db.py         # Database testing utilities
    └── data/              # Generated data files
        ├── __init__.py    # Data module initialization
        ├── manual_imports.py # Manual additions to the AO structure
        ├── MML_ao_*.py    # Generated Python dictionary files (SR, BR, GTL, etc.)
        └── MML_ao_*.mat   # Original MATLAB data files
```

## Workflow

1. The MATLAB .mat files in the `data/` directory contain the raw accelerator objects data from the accelerator control system.
2. The `process_matlab_ao.py` script processes these files to:
   - Convert MATLAB data structures to Python dictionaries
   - Clean and normalize the data
   - Apply whitelist/blacklist filters based on configuration
   - Apply system-specific post-processing
   - Add manual imports from manual_imports.py
   - Save the processed data as Python dictionaries (.py files)

3. The `database_connection.py` module provides functions to:
   - Connect to MongoDB
   - Load the Python dictionaries into the database
   - Validate the database structure
   - Query the database

## Usage

To reset the database and reload all data:

```python
from database.ao.database_connection import get_collection

# Reset and reload the database
collection = get_collection(hard_reset=True)
```

To test the database connection:

```bash
python database/ao/test_db.py
```

## Notes

When adding or modifying fields:
1. Update the configuration in `config.py`
2. For manual additions, edit `data/manual_imports.py`
3. Run `process_matlab_ao.py` to regenerate the Python dictionaries
4. Reset the database to load the updated data 