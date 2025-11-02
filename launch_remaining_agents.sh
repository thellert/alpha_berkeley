#!/bin/bash

# Get all remaining files
REMAINING_FILES=$(grep "^- ⬜ \`src/" RENAME_PROGRESS.md | sed 's/^- ⬜ `\(.*\)`$/\1/')

echo "Found $(echo "$REMAINING_FILES" | wc -l) files to process"
echo ""
echo "Files to process:"
echo "$REMAINING_FILES"
