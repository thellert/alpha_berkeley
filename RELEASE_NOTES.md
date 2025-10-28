# Alpha Berkeley Framework - Latest Release (v0.7.5)

🚀 **Performance Enhancement Release** - Parallel capability classification with configurable concurrency control.

## What's New in v0.7.5

### ⚡ Parallel Capability Classification

#### **Performance Improvements**
- **Parallel Processing**: Multiple capabilities now classified simultaneously using `asyncio.gather()`
- **Semaphore Control**: Configurable concurrency limits prevent API flooding while maintaining performance
- **New Configuration**: `max_concurrent_classifications: 5` setting balances speed vs. API rate limits

#### **Architecture Enhancements**
- **New `CapabilityClassifier` Class**: Encapsulates individual capability classification with proper resource management
- **Enhanced Error Handling**: Robust handling of import errors and classification failures
- **Improved Reclassification Logic**: New `_detect_reclassification_scenario()` function with better state management

#### **Configuration & Control**
- **New Setting**: `execution_control.limits.max_concurrent_classifications` (default: 5)
- **Cleaner State Management**: Proper error state cleanup during reclassification
- **Better Logging**: Enhanced visibility into parallel classification process

### 📚 Documentation Updates

#### **Comprehensive Documentation**
- Updated classification guides with parallel processing examples
- Added `CapabilityClassifier` class documentation and API references
- Enhanced configuration documentation with new concurrency settings
- Updated all configuration examples across developer guides

#### **Build System Improvements**
- Fixed documentation build system for pip-installable framework
- Added `docs/config.yml` for build compatibility
- Updated installation guide with docs extras option
- Fixed various documentation formatting and cross-reference issues

## Benefits

- **Faster Classification**: Multiple capabilities processed simultaneously
- **Resource Control**: Semaphore prevents API rate limiting
- **Robust Error Handling**: Individual failures don't stop the entire process
- **Scalable Architecture**: Handles large capability registries efficiently
- **Configurable Performance**: Balance speed vs. API limits based on your needs

## Migration Notes

No breaking changes. The new parallel classification system is backward compatible and enabled by default with sensible concurrency limits.

To customize concurrency:

```yaml
# config.yml
execution_control:
  limits:
    max_concurrent_classifications: 10  # Increase for faster classification
```

---

## Previous Release (v0.7.4)

🐛 **Bug Fix Release** - Fixed template generation issues affecting registry class names and import paths.

### 🔧 Template Bug Fixes

#### **Registry Class Name Generation**
- **Fixed duplicate "RegistryProvider" suffix** in generated registry class names
- Previously generated: `WeatherTutorialRegistryProviderRegistryProvider` ❌
- Now generates: `WeatherTutorialRegistryProvider` ✅
- Affects all three app templates: hello_world_weather, wind_turbine, minimal
- Projects generated with v0.7.3 may need manual class name correction

#### **Import Path Documentation**
- **Updated template documentation** to use correct v0.7.0 import patterns
- Changed from `applications.hello_world_weather.*` to `hello_world_weather.*`
- Updated examples in mock_weather_api.py and capabilities/__init__.py
- Ensures generated projects follow correct decoupled architecture

#### **Requirements Template Rendering**
- **Fixed framework version substitution** in generated requirements.txt
- Moved requirements.txt from static files to rendered templates
- Now properly replaces `{{ framework_version }}` placeholder with actual version
- Ensures generated projects pin correct framework version in requirements.txt

### 🔧 Technical Details

**Files Changed:**
- `src/framework/cli/templates.py` - Fixed class name generation logic
- `src/framework/templates/project/hello_world_weather/src/hello_world_weather/mock_weather_api.py` - Updated import examples
- `src/framework/templates/project/hello_world_weather/src/hello_world_weather/capabilities/__init__.py` - Updated documentation
- `src/framework/templates/project/requirements.txt` → `requirements.txt.j2` - Made template renderable

**Verification:**
```bash
# Test class name generation
framework init test-project --template hello_world_weather
# Should generate: TestProjectRegistryProvider (not TestProjectRegistryProviderRegistryProvider)

# Test requirements.txt generation
cat test-project/requirements.txt
# Should show: alpha-berkeley-framework==0.7.4 (not {{ framework_version }})
```

### 🚨 Action Required for v0.7.3 Users

If you generated a project with v0.7.3, you may need to manually fix the registry class name:

1. **Check your registry file** (e.g., `src/my_app/registry.py`)
2. **Look for duplicate suffix** in class name (e.g., `MyAppRegistryProviderRegistryProvider`)
3. **Rename to correct format** (e.g., `MyAppRegistryProvider`)
4. **Update any imports** that reference the old class name

### 📊 Impact Assessment

- **Low Risk**: Changes only affect newly generated projects
- **Existing Projects**: Continue working without modification
- **Template Users**: Benefit from cleaner generated code
- **Documentation**: More accurate examples and import patterns

---

## Installation

```bash
pip install alpha-berkeley-framework==0.7.5

# Or with extras
pip install alpha-berkeley-framework[scientific]==0.7.5
pip install alpha-berkeley-framework[all]==0.7.5
```

## Quick Start

```bash
# Create a new project with parallel classification
framework init my-agent --template hello_world_weather
cd my-agent

# The new parallel classification system is enabled by default
# Customize concurrency in config.yml if needed
```

For complete installation and setup instructions, see our [Getting Started Guide](https://thellert.github.io/alpha_berkeley/getting-started/).