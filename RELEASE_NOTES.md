# Alpha Berkeley Framework - Latest Release (v0.2.2)

🚀 **Major error handling enhancements and framework improvements** for the Alpha Berkeley Framework!

## What's New

### 🔧 New RECLASSIFICATION Error Severity
- **Smart Task-Capability Matching**: Capabilities can now request reclassification when they receive inappropriate tasks
- **Improved Workflow**: Enhanced error classification system with configurable reclassification attempt limits
- **Better Routing**: Router node now properly handles reclassification errors and prevents infinite loops

### ⚠️ Breaking Changes (Backward Compatible)
- **ErrorClassification Metadata Migration**: Unified error handling with enhanced metadata field
- **Richer Error Context**: All error information now flows through a consistent metadata structure
- **Enhanced LLM Integration**: Better error context for AI-driven recovery and analysis

### 🏗️ Framework Enhancements
- **Enhanced Classification Workflow**: Improved reclassification handling with proper failure context
- **Router Node Improvements**: Added reclassification tracking and intelligent routing logic
- **Configuration System**: New execution limits configuration for better control
- **Error Node Enhancements**: Comprehensive error handling improvements

### 📚 Documentation & Examples
- **Major Documentation Cleanup**: Removed outdated files and enhanced RST documentation structure
- **Enhanced Hello World Example**: Better classifier examples and improved context access patterns
- **Complete Error Handling Docs**: Updated documentation for new reclassification workflow
- **Developer Guide Improvements**: Enhanced infrastructure component documentation

## Upgrade Notes

This release maintains full backward compatibility. The main changes are:
- New `RECLASSIFICATION` error severity level available for capability developers
- ErrorClassification now uses unified metadata field (automatic migration handled)
- Enhanced error handling workflow with better context for AI-driven recovery
- Improved documentation structure and examples

## Get Started

1. Update your installation: `pip install --upgrade alpha-berkeley-framework`
2. Follow the [installation guide](https://thellert.github.io/alpha_berkeley/getting-started/installation/)
3. Explore the [complete documentation](https://thellert.github.io/alpha_berkeley/)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.2.2`
3. **Title**: `Alpha Berkeley Framework v0.2.2 - Enhanced Error Handling & Framework Improvements`
4. **Description**: Copy the content above (from "🚀 Major error handling" through "See the error handling guide")

## Technical Details

- New RECLASSIFICATION severity enables smart task-capability matching
- Unified metadata approach provides richer context for error analysis and recovery
- Enhanced classification workflow with configurable attempt limits prevents infinite loops
- Framework-wide migration to new ErrorClassification metadata structure
- Complete documentation restructuring with enhanced developer guides
- Enhanced hello world weather example demonstrates best practices

---

*Current Release: v0.2.2 (August 2025)*  
*Release Type: Error Handling Enhancements & Framework Improvements*  
*Previous Release: v0.2.1 with stability improvements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
