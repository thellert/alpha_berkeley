#!/usr/bin/env python3
"""
Check progress of the ALS WIKI pipeline.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project paths
project_root = os.environ.get("PROJECT_ROOT", str(Path(__file__).parent.parent.parent.parent.parent))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "src"))

from src.applications.als_assistant.database.ALS_wiki.pipeline import PipelineState


def main():
    """Check pipeline progress."""
    # Use PROJECT_ROOT to build correct path
    project_root = os.environ.get("PROJECT_ROOT", str(Path(__file__).parent.parent.parent.parent.parent))
    output_dir = os.path.join(project_root, "src/applications/als_assistant/database/ALS_wiki/artifacts")
    
    print("🔍 ALS WIKI Pipeline Progress Check")
    print("=" * 50)
    
    state = PipelineState(output_dir)
    
    # Try to load progress checkpoint
    checkpoint_data = state.load_checkpoint("progress")
    if not checkpoint_data:
        print("❌ No progress checkpoint found")
        print("   Pipeline has not been started or no checkpoints saved yet.")
        return
    
    # Get progress summary
    progress = state.get_progress_summary()
    
    print("📊 Progress Summary:")
    print(f"   Total batches: {progress['total_batches']}")
    print(f"   Completed batches: {progress['completed_batches']}")
    print(f"   Progress: {progress['completion_percentage']:.1f}%")
    print(f"   Current step: {progress['current_step']}")
    print(f"   Runtime: {progress['runtime'] or 'Unknown'}")
    print(f"   Last checkpoint: {progress['last_checkpoint']}")
    
    print("\n📋 Steps Completed:")
    for step in ["extraction", "canonicalization", "tree_building", "pruning"]:
        status = "✅" if step in progress['steps_completed'] else "⏳"
        print(f"   {status} {step.replace('_', ' ').title()}")
    
    # Show checkpoint files
    checkpoint_dir = Path(output_dir) / "checkpoints"
    if checkpoint_dir.exists():
        print(f"\n📁 Checkpoint Files ({checkpoint_dir}):")
        for file in sorted(checkpoint_dir.glob("*.json")):
            size_kb = file.stat().st_size / 1024
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"   📄 {file.name} ({size_kb:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # Show artifacts
    artifacts_dir = Path(output_dir)
    if artifacts_dir.exists():
        print(f"\n📦 Generated Artifacts ({artifacts_dir}):")
        for file in sorted(artifacts_dir.glob("*.json")):
            if file.parent.name != "checkpoints":
                size_kb = file.stat().st_size / 1024
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                print(f"   📄 {file.name} ({size_kb:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # Estimate remaining time
    if progress['completion_percentage'] > 0 and progress['runtime']:
        try:
            runtime_hours = float(progress['runtime'].split('h')[0])
            estimated_total = runtime_hours / (progress['completion_percentage'] / 100)
            remaining = estimated_total - runtime_hours
            print(f"\n⏱️  Estimated remaining time: {remaining:.1f} hours")
        except:
            pass
    
    print(f"\n💡 To resume: python example_usage.py")
    print(f"💡 To restart: Set fresh_start=True in example_usage.py")


if __name__ == "__main__":
    main()
