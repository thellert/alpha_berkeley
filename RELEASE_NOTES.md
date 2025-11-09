# Osprey Framework - Latest Release (v0.8.4)

🔧 **Registry Architecture Enhancement** - Extend and Standalone Registry Modes

## What's New in v0.8.4

### 🏗️ Registry Modes

**Two distinct modes for application registries:**

- **Extend Mode (Recommended)**: Applications extend framework defaults via `ExtendedRegistryConfig`
  - Framework components loaded automatically (memory, Python, time parsing, routing, etc.)
  - Applications add, exclude, or override framework components
  - Returned by `extend_framework_registry()` helper function
  - Reduces boilerplate and simplifies upgrades
  - Perfect for 95%+ of applications

- **Standalone Mode (Advanced)**: Applications provide complete registry including all framework components
  - Framework registry is NOT loaded
  - Full control over all components
  - Used when `RegistryConfig` is returned directly (not via helper)
  - For minimal deployments or custom framework variations

Mode detection is automatic based on registry type (`isinstance(config, ExtendedRegistryConfig)`)

### ✨ New Features

- **`ExtendedRegistryConfig` marker class**: Signals Extend mode to the registry manager
  - Subclass of `RegistryConfig` with identical fields
  - Type-based detection enables automatic framework merging
  - Added to `__all__` exports in `osprey.registry`

- **`generate_explicit_registry_code()` helper function**: For template generation
  - Generates complete registry Python code combining framework + app components
  - Used by CLI template system for creating standalone registries
  - Useful for applications that want full visibility of all components
  - Takes app metadata and component lists, returns formatted Python source code

- **Comprehensive test suite**: 500+ lines across 4 new test files
  - `test_registry_modes.py`: Tests for Extend vs Standalone mode detection
  - `test_registry_loading.py`: Tests for registry loading mechanisms
  - `test_registry_helpers.py`: Tests for helper functions
  - `test_registry_validation.py`: Tests for registry validation

### 🔄 Changed

- **Registry Helper**: `extend_framework_registry()` now returns `ExtendedRegistryConfig` instead of `RegistryConfig`
  - Backward compatible (ExtendedRegistryConfig is a subclass of RegistryConfig)
  - Type signature change enables automatic mode detection
  - Applications using type hints should update return type annotation

- **CLI Terminology Update**: More intuitive naming
  - `compact` → `extend` (emphasizes extension of framework)
  - `explicit` → `standalone` (clarifies independent operation)
  - Updated all documentation, commands, and templates

- **Enhanced Documentation**: Comprehensive coverage of both modes
  - Developer guide updated with mode selection guidance
  - API reference documentation expanded with ExtendedRegistryConfig details
  - Code examples updated to show ExtendedRegistryConfig return type
  - Migration guide for upgrading from older versions

## Breaking Changes

⚠️ **These changes require minor updates to existing code:**

### 1. RegistryManager Constructor

**Change**: Parameter changed from `registry_paths: List[str]` to `registry_path: Optional[str]`

**Impact**: Low - most applications use `initialize_registry()` which reads from config

**Migration**:
```python
# Old (v0.8.3 and earlier):
manager = RegistryManager(registry_paths=[path1, path2])

# New (v0.8.4+):
manager = RegistryManager(registry_path=path)  # Single registry only
```

**Rationale**: Simplified to single-application model matching actual usage patterns. Framework now supports one application registry per instance (loaded from `config.yml`).

### 2. Type Signature Change

**Change**: `extend_framework_registry()` return type changed to `ExtendedRegistryConfig`

**Impact**: Very low - backward compatible at runtime (subclass relationship)

**Migration**:
```python
# Old type hint:
def get_registry_config(self) -> RegistryConfig:

# New type hint:
def get_registry_config(self) -> ExtendedRegistryConfig:
```

Only affects code using explicit type checking. Runtime behavior unchanged.

## Upgrading from v0.8.3

### For Most Users (using extend_framework_registry)

**No changes required!** Your code will continue to work:

```python
from osprey.registry import extend_framework_registry

# This still works exactly the same
config = extend_framework_registry(
    capabilities=[...],
    context_classes=[...]
)
```

**Optional improvement**: Update type hints for better IDE support:

```python
from osprey.registry import ExtendedRegistryConfig

def get_registry_config(self) -> ExtendedRegistryConfig:  # Updated type hint
    return extend_framework_registry(...)
```

### For Advanced Users (direct RegistryManager usage)

If you instantiate `RegistryManager` directly:

```python
# Update parameter name:
from osprey.registry import RegistryManager

# Old:
manager = RegistryManager(registry_paths=[path])

# New:
manager = RegistryManager(registry_path=path)
```

### For CLI Users

**Terminology change** in commands:

```bash
# Old command options (still work for backward compatibility):
osprey init my-project --registry-style compact
osprey init my-project --registry-style explicit

# New command options (recommended):
osprey init my-project --registry-style extend
osprey init my-project --registry-style standalone
```

## Installation

```bash
pip install --upgrade osprey-framework
```

## Documentation

- **Main Documentation**: https://als-apg.github.io/osprey
- **Registry System Guide**: https://als-apg.github.io/osprey/developer-guides/03_core-framework-systems/03_registry-and-discovery.html
- **Migration Guide**: https://als-apg.github.io/osprey/getting-started/migration-guide.html
- **API Reference**: https://als-apg.github.io/osprey/api_reference/01_core_framework/03_registry_system.html

## Developer Notes

- Registry system now uses type-based mode detection for cleaner separation of concerns
- Standalone mode enables minimal deployments and custom framework variations
- Extend mode remains the recommended default for >95% of applications
- See developer guide "Registry and Discovery" for complete mode selection guidance

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details of all changes.
