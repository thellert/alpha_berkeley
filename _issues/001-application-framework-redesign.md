## 📋 Executive Summary

The Alpha Berkeley Framework currently requires all applications to reside within the main framework repository. This monolithic architecture creates an unsustainable development model where:
- Application developers must push changes to the framework repository
- Framework upgrades force application developers to rebase constantly
- Framework and application development cycles are tightly coupled
- Teams cannot work independently on applications

**This issue proposes making the framework a pip-installable dependency, allowing production applications to live in separate repositories (public or private) while maintaining the interface design and discovery mechanisms that already exist.**

**Scope:** Production applications with independent development teams (e.g., ALS Assistant) will move to separate repositories. Tutorial/example applications will be provided as CLI scaffolding tools that generate complete, editable starter projects.

---

## 🎯 Problem Statement

**Applications are structurally coupled to the framework repository.** Production applications with independent development teams cannot work in separate repositories because the framework is not a dependency - it's a container that must hold all application code.

### Current Pain Points

```bash
# Application developers must work inside framework repo
git clone https://github.com/thellert/alpha_berkeley  # Clone entire framework
cd alpha_berkeley
# Edit src/applications/als_assistant/...
git commit -m "Add ALS feature"                       # Commits to framework repo!
git push                                              # Application changes pushed to framework!

# Framework team upgrades dependencies
git pull                                              # Must rebase immediately
# Conflicts, broken imports, forced coordination...
```

### Desired State

```bash
# New users: One command to get started
pip install alpha-berkeley-framework                  # Framework as dependency
framework init my-assistant                           # Creates complete project
cd my-assistant
framework deploy up                                   # Start services
framework chat                                        # Run it!

# Development: Everything self-contained
# Edit my_assistant/...
git commit -m "Add new feature"                       # Commits to own repo
git push                                              # Own repo, own releases
# Framework upgrades? pip install --upgrade alpha-berkeley-framework
```

### Direct Consequences

1. **Repository pollution** - domain-specific application code mixed with framework code
2. **Development friction** - framework upgrades force immediate rebasing, version pinning impossible
3. **Dependency conflicts** - single `pyproject.toml` must satisfy all applications (`pyepics`, `als-archiver-client`, etc.)

---

## 📊 Current State

Current monolithic structure embeds all applications:
```
alpha_berkeley/
├── src/
│   ├── framework/              # Core framework
│   └── applications/           # ❌ ALL APPLICATIONS EMBEDDED
│       ├── als_assistant/      # 5000+ lines, domain-specific - SHOULD BE SEPARATE
│       ├── wind_turbine/       # Tutorial/example - CAN STAY
│       └── hello_world_weather/# Tutorial/example - CAN STAY
├── pyproject.toml              # Single dependency file for all applications
└── config.yml                  # Global configuration
```

**Note:** Tutorial applications (`hello_world_weather`, `wind_turbine`) will be provided as scaffolding templates rather than embedded in the framework repository. The issue is with production applications like `als_assistant` that have separate development teams.

### What Works Well

The framework has excellent architecture that should be preserved:

**✅ Registry Interface** - Clean abstraction via `RegistryConfigProvider`:
```python
class ALSExpertRegistryProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[...],
            context_classes=[...],
        )
```

**✅ Discovery Mechanism** - Convention-based, automatic discovery from config  
**✅ Component Architecture** - Clean separation with override mechanisms and dependency management

---

## 🎯 Proposed Solution

**Make the framework a pip-installable dependency** so applications can live in separate repositories (public or private) while maintaining the excellent registry interface and discovery mechanisms that already exist.

### High-Level Approach

1. **Package the framework** as a standalone pip-installable package (`alpha-berkeley-framework`)
2. **Move applications to separate repositories** - each application becomes its own repo with framework as dependency
3. **Use explicit path-based discovery** - applications specify exact paths to registries in `config.yml`
4. **Single configuration file** - one `config.yml` per application with inline configuration
5. **CLI scaffolding tools** - provide `create-example` and `create-app` commands to generate starter projects
6. **Support direct source code editing** - no pip install required for applications during development
7. **Maintain registry interface** - Keep `RegistryConfigProvider` unchanged

### Result

```bash
# Framework repository (pip-installable package)
alpha_berkeley/
├── src/framework/                 # Everything here gets pip-installed
│   ├── __init__.py                # Framework version
│   ├── cli/                       # CLI commands with lazy loading
│   │   ├── main.py                # Main CLI group (lazy-loading)
│   │   ├── init_cmd.py            # framework init
│   │   ├── deploy_cmd.py          # framework deploy
│   │   ├── chat_cmd.py            # framework chat
│   │   ├── health_cmd.py          # framework health
│   │   ├── export_config_cmd.py   # framework export-config
│   │   └── templates.py           # Template manager abstraction
│   │
│   ├── templates/                 # Bundled as package data
│   │   ├── apps/                  # Application templates
│   │   │   ├── hello_world_weather/  # Complete tutorial
│   │   │   ├── wind_turbine/      # Complex example
│   │   │   └── minimal/           # Starter template
│   │   ├── project/               # Project scaffolding
│   │   │   ├── config.yml.j2      # ~320 line self-contained config
│   │   │   ├── pyproject.toml.j2
│   │   │   ├── env.example.j2     # .env template
│   │   │   ├── README.md.j2
│   │   │   └── gitignore          # Renamed to .gitignore on copy
│   │   └── services/              # Service Docker configurations
│   │       ├── jupyter/           # Complete with Dockerfile, kernels
│   │       ├── open-webui/        # With functions, custom CSS
│   │       └── pipelines/         # With main.py interface
│   │
│   ├── registry/
│   │   ├── helpers.py             # extend_framework_registry()
│   │   ├── manager.py             # Path-based discovery
│   │   └── ...
│   ├── deployment/                # Container management
│   ├── interfaces/                # CLI and OpenWebUI interfaces
│   ├── utils/                     # Configuration system
│   └── ...                        # Other framework modules
│
├── tests/                         # Not pip-installed (dev only)
├── docs/                          # Not pip-installed
└── pyproject.toml                 # Framework package definition

# User's project (created by framework init)
my-assistant/                      # Complete self-contained project
├── src/my_assistant/              # Application code
│   ├── registry.py                # Uses extend_framework_registry()
│   ├── capabilities/              # Domain capabilities
│   └── context_classes.py         # Domain context types
├── services/                      # Docker services (copied from templates)
│   ├── docker-compose.yml
│   ├── jupyter/
│   ├── open-webui/
│   └── pipelines/
├── config.yml                     # Self-contained (~320 lines)
├── .env.example                   # Environment template
├── .gitignore
├── pyproject.toml                 # dependencies = ["alpha-berkeley-framework>=0.7.0"]
└── README.md                      # Getting started guide
```

---

## 🎓 Learning Path & Examples

### Scaffolding-Based Examples

**Philosophy:** Examples should be development tools, not runtime components. Instead of bundling tutorials inside the pip package, we provide CLI commands that generate complete, editable starter projects.

**User Experience:**
```bash
# Install framework
pip install alpha-berkeley-framework

# Create a complete working project (app + services)
framework init my-project --template hello_world_weather
# Output:
#   🚀 Creating project: my-project
#     ✓ Creating application code...
#     ✓ Creating service configurations (Jupyter, OpenWebUI, Pipelines)...
#     ✓ Creating project configuration...
#   ✅ Project created successfully!

cd my-project

# Everything is visible, editable, explorable
ls -la
# src/my_project/      ← Your application code
# services/            ← Docker services (Jupyter, OpenWebUI, Pipelines)
# config.yml           ← Configuration
# .env.example         ← Environment template
# pyproject.toml       ← Dependencies
# README.md            ← Getting started guide

# Explore application code
cat src/my_project/registry.py           # Understand capability registration
cat src/my_project/capabilities/current_weather.py  # See implementation
cat config.yml                            # See configuration

# Explore service configurations
cat services/docker-compose.yml       # Service orchestration
cat services/jupyter/Dockerfile       # Jupyter environment
cat services/pipelines/main.py        # OpenWebUI pipeline interface

# Setup and run
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, etc.)

framework deploy up     # Start services
# Output:
#   🚀 Starting services...
#   ✅ Services started successfully!
#   📊 Service URLs:
#     ✓ Jupyter (read-only): http://localhost:8088
#     ✓ Jupyter (write): http://localhost:8089
#     ✓ OpenWebUI: http://localhost:8080
#     ✓ Pipelines: http://localhost:9099

framework chat          # Run CLI interface

# Modify to learn
vim src/my_project/capabilities/current_weather.py
framework chat  # Changes reflected immediately

# Or use web interface
# Browse to http://localhost:8080

# Check system health
framework health  # Validates Python, dependencies, config, etc.

# View framework defaults
framework export-config  # Shows default configuration template

# When ready, create your own app
cd ..
framework init my_beamline_assistant  # Creates fresh project with services
```

**Benefits:**
- ✅ **Transparent learning** - all code visible and editable
- ✅ **Natural progression** - scaffold → explore → modify → build
- ✅ **Standard pattern** - matches create-react-app, django-admin startproject
- ✅ **Independent apps** - each has own directory with single config
- ✅ **Easy comparison** - switch between tutorial and production apps

**Available Commands:**

**Unified CLI** (Lazy-loading Click group at `src/framework/cli/main.py`):
- `framework init <project-name>` - Create complete self-contained project with services
  - `--template <name>` - Use specific template (minimal, hello_world_weather, wind_turbine)
  - `--registry-style <style>` - Choose compact (default) or explicit registry
  - `--output-dir <path>` - Custom output directory
  - `--force` - Overwrite existing directory
- `framework deploy [up|down|restart|status|rebuild|clean]` - Manage Docker services
  - Intelligent service management with validation
  - Service health checking
- `framework chat` - Interactive CLI conversation interface
- `framework health` - System diagnostics
  - Validates Python version, dependencies
  - Checks config.yml and registry files
  - Tests container connectivity
  - Comprehensive validation
- `framework export-config` - View framework defaults
  - Shows complete framework configuration template
  - Supports YAML and JSON output
  - Helps understand configuration options

**Legacy Entry Points** (backward compatibility):
- `alpha-berkeley` - Direct conversation interface
- `alpha-berkeley-deploy` - Container management
- `alpha-berkeley-docs` - Documentation server

**Performance:** Lazy loading keeps `framework --help` fast by importing heavy dependencies (langgraph, langchain) only when commands are invoked.

**Template Structure Note:** Application templates contain files at root level (e.g., `registry.py.j2`, `capabilities/`), not nested under `{{app_name}}/`. The CLI creates the package directory and copies template files into it.

**Design Goal:** New users should be able to install, create, deploy, and run in under 5 minutes.

---

## 🎯 Goals and Requirements

### Primary Goals

1. **Decouple Application Repositories**
   - Applications live in separate git repositories
   - Application teams commit to their own repos, not framework repo
   - Framework team works independently of application teams
   - Clear ownership boundaries

2. **Framework as Dependency**
   - Framework pip-installable as standalone package
   - Applications declare framework as dependency with version pinning
   - Applications can upgrade framework on their own schedule
   - Framework upgrades don't force immediate rebasing

3. **Preserve Excellent Design**
   - Keep `RegistryConfigProvider` interface unchanged
   - Adapt discovery mechanism for external applications
   - Maintain configuration merging and override mechanisms

### Key Requirements

**Repository Decoupling:**
- Framework lives in its own repository
- Production applications live in separate repositories (public or private)
- Tutorial/example applications provided as CLI scaffolding templates
- Framework installable via `pip install alpha-berkeley-framework`

**Framework as Dependency:**
- Applications declare framework dependency in their `pyproject.toml`
- Applications pin to specific framework versions
- Framework upgradeable independently by each application
- No forced lockstep versioning

**Discovery Mechanism:**
- **Explicit path-based discovery** - applications specify exact registry file paths
- No conventions or magic - everything explicit in `config.yml`
- Module paths in registries match actual package structure
- Framework-bundled templates for quick start (not runtime components)
- Support for multiple applications in one config for easy switching

**Registry Pattern:**
- **Helper function pattern** - `extend_framework_registry()` simplifies application registries
- **Compact by default** - 5-10 lines of code instead of 80+ lines of boilerplate (~70% reduction)
- **Explicit when needed** - optional explicit template shows all framework components
- **Clean exclusions** - `exclude_capabilities=["python"]` instead of `framework_exclusions` dict hack
- **Progressive disclosure** - beginner → intermediate → advanced learning path
- Used in all generated templates (hello_world_weather, wind_turbine, minimal)

**Import Paths:**
- Applications use their own package names (not `applications.*` prefix)
- Framework imports unchanged
- No cross-application imports possible

**Configuration:**
- **Single config file per application** - all configuration in one place
- Self-contained configuration with complete transparency (all settings visible)
- Framework defaults served as reference template at project creation
- `framework export-config` command for viewing framework defaults
- Industry-standard approach (similar to Django, React, Express)

### Constraints

**Must Preserve:**
- `RegistryConfigProvider` interface (production-quality, well-adopted)
- Component registration pattern (clean and extensible)
- Configuration merging behavior (expected by existing apps)
- Override mechanism (critical customization feature)

**Breaking Changes Required:**
- Repository structure (move applications to separate repos)
- Import statements (update from `applications.*` to package names)
- Dependency declarations (framework becomes a dependency)
- Discovery mechanism (add entry point support)

**Migration Support:**
- Tutorial/example applications converted to scaffolding templates
- CLI scaffolding commands for creating new projects
- Tooling for import path updates
- Detailed migration documentation for production applications

---

## 🔧 Development Workflow

**Target User Experience:**
```bash
# 1. Install framework as pip package
pip install alpha-berkeley-framework

# 2. Create new project (application + services)
framework init my-project
cd my-project

# 3. Setup environment
cp .env.example .env
# Edit .env with API keys

# 4. Start services
framework deploy up
# Services: Jupyter (8088/8089), OpenWebUI (8080), Pipelines (9099)

# 5. Work on application code directly
# Edit capabilities, add features, develop...
vim src/my_project/capabilities/my_capability.py

# 6. Run interface - changes immediately reflected, no reinstall needed
framework chat                        # Interactive CLI
# OR: Browse to http://localhost:8080 for web interface

# 7. System diagnostics
framework health                      # Comprehensive validation

# 8. View framework defaults
framework export-config               # Understand configuration
```

### How Applications Are Discovered

**Configuration File (`my-project/config.yml`):**
```yaml
# ============================================================
# My Project Configuration
# ============================================================
# Self-contained configuration with all settings visible
# Framework defaults included for complete transparency
# ============================================================

# Root directory (absolute path)
project_root: /path/to/my-project

# Application Registry
registry_path: ./src/my_project/registry.py

# ============================================================
# MODEL CONFIGURATION (8 required framework models)
# ============================================================
models:
  orchestrator:
    provider: cborg
    model_id: anthropic/claude-sonnet
  response:
    provider: cborg
    model_id: google/gemini-flash
  # ... 6 more models

# ============================================================
# SERVICE CONFIGURATION
# ============================================================
services:
  jupyter:
    path: ./services/jupyter
    # ... service configuration
  open_webui:
    port_host: 8080
  pipelines:
    port_host: 9099

# ============================================================
# SAFETY CONTROLS & EXECUTION
# ============================================================
approval:
  global_mode: "selective"

execution_control:
  epics:
    writes_enabled: false
  limits:
    graph_recursion_limit: 100

# ... additional configuration sections (file_paths, logging, api providers, etc.)
```

**Note:** Complete configuration (~320 lines) generated at project creation. View framework defaults anytime with `framework export-config`.

**Discovery Flow:**
1. CLI runs `initialize_registry()` (from pip-installed framework)
2. Framework loads `config.yml` from current directory (or `CONFIG_FILE` env var)
3. Framework reads `registry_path` from config:
   - Supports top-level: `registry_path: ./src/my_app/registry.py` 
   - Supports nested: `application.registry_path: ...`
   - Supports multiple apps (advanced): `applications.app1.registry_path`, etc.
4. Framework loads registry using `importlib.util.spec_from_file_location()`:
   - Adds parent directory to `sys.path` temporarily (like Django, Sphinx, Airflow)
   - Validates exactly one `RegistryConfigProvider` per file (strict enforcement)
   - Comprehensive error messages with resolution hints
5. Module imports work naturally (e.g., `my_project.capabilities.*`)
6. Registry merges: framework + application (applications override framework)
7. `.env` file automatically loaded from project directory

**Key Benefits:**
- **Single config file** - all configuration in one place
- **Complete transparency** - every setting visible and editable
- **Explicit paths** - no conventions or magic to learn
- **Editable source** - applications never pip-installed during development
- **Immediate changes** - no reinstall/rebuild needed
- **Natural imports** - module paths match actual package structure
- **Stable configuration** - user controls config lifecycle (industry standard)
- **Environment variables** - `.env` file support with python-dotenv

### Configuration System

**Key Principle:** Self-contained configuration with complete transparency.

**Design:**
- **One `config.yml`** per application repository
- Complete, self-contained configuration (~320 lines)
- Framework defaults copied into template at project creation
- All settings visible and editable in one place
- Application registry path: `registry_path` (top-level) or `application.registry_path`
- Well-organized with clear section comments for easy navigation

**Benefits:**
- Complete transparency - every setting visible
- Self-documenting with inline comments
- Users control config lifecycle (industry standard approach)
- Easy to search and edit
- Framework defaults accessible via `framework export-config` command
- Stable across framework upgrades (similar to Django, React)

### Registry System

**Key Principle:** Extend framework registry instead of manually merging.  
**Implementation:** `src/framework/registry/helpers.py`

**Compact Style (Default - Recommended):**
```python
# my_project/registry.py (5-10 lines!)
from framework.registry import (
    extend_framework_registry, 
    CapabilityRegistration,
    ContextClassRegistration,
    RegistryConfig,
    RegistryConfigProvider
)

class MyProjectRegistryProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return extend_framework_registry(
            capabilities=[
                CapabilityRegistration(
                    name="my_capability",
                    module_path="my_project.capabilities.my_capability",
                    class_name="MyCapability",
                    description="My custom capability",
                    provides=["MY_CONTEXT"],
                    requires=[]
                ),
            ],
            context_classes=[
                ContextClassRegistration(
                    context_type="MY_CONTEXT",
                    module_path="my_project.context_classes",
                    class_name="MyContext"
                )
            ],
            # Optional: exclude framework components you don't need
            exclude_capabilities=["python"],
        )
```

**Real Example:** See `src/framework/templates/apps/hello_world_weather/registry.py.j2` for production template.

**Explicit Style (Advanced - Optional):**
```python
# my_project/registry.py (500+ lines)
class MyProjectRegistryProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            core_nodes=[
                # All framework nodes explicitly listed (200+ lines)
                NodeRegistration(name="router", ...),
                NodeRegistration(name="orchestrator", ...),
                # ...
            ],
            capabilities=[
                # All framework capabilities explicitly listed (200+ lines)
                CapabilityRegistration(name="memory", ...),
                CapabilityRegistration(name="python", ...),
                # ... framework components
                
                # Your application capabilities
                CapabilityRegistration(name="my_capability", ...),
            ],
            # ... etc
        )
```

**Template Choice:**
```bash
# Default: Compact style (recommended for most users)
framework init my-project

# Explicit style for advanced users (shows all framework components)
framework init my-project --registry-style explicit
```

**Benefits:**
- **70% less code** - focus on what's unique to your application
- **Automatic updates** - framework changes don't break your registry
- **Clean exclusions** - `exclude_capabilities=["python"]` instead of dict hack
- **Progressive disclosure** - start simple, go explicit when needed
- Used in all 3 app templates (minimal, hello_world_weather, wind_turbine)

---

## 🔮 Future Considerations

**Note:** A potential future rename of the CLI command from `framework` to a different name is under consideration but not yet decided. If implemented, this would be a straightforward search-and-replace across the codebase with backward-compatible legacy entry points maintained.

---

## 📚 References

**Design Documents:**
- [Example Creation & Application Scaffolding](./example_creation.md) - CLI scaffolding system design
- [Registry Helper Design](./registry-helper-design.md) - Registry simplification with helper functions
- [Provider Registry](./provider_registry.md) - Provider system design

**Documentation:**
- [Registry and Discovery](../docs/source/developer-guides/03_core-framework-systems/03_registry-and-discovery.rst)
- [Configuration Architecture](../docs/source/developer-guides/03_core-framework-systems/06_configuration-architecture.rst)
- [Building Applications](../docs/source/developer-guides/02_quick-start-patterns/01_building-your-first-capability.rst)

**Key Implementation Files:**
- `src/framework/cli/main.py` - Unified CLI with lazy loading
- `src/framework/cli/init_cmd.py` - Project initialization
- `src/framework/cli/health_cmd.py` - System diagnostics
- `src/framework/cli/export_config_cmd.py` - Configuration export
- `src/framework/registry/manager.py` - Registry manager with path-based discovery
- `src/framework/registry/helpers.py` - Helper functions (extend_framework_registry, etc.)
- `src/framework/registry/base.py` - RegistryConfigProvider interface
- `src/framework/utils/config.py` - Configuration system with .env support
- `src/framework/templates/` - Complete template system
- `pyproject.toml` - Package definition

**Template Examples:**
- `src/framework/templates/apps/hello_world_weather/registry.py.j2` - Simple example using helpers
- `src/framework/templates/apps/wind_turbine/registry.py.j2` - Complex example with exclusions
- `src/framework/templates/apps/minimal/registry.py.j2` - Minimal starter template
- `src/framework/templates/project/config.yml.j2` - Complete configuration template

**External Resources:**
- [Python importlib.util](https://docs.python.org/3/library/importlib.html#importlib.util.spec_from_file_location) - Dynamic module loading
- [Click Documentation](https://click.palletsprojects.com/) - CLI framework
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Template engine