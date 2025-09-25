# ALS Accelerator WIKI Tree-Building Algorithm

A typed, Pydantic-based pipeline for extracting durable knowledge from logbook entries and organizing it into a compact, reviewable wiki tree structure.

## Overview

This system processes multi-year logbook entries to propose a compact tree structure (~300–700 pages) for the ALS Accelerator WIKI. It focuses on identifying **durable, reusable knowledge** (concepts, procedures, stable components) while filtering out operational noise.

## Pipeline Steps

1. **Step A**: Extract candidate topics from logbook entries
2. **Step B1**: Incremental canonicalization and deduplication  
3. **Step B2**: Global canonicalization finalization
4. **Step C**: Build compact 2-3 level tree hierarchy
5. **Step D**: Prioritize and prune to target leaf count

## File Structure

```
ALS_wiki/
├── wiki_guidelines.md      # Detailed algorithm specification
├── __init__.py            # Package initialization
├── schemas.py             # All Pydantic models
├── prompts.py             # Prompt builders for Steps A, B1, B2, C, D
├── pipeline.py            # Core logic and orchestrator
├── example_usage.py       # Usage demonstration
├── README.md              # This file
└── artifacts/             # Generated output files
    ├── canonical_topics.json
    ├── tree.json
    └── pruned_tree.json
```

## Usage

### Basic Usage

```python
from ALS_wiki import run_pipeline_sync

result = run_pipeline_sync(
    logbook_path="/path/to/logbook.jsonl",
    output_dir="./artifacts",
    batch_size=50,  # entries per batch (optional, default: 50)
    checkpoint_frequency=10  # checkpoint every N batches (optional, default: 10)
)
```

### Advanced Usage

```python
from ALS_wiki import run_pipeline
from datetime import datetime, timedelta
import asyncio

async def main():
    # Example 1: Process only last 2 years
    since = datetime.now() - timedelta(days=365 * 2)
    
    result = await run_pipeline(
        logbook_path="/path/to/logbook.jsonl",
        output_dir="./artifacts",
        since=since,
        batch_size=25  # Smaller batches for testing
    )
    
    # Example 2: Process specific date range
    since = datetime(2023, 1, 1)      # Start date
    until = datetime(2024, 12, 31)    # End date
    
    result = await run_pipeline(
        logbook_path="/path/to/logbook.jsonl",
        output_dir="./artifacts",
        since=since,
        until=until,
        batch_size=100  # Larger batches for bulk processing
    )
    
    # Example 3: Process last 6 months only
    since = datetime.now() - timedelta(days=180)
    until = datetime.now()
    
    result = await run_pipeline(
        logbook_path="/path/to/logbook.jsonl",
        output_dir="./artifacts",
        since=since,
        until=until
    )
    
    print("Generated files:", result)

asyncio.run(main())
```

### Command Line Usage

```bash
cd ALS_wiki/
python example_usage.py
```

## Configuration

Key constants in `pipeline.py`:

- `MAX_CHILDREN = 7`: Maximum children per tree node
- `TARGET_LEAVES = 500`: Target number of leaf pages
- `BATCH_SIZE = 50`: Logbook entries per processing batch
- `TIME_WINDOW_YEARS = 3`: Years of logbook history to process (default)

### Model Configurations

LLM models are configured directly in `pipeline.py` via the `WIKI_MODELS` dictionary:

```python
WIKI_MODELS = {
    "extract": {
        "provider": "cborg",
        "model_id": "anthropic/claude-sonnet",
        "max_tokens": 4096,
        "temperature": 0.1
    },
    "canon_incremental": {
        "provider": "cborg", 
        "model_id": "anthropic/claude-sonnet",
        "max_tokens": 2048,
        "temperature": 0.1
    },
    # ... etc for canon_global, tree, prune
}
```

Each pipeline step uses its dedicated model configuration optimized for that task.

## Date Range Filtering

The pipeline supports flexible date range filtering:

### Parameters
- `since`: Only process entries **after** this date (inclusive)
- `until`: Only process entries **before** this date (inclusive)

### Default Behavior
- If `since` is not specified: defaults to 3 years ago
- If `until` is not specified: no upper limit (processes to present)

### Common Use Cases

```python
from datetime import datetime, timedelta

# Last year only
since = datetime.now() - timedelta(days=365)
until = datetime.now()

# Specific calendar year
since = datetime(2024, 1, 1)
until = datetime(2024, 12, 31)

# Recent maintenance period
since = datetime(2024, 6, 1)
until = datetime(2024, 8, 31)

# Everything before a major upgrade
until = datetime(2024, 3, 15)  # since will default to 3 years ago
```

## Output Files

1. **canonical_topics.json**: Deduplicated canonical topics with metadata
2. **tree.json**: Initial tree structure organized by system buckets
3. **pruned_tree.json**: Final tree with priority assignments and pruning
4. **wiki_tree_live.md**: 📝 **Live Markdown view** - human-readable tree structure that updates during pipeline execution
5. **checkpoints/**: Binary and JSON checkpoint files for resuming interrupted runs

### Live Markdown Features

The `wiki_tree_live.md` file provides:
- **Real-time updates**: Updates every `checkpoint_frequency` batches during extraction
- **Human-readable format**: Topics organized by system bucket
- **Tree visualization**: Hierarchical structure with priorities
- **IDE-friendly**: Easy to view progress in any text editor
- **Progress tracking**: Shows completion status and statistics
- **Synchronized updates**: Markdown updates align with checkpoint saves

**View live updates:**
```bash
python view_tree.py --watch  # Monitor for real-time changes
python view_tree.py          # View current state
```

## System Buckets

Topics are organized into these system buckets:
- Injector, Booster, BTS, Storage Ring
- RF, Magnets, Power Supplies, Insertion Devices  
- Diagnostics, Vacuum, Timing, Controls
- Safety, Operations, Procedures, Playbooks

## Requirements

- Python 3.8+
- pydantic
- Access to LLM service (configured via `src.core.config` and `src.core.llm`)

## Key Design Principles

- **Ignore frequency**: Presence ≠ importance
- **Durability filter first**: Cut operational noise early
- **Caps prevent sprawl**: Max 7 children, FAQ & Misc overflow
- **Sections, not pages**: Merge small topics into parent sections
- **One-time human review**: For merges and final organization

## Troubleshooting

If you encounter import errors for `src.core.config` or `src.core.llm`, the system will fall back to mock implementations. To use the full pipeline, ensure these modules are available in your Python path.
