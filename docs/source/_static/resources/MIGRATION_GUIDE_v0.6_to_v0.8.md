# Migration Guide: v0.6.x → v0.8.0 (Full Migration)

This guide is for migrating applications from **Alpha Berkeley Framework v0.6.x or earlier** (monolithic structure) to **Osprey Framework v0.8.0** (pip-installable).

**Migration Type**: Full Architectural Migration + Rename  
**Estimated Time**: 2-4 hours  
**Complexity**: Complex - involves restructuring and two sets of import changes

---

## ✅ Pre-Migration Checklist

Confirm with the user:
- [ ] They are on **v0.6.x or earlier** (monolithic structure)
- [ ] Their application is currently **embedded** in `src/applications/`
- [ ] They have **version control** (git) with committed changes
- [ ] They have the **old repository path** available

---

## 📋 Migration Overview

This migration involves TWO major changes:

1. **Architectural**: Monolithic → Separate pip-installable framework
   - Move from `src/applications/my_app/` to standalone `src/my_app/`
   - Update imports: `applications.my_app` → `my_app`

2. **Rename**: Alpha Berkeley Framework → Osprey Framework
   - Update imports: `framework.*` → `osprey.*`
   - Update package: `alpha-berkeley-framework` → `osprey-framework`

---

## 📋 Migration Steps

### Step 1: Install Osprey Framework

```bash
# Install new package (skip old versions entirely)
pip install osprey-framework

# Verify installation
osprey --version  # Should show 0.8.0 or later
osprey --help
```

**What to check:**
- Command completes without errors
- `osprey --version` shows 0.8.0+
- `osprey --help` displays commands

---

### Step 2: Create New Application Repository

**Option A - Use Scaffolding (RECOMMENDED):**

```bash
# Create new project from template
osprey init my-app --template minimal

# Navigate to project
cd my-app
```

**Option B - Manual Setup:**

```bash
# Create directory structure
mkdir -p my-app/src/my_app/capabilities
cd my-app

# Create base files
touch src/my_app/__init__.py
touch src/my_app/registry.py
touch src/my_app/context_classes.py

# Create config
touch config.yml
touch .env
```

**Recommended:** Use Option A (scaffolding) to get proper structure automatically.

---

### Step 3: Copy Application Code

```bash
# Define old repository path (ask user for this)
OLD_REPO=/path/to/alpha_berkeley

# Ask user: What is their application name? (e.g., "my_app", "weather_agent")
APP_NAME=my_app  # Replace with actual name

# Copy application code
cp -r $OLD_REPO/src/applications/$APP_NAME/* src/$APP_NAME/

# Copy custom services if they exist
if [ -d "$OLD_REPO/services/applications/$APP_NAME" ]; then
    mkdir -p services
    cp -r $OLD_REPO/services/applications/$APP_NAME/* services/
    echo "✅ Custom services copied"
else
    echo "ℹ️  No custom services found"
fi

# Copy tests if they exist
if [ -d "$OLD_REPO/src/applications/$APP_NAME/tests" ]; then
    cp -r $OLD_REPO/src/applications/$APP_NAME/tests tests/
    echo "✅ Tests copied"
fi
```

---

### Step 4: Update ALL Import Paths (Two-Part Update)

This is the most critical step. You need **TWO sets of replacements**.

#### Part A: Remove `applications.` Prefix

**Search and replace in ALL `.py` files in `src/$APP_NAME/`:**

```bash
# Automated approach (creates .bak backup files for safety):
find src/$APP_NAME -name "*.py" -type f -exec sed -i.bak 's/from applications\.'$APP_NAME'/from '$APP_NAME'/g' {} +
find src/$APP_NAME -name "*.py" -type f -exec sed -i.bak 's/import applications\.'$APP_NAME'/import '$APP_NAME'/g' {} +

# Remove backup files after verifying changes:
# find src/$APP_NAME -name "*.bak" -delete
```

**Manual patterns:**

```python
# BEFORE (v0.6.x):
from applications.my_app.capabilities.weather import WeatherCapability
from applications.my_app.context_classes import WeatherContext
import applications.my_app.registry

# AFTER (intermediate):
from my_app.capabilities.weather import WeatherCapability
from my_app.context_classes import WeatherContext
import my_app.registry
```

#### Part B: Update `framework` → `osprey`

**Search and replace in ALL `.py` files:**

```bash
# Automated approach (creates .bak backup files for safety):
find src/$APP_NAME -name "*.py" -type f -exec sed -i.bak 's/from framework\./from osprey./g' {} +
find src/$APP_NAME -name "*.py" -type f -exec sed -i.bak 's/"framework\./"osprey./g' {} +

# Remove backup files after verifying changes:
# find src/$APP_NAME -name "*.bak" -delete
```

**Manual patterns - Common Imports:**

```python
# STATE & BASE CLASSES
from framework.state import AgentState
from framework.base.capability import BaseCapability
from framework.base.node import BaseNode
from framework.base.planning import BasePlanner
# →
from osprey.state import AgentState
from osprey.base.capability import BaseCapability
from osprey.base.node import BaseNode
from osprey.base.planning import BasePlanner

# REGISTRY
from framework.registry.manager import RegistryManager
from framework.registry import extend_framework_registry
# →
from osprey.registry.manager import RegistryManager
from osprey.registry import extend_framework_registry

# SERVICES
from framework.services.model_providers import ModelProvider
from framework.services.llm_interface import LLMInterface
# →
from osprey.services.model_providers import ModelProvider
from osprey.services.llm_interface import LLMInterface

# DATA MANAGEMENT
from framework.data_management.checkpoint import CheckpointManager
# →
from osprey.data_management.checkpoint import CheckpointManager

# ERROR HANDLING
from framework.base.errors import ErrorSeverity, CapabilityExecutionError
# →
from osprey.base.errors import ErrorSeverity, CapabilityExecutionError

# UTILITIES
from framework.utils.logging import get_logger
# →
from osprey.utils.logging import get_logger
```

**Complete example transformation:**

```python
# BEFORE (v0.6.x):
from applications.weather_agent.capabilities.current_weather import CurrentWeatherCapability
from applications.weather_agent.context_classes import WeatherContext
from framework.state import AgentState
from framework.base.capability import BaseCapability
from framework.registry import extend_framework_registry

# AFTER (v0.8.0):
from weather_agent.capabilities.current_weather import CurrentWeatherCapability
from weather_agent.context_classes import WeatherContext
from osprey.state import AgentState
from osprey.base.capability import BaseCapability
from osprey.registry import extend_framework_registry
```

---

### Step 5: Update Registry File

The registry structure has been simplified. Update `src/$APP_NAME/registry.py`:

**IMPORTANT**: When updating your registry, make sure to update the `module_path` in all registrations:
- Remove `applications.` prefix: `applications.my_app.capabilities.X` → `my_app.capabilities.X`
- Keep framework imports as `osprey.registry` (already covered in Step 4)

```python
"""Registry for My Application."""

from osprey.registry import (
    extend_framework_registry,
    CapabilityRegistration,
    ContextClassRegistration,
    RegistryConfigProvider,
    RegistryConfig,
)

class MyAppRegistryProvider(RegistryConfigProvider):
    """Registry configuration provider for My Application."""
    
    def get_registry_config(self) -> RegistryConfig:
        """Return registry configuration."""
        return extend_framework_registry(
            capabilities=[
                CapabilityRegistration(
                    name="my_capability",
                    module_path="my_app.capabilities.my_capability",  # NOTE: No "applications." prefix!
                    class_name="MyCapability",
                    description="Description of what this capability does",
                    provides=["MY_CONTEXT"],
                    requires=[],
                ),
                # Add all your capabilities here...
            ],
            context_classes=[
                ContextClassRegistration(
                    context_type="MY_CONTEXT",
                    module_path="my_app.context_classes",
                    class_name="MyContext",
                ),
                # Add all your context classes here...
            ],
            # Optional: exclude framework capabilities you don't need
            # exclude_capabilities=["python_repl"],
        )
```

**Ask the user to provide:**
- List of their capability names and classes
- List of their context types and classes
- Dependencies between capabilities (provides/requires)

---

### Step 6: Create Configuration File

```bash
# Generate base configuration from framework
osprey export-config > config.yml
```

**Then edit `config.yml` with project-specific values:**

```yaml
# ESSENTIAL SETTINGS TO UPDATE:

# 1. Project paths (use absolute paths)
project_root: /absolute/path/to/my-app
registry_path: ./src/my_app/registry.py
build_dir: ./build

# 2. Models configuration (update all 8 models)
models:
  orchestrator:
    provider: openai  # or anthropic, google, cborg
    model_id: gpt-4   # or claude-3-5-sonnet, gemini-pro, etc.
  response:
    provider: openai
    model_id: gpt-4
  planner:
    provider: openai
    model_id: gpt-4
  executor:
    provider: openai
    model_id: gpt-4
  error_handler:
    provider: openai
    model_id: gpt-4
  memory:
    provider: openai
    model_id: gpt-4
  capability_selector:
    provider: openai
    model_id: gpt-4
  context_analyzer:
    provider: openai
    model_id: gpt-4

# 3. Service paths (if using containers)
services:
  jupyter:
    path: ./services/jupyter
  open_webui:
    path: ./services/open-webui
    port_host: 8080
  pipelines:
    path: ./services/pipelines
    port_host: 9099
```

**Ask user:**
- What model provider(s) they use
- What model IDs they prefer
- Whether they need container services

---

### Step 7: Create Dependency Files

**Create `requirements.txt`:**

```txt
# Core framework
osprey-framework>=0.8.0

# Add your application-specific dependencies below
# For example:
# requests>=2.31.0
# pandas>=2.0.0
# numpy>=1.24.0
```

**OR create `pyproject.toml`:**

```toml
[project]
name = "my-app"
version = "1.0.0"
description = "My application built with Osprey Framework"
requires-python = ">=3.11"
dependencies = [
    "osprey-framework>=0.8.0",
    # Add your dependencies here
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

**Ask user** what additional dependencies their application needs.

---

### Step 8: Setup Environment File

```bash
# Create .env file
cat > .env << 'EOF'
# API Keys (uncomment and add your keys)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
# CBORG_API_KEY=...

# Optional: Override config settings
# PROJECT_ROOT=/path/to/project
EOF
```

**Ask user** which API keys they need to provide.

---

### Step 9: Update String Module References

Search for any remaining string-based module references:

```bash
# Find them:
grep -r '"framework\.' src/$APP_NAME/ --include="*.py"
grep -r '"applications\.' src/$APP_NAME/ --include="*.py"
```

**Update patterns:**

```python
# Dynamic imports
module = importlib.import_module("framework.capabilities.memory")
path = "framework.state.AgentState"
# →
module = importlib.import_module("osprey.capabilities.memory")
path = "osprey.state.AgentState"

# Module paths in strings
capability_module = f"applications.{app_name}.capabilities.{cap_name}"
# →
capability_module = f"{app_name}.capabilities.{cap_name}"
```

---

## 🔍 Verification Steps

### 1. Search for Old References

```bash
# Should find NOTHING:
grep -r "applications\." src/$APP_NAME/ --include="*.py"
grep -r "from framework\." src/$APP_NAME/ --include="*.py"
grep -r "alpha-berkeley" . --exclude-dir=venv

# Should find your new imports:
grep -r "from osprey\." src/$APP_NAME/ --include="*.py"
grep -r "from $APP_NAME\." src/$APP_NAME/ --include="*.py"
```

### 2. Test Imports

```python
# Create test_migration.py
"""Test that all imports work after migration."""

def test_osprey_imports():
    """Test core Osprey framework imports."""
    from osprey.state import AgentState
    from osprey.base.capability import BaseCapability
    from osprey.base.node import BaseNode
    from osprey.registry.manager import RegistryManager
    print("✅ Osprey framework imports working")

def test_app_imports():
    """Test application imports."""
    # Replace my_app with actual app name
    from my_app.capabilities import *  # Import your capabilities
    from my_app.registry import MyAppRegistryProvider
    from my_app.context_classes import *  # Import your contexts
    print("✅ Application imports working")

def test_registry():
    """Test registry loads correctly."""
    from my_app.registry import MyAppRegistryProvider
    provider = MyAppRegistryProvider()
    config = provider.get_registry_config()
    print(f"✅ Registry loaded with {len(config.capabilities)} capabilities")

if __name__ == "__main__":
    test_osprey_imports()
    test_app_imports()
    test_registry()
    print("\n✅ All tests passed!")
```

Run it:
```bash
python test_migration.py
```

### 3. Run Health Check

```bash
osprey health

# Should report:
# ✅ Python version
# ✅ Osprey framework installed  
# ✅ Config file valid
# ✅ Registry file found
# ✅ Dependencies available
```

### 4. Validate Configuration

```bash
# Test config loading
osprey export-config --project .

# Should output your config without errors
```

### 5. Run Tests

```bash
# If you copied tests, run them:
pytest

# Or with verbose output:
pytest -v
```

### 6. Test Application

```bash
# Try the CLI
osprey chat --project .

# Should start without errors
# Test with a simple query
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'applications'"

**Cause:** Missed updating an import from old structure

**Solution:**
```bash
# Find it:
grep -r "from applications\." . --include="*.py"

# Fix it:
# from applications.my_app.X → from my_app.X
```

---

### Issue: "ModuleNotFoundError: No module named 'framework'"

**Cause:** Missed updating a framework import

**Solution:**
```bash
# Find it:
grep -r "from framework\." . --include="*.py"

# Fix it:
# from framework.X → from osprey.X
```

---

### Issue: Registry not loading correctly

**Cause:** Registry file has old imports or incorrect structure

**Solution:**
1. Check registry imports use `from osprey.registry`
2. Check module_path in registrations don't have `applications.` prefix
3. Check module_path doesn't have `framework.` anywhere

---

### Issue: "Config file not found"

**Cause:** config.yml not in project root

**Solution:**
```bash
# Make sure you're in project directory
pwd  # Should show /path/to/my-app

# Generate config if missing:
osprey export-config > config.yml

# Edit with correct paths
```

---

## ✅ Migration Complete Checklist

- [ ] ✅ New repository structure created
- [ ] ✅ Application code copied to `src/$APP_NAME/`
- [ ] ✅ All `applications.$APP_NAME` → `$APP_NAME` imports updated
- [ ] ✅ All `framework.*` → `osprey.*` imports updated
- [ ] ✅ Registry file updated with `osprey.registry` imports
- [ ] ✅ Configuration file created and customized
- [ ] ✅ Dependencies file created (requirements.txt or pyproject.toml)
- [ ] ✅ Environment file created (.env)
- [ ] ✅ No old references: `grep -r "applications\." src/` returns nothing
- [ ] ✅ No old references: `grep -r "from framework\." src/` returns nothing
- [ ] ✅ Test imports work
- [ ] ✅ `osprey health` passes
- [ ] ✅ Tests pass (if applicable)
- [ ] ✅ Application runs successfully

---

## 📝 Final Steps

After successful migration:

1. **Initialize git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Migrated to Osprey Framework v0.8.0"
   ```

2. **Create remote repository** and push:
   ```bash
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

3. **Update documentation:**
   - Installation instructions
   - Development setup
   - Deployment procedures

4. **Test in clean environment:**
   ```bash
   # Create new venv
   python -m venv test_env
   source test_env/bin/activate
   pip install -r requirements.txt
   osprey health
   ```

---

## 🎯 Summary of Changes

**What changed:**
- Repository structure: Monolithic → Standalone
- Application imports: `applications.my_app.*` → `my_app.*`
- Framework imports: `framework.*` → `osprey.*`
- Package name: `alpha-berkeley-framework` → `osprey-framework`
- CLI command: `python -m ...` → `osprey`
- Configuration: Global → Per-application

**What stayed the same:**
- Core functionality and APIs
- Capability and node patterns
- Context class system
- Execution model

---

## 📚 Additional Resources

- **Documentation**: https://als-apg.github.io/osprey
- **Migration Guide** (full): https://als-apg.github.io/osprey/getting-started/migration-guide.html
- **GitHub**: https://github.com/als-apg/osprey
- **Issues**: https://github.com/als-apg/osprey/issues

---

**Migration Path**: v0.6.x → v0.8.0 (Full Migration)  
**Version**: 0.8.0  
**Last Updated**: November 2025

