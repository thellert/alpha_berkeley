# Alpha Berkeley Framework - Latest Release (v0.7.4)

🐛 **Bug Fix Release** - Fixed template generation issues affecting registry class names and import paths.

## What's New in v0.7.4

### 🔧 Template Bug Fixes

#### **Registry Class Name Generation**
- **Fixed duplicate "RegistryProvider" suffix** in generated registry class names
- Previously generated: `WeatherTutorialRegistryProviderRegistryProvider` ❌
- Now generates: `WeatherTutorialRegistryProvider` ✅
- Affects all three app templates: hello_world_weather, wind_turbine, minimal
- Projects generated with v0.7.3 may need manual class name correction

#### **Import Path Documentation**
- **Updated template documentation** to use correct v0.7.0 import patterns
- Changed from `applications.hello_world_weather.*` to `hello_world_weather.*`
- Updated examples in mock_weather_api.py and capabilities/__init__.py
- Ensures generated projects follow correct decoupled architecture

#### **Requirements Template Rendering**
- **Fixed framework version substitution** in generated requirements.txt
- Moved requirements.txt from static files to rendered templates
- Now properly replaces `{{ framework_version }}` placeholder with actual version
- Ensures generated projects pin correct framework version

## What's New in v0.7.3

### 🐳 Container Deployment Improvements

#### **Development Mode Support**
- **New `--dev` flag** for deploy CLI command enables local framework testing
- **Local framework override** - seamlessly switch between PyPI and local framework versions
- **Smart dependency installation** - containers detect dev mode and install local framework
- **Improved development workflow** - no need to rebuild containers when testing framework changes

#### **PyPI Distribution Integration**
- **Project templates updated** to use PyPI framework distribution by default
- **Automatic framework dependency** added to generated `pyproject.toml` and `requirements.txt`
- **Removed hardcoded paths** from configuration templates for better portability
- **Agent data structure creation** - ensures proper directory structure for container mounts

#### **Service Template Enhancements**
- **Improved container startup** with better logging and error messages
- **Fallback mechanisms** for missing requirements.txt files
- **Changed restart policy** to 'no' for better development experience
- **Enhanced start scripts** with PyPI framework and dev mode detection

## What's New in v0.7.2

### 📦 Simplified Installation

**PostgreSQL dependencies moved to optional extras** - The framework now installs without requiring PostgreSQL packages, making it much easier to get started:

```bash
# Basic installation (uses in-memory storage)
pip install alpha-berkeley-framework

# With PostgreSQL for persistent conversations  
pip install alpha-berkeley-framework[postgres]

# Full installation with all features
pip install alpha-berkeley-framework[all]
```

**Benefits:**
- ✅ Faster, simpler installation process
- ✅ No PostgreSQL setup required for development/testing
- ✅ Framework works perfectly with in-memory checkpointing
- ✅ Production users can still get persistent state with `[postgres]` extra

---

## What's New in v0.7.0+

### 🏗️ Framework Decoupling (Breaking Changes)

The framework has transitioned from a monolithic architecture to a **pip-installable dependency model**, fundamentally changing how applications are built and deployed.

**Before (v0.6.x):**
```bash
# Applications embedded in framework repo
git clone https://github.com/thellert/alpha_berkeley
cd alpha_berkeley/src/applications/my_app  # Edit inside framework
```

**Now (v0.7.0):**
```bash
# Framework as pip dependency
pip install alpha-berkeley-framework
framework init my-app --template hello_world_weather
cd my-app  # Independent repository
```

### ✨ New Features

#### Unified CLI System
- **`framework init`** - Create new projects from templates (minimal, hello_world_weather, wind_turbine)
- **`framework deploy`** - Manage Docker services (up/down/restart/status/rebuild/clean)
- **`framework chat`** - Interactive conversation interface
- **`framework health`** - Comprehensive system diagnostics (Python, dependencies, config, containers)
- **`framework export-config`** - View framework default configuration

All commands use lazy loading for fast startup, loading heavy dependencies only when needed.

#### Template System
Three production-ready templates for instant project generation:
- **Minimal** - Bare-bones starter with TODO placeholders
- **Hello World Weather** - Simple weather query example (tutorial)
- **Wind Turbine** - Complex multi-capability monitoring system (advanced tutorial)

Each template generates a complete, self-contained project with:
- Application code (capabilities, registry, context classes)
- Service configurations (Jupyter, OpenWebUI, Pipelines)
- Self-contained configuration file (~320 lines)
- Environment template (.env.example)
- Dependencies file (pyproject.toml)
- Getting started documentation

#### Registry Helper Functions
Simplify application registries by ~70% with `extend_framework_registry()`:

```python
# Before: 80+ lines of boilerplate
class MyAppRegistry(RegistryConfigProvider):
    def get_registry_config(self):
        return RegistryConfig(
            core_nodes=[...],  # 200+ lines listing framework nodes
            capabilities=[...], # 200+ lines listing framework capabilities
            # ... manual merging
        )

# After: 5-10 lines focused on your app
class MyAppRegistry(RegistryConfigProvider):
    def get_registry_config(self):
        return extend_framework_registry(
            capabilities=[...],  # Only your capabilities
            exclude_capabilities=["python"],  # Optional exclusions
        )
```

#### Path-Based Discovery
- Explicit registry file paths in `config.yml` (no magic conventions)
- Applications never pip-installed during development
- Immediate code changes (no rebuild/reinstall)
- Natural import paths matching package structure

#### Self-Contained Configuration
- One `config.yml` per application (~320 lines)
- Complete transparency - all settings visible
- Framework defaults included at project creation
- User controls config lifecycle (industry standard)
- Environment variable support with `.env` files

### 📚 Documentation

#### New Migration Guide
Comprehensive upgrade guide for v0.6.x users:
- Breaking changes overview
- Step-by-step migration instructions (10 steps)
- Automated import path updates
- Common issues and solutions
- Migration progress checklist

**Location:** `docs/source/getting-started/migration-guide.rst`

#### Updated Getting Started
- Fresh installation path
- Migration path (v0.6.x → v0.7.0)
- Updated tutorials using new CLI
- Template-based examples

### 🔄 Breaking Changes

This is a **major release** with significant breaking changes:

#### 1. Import Paths Changed
```python
# OLD ❌
from applications.my_app.capabilities import MyCapability

# NEW ✅
from my_app.capabilities import MyCapability
```

#### 2. CLI Commands Unified
```bash
# OLD ❌
python -m interfaces.CLI.direct_conversation
python -m deployment.container_manager deploy_up

# NEW ✅
framework chat
framework deploy up
```

#### 3. Configuration Structure
- Each application has own `config.yml` (no global config)
- `registry_path` specifies exact registry file location
- Self-contained configuration with all settings visible

#### 4. Repository Structure
- `interfaces/` → `src/framework/interfaces/` (pip-installed)
- `deployment/` → `src/framework/deployment/` (pip-installed)
- `src/configs/` → `src/framework/utils/` (merged)
- Applications → separate repositories (production) or templates (tutorials)

#### 5. Discovery Mechanism
- Explicit path-based discovery via `registry_path` in config
- No automatic scanning of `applications/` directory
- Registry must contain exactly one `RegistryConfigProvider` class

### 🎯 Migration Path

**For Production Applications:**
1. Install framework: `pip install alpha-berkeley-framework`
2. Create new repository structure
3. Copy application code
4. Update import paths (automated script available)
5. Simplify registry with `extend_framework_registry()`
6. Create self-contained `config.yml`
7. Validate with `framework health`

**For Tutorial Applications:**
Regenerate from templates:
```bash
framework init my-weather --template hello_world_weather
framework init my-turbine --template wind_turbine
```

**Complete instructions:** See migration guide in documentation.

### ⚡ Performance & Developer Experience

- **Lazy Loading** - CLI commands load dependencies on-demand (fast `--help`)
- **Immediate Changes** - Edit code, run immediately (no pip install)
- **Explicit Configuration** - All settings visible in one file
- **Template-Based** - New projects in seconds
- **Health Diagnostics** - Comprehensive validation with `framework health`

### 📦 Installation

```bash
# Install framework
pip install alpha-berkeley-framework

# Verify installation
framework --version
framework --help

# Create first project
framework init my-assistant --template hello_world_weather
cd my-assistant

# Setup and run
cp .env.example .env
# Edit .env with API keys
framework deploy up
framework chat
```

## Upgrade Notes

### Required Actions for Existing Users

1. **Read Migration Guide** - Comprehensive upgrade instructions
2. **Update Import Paths** - Change `applications.*` to package names
3. **Simplify Registry** - Use `extend_framework_registry()` helper
4. **Create Config** - Self-contained `config.yml` for each app
5. **Test Migration** - Use `framework health` to validate

### Backward Compatibility

- **Legacy entry points maintained** - `alpha-berkeley`, `alpha-berkeley-deploy` still work
- **Registry interface unchanged** - `RegistryConfigProvider` preserved
- **Core functionality preserved** - All framework features maintained

### Dependencies

- Python 3.11+ required
- New dependencies: None (framework functionality unchanged)
- Framework now pip-installable with proper package data

## Known Issues

None at release time. Please report issues at: https://github.com/thellert/alpha_berkeley/issues

## Get Started with v0.7.0

1. **Fresh Installation**: Follow [Installation Guide](https://thellert.github.io/alpha_berkeley/getting-started/installation)
2. **Upgrading**: Follow [Migration Guide](https://thellert.github.io/alpha_berkeley/getting-started/migration-guide)
3. **Templates**: Try `framework init --help` to see available templates
4. **Documentation**: Visit [complete documentation](https://thellert.github.io/alpha_berkeley)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.7.0`
3. **Title**: `Alpha Berkeley Framework v0.7.0 - Framework Decoupling`
4. **Description**: Copy the content above (from "🎉 Major Architecture Release" through "Breaking Changes")
5. **Mark as major release** - This is a breaking change release

## Technical Details

### Architecture Changes
- Framework repository restructured for pip installation
- Applications moved from `src/applications/` to separate repos or templates
- Unified CLI with lazy loading (5 commands)
- Template system with 3 production-ready templates
- Registry helper functions reduce boilerplate by ~70%
- Path-based discovery with explicit configuration

### Implementation Stats
- **100+ tasks completed** across 6 phases
- Template system: 3 app templates + project templates + service templates
- CLI infrastructure: 5 commands (~2000 lines)
- Registry helpers: `extend_framework_registry()` (~200 lines)
- Migration guide: Comprehensive documentation (~730 lines)
- Configuration system: Self-contained config generation

### File Structure
```
Framework (pip-installed):
  src/framework/
    ├── cli/                    # 5 commands with lazy loading
    ├── templates/              # Bundled as package data
    │   ├── apps/              # 3 application templates
    │   ├── project/           # Project scaffolding
    │   └── services/          # Docker configurations
    ├── registry/helpers.py    # Registry helper functions
    └── ...                    # Core framework modules

User Project (generated):
  my-project/
    ├── src/my_project/        # Application code
    ├── services/              # Docker services
    ├── config.yml             # Self-contained config
    └── pyproject.toml         # Framework as dependency
```

---

## Previous Release (v0.6.0)

### ⚡ Performance Optimization System
- Task extraction bypass modes
- Capability selection bypass modes  
- Runtime slash commands for performance tuning
- Reduced LLM overhead in preprocessing pipeline

See [CHANGELOG.md](CHANGELOG.md) for complete release history.

---

*Current Release: v0.7.0 (October 2025)*  
*Release Type: Major Release - Breaking Changes*  
*Previous Release: v0.6.0 with performance optimization*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
