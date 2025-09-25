"""Simple test script for the launcher service.

This script provides basic testing of the launcher service functionality
without requiring the full framework setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables before any other imports
from dotenv import load_dotenv
load_dotenv()

# Ensure CBORG_API_KEY is available for the test
if not os.environ.get('CBORG_API_KEY'):
    raise RuntimeError("CBORG_API_KEY not found in environment - check .env file")

# Add the src directory to the Python path using PROJECT_ROOT from .env
project_root = Path(os.getenv("PROJECT_ROOT"))
if not project_root or not project_root.exists():
    raise RuntimeError("PROJECT_ROOT environment variable not set or path doesn't exist")
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from applications.als_assistant.services.launcher.service import LauncherService
from applications.als_assistant.services.launcher.models import LauncherServiceRequest, LauncherConfig


async def test_launcher_service():
    """Test the launcher service with various queries."""
    
    # Create a test config
    config = LauncherConfig(
        phoebus_executable="/home/als/physbase/hlc/Scripts/runPhoebus.sh"  # Use real Phoebus executable
    )
     
    # Create the service
    service = LauncherService(config)
    
    # Get complete configurable for the launcher service
    from configs.config import _get_configurable
    configurable = _get_configurable()
    
    # Test cases with explicit PV addresses
    test_cases = [
        {
            "query": "Open Data Browser for LCW data, last 6h, highlight the last 2h as maintenance",
            "pv_addresses": ["B37:Ex106CHW:WetBulbTempF","SR02C___LCWTEMPAM00","SR12C:QFA2:TC3"],
            "runtime_config": configurable,
            "description": "Data browser with explicit PV addresses"
            
        },
        # {
        #     "query": "Open Data Browser for temperature data, last 6h",
        #     "pv_addresses": ["SR01:CC:FPGA:temperature","SR01:CC:QSFP1:temperature"],
        #     "runtime_config": configurable,
        #     "description": "Data browser with explicit PV addresses"
        # },
        # {
        #     "query": "Open Data Browser for beam current",
        #     "pv_addresses": [],
        #     "description": "Data browser without provided PV"
        # },
        # {
        #     "query": "Show me the phoebus panel",
        #     "pv_addresses": None,
        #     "description": "Phoebus panel request"
        # },
        # {
        #     "query": "Open data browser",
        #     "pv_addresses": None,
        #     "description": "Data browser without specific PVs"
        # }
    ]
    
    print("Testing Launcher Service")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Query: {case['query']}")
        if case['pv_addresses']:
            print(f"   PVs: {case['pv_addresses']}")
        print("-" * 30)
        
        request = LauncherServiceRequest(
            query=case["query"],
            pv_addresses=case["pv_addresses"],
            runtime_config=case["runtime_config"]
        )
        result = await service.execute(request)
        
        if result.success:
            print(f"✅ Success: {result.command_name}")
            print(f"   Description: {result.command_description}")
            print(f"   Launch URI: {result.launch_uri}")
        else:
            print(f"❌ Failed: {result.error_message}")



if __name__ == "__main__":
    
    # Run tests
    asyncio.run(test_launcher_service())
