# Alpha Berkeley Framework - Latest Release (v0.4.5)

🚀 **Enhanced UI capabilities and infrastructure improvements** - new launchable commands system, enhanced result display, and improved configuration management.

## What's New

### 🚀 New Features & Capabilities
- **Launchable Commands System**: New centralized infrastructure for registering and displaying executable commands (web apps, desktop tools, viewers) directly through both CLI and OpenWebUI interfaces
- **Enhanced UI Result Display**: Comprehensive system for displaying figures, commands, and notebooks with rich formatting, metadata, and user-friendly presentation
- **MCP Protocol Support**: Added Model Context Protocol integration capabilities with `fastmcp` dependency

### 🎯 Interface Improvements
- **CLI Enhancement**: Added comprehensive result display methods with formatted output for figures, commands, and notebooks including file paths and launch instructions
- **OpenWebUI Improvements**: Refactored result extraction system with improved command handling, notebook links, and error handling
- **Unified Display System**: Consistent presentation of generated content across both CLI and web interfaces

### ⚙️ Infrastructure Enhancements
- **Configuration Management**: Enhanced path resolution with host/container environment awareness and application-specific file paths support
- **State Management**: New `ui_launchable_commands` registry and `StateManager.register_command()` method for capability-agnostic command registration
- **Response Generation**: Updated prompt system to handle command display with interface-aware formatting and user guidance

## Upgrade Notes

This is a patch release with enhanced UI capabilities and infrastructure improvements:

- **New Dependencies**: Added `fastmcp` for Model Context Protocol support - run `pip install -r requirements.txt` to update
- **Backwards Compatibility**: All existing functionality is preserved with enhanced capabilities
- **Enhanced Interfaces**: Both CLI and OpenWebUI now provide richer result display with figures, commands, and notebooks
- **Configuration**: New path resolution options available but existing configurations continue to work

## Get Started

1. Update to v0.4.5 for enhanced UI capabilities and improved infrastructure
2. View the [complete documentation](https://thellert.github.io/alpha_berkeley/)
3. Report any issues on [GitHub Issues](https://github.com/thellert/alpha_berkeley/issues)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.4.0`
3. **Title**: `Alpha Berkeley Framework v0.4.0 - Major Feature Release`
4. **Description**: Copy the content above (from "🚀 Major feature release" through "Get Started")

## Technical Details

- Added `ReclassificationRequiredError` exception to framework error system
- Enhanced router error handling with consistent reclassification limit enforcement
- Unified reclassification system eliminating dual state/error paths
- Removed obsolete `control_needs_reclassification` agent state field
- Added `PythonExecutorConfig` class for centralized Python execution settings
- Implemented `recursively_summarize_data()` utility for context window management
- Enhanced figure registration with batch processing capabilities
- Added response chunking for large outputs in OpenWebUI interface

---

*Current Release: v0.4.5 (September 2025)*  
*Release Type: Patch Release*  
*Previous Release: v0.4.4 with example formatting system improvements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
