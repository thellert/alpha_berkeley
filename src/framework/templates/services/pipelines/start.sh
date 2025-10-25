#!/bin/bash
# Pipelines startup wrapper - installs framework before starting server
set -e

echo "=============================================="
echo "Starting Pipelines Container"
echo "=============================================="

# Install framework from development source
if [ -d "/pipelines/framework_src" ]; then
    echo "Installing framework from /pipelines/framework_src (editable mode)..."
    pip install -e /pipelines/framework_src
    echo "✓ Framework installed successfully"
    
    # Install framework dependencies
    if [ -f "/pipelines/framework_src/requirements.txt" ]; then
        echo "Installing framework dependencies..."
        pip install --no-cache-dir -r /pipelines/framework_src/requirements.txt
        echo "✓ Framework dependencies installed"
    fi
else
    echo "WARNING: /pipelines/framework_src not found"
    echo "Attempting to use framework from pip install..."
fi

# Verify pipeline interface files exist
if [ -n "$PIPELINES_DIR" ] && [ -f "$PIPELINES_DIR/main.py" ]; then
    echo "✓ Pipeline interface found at $PIPELINES_DIR/main.py"
    ls -la "$PIPELINES_DIR"
else
    echo "WARNING: Pipeline interface not found at $PIPELINES_DIR"
    echo "Make sure main.py was copied during project initialization"
fi

# Call the original pipelines start script
echo "Starting pipelines server..."
cd /app
exec bash start.sh

