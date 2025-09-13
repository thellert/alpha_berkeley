# Alpha Berkeley Framework - Latest Release (v0.4.3)

🎨 **UI and response improvements** - enhanced user experience with notebook-aware interfaces and better response generation.

## What's New

### 🎨 UI and Interface Enhancements
- **OpenWebUI Integration**: Added comprehensive notebook link display with seamless integration of text, figures, and clickable notebook links
- **Response Generation**: Enhanced prompts with notebook awareness and interface-specific user guidance
- **Context Loading**: Improved logging and registry initialization for better debugging and error handling

### 🔧 User Experience Improvements
- **Wind Turbine Application**: Refactored response generation with streamlined guidelines and cleaner code organization
- **Comprehensive Responses**: Better integration of execution results, visualizations, and notebook access in user interfaces
- **Enhanced Debugging**: Replaced print statements with proper logging throughout the system

## Upgrade Notes

This is a patch release with UI and response improvements:

- **Enhanced User Experience**: Comprehensive notebook integration across interfaces with better user guidance
- **Improved Response Quality**: Context-aware response generation with interface-specific capabilities
- **Better Debugging**: Enhanced logging and error handling throughout the system
- **Backwards Compatibility**: All changes maintain backwards compatibility

## Get Started

1. Update to v0.4.3 for enhanced UI experience and improved response generation
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

*Current Release: v0.4.3 (September 2025)*  
*Release Type: Patch Release*  
*Previous Release: v0.4.2 with Python execution enhancements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
