# Osprey Framework - Latest Release (v0.8.5)

🐛 **Bug Fix Release** - Python Executor Configuration and Subprocess Execution

## What's New in v0.8.5

### 🐛 Critical Bug Fixes

**Python Executor Configuration Fixes:**
- Fixed deprecated 'framework' config nesting throughout python_executor components
- Added `CONFIG_FILE` environment variable support for subprocess execution
  - Critical fix for registry/context loading in subprocesses
  - Ensures correct config path resolution when CWD ≠ project root
- Fixed config path access in `LocalCodeExecutor` for `python_env_path` setting
- Updated `execution_wrapper` to pass `config_path` to registry initialization

**Code Quality Improvements:**
- Improved exception chaining with `from e` for better error traceability
- Removed all trailing whitespace (W291, W293) across codebase
- Applied automatic ruff formatting fixes for consistency
- Improved logging: reduced verbosity and added structured formatting
- Extracted duplicate streaming logic into helper method in CLI

### 🔧 Technical Details

These changes fix bugs that prevented proper context loading and configuration access in subprocess-based Python execution scenarios. The `CONFIG_FILE` environment variable fix is particularly critical for production deployments where the Python executor spawns subprocesses that need to access the correct configuration.

## Upgrading from v0.8.4

**No breaking changes.** This is a patch release with bug fixes only.

Simply upgrade to v0.8.5:

```bash
pip install --upgrade osprey-framework
```

## Installation

```bash
pip install --upgrade osprey-framework==0.8.5
```

## Documentation

- **Main Documentation**: https://als-apg.github.io/osprey
- **Registry System Guide**: https://als-apg.github.io/osprey/developer-guides/03_core-framework-systems/03_registry-and-discovery.html
- **API Reference**: https://als-apg.github.io/osprey/api_reference/01_core_framework/03_registry_system.html

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details of all changes.
