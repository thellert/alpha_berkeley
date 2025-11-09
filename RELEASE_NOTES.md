# Osprey Framework - Latest Release (v0.8.3)

🐳 **Container Runtime Flexibility Release** - Docker & Podman Support with Auto-Detection

## What's New in v0.8.3

### 🐳 Docker Runtime Support
- **Flexible Container Runtime**: Framework now supports both Docker and Podman
  - Automatic detection: Prefers Docker, falls back to Podman
  - Configuration option: `container_runtime` in `config.yml` (`auto`, `docker`, or `podman`)
  - Environment variable override: `CONTAINER_RUNTIME` for per-command selection
  - Modern runtimes only: Docker Desktop 4.0+ or Podman 4.0+ (native compose support)

### 🔧 Runtime Detection Module
- **New `runtime_helper.py`**: Intelligent runtime detection with caching
  - Platform-specific error messages (macOS/Linux/Windows)
  - Helpful troubleshooting guidance when Docker/Podman not running
  - Module-level caching for performance
  - Comprehensive test suite (33 tests)

### 🛠️ Container Management Updates
- **Updated 6 functions** in `container_manager.py` to use runtime abstraction
- **Runtime-agnostic health checks** in `health_cmd.py`
- **Runtime-agnostic mount detection** in `interactive_menu.py`
- **Fixed JSON parsing**: `osprey deploy status` now handles both Docker (NDJSON) and Podman (JSON array) formats
- All compose operations work seamlessly with both runtimes

### 📚 Documentation Updates
- **Installation Guide**: Side-by-side Docker and Podman installation instructions
- **API Reference**: Added `runtime_helper` module documentation
- **Developer Guide**: Updated container deployment references
- **Tutorial Updates**: Updated prerequisites and examples
- **Documentation Workflow**: Added comprehensive `UPDATE_DOCS.md` guide

### 📦 Dependency Changes
- **Removed Python packages**: `podman` and `podman-compose` no longer required
- **System installation**: Container runtimes now installed via system package managers
  - macOS/Windows: Docker Desktop 4.0+ OR Podman 4.0+
  - Linux: Docker CE 4.0+ OR Podman 4.0+
- Framework uses CLI tools (`docker`/`podman` commands), not Python SDKs

### 🎯 Custom AI Provider Registration
- **Applications can register custom AI providers** through the registry system
- Added `providers` parameter to `extend_framework_registry()` helper function
- Added `exclude_providers` parameter to exclude framework providers
- Added `override_providers` parameter to replace framework providers
- Support for institutional AI services (Azure, Stanford AI, national lab endpoints)
- Comprehensive test suite (16 tests) covering all provider registration scenarios

## Breaking Changes

### Installation Requirements
- **Users must install Docker Desktop 4.0+ OR Podman 4.0+ separately**
- Python packages no longer provide container runtime functionality
- See [installation guide](https://als-apg.github.io/osprey/getting-started/installation.html) for platform-specific instructions

### Impact
- **Existing Podman users**: Unaffected - auto-detection will find Podman if Docker not installed
- **New users**: More flexibility - can use Docker Desktop (most common) or Podman
- **Docker and Podman use separate namespaces**: Existing containers/volumes won't be visible after switching runtimes

## Upgrade Instructions

1. **Install Container Runtime** (if not already installed):
   - **Docker Desktop**: https://docs.docker.com/get-started/get-docker/
   - **Podman**: https://podman.io/docs/installation

2. **Upgrade Framework**:
   ```bash
   pip install --upgrade osprey-framework
   ```

3. **Verify Installation**:
   ```bash
   # Check Docker
   docker --version
   docker compose version
   
   # Or check Podman
   podman --version
   podman compose version
   ```

4. **Optional: Configure Runtime**:
   ```yaml
   # config.yml
   container_runtime: auto  # or 'docker' or 'podman'
   ```

## Testing

This release includes comprehensive test coverage:
- **33 new tests** for runtime detection and selection
- **16 new tests** for custom provider registration
- **All 128 tests passing** with <2s runtime

## Links

- **Documentation**: https://als-apg.github.io/osprey
- **Installation Guide**: https://als-apg.github.io/osprey/getting-started/installation.html
- **API Reference**: https://als-apg.github.io/osprey/api_reference/
- **GitHub Repository**: https://github.com/als-apg/osprey
- **Issue Tracker**: https://github.com/als-apg/osprey/issues

## Contributors

Thanks to everyone who contributed to this release!

---

For the complete changelog, see [CHANGELOG.md](https://github.com/als-apg/osprey/blob/main/CHANGELOG.md).
