#!/usr/bin/env python3
"""Helper script to update RENAME_PROGRESS.md status."""

import sys
from pathlib import Path


def update_status(file_path: str, new_status: str, progress_filename: str = "RENAME_PROGRESS.md"):
    """
    Update the status of a file in a progress tracking file.

    Args:
        file_path: Relative path like 'src/osprey/base/capability.py' or 'docs/source/index.rst'
        new_status: One of '⬜', '🔄', or '✅'
        progress_filename: Name of the progress file (default: 'RENAME_PROGRESS.md')
    """
    progress_file = Path(__file__).parent / progress_filename

    if not progress_file.exists():
        print(f"Error: {progress_file} not found")
        sys.exit(1)

    content = progress_file.read_text()

    # Normalize the file path for Python files only
    if progress_filename == "RENAME_PROGRESS.md" and not file_path.startswith("src/osprey/"):
        file_path = f"src/osprey/{file_path}"

    # Find and replace the line
    lines = content.split('\n')
    updated = False

    for i, line in enumerate(lines):
        if f"`{file_path}`" in line:
            # Replace the status symbol at the beginning
            if line.startswith('- ⬜'):
                lines[i] = line.replace('- ⬜', f'- {new_status}', 1)
            elif line.startswith('- 🔄'):
                lines[i] = line.replace('- 🔄', f'- {new_status}', 1)
            elif line.startswith('- ✅'):
                lines[i] = line.replace('- ✅', f'- {new_status}', 1)
            updated = True
            print(f"Updated {file_path} to {new_status}")
            break

    if not updated:
        print(f"Warning: Could not find {file_path} in progress file")
        sys.exit(1)

    # Update summary counts
    not_started = sum(1 for line in lines if line.startswith('- ⬜'))
    working_on = sum(1 for line in lines if line.startswith('- 🔄'))
    completed = sum(1 for line in lines if line.startswith('- ✅'))
    total = not_started + working_on + completed

    # Update summary section
    for i, line in enumerate(lines):
        if line.startswith('- **Total Files:**'):
            lines[i] = f'- **Total Files:** {total}'
        elif line.startswith('- **Not Started:**'):
            lines[i] = f'- **Not Started:** {not_started}'
        elif line.startswith('- **Working On:**'):
            lines[i] = f'- **Working On:** {working_on}'
        elif line.startswith('- **Completed:**'):
            lines[i] = f'- **Completed:** {completed}'

    # Write back
    progress_file.write_text('\n'.join(lines))
    print(f"Progress: {completed}/{total} complete ({not_started} not started, {working_on} in progress)")


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python update_progress.py <file_path> <status> [progress_file]")
        print("Status: ⬜ (not started), 🔄 (working), ✅ (completed)")
        print("Progress file: RENAME_PROGRESS.md (default) or DOCS_RENAME_PROGRESS.md")
        sys.exit(1)

    progress_file = sys.argv[3] if len(sys.argv) == 4 else "RENAME_PROGRESS.md"
    update_status(sys.argv[1], sys.argv[2], progress_file)
