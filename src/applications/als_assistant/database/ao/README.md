# Accelerator Object (AO) Database Module

This module handles MATLAB Accelerator Object (AO) data conversion, storage, and retrieval for accelerator controls.

## Structure

- `ao_config.py` - Configuration settings for AO database connections and processing
- `ao_database.py` - Database connection utilities and validation logic
- `process_matlab_data.py` - MATLAB data conversion and processing tools
- `get_all_pvs.py` - Script to generate a comprehensive list of all PVs from AO data
- `data/` - Contains processed AO dictionaries and manual imports
- `__init__.py` - Package initialization

## Key Features

- **Automatic Environment Detection**: Automatically detects and connects to either containerized or local MongoDB
- Convert MATLAB AO structures into Python dictionaries
- Apply system-specific filters and transformations
- Store and retrieve AO data from MongoDB
- Validate database structure integrity
- Process special cases for different accelerator systems (SR, BR, BTS, GTB → GTL/LN/LTB)

## Database Connection

The system automatically detects your environment:
- **Container Environment**: Connects to `mongo:27017` (Docker container)
- **Local Environment**: Falls back to `localhost:27017` (local MongoDB instance)

No configuration changes needed - it works in both environments seamlessly.

## Usage

### Processing MATLAB files:
```python
from applications.als_assistant.database.ao.process_matlab_data import main

# Process for a specific system
main(system='SR')  # Options: 'SR', 'BR', 'BTS', 'GTB'
```

### Database access:
```python
from applications.als_assistant.database.ao.ao_database import get_collection

# Get the MongoDB collection for AO data (auto-connects to available MongoDB)
collection = get_collection()

# Query for a specific system
sr_data = collection.find_one({"system": "SR"})
```

### Generating PV list:
```bash
# Run the script to generate all_pvs.txt with all PV names
python get_all_pvs.py
```

This creates `all_pvs.txt` containing all unique PV names from the AO database.

## Data Workflow

1. MATLAB `.mat` files are loaded from the `data/` directory
2. Files are processed with `process_matlab_data.py`
3. Processed data is filtered and transformed based on configurations in `ao_config.py`
4. System-specific post-processing is applied:
   - **GTB**: Split into three subsystems (GTL, LN, LTB)
   - **SR, BR, BTS**: Direct processing
5. Data is stored in Python dictionaries in the `data/` directory
6. Manual imports from `data/manual_imports.py` are merged with the processed data
7. `ao_database.py` loads these dictionaries into MongoDB when needed

## Available Systems

- **SR** (Storage Ring)
- **BR** (Booster Ring) 
- **BTS** (Booster-to-Storage transport)
- **GTL** (Gun-to-Linac transport) - derived from GTB
- **LN** (Linac) - derived from GTB  
- **LTB** (Linac-to-Booster transport) - derived from GTB

## Configuration

Database settings are managed through `config.yml`:
```yaml
database:
  ao_db:
    database_name: agentic_db
    collection_name: ao
    host: localhost  # Fallback for local usage

services:
  mongo:
    name: mongo
    port_host: 27017
    port_container: 27017
``` 