# Alpha Berkeley Framework - Latest Release (v0.4.1)

🔧 **Notebook registry enhancement** - improved notebook management with structured metadata support.

## What's New

### 🏗️ Notebook Registry Enhancements
- **Centralized Notebook Registry**: Added structured notebook registry system replacing simple link list with rich metadata support
- **StateManager Integration**: New `register_notebook()` method for capability-agnostic notebook registration with timestamps and metadata
- **Response Context Tracking**: Enhanced ResponseContext to track notebook availability for improved user guidance

### 🔧 Technical Improvements
- **Structured Data Management**: Replaced `ui_notebook_links` with `ui_captured_notebooks` registry in agent state
- **Metadata Support**: Notebook registration now supports display names, capability tracking, and automatic timestamp generation
- **State Management**: Updated state reset logic to use new registry format for better notebook lifecycle management

## Upgrade Notes

This is a patch release with notebook registry enhancements:

- **Registry Migration**: Existing notebook links will be automatically converted to new structured format
- **API Enhancement**: New `StateManager.register_notebook()` method available for capabilities
- **Response Context**: Response generation now has access to notebook availability information
- **Backwards Compatibility**: All changes maintain backwards compatibility

## Get Started

1. Update to v0.4.1 for enhanced notebook registry and improved metadata support
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

*Current Release: v0.4.1 (September 2025)*  
*Release Type: Patch Release*  
*Previous Release: v0.4.0 with major feature enhancements and critical bug fixes*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
