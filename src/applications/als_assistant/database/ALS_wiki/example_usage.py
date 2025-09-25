#!/usr/bin/env python3
"""
Example usage of the ALS WIKI tree-building pipeline.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use PROJECT_ROOT from environment, fallback to relative path
project_root = os.environ.get("PROJECT_ROOT")
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "src"))  # Add src folder for framework imports

from src.applications.als_assistant.database.ALS_wiki.pipeline import run_pipeline_sync


def main():
    """Run the WIKI pipeline on the logbook data."""
    
    # Configuration - build paths using PROJECT_ROOT
    project_root = os.environ.get("PROJECT_ROOT", str(Path(__file__).parent.parent.parent.parent.parent))
    logbook_path = os.path.join(project_root, "src/applications/als_assistant/database/logbook/logbook_250525.jsonl")
    output_dir = os.path.join(project_root, "src/applications/als_assistant/database/ALS_wiki/artifacts")
    
    # Batch size for processing (entries per batch sent to LLM)
    batch_size = 3  # Adjust based on your model's context window and performance
    
    # Checkpoint/Resume options
    resume = True          # Resume from checkpoints if available
    fresh_start = False    # Set to True to ignore checkpoints and start fresh
    checkpoint_frequency = 2  # Save checkpoints and update Markdown every N batches
    
    # Date range configuration
    # # Example 1: Process entries
    # since = datetime.now() - timedelta(days=100)
    # until = datetime.now() - timedelta(days=30)
    
    since = datetime(2025, 1, 1)
    until = datetime(2025, 7, 1)
     
    # Example 2: Process entries from a specific date range (uncomment to use)
    # since = datetime(2023, 1, 1)  # Start from Jan 1, 2023
    # until = datetime(2024, 12, 31)  # End at Dec 31, 2024
    
    # Example 3: Process only entries from the last 6 months (uncomment to use)
    # since = datetime.now() - timedelta(days=180)
    # until = datetime.now()
    
    print("ALS Accelerator WIKI Tree Builder")
    print("=" * 40)
    print(f"Logbook: {logbook_path}")
    print(f"Output: {output_dir}")
    print(f"Batch size: {batch_size} entries per batch")
    print(f"Checkpoint frequency: Every {checkpoint_frequency} batches")
    print(f"Resume mode: {'Fresh start' if fresh_start else ('Resume' if resume else 'No checkpoints')}")
    print(f"Processing entries since: {since.strftime('%Y-%m-%d %H:%M:%S')}")
    if until:
        print(f"Processing entries until: {until.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Processing entries until: (no limit)")
    print()
    
    # Check if logbook file exists
    if not Path(logbook_path).exists():
        print(f"Error: Logbook file not found: {logbook_path}")
        return
    
    try:
        # Run the pipeline
        result = run_pipeline_sync(
            logbook_path=logbook_path,
            output_dir=output_dir,
            since=since,
            until=until,
            batch_size=batch_size,
            resume=resume,
            fresh_start=fresh_start,
            checkpoint_frequency=checkpoint_frequency
        )
        
        if "error" in result:
            print(f"Pipeline failed: {result['error']}")
            return
        
        print("\nPipeline completed successfully!")
        print("Generated files:")
        for name, path in result.items():
            print(f"  {name}: {path}")
        
        print("\nNext steps:")
        print("1. 📝 Review the live Markdown: wiki_tree_live.md")
        print("2. 📊 Check canonical topics: canonical_topics.json")
        print("3. 🌳 Examine tree structure: tree.json")
        print("4. 🎯 Review final prioritized tree: pruned_tree.json")
        print("5. 🏗️  Use the tree structure to build your wiki pages")
        print("\n💡 View live updates: python view_tree.py --watch")
        
    except Exception as e:
        print(f"Error running pipeline: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
