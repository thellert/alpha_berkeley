#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Custom startup script initiated..."

# Determine container type from environment
EXECUTION_MODE=${EPICS_EXECUTION_MODE:-unknown}

echo "=============================================="
echo "Starting Jupyter Container: $EXECUTION_MODE"
if [ "$EXECUTION_MODE" = "read" ]; then
    echo "🔒 Read Container - Read-Only & Simulation"
elif [ "$EXECUTION_MODE" = "write_access" ]; then
    echo "⚠️  Write Access Container - DANGEROUS!"
else
    echo "❓ Unknown execution mode: $EXECUTION_MODE"
fi
echo "=============================================="

# Ensure standard paths are likely available
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"

echo "Current PATH: $PATH"
echo "Running whoami: $(whoami)"
echo "Locating pip: $(which pip || echo 'pip not found in PATH')"
echo "Locating start-notebook.sh: $(which start-notebook.sh || echo 'start-notebook.sh not found in PATH')"
echo "Locating /usr/local/bin/start-notebook.sh: $(ls -l /usr/local/bin/start-notebook.sh || echo '/usr/local/bin/start-notebook.sh does not exist')"

# Install all framework dependencies
pip install --no-cache-dir -r /jupyter/repo_src/requirements.txt
echo "All framework packages installed from main requirements.txt"

echo "Creating IPython default profile startup directory..."
mkdir -p /home/jovyan/.ipython/profile_default/startup/
echo "Copying kernel startup script to IPython profile."
# Note: The source path is the location of startup_script.py within the container
cp /jupyter/startup_script.py /home/jovyan/.ipython/profile_default/startup/00-custom-kernel-init.py
echo "Ensuring .ipython directory is owned by jovyan."
# The base image should handle jovyan's home dir permissions, but this is a safeguard.
chown -R jovyan:users /home/jovyan/.ipython || echo "Warning: chown on .ipython directory failed, this might lead to permission issues for the kernel."

echo "Setting up Jupyter work directory..."
# Create work directory if it doesn't exist
mkdir -p /home/jovyan/work

# Ensure work directory is owned by jovyan
chown -R jovyan:users /home/jovyan/work || echo "Warning: chown on work directory failed"

echo "Starting jupyter Notebook server..."
# Execute jupyterLab using the start-notebook.sh script with all necessary parameters
exec /usr/local/bin/start-notebook.sh --notebook-dir=/home/jovyan/work --NotebookApp.token='' --NotebookApp.disable_check_xsrf=True --allow-root --port=8088 