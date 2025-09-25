#!/usr/bin/env python3
"""
Standalone test script for the PV Finder.
This script tests the PV finder directly without using the server.
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
project_root = os.getenv('PROJECT_ROOT')
src_dir = Path(project_root) / 'src' if project_root else None
sys.path.insert(0, str(src_dir))
   
# Now import the PV finder components
from applications.als_assistant.services.pv_finder.agent import run_pv_finder_graph, initialize_nltk_resources
from applications.als_assistant.database.ao.ao_database import get_collection as get_ao_collection
from configs.logger import get_logger
from applications.als_assistant.services.pv_finder.tools import list_systems, list_families, list_common_names, inspect_fields, get_field_data, list_channel_names, get_AT_index

# Set up logging
logger = get_logger("als_assistant", "pv_finder_test")

# # Initialize database with hard reset to ensure latest data
# logger.info("Initializing AO database with hard reset to load latest data...")
# get_ao_collection(auto_load=True, hard_reset=True, validate=True)
# logger.info("Database initialization complete.")

result = list_channel_names(system='SR', family='EPBI_TC_UP', field='Monitor', sectors=[1], devices=None)
logger.info(f"list_channel_names(system='SR', family='EPBI_TC_UP', field='Monitor', sectors=[1], devices=None) = {result}")

# Test basic functionality
logger.info("Testing basic PV finder functionality...")
logger.info("Testing BTS families:")
logger.info(list_families('BTS'))

logger.info("\nTesting BTS BPM fields:")
logger.info(inspect_fields('BTS', 'BPM'))

logger.info("\nTesting our specific BTS BPM function call:")
result = list_channel_names(system='BTS', family='BPM', field='X', devices=[6])
logger.info(f"list_channel_names(system='BTS', family='BPM', field='X', devices=[6]) = {result}")

logger.info("\nTesting BTS BPM Y field (benchmark target):")
result_y = list_channel_names(system='BTS', family='BPM', field='Y')
logger.info(f"list_channel_names(system='BTS', family='BPM', field='Y') = {result_y}")