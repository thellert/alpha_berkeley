# Alpha Berkeley Framework - Latest Release (v0.3.1)

🔧 **Documentation workflow improvements** - a maintenance release for the Alpha Berkeley Framework.

## What's New

### 📚 Documentation Workflow Enhancements
- **Manual Trigger Support**: Added workflow_dispatch trigger for manual documentation builds
- **Tag-based Rebuilds**: Documentation now automatically rebuilds when version tags are created
- **Enhanced Build Controls**: Support for both automatic (tag/push) and manual triggering
- **Version Sync Fix**: Fixed issue where moving git tags didn't trigger documentation rebuilds

### 🧹 Minor Fixes
- **Gitignore Cleanup**: Added `.nfs*` pattern and fixed malformed entries

## Upgrade Notes

This is a small maintenance release focused on documentation infrastructure. No code changes affect the framework functionality.

## Get Started

1. No installation changes required - this is a documentation infrastructure update
2. View the [complete documentation](https://thellert.github.io/alpha_berkeley/)

---

## GitHub Release Instructions

When creating the GitHub release:

1. Go to GitHub repo → Releases → "Create a new release"
2. **Tag**: `v0.3.1`
3. **Title**: `Alpha Berkeley Framework v0.3.1 - Documentation Workflow Improvements`
4. **Description**: Copy the content above (from "🔧 Documentation workflow improvements" through "Get Started")

## Technical Details

- Added `workflow_dispatch` and `tags: ['v*']` triggers to documentation workflow
- Enhanced deployment conditions for manual and tag-based builds
- Fixed gitignore patterns for development environments

---

*Current Release: v0.3.1 (September 2025)*  
*Release Type: Documentation Workflow Improvements*  
*Previous Release: v0.3.0 with interface enhancements and figure display improvements*

---

**Note**: This file always contains information about the current release. For historical release information, see [CHANGELOG.md](CHANGELOG.md).
