# Migration Guide: v0.7.x → v0.8.0 (Quick Rename)

This guide is for migrating applications from **Alpha Berkeley Framework v0.7.x** to **Osprey Framework v0.8.0**.

**Migration Type**: Quick Rename Only  
**Estimated Time**: 15-30 minutes  
**Complexity**: Simple - only package name and import paths change

---

## ✅ Pre-Migration Checklist

Confirm with the user:
- [ ] They are on **v0.7.x** (pip-installable architecture)
- [ ] Their application is in a **separate repository** (not embedded in framework)
- [ ] They have **version control** (git) set up
- [ ] Their **virtual environment is activated**

---

## 📋 Migration Steps

### Step 1: Update Package Installation

```bash
# Uninstall old package
pip uninstall alpha-berkeley-framework -y

# Install new package
pip install osprey-framework

# Verify installation
osprey --version  # Should show 0.8.0 or later
```

**What to check:**
- Command completes without errors
- `osprey --version` shows 0.8.0+

---

### Step 2: Update Python Import Statements

**Search and replace in ALL `.py` files:**

```python
# FIND (regex):    from framework\.
# REPLACE WITH:    from osprey.
```

**Common import patterns to update:**

```python
# STATE MANAGEMENT
from framework.state import AgentState, StateManager
# → 
from osprey.state import AgentState, StateManager

# BASE CLASSES
from framework.base.capability import BaseCapability
from framework.base.node import BaseNode
from framework.base.planning import BasePlanner, PlannedStep
# →
from osprey.base.capability import BaseCapability
from osprey.base.node import BaseNode
from osprey.base.planning import BasePlanner, PlannedStep

# REGISTRY
from framework.registry.manager import RegistryManager
from framework.registry import (
    extend_framework_registry,
    CapabilityRegistration,
    ContextClassRegistration,
)
# →
from osprey.registry.manager import RegistryManager
from osprey.registry import (
    extend_framework_registry,
    CapabilityRegistration,
    ContextClassRegistration,
)

# SERVICES
from framework.services.model_providers import ModelProvider
from framework.services.llm_interface import LLMInterface
# →
from osprey.services.model_providers import ModelProvider
from osprey.services.llm_interface import LLMInterface

# DATA MANAGEMENT
from framework.data_management.checkpoint import CheckpointManager
from framework.data_management.execution_log import ExecutionLogger
# →
from osprey.data_management.checkpoint import CheckpointManager
from osprey.data_management.execution_log import ExecutionLogger

# ERROR HANDLING
from framework.base.errors import (
    ErrorSeverity,
    ErrorClassification,
    CapabilityExecutionError,
)
# →
from osprey.base.errors import (
    ErrorSeverity,
    ErrorClassification,
    CapabilityExecutionError,
)

# UTILITIES
from framework.utils.logging import get_logger
from framework.utils.path_manager import PathManager
# →
from osprey.utils.logging import get_logger
from osprey.utils.path_manager import PathManager
```

**Also update TYPE_CHECKING imports:**

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from framework.state import AgentState
    from framework.base.planning import PlannedStep
    from framework.base.capability import BaseCapability
# →
if TYPE_CHECKING:
    from osprey.state import AgentState
    from osprey.base.planning import PlannedStep
    from osprey.base.capability import BaseCapability
```

**Implementation tip:** Use your file editing tools to do a global search and replace across the entire project.

---

### Step 3: Update String-Based Module References

**Search and replace in ALL `.py` files:**

```python
# FIND (regex):    "framework\.
# REPLACE WITH:    "osprey.
```

**Common string patterns:**

```python
# Dynamic imports
module_path = "framework.capabilities.my_capability"
module = importlib.import_module("framework.services.memory")
# →
module_path = "osprey.capabilities.my_capability"
module = importlib.import_module("osprey.services.memory")

# Module references in strings
__module__ = "framework.capabilities.weather"
class_path = "framework.state.AgentState"
# →
__module__ = "osprey.capabilities.weather"
class_path = "osprey.state.AgentState"

# Configuration or registry strings
capability_module = f"framework.capabilities.{name}"
# →
capability_module = f"osprey.capabilities.{name}"
```

---

### Step 4: Update Logger Names (Conditional)

**Only update if code explicitly uses "framework" in logger initialization:**

```python
# IF you see this pattern:
logger = get_logger("framework.my_module")
logger = get_logger("framework.capabilities.weather")
# →
logger = get_logger("osprey.my_module")
logger = get_logger("osprey.capabilities.weather")

# HOWEVER, most code uses __name__ which updates automatically:
logger = get_logger(__name__)  # ✅ No change needed - updates automatically
```

**Check:** Search for `get_logger("framework` to find instances that need updating.

---

### Step 5: Update Dependency Files

**requirements.txt:**

```txt
# FIND:
alpha-berkeley-framework>=0.7.0
alpha-berkeley-framework>=0.7.7
alpha-berkeley-framework==0.7.8

# REPLACE WITH:
osprey-framework>=0.8.0
```

**pyproject.toml:**

```toml
# FIND in dependencies array:
"alpha-berkeley-framework>=0.7.0"

# REPLACE WITH:
"osprey-framework>=0.8.0"
```

**setup.py (if exists):**

```python
# FIND:
install_requires=["alpha-berkeley-framework>=0.7.0"]

# REPLACE WITH:
install_requires=["osprey-framework>=0.8.0"]
```

---

### Step 6: Update Documentation Strings (Optional but Recommended)

**Update brand references in docstrings:**

```python
# BEFORE:
"""
My Weather Capability for the Alpha Berkeley Framework.

This capability integrates with the Alpha Berkeley framework's
execution model to provide weather data.
"""

# AFTER:
"""
My Weather Capability for the Osprey Framework.

This capability integrates with the Osprey framework's
execution model to provide weather data.
"""
```

**IMPORTANT - DO NOT CHANGE these generic uses:**

```python
# KEEP AS-IS (generic architectural terms):
"""Base class for framework capabilities."""
"""The framework's lazy loading pattern prevents circular imports."""
"""Integration with framework systems."""
"""This is true throughout the framework."""
```

**Rule:** Only change "Alpha Berkeley Framework" → "Osprey Framework". Keep lowercase "framework" as-is when it's describing architecture generically.

---

### Step 7: Update README and Documentation (Optional)

If the project has a README.md or documentation:

```markdown
# FIND:
Alpha Berkeley Framework
alpha-berkeley-framework
pip install alpha-berkeley-framework

# REPLACE WITH:
Osprey Framework
osprey-framework
pip install osprey-framework
```

---

## 🔍 Verification Steps

**Run these checks after completing all updates:**

### 1. Search for Remaining Old References

```bash
# Should find NOTHING (or only comments/strings that are fine):
grep -r "from framework\." . --include="*.py" --exclude-dir=venv --exclude-dir=.venv --exclude-dir=build --exclude-dir=dist

# Should find NOTHING:
grep -r "alpha-berkeley-framework" . --exclude-dir=venv --exclude-dir=.venv --exclude-dir=build --exclude-dir=dist

# Should find your new imports:
grep -r "from osprey\." . --include="*.py" --exclude-dir=venv --exclude-dir=.venv
```

### 2. Test Imports

```python
# Create a test file: test_migration.py
"""Test that all imports work."""

def test_core_imports():
    """Test core framework imports."""
    from osprey.state import AgentState
    from osprey.base.capability import BaseCapability
    from osprey.base.node import BaseNode
    from osprey.registry.manager import RegistryManager
    print("✅ Core Osprey imports working")

def test_app_imports():
    """Test application imports."""
    # Import your main application modules
    # For example:
    # from my_app.capabilities.weather import WeatherCapability
    # from my_app.registry import MyAppRegistryProvider
    print("✅ Application imports working")

if __name__ == "__main__":
    test_core_imports()
    test_app_imports()
    print("\n✅ All imports successful!")
```

Run it:
```bash
python test_migration.py
```

### 3. Verify Package Installation

```bash
# Check installed packages
pip list | grep osprey
# Should show: osprey-framework 0.8.0 (or later)

# Check CLI is available
which osprey
# Should show path to osprey command

# Test CLI
osprey --version
# Should output: 0.8.0 or later

osprey --help
# Should display help without errors
```

### 4. Run Health Check

```bash
osprey health
# Should report all green checks
```

### 5. Run Tests

```bash
# Run your existing test suite
pytest

# Or with verbose output
pytest -v

# Or specific tests
pytest tests/
```

### 6. Test Application Functionality

```bash
# Try running your application
osprey chat --project /path/to/your/project

# Or other relevant commands
osprey deploy status
osprey export-config
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'framework'"

**Cause:** Old import statement wasn't updated

**Solution:**
```bash
# Find the problematic file
grep -r "from framework\." . --include="*.py" --exclude-dir=venv

# Update the import in that file:
# from framework.X → from osprey.X
```

---

### Issue: "ModuleNotFoundError: No module named 'osprey'"

**Cause:** New package not installed

**Solution:**
```bash
# Make sure old package is uninstalled
pip uninstall alpha-berkeley-framework -y

# Install new package
pip install osprey-framework

# Verify
python -c "import osprey; print(osprey.__version__)"
```

---

### Issue: "command not found: osprey"

**Cause:** Package installed in wrong environment

**Solution:**
```bash
# Check which Python/pip you're using
which python
which pip

# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Reinstall
pip install osprey-framework

# Verify
which osprey
```

---

### Issue: Tests fail with import errors

**Cause:** Test files have old imports

**Solution:**
```bash
# Check test files
grep -r "from framework\." tests/ --include="*.py"

# Update test imports the same way:
# from framework.X → from osprey.X
```

---

### Issue: "ImportError: cannot import name 'X' from 'osprey'"

**Cause:** Might have a local file/directory named `osprey` conflicting

**Solution:**
```bash
# Check for conflicting files (excluding the installed package)
find . -name "osprey.py" -o -name "osprey" -type d | grep -v venv | grep -v ".venv" | grep -v site-packages

# If found, rename your local file:
# mv osprey.py my_osprey.py
```

---

## ✅ Migration Complete Checklist

Confirm all items before marking migration complete:

- [ ] ✅ `pip list` shows `osprey-framework>=0.8.0`
- [ ] ✅ No old package: `pip list | grep alpha-berkeley` returns nothing
- [ ] ✅ All `from framework.*` updated to `from osprey.*`
- [ ] ✅ All `"framework.*` strings updated to `"osprey.*`
- [ ] ✅ `requirements.txt` and/or `pyproject.toml` updated
- [ ] ✅ No old references found: `grep -r "from framework\." .` returns nothing
- [ ] ✅ Test imports work: `python -c "from osprey.state import AgentState"`
- [ ] ✅ CLI works: `osprey --version` shows 0.8.0+
- [ ] ✅ Health check passes: `osprey health`
- [ ] ✅ Tests pass: `pytest`
- [ ] ✅ Application runs successfully

---

## 📝 Final Steps

After successful migration:

1. **Commit changes:**
   ```bash
   git add -A
   git commit -m "Migrate from Alpha Berkeley Framework to Osprey Framework v0.8.0"
   ```

2. **Update CI/CD pipelines** (if applicable):
   - Update package installation commands
   - Update any hardcoded package names

3. **Update team documentation:**
   - Installation instructions
   - Development setup guides
   - Deployment scripts

4. **Notify team members** of the migration

---

## 🎯 Summary of Changes

**What changed:**
- Package name: `alpha-berkeley-framework` → `osprey-framework`
- Import paths: `from framework.*` → `from osprey.*`
- CLI command: `framework` → `osprey`

**What stayed the same:**
- All APIs and functionality
- Configuration file format
- Project structure
- Capability/node registration patterns

---

## 📚 Additional Resources

- **Documentation**: https://als-apg.github.io/osprey
- **GitHub Repository**: https://github.com/als-apg/osprey
- **Issue Tracker**: https://github.com/als-apg/osprey/issues
- **Changelog**: https://github.com/als-apg/osprey/blob/main/CHANGELOG.md

---

**Migration Path**: v0.7.x → v0.8.0 (Rename Only)  
**Version**: 0.8.0  
**Last Updated**: November 2025

