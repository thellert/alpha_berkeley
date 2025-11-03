# Osprey Rename - Remaining Tasks

## 🎉 CURRENT STATUS - UPDATED 2025-11-03

**✅ PHASES 1-7 COMPLETED AND COMMITTED!**

**Commit:** `6a87935 - refactor: rebrand from Alpha Berkeley Framework to Osprey Framework`

**What's Done:**
- ✅ All code renamed: `src/framework/` → `src/osprey/`
- ✅ All imports updated: `from framework.*` → `from osprey.*`
- ✅ Package configuration: `pyproject.toml` updated
- ✅ Version: 0.8.0
- ✅ README.md: Updated with new branding, URLs, commands
- ✅ CHANGELOG.md: v0.8.0 entry with migration guide
- ✅ All 55 tests passing
- ✅ Package imports correctly: `import osprey; osprey.__version__ == '0.8.0'`
- ✅ Old `src/framework/` directory removed

**Current Branch:** `rename-to-osprey`
**Status:** Ready for testing, building, and deployment

---

## 📍 YOU ARE HERE: Phase 8-12 (Deployment Path)

**Next Steps (2-3 hours):**
1. Post-commit testing & validation (30 min)
2. Build distribution packages (15 min)
3. Merge to main & tag v0.8.0 (15 min)
4. GitHub repository migration (30 min)
5. PyPI publication (30 min)
6. Final verification (30 min)

---

## 📝 IMPORTANT: Package Naming Reference

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

## 📋 PHASE 8: Post-Commit Testing & Validation

**Goal:** Verify everything works before merging to main

### Task 8.1: Clean and Reinstall
```bash
# Clean old build artifacts
rm -rf dist/ build/ src/*.egg-info src/osprey_framework.egg-info

# Install package in dev mode
cd /Users/thellert/LBL/ML/alpha_berkeley
pip install -e .
```

**Expected:** Package installs without errors

### Task 8.2: Test CLI Commands
```bash
# Verify CLI is available
which osprey
osprey --version  # Should show: 0.8.0

# Test key commands (non-interactive)
osprey --help
osprey health
osprey deploy status
osprey export-config
```

**Expected:** All commands work without errors

### Task 8.3: Test Template Generation
```bash
# Generate test projects
mkdir -p /tmp/test-osprey-rename
cd /tmp/test-osprey-rename

osprey init test-minimal --template minimal
osprey init test-weather --template hello_world_weather

# Verify imports in generated code
cd test-minimal
grep -r "from osprey" .     # Should find osprey imports
grep -r "from framework" .  # Should find NOTHING

cd ../test-weather
grep -r "from osprey" .     # Should find osprey imports
grep -r "from framework" .  # Should find NOTHING
```

**Expected:** Templates generate with correct `osprey` imports

### Task 8.4: Run Full Test Suite
```bash
cd /Users/thellert/LBL/ML/alpha_berkeley
pytest -v
```

**Expected:** All 55 tests pass

### Task 8.5: Build Distribution Packages
```bash
cd /Users/thellert/LBL/ML/alpha_berkeley
python -m build
```

**Expected Output:**
```
dist/osprey_framework-0.8.0-py3-none-any.whl
dist/osprey_framework-0.8.0.tar.gz
```

**Note:** Underscore in filenames is correct (PyPI converts hyphens to underscores)

### Task 8.6: Test Wheel Installation (Optional but Recommended)
```bash
# Create clean test environment
python -m venv /tmp/osprey-wheel-test
source /tmp/osprey-wheel-test/bin/activate

# Install from wheel
pip install /Users/thellert/LBL/ML/alpha_berkeley/dist/osprey_framework-0.8.0-py3-none-any.whl

# Test it works
osprey --version  # Should show: 0.8.0
osprey --help
python -c "from osprey.state import AgentState; print('✓ Import works!')"

# Cleanup
deactivate
rm -rf /tmp/osprey-wheel-test
```

**Expected:** Package installs and works from wheel

---

## 📋 PHASE 9: Merge to Main & Tag

**Goal:** Get the rename onto main branch and create v0.8.0 tag

### Task 9.1: Review Changes
```bash
cd /Users/thellert/LBL/ML/alpha_berkeley
git status  # Should be clean (or only have CLI styling changes uncommitted)
git log --oneline -1  # Should show the rename commit
```

### Task 9.2: Merge to Main
```bash
git checkout main
git merge rename-to-osprey

# If there are conflicts, resolve them
# Then: git commit
```

**Expected:** Clean merge (or minimal conflicts)

### Task 9.3: Create Version Tag
```bash
git tag -a v0.8.0 -m "Release: v0.8.0 - Rebranding to Osprey Framework

Major Changes:
- Renamed from Alpha Berkeley Framework to Osprey Framework
- Package: alpha-berkeley-framework → osprey-framework
- Imports: from framework.* → from osprey.*
- CLI: framework → osprey
- Repository will move to als-apg/osprey

Breaking changes - see CHANGELOG.md for migration guide."
```

### Task 9.4: Push to GitHub
```bash
git push origin main
git push origin v0.8.0
```

**At this point:**
- ✅ Code says "osprey" everywhere
- ✅ Version is 0.8.0
- ⚠️ Repository URL still says "thellert/alpha_berkeley"
- **This is FINE!** Package name is independent of repository URL

---

## 📋 PHASE 10: GitHub Repository Migration

**Goal:** Move repository to als-apg/osprey with automatic redirects

### 🔄 Understanding GitHub Redirects

**How It Works:**
GitHub automatically creates **permanent redirects** when you transfer or rename a repository.

**The Process:**
```
Current:     github.com/thellert/alpha_berkeley
After Transfer: github.com/als-apg/alpha_berkeley  (redirect: thellert → als-apg)
After Rename:   github.com/als-apg/osprey         (redirect: alpha_berkeley → osprey)
```

**Result: Chain of redirects**
```
thellert/alpha_berkeley → als-apg/alpha_berkeley → als-apg/osprey
```

**What This Means:**
- ✅ All old URLs automatically redirect to new location
- ✅ Git operations transparently follow redirects
- ✅ Old links in documentation continue to work
- ✅ No breaking changes for existing clones/forks
- ✅ Redirects are permanent (maintained by GitHub indefinitely)

**Testing After Migration:**
```bash
# All of these will work and redirect to als-apg/osprey:
git clone https://github.com/thellert/alpha_berkeley.git
git clone https://github.com/als-apg/alpha_berkeley.git
git clone https://github.com/als-apg/osprey.git

# Browser redirects:
https://github.com/thellert/alpha_berkeley  → https://github.com/als-apg/osprey ✓
https://github.com/als-apg/alpha_berkeley   → https://github.com/als-apg/osprey ✓
```

### Task 10.1: Transfer Repository to als-apg
```
1. Go to: https://github.com/thellert/alpha_berkeley/settings
2. Scroll to "Danger Zone"
3. Click "Transfer repository"
4. New owner: als-apg
5. Type repository name to confirm: alpha_berkeley
6. Click "I understand, transfer this repository"

Result: https://github.com/als-apg/alpha_berkeley
```

**What Happens:**
- Repository moves to als-apg organization
- GitHub creates redirect: `thellert/alpha_berkeley` → `als-apg/alpha_berkeley`
- All git operations to old URL automatically redirect

### Task 10.2: Verify First Redirect
```bash
# Test in browser
# Visit: https://github.com/thellert/alpha_berkeley
# Should redirect to: https://github.com/als-apg/alpha_berkeley

# Test git operations
git ls-remote https://github.com/thellert/alpha_berkeley.git
# Should work (redirects automatically)
```

### Task 10.3: Rename Repository to "osprey"
```
1. Go to: https://github.com/als-apg/alpha_berkeley/settings
2. Under "Repository name"
3. Change to: osprey
4. Click "Rename"

Result: https://github.com/als-apg/osprey
```

**What Happens:**
- Repository renamed to "osprey"
- GitHub creates redirect: `als-apg/alpha_berkeley` → `als-apg/osprey`
- Both redirects now chain together

### Task 10.4: Verify Complete Redirect Chain
```bash
# Test in browser - ALL should redirect to als-apg/osprey:
# 1. https://github.com/thellert/alpha_berkeley
# 2. https://github.com/als-apg/alpha_berkeley
# 3. https://github.com/als-apg/osprey (final destination)

# Test git operations with OLD URL still works:
git ls-remote https://github.com/thellert/alpha_berkeley.git
# Should work (follows redirect chain)
```

### Task 10.5: Update Your Local Remote
```bash
cd /Users/thellert/LBL/ML/alpha_berkeley
git remote set-url origin https://github.com/als-apg/osprey.git
git remote -v
# Should show: origin  https://github.com/als-apg/osprey.git

# Verify it works
git fetch
git status
```

### Task 10.6: Configure GitHub Pages (if applicable)
```
1. Go to: https://github.com/als-apg/osprey/settings/pages
2. Source: Select your docs branch/folder
3. Save

New docs URL: https://als-apg.github.io/osprey
```

**Note:** Old docs URL may redirect after DNS propagation (24-48 hours)

---

## 📋 PHASE 11: PyPI Publication Strategy

**Goal:** Publish osprey-framework to PyPI

### 🎯 Understanding PyPI vs GitHub

**Key Insight:** PyPI package name and GitHub repository name are **completely independent**.

```python
# pyproject.toml
name = "osprey-framework"  # ← PyPI package name

# GitHub
Repository: https://github.com/als-apg/osprey  # ← Can be different!

# In Python code
from osprey.state import AgentState  # ← Also different!
```

**Example from ecosystem:**
- Package: `scikit-learn` (PyPI)
- Import: `import sklearn` (Python)
- Repo: `github.com/scikit-learn/scikit-learn` (GitHub)

### PyPI Current Status Check

**Before proceeding, determine:**
1. Does `alpha-berkeley-framework` exist on PyPI?
2. Does `osprey-framework` exist on PyPI?

```bash
# Check manually at:
# https://pypi.org/project/alpha-berkeley-framework/
# https://pypi.org/project/osprey-framework/
```

### Strategy A: Fresh Start (No Old Package on PyPI)

**If `alpha-berkeley-framework` was never published:**

```bash
# Simply publish the new package
cd /Users/thellert/LBL/ML/alpha_berkeley
twine upload dist/osprey_framework-0.8.0*
```

**Result:**
- ✅ `pip install osprey-framework` works
- ✅ Clean start, no legacy confusion
- ✅ Package available at: `https://pypi.org/project/osprey-framework/`

**Advantages:**
- Simplest approach
- No maintenance of two packages
- No user confusion

### Strategy B: Migration (Old Package Exists on PyPI)

**If `alpha-berkeley-framework` is already published:**

#### Step 1: Publish New Package
```bash
cd /Users/thellert/LBL/ML/alpha_berkeley
python -m build  # Already done in Phase 8
twine upload dist/osprey_framework-0.8.0*
```

**Result:** New package at `https://pypi.org/project/osprey-framework/`

#### Step 2: Deprecate Old Package (Choose ONE approach)

**Option B1: Tombstone Release (Recommended for smooth migration)**

Create a final release of `alpha-berkeley-framework` that automatically installs `osprey-framework`:

```python
# In alpha-berkeley-framework's setup:
setup(
    name="alpha-berkeley-framework",
    version="0.8.0",
    install_requires=[
        "osprey-framework>=0.8.0",
    ],
    description="DEPRECATED: Renamed to osprey-framework. Installing this package will install osprey-framework instead.",
)
```

**What happens:**
```bash
pip install alpha-berkeley-framework
# Automatically installs osprey-framework!
```

**Pros:**
- Users with old name automatically get new package
- Smooth migration path
- Old imports still break (intentional - forces code update)

**Cons:**
- Maintains both package names
- Small maintenance overhead

---

**Option B2: Update Description Only (Simpler)**

Just update the old package's PyPI page description:

```markdown
⚠️ **DEPRECATED - Package Renamed**

This package has been renamed to **osprey-framework**.

**New Installation:**
```bash
pip install osprey-framework
```

**Migration Guide:**
https://als-apg.github.io/osprey/getting-started/migration-guide.html

**Repository:**
https://github.com/als-apg/osprey

No further updates will be published to this package.
```

**Pros:**
- Simple, one-time update
- Old version still available for legacy users
- Clear warning to new users

**Cons:**
- Users on auto-update won't get new package automatically

---

**Option B3: Do Nothing**

Just publish new package and let old one stay as-is.

**When to use:**
- Old package has very few users
- Most users install from GitHub anyway
- Want to minimize effort

---

### Task 11.1: Publish to PyPI

**Prerequisites:**
- [ ] PyPI account credentials configured
- [ ] `twine` installed: `pip install twine`
- [ ] Distribution files exist: `dist/osprey_framework-0.8.0*`

```bash
cd /Users/thellert/LBL/ML/alpha_berkeley

# Upload to PyPI
twine upload dist/osprey_framework-0.8.0*

# Or upload to TestPyPI first (recommended):
twine upload --repository testpypi dist/osprey_framework-0.8.0*
```

**Expected Output:**
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading osprey_framework-0.8.0-py3-none-any.whl
Uploading osprey_framework-0.8.0.tar.gz
View at: https://pypi.org/project/osprey-framework/0.8.0/
```

### Task 11.2: Verify PyPI Publication
```bash
# Test installation from PyPI
pip install --index-url https://test.pypi.org/simple/ osprey-framework  # If using TestPyPI
# OR
pip install osprey-framework  # If using production PyPI

# Verify it works
osprey --version
python -c "from osprey.state import AgentState; print('✓ Works!')"
```

### Task 11.3: Handle Old Package (If Applicable)

Based on your chosen strategy (B1, B2, or B3), implement the deprecation approach.

---

## 📋 PHASE 12: Final Verification

**Goal:** Confirm everything works end-to-end

### Task 12.1: Clean Installation Test
```bash
# Create fresh environment
python -m venv /tmp/final-osprey-test
source /tmp/final-osprey-test/bin/activate

# Install from PyPI
pip install osprey-framework

# Test everything
osprey --version  # Should show: 0.8.0
osprey --help
osprey health

# Test imports
python -c "
from osprey.state import AgentState
from osprey.base import Capability
from osprey.models import ModelFactory
print('✓ All imports work!')
"

# Cleanup
deactivate
rm -rf /tmp/final-osprey-test
```

### Task 12.2: Test Template Generation from PyPI Install
```bash
# In the test environment
source /tmp/final-osprey-test/bin/activate
mkdir /tmp/osprey-pypi-templates
cd /tmp/osprey-pypi-templates

# Generate from templates
osprey init pypi-minimal --template minimal
osprey init pypi-weather --template hello_world_weather

# Verify correct imports
cd pypi-minimal
grep -r "from osprey" .
grep -r "from framework" .  # Should find nothing

deactivate
```

### Task 12.3: Verify GitHub Redirects
```bash
# Test old URL redirects
curl -I https://github.com/thellert/alpha_berkeley
# Should show: HTTP 301 → als-apg/osprey

# Test clone still works with old URL
git clone https://github.com/thellert/alpha_berkeley.git /tmp/redirect-test
cd /tmp/redirect-test
git remote -v
# Will show old URL, but operations redirect
rm -rf /tmp/redirect-test
```

### Task 12.4: Verify Documentation
```
Visit: https://als-apg.github.io/osprey

Check:
- [ ] Site loads correctly
- [ ] Navigation works
- [ ] API reference shows "osprey" (not "framework")
- [ ] Install instructions show `pip install osprey-framework`
- [ ] Migration guide is accessible
```

### Task 12.5: Update External Links
```
Update references in:
- [ ] Social media profiles
- [ ] Personal website
- [ ] Email signatures
- [ ] Presentations
- [ ] arXiv paper (if possible)
- [ ] Any external documentation
```

---

## ✅ COMPLETION CHECKLIST

### Phase 8: Testing & Build
- [ ] Clean build artifacts removed
- [ ] Package installed in dev mode
- [ ] CLI commands work
- [ ] Templates generate correctly
- [ ] All tests pass
- [ ] Distribution built successfully
- [ ] Wheel tested in clean environment

### Phase 9: Merge & Tag
- [ ] Merged to main branch
- [ ] v0.8.0 tag created
- [ ] Pushed to GitHub

### Phase 10: GitHub Migration
- [ ] Repository transferred to als-apg
- [ ] Repository renamed to "osprey"
- [ ] Redirects verified working
- [ ] Local remote updated
- [ ] GitHub Pages configured

### Phase 11: PyPI
- [ ] Package published to PyPI
- [ ] Installation from PyPI tested
- [ ] Old package handled (if applicable)

### Phase 12: Final Verification
- [ ] Clean installation works
- [ ] Templates generate correctly from PyPI
- [ ] GitHub redirects working
- [ ] Documentation live and correct
- [ ] External links updated

---

## 🎯 SUCCESS CRITERIA

You'll know you're done when:
- ✅ `pip install osprey-framework` works
- ✅ Package available at `https://pypi.org/project/osprey-framework/`
- ✅ `osprey --help` shows all commands
- ✅ `osprey init` generates working projects with osprey imports
- ✅ `from osprey.state import AgentState` works correctly
- ✅ `https://github.com/als-apg/osprey` is live
- ✅ `https://als-apg.github.io/osprey` shows documentation
- ✅ Old URLs (thellert/alpha_berkeley) redirect properly
- ✅ All tests passing
- ✅ No references to "framework" package in new code

---

## 📞 ROLLBACK PROCEDURES

### If Something Goes Wrong in Phase 8-9:
```bash
# On rename-to-osprey branch
git reset --hard HEAD~1  # Undo commit
# Or switch branches:
git checkout main
git branch -D rename-to-osprey
```

### If Something Goes Wrong After Phase 10 (GitHub Migration):
- **GitHub redirects are permanent** - they continue to work
- Worst case: Contact GitHub support to reverse transfer
- Best: Move forward, fix issues in new location

### If Something Goes Wrong with PyPI:
- **Cannot delete PyPI releases** (only yank them)
- Yanking hides package from searches but doesn't break existing installs
- Best: Publish a new patch version with fixes (0.8.1)

---

## 📊 Estimated Timeline

- **Phase 8** (Testing & Build): 30-45 minutes
- **Phase 9** (Merge & Tag): 15 minutes
- **Phase 10** (GitHub Migration): 30 minutes
- **Phase 11** (PyPI Publication): 30 minutes
- **Phase 12** (Final Verification): 30 minutes

**Total:** ~2-3 hours

---

## 🦅 You've Got This!

The hard part is done! All the code is renamed and tested. What's left is:
1. Standard deployment procedures (build, merge, tag)
2. GitHub repository housekeeping (transfer, rename)
3. PyPI publication (standard Python packaging)

GitHub's redirect system ensures no breaking changes for repository access.
The version bump (0.8.0) and CHANGELOG clearly signal the breaking changes in import paths.

Good luck! 🚀
