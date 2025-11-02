# NOTE: Phase one was completed already

---

## 🚀 CURRENT STATUS - UPDATED 2025-11-02

**PHASES COMPLETED:** ✅ Phase 1, ✅ Phase 2, ✅ Phase 3 (98%)

**YOU ARE HERE:** 📍 Phase 4 - Critical Remaining Updates

**NEXT STEPS (30-60 minutes):**
1. Update `pyproject.toml` (package name, version, URLs, entry points)
2. Update `src/osprey/__init__.py` (version → 0.8.0)
3. Add v0.8.0 entry to `CHANGELOG.md`
4. Update 4 template files (package references)
5. Quick URL updates in docs/conf.py and cli/interactive_menu.py
6. **Then**: Atomic commit + testing (Phase 7-8)

**AMAZING PROGRESS:**
- ✅ 134/136 Python files renamed (98.5%)
- ✅ 67/123 docs files renamed (54.5%)
- ✅ All imports fixed
- ✅ Directory renamed
- ✅ Tests passing

**See Phase 4 below for specific files and line numbers →**

---

## 📝 IMPORTANT: PyPI Package Naming

**PyPI Package Name:** `osprey-framework` (with hyphen)
- Use in `pyproject.toml`: `name = "osprey-framework"`
- Use in pip install: `pip install osprey-framework`
- PyPI URL: `https://pypi.org/project/osprey-framework/`

**Distribution Filenames:** `osprey_framework` (with underscore)
- Build tools automatically convert hyphens to underscores in filenames
- Example: `osprey_framework-0.8.0-py3-none-any.whl`
- This is normal Python packaging behavior

**Import Path:** `osprey` (no hyphen or underscore)
- Use in code: `from osprey.state import AgentState`
- Package directory: `src/osprey/`

---

## 🔍 ADDITIONAL ISSUES DISCOVERED (2025-11-01)

**Beyond the original plan, these issues were found during codebase analysis:**

1. **Version number**: Must update from `0.7.8` → `0.8.0` in pyproject.toml
2. **String-based module references**: 41 matches of `"framework."` in registry and docs
3. **Docker compose files**: Multiple template files reference `alpha-berkeley-framework`
4. **Shell scripts**: startup scripts in templates reference old package name
5. **GitHub URLs**: 23 matches of `thellert/alpha_berkeley` need updating
6. **Documentation URLs**: `thellert.github.io/alpha_berkeley` → `als-apg.github.io/osprey`
7. **pyproject.toml testpaths**: Line 269 has old `"services/framework/*/tests"` path
8. **pyproject.toml package-data**: Lines 194-195 have incorrect `"deployment"` and `"docs"` entries
9. **CLI command examples**: Need careful manual review to avoid false positives
10. **.egg-info directory**: Will be cleaned up with build artifacts

**Strategy**: Use IDE search-and-replace for systematic updates (see Phase 3)

---

## 📋 PHASE 2: Osprey Rename Preparation ✅ COMPLETED

### ✅ Task 3: Create Branches and Backup
- [x] **3a.** Create rename branch ✅
- [x] **3b.** Create safety backup branch ✅  
- [x] **3c.** Run baseline tests ✅ (all 55 tests passed)

---

## 📋 PHASE 3: Manual IDE Search & Replace ✅ MOSTLY COMPLETED

**Progress Summary:**
- ✅ 134/136 Python files renamed (98.5% complete)
- ✅ 67/123 documentation files renamed (54.5% complete)
- ✅ All Python imports updated (`from framework.` → `from osprey.`)
- ✅ Directory renamed (`src/framework` → `src/osprey`)
- ✅ Path references fixed (Makefile, config.yml)

### ✅ Task 4: IDE-Based Find & Replace Operations

- [x] **4a.** Rename main directory ✅
- [x] **4b.** Python imports: `from framework.` → `from osprey.` ✅ (verified: 0 matches remaining)
- [x] **4c.** String-based module references ✅ (done via manual file edits)
- [x] **4d.** Logger name strings ✅ (done via manual file edits)
- [ ] **4e.** Package name in strings: `alpha-berkeley-framework` → `osprey-framework` ⚠️ REMAINING
  - **Status**: 23 matches in 10 files still need updating
  - **Files**: pyproject.toml (2), templates (3), README.md, CHANGELOG.md, etc.
  
- [x] **4f.** Python import name: `alpha_berkeley_framework` → `osprey` ✅
- [ ] **4g.** Repository URLs: `thellert/alpha_berkeley` → `als-apg/osprey` ⚠️ REMAINING
  - **Status**: 28 matches in 8 files
  - **Files**: pyproject.toml, docs, cli/interactive_menu.py, conf.py
  
- [ ] **4h.** Documentation URLs: `thellert.github.io/alpha_berkeley` → `als-apg/osprey` ⚠️ (covered by 4g)
- [x] **4i.** Brand name: `Alpha Berkeley Framework` → `Osprey Framework` ✅ (mostly done)
- [x] **4j.** CLI command in examples ✅ (done via manual file edits)
- [x] **4k.** CLI command at start of line ✅ (done via manual file edits)
- [x] **4l.** Path references: `src/framework` → `src/osprey` ✅

---

## 📋 PHASE 4: Critical Remaining Updates ⚠️ IN PROGRESS

**🎯 REMAINING WORK SUMMARY:**

**Critical (Must Do):**
1. ✏️ `pyproject.toml` - Package name, version, URLs, entry points
2. ✏️ `src/osprey/__init__.py` - Update version to 0.8.0
3. ✏️ `CHANGELOG.md` - Add v0.8.0 entry (template provided below)

**Template Files (Should Do):**
4. ✏️ `src/osprey/templates/project/pyproject.toml.j2` - Fix package dependency
5. ✏️ `src/osprey/templates/project/requirements.txt` - Fix package name
6. ✏️ `src/osprey/templates/services/pipelines/start.sh` - Fix package name
7. ✏️ `src/osprey/templates/services/jupyter/custom_start.sh` - Fix package name

**Documentation (Nice to Have):**
8. ✏️ `docs/source/conf.py` - Update GitHub URLs
9. ✏️ `src/osprey/cli/interactive_menu.py` - Update repository URL
10. ✏️ Remaining 56 documentation autosummary files (may auto-regenerate)

---

### 🔴 Task 5: pyproject.toml Updates (CRITICAL)

- [ ] **5a.** Update pyproject.toml manually - **MUST DO BEFORE COMMIT**
  ```toml
  # Line 6: Package name (use hyphens for PyPI)
  name = "osprey-framework"
  
  # Line 7: Update version
  version = "0.8.0"
  
  # Line 8: Update description (optional)
  description = "An open-source, domain-agnostic, capability-based architecture for building intelligent agents"
  
  # Line 150: Optional dependencies (should be auto-fixed by 4e, verify)
  all = ["osprey-framework[docs,scientific,databases,postgres,memory,dev,nlp,utils]"]
  
  # Lines 154-159: Project URLs (should be auto-fixed by 4g-4h, verify)
  Homepage = "https://als-apg.github.io/osprey"
  Documentation = "https://als-apg.github.io/osprey"
  Repository = "https://github.com/als-apg/osprey"
  Issues = "https://github.com/als-apg/osprey/issues"
  Changelog = "https://github.com/als-apg/osprey/blob/main/CHANGELOG.md"
  
  # Lines 162-169: CLI entry points
  [project.scripts]
  osprey = "osprey.cli.main:cli"
  # DECISION: Remove or rename alpha-berkeley legacy entry points?
  # Option 1: Remove them entirely (clean break)
  # Option 2: Keep for backward compatibility (point to osprey)
  alpha-berkeley = "osprey.interfaces.cli.direct_conversation:main"
  alpha-berkeley-deploy = "osprey.deployment.container_manager:main"
  alpha-berkeley-docs = "docs.launch_docs:main"
  
  # Line 173-175: Package discovery
  [tool.setuptools.packages.find]
  where = ["src"]
  include = ["osprey*"]
  
  # Line 178-193: Package data
  [tool.setuptools.package-data]
  "osprey" = [
      "config.yml",
      "templates/**/*",
      "templates/**/*.j2",
      # ... (keep all the patterns)
  ]
  # REMOVE the old "framework" entry
  # REMOVE "deployment" and "docs" entries (line 194-195)
  
  # Line 269: testpaths - IMPORTANT FIX
  testpaths = [
      "tests",
      "src/applications/*/tests",
      # REMOVE: "services/framework/*/tests"  (old structure)
  ]
  
  # Line 306: Ruff isort config (should be auto-fixed, verify)
  known-first-party = ["osprey", "configs", "applications", "interfaces", "deployment"]
  ```

---

## 📋 PHASE 5: File-Specific Updates

### ✅ Task 6: Update Core Framework Files

- [ ] **6a.** Update src/osprey/__init__.py
  ```python
  """Osprey Framework.
  
  Core framework package providing infrastructure for building
  intelligent agents with specialized capabilities.
  """
  
  __version__ = "0.8.0"
  
  __all__ = ['__version__']
  
  # Framework is designed for on-demand imports
  # Use specific imports like: from osprey.state import AgentState
  ```

- [ ] **6b.** Update README.md
  - Should be mostly handled by search/replace
  - Manually verify install instructions
  - Ensure all examples use `osprey` CLI command
  - Add migration note at top

- [ ] **6c.** Update CHANGELOG.md
  - Keep historical references as-is
  - Add NEW v0.8.0 entry at the TOP (see template below)

- [ ] **6d.** CHANGELOG v0.8.0 entry template
  ```markdown
  ## [0.8.0] - 2025-11-XX
  
  ### 🦅 Major Changes - Rebranding to Osprey Framework
  
  **Breaking Changes:**
  - Package renamed: `alpha-berkeley-framework` → `osprey-framework`
  - Import paths: `from osprey.*` → `from osprey.*`
  - CLI command: `framework` → `osprey`
  - Repository: `thellert/alpha_berkeley` → `als-apg/osprey`
  
  ### Migration Guide
  1. Uninstall old package: `pip uninstall alpha-berkeley-framework`
  2. Install new package: `pip install osprey-framework`
  3. Update imports: Find/replace `from osprey.` → `from osprey.`
  4. Update CLI commands: Replace `framework` with `osprey` in scripts
  
  GitHub automatically redirects old repository URLs.
  
  ### Includes All Features from v0.7.7
  - Interactive TUI menu system
  - Multi-project support
  - Enhanced documentation
  - All bug fixes from v0.7.7
  ```

---

## 📋 PHASE 6: Verification Steps

### ✅ Task 7: Verify All Changes

- [ ] **7a.** Search for remaining "framework" references
  ```bash
  # Should find ONLY:
  # - Generic use of word "framework" (not package name)
  # - Historical CHANGELOG entries (keep those)
  # - Documentation explaining the framework concept
  grep -ri "from framework\." . --exclude-dir=venv --exclude-dir=.git --exclude-dir=dist
  # Should return: NO RESULTS
  ```

- [ ] **7b.** Search for remaining "alpha-berkeley" references
  ```bash
  grep -ri "alpha-berkeley" . --exclude-dir=venv --exclude-dir=.git --exclude-dir=dist
  # Should find ONLY:
  # - Historical CHANGELOG entries
  # - Migration documentation
  # - Optional: legacy CLI entry points (if kept)
  ```

- [ ] **7c.** Verify critical files manually
  - [ ] pyproject.toml: All 10+ changes applied?
  - [ ] src/osprey/__init__.py: Updated?
  - [ ] README.md: All references updated?
  - [ ] CHANGELOG.md: New v0.8.0 entry added?
  - [ ] All template files: Check a few random ones

- [ ] **7d.** Check imports work
  ```bash
  # Quick syntax check
  python -c "import osprey; print(osprey.__version__)"
  # Should print: 0.8.0
  ```

- [ ] **7e.** ATOMIC COMMIT - Commit all changes together
  ```bash
  git add -A
  git status  # Review what's being committed
  git commit -m "refactor: rebrand from Alpha Berkeley Framework to Osprey Framework

BREAKING CHANGES:
- Package renamed: alpha-berkeley-framework → osprey-framework
- Import paths: from osprey.* → from osprey.*
- CLI command: framework → osprey
- Repository: thellert/alpha_berkeley → als-apg/osprey
- Version bumped to 0.8.0

This is an atomic commit that includes:
- Directory rename (src/framework → src/osprey)
- All import statement updates
- Configuration file updates (pyproject.toml)
- CLI entry point updates
- Template file updates
- Documentation updates
- Test file updates

Migration guide in CHANGELOG.md

Closes #[issue-number] (if applicable)"
  ```

---

## 📋 PHASE 8: Post-Commit Testing & Validation

### ✅ Task 10: Comprehensive Testing
- [ ] **10a.** Clean old build artifacts
  ```bash
  rm -rf dist/ build/ src/*.egg-info
  ```

- [ ] **10b.** Uninstall old package
  ```bash
  pip uninstall alpha-berkeley-framework -y
  ```

- [ ] **10c.** Install new package in dev mode
  ```bash
  pip install -e .
  ```

- [ ] **10d.** Test new CLI command exists
  ```bash
  which osprey
  osprey --help
  ```

- [ ] **10e.** Test all CLI commands
  ```bash
  osprey --version
  osprey health
  osprey deploy status
  # Don't run chat (interactive)
  ```

- [ ] **10f.** Run full test suite
  ```bash
  pytest -v
  # All tests should pass
  ```

- [ ] **10g.** Test template generation
  ```bash
  mkdir -p /tmp/test-osprey
  osprey init test-minimal --template minimal --output-dir /tmp/test-osprey
  osprey init test-weather --template hello_world_weather --output-dir /tmp/test-osprey
  ```

- [ ] **10h.** Verify generated project structure
  ```bash
  cd /tmp/test-osprey/test-minimal
  # Check imports in files
  grep -r "from osprey" .
  grep -r "import osprey" .
  # Should find osprey imports, not framework
  
  grep -r "from framework" .
  # Should find NOTHING
  ```

- [ ] **10i.** Build distribution
  ```bash
  cd /Users/thellert/LBL/ML/alpha_berkeley
  python -m build
  # Expected: 
  # - dist/osprey_framework-0.8.0-py3-none-any.whl
  # - dist/osprey_framework-0.8.0.tar.gz
  # Note: Build tools convert hyphens to underscores in filenames
  ```

- [ ] **10j.** Test wheel installation in clean environment
  ```bash
  python -m venv /tmp/osprey-test-venv
  source /tmp/osprey-test-venv/bin/activate
  pip install dist/osprey_framework-0.8.0-py3-none-any.whl
  osprey --help
  osprey health
  python -c "from osprey.state import AgentState; print('Import works!')"
  deactivate
  rm -rf /tmp/osprey-test-venv
  ```

---

## 📋 PHASE 9: Merge and Tag

### ✅ Task 11: Final Merge
- [ ] **11a.** Review all changes one final time
  ```bash
  git status
  git log --oneline rename-to-osprey ^main
  # Review commit history
  ```

- [ ] **11b.** Merge to main
  ```bash
  git checkout main
  git merge rename-to-osprey
  # Resolve any conflicts if they exist
  ```

- [ ] **11c.** Create version tag
  ```bash
  git tag -a v0.8.0 -m "Release: v0.8.0 - Rebranding to Osprey Framework

Major Changes:
- Renamed from Alpha Berkeley Framework to Osprey Framework
- Package: alpha-berkeley-framework → osprey-framework
- Imports: from osprey.* → from osprey.*
- CLI: framework → osprey
- Repository will move to als-apg/osprey

Breaking changes - see CHANGELOG.md for migration guide."
  ```

- [ ] **11d.** Push to GitHub (still thellert/alpha_berkeley)
  ```bash
  git push origin main
  git push origin v0.8.0
  # At this point: code says "osprey", repo still says "alpha_berkeley"
  # This is fine! The redirect will fix it in the next phase
  ```

---

## 📋 PHASE 10: Repository Migration (FINAL CRITICAL STEP)

### ✅ Task 12: Transfer and Rename on GitHub
- [ ] **12a.** Transfer repository to als-apg
  ```
  1. Go to: https://github.com/thellert/alpha_berkeley/settings
  2. Scroll to "Danger Zone"
  3. Click "Transfer repository"
  4. New owner: als-apg
  5. Type repository name to confirm
  6. Transfer
  
  Result: https://github.com/als-apg/alpha_berkeley
  ```

- [ ] **12b.** Verify first redirect works
  ```bash
  # Test redirect in browser
  # https://github.com/thellert/alpha_berkeley
  # Should redirect to: https://github.com/als-apg/alpha_berkeley
  
  # Test git redirect
  git ls-remote https://github.com/thellert/alpha_berkeley.git
  # Should work (redirects)
  ```

- [ ] **12c.** Rename repository to osprey
  ```
  1. Go to: https://github.com/als-apg/alpha_berkeley/settings
  2. Repository name field
  3. Change to: osprey
  4. Click "Rename"
  
  Result: https://github.com/als-apg/osprey
  ```

- [ ] **12d.** Verify complete redirect chain
  ```bash
  # In browser:
  # https://github.com/thellert/alpha_berkeley → https://github.com/als-apg/osprey ✓
  # https://github.com/als-apg/alpha_berkeley → https://github.com/als-apg/osprey ✓
  
  # Git operations:
  git ls-remote https://github.com/thellert/alpha_berkeley.git
  # Should work (redirects to als-apg/osprey)
  ```

- [ ] **12e.** Update your local git remote
  ```bash
  cd /Users/thellert/LBL/ML/alpha_berkeley
  git remote set-url origin https://github.com/als-apg/osprey.git
  git remote -v
  # Should show: als-apg/osprey
  
  git fetch
  git status
  # Verify everything still works
  ```

- [ ] **12f.** Configure GitHub Pages
  ```
  1. Go to: https://github.com/als-apg/osprey/settings/pages
  2. Source: gh-pages branch (or main/docs, depending on your setup)
  3. Save
  
  New docs URL: https://als-apg.github.io/osprey
  ```

---

## 📋 PHASE 11: PyPI and Cleanup

### ✅ Task 13: Publish and Update External Links
- [ ] **13a.** Publish to PyPI
  ```bash
  # Note: Distribution files use underscores, but PyPI project name is osprey-framework
  twine upload dist/osprey_framework-0.8.0*
  # Package will be available at: https://pypi.org/project/osprey-framework/
  # Install with: pip install osprey-framework
  ```

- [ ] **13b.** Update old PyPI package page
  ```
  1. Go to: https://pypi.org/project/alpha-berkeley-framework/
  2. Edit project description
  3. Add deprecation notice:
  
  "⚠️ DEPRECATED: This package has been renamed to osprey-framework
  
  Please install the new package:
  pip install osprey-framework
  
  Documentation: https://als-apg.github.io/osprey
  GitHub: https://github.com/als-apg/osprey"
  ```

- [ ] **13c.** Create placeholder repo at old location
  ```
  Prevents namespace squatting
  
  1. Create new repo: thellert/alpha_berkeley
  2. Add single README.md:
  
  # ⚠️ Repository Moved
  
  This repository has been moved to:
  **https://github.com/als-apg/osprey**
  
  The project has been renamed to "Osprey Framework".
  
  - 📦 PyPI: `pip install osprey-framework`
  - 📖 Docs: https://als-apg.github.io/osprey
  - 🐛 Issues: https://github.com/als-apg/osprey/issues
  
  GitHub automatically redirects git operations, but please
  update your links and remotes for long-term stability.
  ```

- [ ] **13d.** Update arXiv paper (if possible)
  - Update GitHub link in paper metadata
  - Add note about rename if allowed

- [ ] **13e.** Update external links
  - Social media profiles
  - Personal website
  - Email signatures
  - Presentations

- [ ] **13f.** Post announcement
  - GitHub Discussions in als-apg/osprey
  - Mailing lists (if any)
  - Social media
  - Example announcement:
  ```markdown
  🦅 Alpha Berkeley Framework is now Osprey Framework!
  
  We've rebranded and moved:
  - New package: `pip install osprey-framework`
  - New home: https://github.com/als-apg/osprey
  - New docs: https://als-apg.github.io/osprey
  
  GitHub automatically redirects old URLs, but please update
  your bookmarks and git remotes.
  
  See release notes for migration guide: [link to v0.8.0 release]
  ```

---

## 📋 PHASE 12: Final Verification

### ✅ Task 14: End-to-End Testing
- [ ] **14a.** Clean install in fresh environment
  ```bash
  python -m venv /tmp/final-test
  source /tmp/final-test/bin/activate
  pip install osprey-framework
  osprey --version  # Should show 0.8.0
  ```

- [ ] **14b.** Verify all CLI commands
  ```bash
  osprey --help
  osprey health
  osprey deploy status
  osprey export-config
  ```

- [ ] **14c.** Generate and test projects from templates
  ```bash
  mkdir /tmp/final-projects
  osprey init final-test-minimal --template minimal --output-dir /tmp/final-projects
  osprey init final-test-weather --template hello_world_weather --output-dir /tmp/final-projects
  
  cd /tmp/final-projects/final-test-minimal
  cat registry.py  # Check for correct imports
  cd ../final-test-weather
  cat capabilities/current_weather.py  # Check imports
  ```

- [ ] **14d.** Verify documentation site
  ```
  Visit: https://als-apg.github.io/osprey
  Check:
  - Site loads correctly
  - Navigation works
  - API reference shows osprey (not framework)
  - Install instructions show osprey-framework
  ```

- [ ] **14e.** Verify GitHub redirects
  ```bash
  # Test old URLs redirect:
  curl -I https://github.com/thellert/alpha_berkeley
  # Should see: 301 → als-apg/osprey
  
  git clone https://github.com/thellert/alpha_berkeley.git /tmp/test-redirect
  # Should work (redirects to als-apg/osprey)
  cd /tmp/test-redirect
  git remote -v
  # Will show old URL but operations redirect
  ```

---

## ✅ COMPLETION CHECKLIST

### Phase 1 (Do Now):
- [x] v0.7.7 released and working (tag created, code pushed, dist built)
- [ ] Published to PyPI
- [ ] Tested installation in clean environment
- [ ] 1-2 week stabilization period complete

### Phase 2 (Do Later):
- [ ] All code renamed from framework → osprey
- [ ] All tests passing
- [ ] Templates generate correct code
- [ ] Distribution builds successfully
- [ ] v0.8.0 tagged and merged to main

### Phase 3 (Final Step):
- [ ] Repository transferred to als-apg
- [ ] Repository renamed to osprey
- [ ] Redirects verified working
- [ ] PyPI package published
- [ ] Old package deprecated
- [ ] Documentation live
- [ ] Announcement posted

---

## 📞 SUPPORT / ROLLBACK

### If Something Goes Wrong:

**Before merge (during rename work):**
```bash
# Easy - just reset the branch
git checkout main
git branch -D rename-to-osprey
git checkout backup-before-rename
# Start over
```

**After merge but before repository move:**
```bash
# Revert the merge
git revert -m 1 HEAD
git push origin main
# Framework code restored
```

**After repository move:**
```bash
# Contact GitHub support to reverse transfer if needed
# Or: Just move forward, redirects handle most issues
```

---

## 🎯 SUCCESS CRITERIA

You'll know you're done when:
- [ ] `pip install osprey-framework` works (note: hyphen in package name)
- [ ] Package available at `https://pypi.org/project/osprey-framework/`
- [ ] `osprey --help` shows all commands
- [ ] `osprey init` generates working projects with osprey imports
- [ ] `from osprey.state import AgentState` works correctly
- [ ] https://github.com/als-apg/osprey is live
- [ ] https://als-apg.github.io/osprey shows documentation
- [ ] Old URLs redirect properly
- [ ] No references to "framework" package in new code
- [ ] All documentation shows `pip install osprey-framework` (with hyphen)

---

## 📝 QUICK REFERENCE: What's Done & What's Left

### ✅ COMPLETED (You did it!)
```
✅ git mv src/framework src/osprey
✅ from framework. → from osprey. (all 297 matches)
✅ "framework. → "osprey. (manual edits)
✅ get_logger("framework") → get_logger("osprey") (manual edits)
✅ alpha_berkeley_framework → osprey (egg-info)
✅ Alpha Berkeley Framework → Osprey Framework (most docs)
✅ CLI command updates in docs (manual edits)
✅ src/framework → src/osprey (Makefile, config.yml)
✅ 134/136 Python files
✅ 67/123 doc files
```

### ⚠️ REMAINING (Quick finish!)
**Critical (30 min):**
```
❌ pyproject.toml:
   Line 6:   name = "osprey-framework"
   Line 7:   version = "0.8.0"
   Line 150: all = ["osprey-framework[...]]"
   Line 154-159: URLs → als-apg/osprey
   Line 165: framework = "osprey.cli.main:cli"  → osprey = "osprey.cli.main:cli"
   Line 175: include = ["osprey*"]
   Line 180: "osprey" = [...package data...]
   Line 269: Remove "services/framework/*/tests"
   Line 306: known-first-party = ["osprey", ...]

❌ src/osprey/__init__.py:
   Line 8:   __version__ = "0.8.0"

❌ CHANGELOG.md:
   Add v0.8.0 entry at top (template in Phase 4)
```

**Templates (15 min):**
```
❌ src/osprey/templates/project/pyproject.toml.j2 (line ~20)
❌ src/osprey/templates/project/requirements.txt (line 1)
❌ src/osprey/templates/services/pipelines/start.sh (line ~20)
❌ src/osprey/templates/services/jupyter/custom_start.sh (line ~15)
```

**URLs (10 min):**
```
❌ docs/source/conf.py (GitHub URLs)
❌ src/osprey/cli/interactive_menu.py (repo URL)
❌ 4 doc files with old repo URLs
```

**Then:**
```
1. Run verification commands (Phase 6)
2. Atomic commit (Phase 7)
3. Test & build (Phase 8)
```

---

**Estimated Time:**
- Phase 1 (v0.7.7): Complete ✓
- Phase 2 (preparation): 30 minutes (branch setup, baseline tests)
- Phase 3 (IDE search/replace): 30-45 minutes (11 operations)
- Phase 4-6 (manual edits & verification): 1-2 hours
- Phase 7 (atomic commit): 5 minutes
- Phase 8 (testing): 30 minutes
- Phase 9 (merge & tag): 15 minutes
- Phase 10 (GitHub migration): 30 minutes
- Phase 11 (PyPI publish): 30 minutes
- Phase 12 (final verification): 30 minutes
- **Total for Phases 2-9: ~4-6 hours focused work**
- **Total including GitHub & PyPI: ~5-7 hours**

Good luck! 🦅

