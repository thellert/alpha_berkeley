# Alpha Berkeley Framework - Latest Release (v0.4.2)

⚡ **Python execution enhancements** - improved notebook generation and integration with centralized registry.

## What's New

### ⚡ Python Execution Enhancements
- **Registry Integration**: Python capability now uses centralized StateManager.register_notebook() with rich execution metadata
- **Improved Notebook Links**: Enhanced URL generation in both local and container execution modes with proper FileManager integration
- **Better Notebook Structure**: Cleaner notebook organization with separate markdown documentation and executable code blocks

### 🔧 Technical Improvements
- **Execution Metadata**: Notebook registration includes execution time, context keys, and code metrics for better tracking
- **Standardized Naming**: Unified notebook naming to 'notebook.ipynb' across all execution modes
- **Enhanced Generation**: Improved notebook cell structure with proper separation of results and executable code

## Upgrade Notes

This is a patch release with Python execution enhancements:

- **Enhanced Integration**: Python execution now fully integrated with centralized notebook registry
- **Improved Links**: Better notebook URL generation across all execution environments
- **Cleaner Notebooks**: Improved notebook structure with better organization of content
- **Backwards Compatibility**: All changes maintain backwards compatibility

## Get Started

1. Update to v0.4.2 for enhanced Python execution and improved notebook generation
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

*Current Release: v0.4.2 (September 2025)*  
*Release Type: Patch Release*  
*Previous Release: v0.4.1 with centralized notebook registry system*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
