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
# Setup project path - using print for early initialization before logger is available
if project_root:
    print(f"INFO: Using PROJECT_ROOT: {project_root}")
else:
    print("WARNING: PROJECT_ROOT not found in environment")

src_dir = Path(project_root) / 'src' if project_root else None

if src_dir and src_dir.exists():
    sys.path.insert(0, str(src_dir))
    print(f"INFO: Added {src_dir} to Python path")
else:
    print("ERROR: Could not determine project root or src directory!")

# Now import the PV finder components
from applications.als_assistant.services.pv_finder.agent import run_pv_finder_graph, initialize_nltk_resources
from configs.logger import get_logger

# Set up logging
logger = get_logger("als_assistant", "pv_finder_test")

async def main():
    """Test the PV Finder with a single query."""
    print("="*60)
    print("PV FINDER STANDALONE TEST")
    print("="*60)
    
    # Initialize NLTK resources (required for the PV finder)
    print("Initializing NLTK resources...")
    initialize_nltk_resources()
    print("✓ NLTK resources initialized\n")
    
    # Test query
    # query = "What is the lifetime PV?"
    # # query = "What is beam current PV?"
    # query = "Injection efficiency"
    query = 'Find all upper EPBI thermocouple PV addresses in Sector 1'
    print(f"Query: '{query}'")
    print("-" * 50)
    
    try:
        # Run the PV finder
        result = await run_pv_finder_graph(query)
        
        # Display results
        if result.pvs:
            print(f"✓ Found {len(result.pvs)} PV(s):")
            for pv in result.pvs:
                print(f"  • {pv}")
        else:
            print("✗ No PVs found")
        
        if result.description:
            print(f"\nDescription:\n{result.description}")
        
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Error with query '{query}': {e}", exc_info=True)
    
    print("="*60)
    print("TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())