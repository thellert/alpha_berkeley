# Alpha Berkeley Framework - Latest Release (v0.2.1)

🔧 **Major stability and usability improvements** for the Alpha Berkeley Framework!

## What's Fixed

### Critical Issues Resolved
- **Containerized Python Execution**: Fixed critical bug where execution metadata wasn't being created in mounted volumes
- **Container Build Failures**: Removed obsolete python3-epics-simulation kernel mounts that caused build failures
- **Path Mapping**: Fixed hardcoded path patterns in container execution using config-driven approach

### Security & Stability Improvements
- **Repository Security**: Updated .gitignore to exclude development services and sensitive configurations
- **Network Security**: Renamed container network from als-agents-network to alpha-berkeley-network for consistency
- **Service Cleanup**: Removed mem0 service references and cleaned up leftover container code

### Developer Experience Enhancements
- **Configuration System Refactoring**: Renamed `unified_config` module to `config` for improved developer experience
- **Professional Naming**: Replaced `UnifiedConfigBuilder` with `ConfigBuilder` to eliminate confusing terminology
- **Automatic Environment Detection**: Added container-aware Python environment detection for convenience
- **Graceful Ollama Fallback**: Implemented automatic URL fallback for development workflows

## Upgrade Notes

This release maintains full backward compatibility. The main changes are:
- Import paths updated from `unified_config` to `config` (automatic detection handles this)
- Container execution is more reliable and requires no manual reconfiguration
- Timezone handling is now consistent across all services

## Get Started

1. Update your installation: `pip install --upgrade alpha-berkeley-framework`
2. Follow the [installation guide](https://thellert.github.io/alpha_berkeley/getting-started/installation/)
3. Explore the [complete documentation](https://thellert.github.io/alpha_berkeley/)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.2.1`
3. **Title**: `Alpha Berkeley Framework v0.2.1 - Critical Fixes & Developer Experience`
4. **Description**: Copy the content above (from "🔧 Major stability" through "Explore the complete documentation")

## Technical Details

- Fixed 'Failed to read execution metadata from container' error through proper volume mounting
- Eliminated manual reconfiguration when switching between local and containerized execution
- Complete refactoring eliminates confusing "unified" terminology from LangGraph migration era
- Added proper timezone data (tzdata) package in Jupyter containers for accurate timestamps
- Maintains backward compatibility through systematic import updates across entire codebase

---

*Current Release: v0.2.1 (January 2025)*  
*Release Type: Stability & Developer Experience*  
*Previous Release: v0.2.0 with advanced tutorials*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
