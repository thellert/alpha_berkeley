#!/bin/bash

# Get all remaining documentation files to process
grep "^- ⬜" /Users/thellert/LBL/ML/alpha_berkeley/DOCS_RENAME_PROGRESS.md | sed 's/^- ⬜ `\(.*\)`$/\1/' | while read -r file; do
    echo "$file"
done
