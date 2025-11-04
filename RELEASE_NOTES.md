# Alpha Berkeley Framework - Latest Release (v0.7.8)

🚀 **User Experience Release** - Interactive Terminal UI and Multi-Project Support

## What's New in v0.7.8

### 🐛 Bug Fixes
- Fixed config system test failure due to incorrect global variable references
- Enhanced `get_config_value()` to support both processed and raw config paths
- Improved template documentation clarity (example vs. valid categories)

---

## What's New in v0.7.7

### 🎨 Interactive Terminal UI (TUI)

The framework now features a comprehensive interactive menu system that launches when you run `framework` with no arguments. This dramatically improves the user experience while maintaining full backward compatibility with direct CLI commands.

#### **Context-Aware Main Menu**
- **Smart Context Detection**: Automatically detects if you're in a project directory or not
- **Adaptive Interface**: Shows different menu options based on your context
- **Beautiful Rich Formatting**: Professional-looking terminal interface with colors and styling
- **Seamless Integration**: Smoothly transitions between menu and direct commands

```bash
# Launch interactive menu
framework

# Or continue using direct commands
framework init my-project
framework chat
framework deploy up
```

#### **Interactive Project Initialization**
Replace this:
```bash
framework init my-weather --template hello_world_weather
# Then manually edit .env file with API keys
```

With this guided experience:
- **Template Selection**: Visual list of available templates with descriptions
- **Provider Selection**: Choose from OpenAI, Anthropic, Google, Ollama, CBORG
  - Each provider shows a user-friendly description (e.g., "Anthropic (Claude models)")
- **Model Selection**: Pick the default model for your project
- **Automatic API Key Detection**: Reads API keys from your shell environment
- **Secure Key Input**: Password-style input for API keys not found in environment
- **Smart Defaults**: Pre-fills common values based on detected environment

#### **Enhanced Provider Display**
All provider adapters now include user-friendly descriptions:
- `anthropic` → "Anthropic (Claude models)"
- `openai` → "OpenAI (GPT models)"
- `google` → "Google (Gemini models)"
- `ollama` → "Ollama (local models)"
- `cborg` → "LBNL CBorg proxy (supports multiple models)"

### 🏗️ Multi-Project Support

Work seamlessly across multiple framework projects without manual configuration switching.

#### **Project Path Resolution**
Three ways to specify which project to work with:

1. **Current Directory** (default): Run commands from within your project
```bash
cd my-weather-agent
framework chat
```

2. **`--project` Flag**: Specify project path explicitly
```bash
framework chat --project ~/my-weather-agent
framework deploy up --project /path/to/my-turbine
```

3. **Environment Variable**: Set once, use everywhere
```bash
export FRAMEWORK_PROJECT=~/my-weather-agent
framework chat
framework deploy status
```

#### **Explicit Configuration Support**
- **Config Path Parameter**: All config functions now accept optional `config_path` parameter
- **Per-Path Caching**: Efficient config caching for multiple projects
- **Registry Path Resolution**: Registry paths resolved relative to config file location
- **No Cross-Project Contamination**: Each project maintains its own isolated configuration

```python
from osprey.utils.config import get_model_config

# Use specific config file
config = get_model_config(config_path="/path/to/project/config.yml")
```

#### **All CLI Commands Enhanced**
Every CLI command now supports the `--project` flag:
- `framework init --project <path>`
- `framework chat --project <path>`
- `framework deploy up --project <path>`
- `framework health --project <path>`
- `framework export-config --project <path>`

### 🎯 Enhanced User Experience

#### **Container Status Display**
The `framework deploy status` command now shows beautiful formatted tables:
- **Rich Tables**: Clear visual hierarchy with colors
- **Status Indicators**: Colored emoji indicators (● Running / ● Stopped)
- **Health Information**: Shows container health status when available
- **Port Mapping**: Clear display of host→container port mappings
- **Helpful Guidance**: Next-step suggestions when no services running

#### **Environment Variable Auto-Detection**
Project initialization now automatically detects and fills environment variables:
- Reads `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc. from your shell
- Shows which variables were detected during `framework init`
- Pre-fills `.env.example` template with actual values
- Falls back to placeholder values if not found
- Secure password-style input for missing keys in TUI

#### **Better Defaults**
- **Default Model**: Changed from `gemini-2.0-flash-exp` to `claude-3-5-haiku-latest`
  - Better performance and reliability out of the box
  - Lower latency for common tasks
- **Cleaner Templates**: Optional docker-compose settings now commented out by default
  - Simpler initial configuration
  - Easy to enable when needed

### 🔧 Technical Improvements

#### **Data Source Logging**
Enhanced data source manager with better status tracking:
```
Data sources checked: 3 (1 with data, 1 empty, 1 failed)
```
- Distinguishes between empty vs. failed sources
- Better UX for understanding data availability
- Clearer debugging information

#### **Configuration System Enhancements**
- Explicit `config_path` parameter throughout config system
- Per-path config caching for efficiency
- Better isolation between projects
- `set_as_default` parameter for explicit path handling
- Maintains backward compatibility with singleton pattern

#### **Provider Integration**
- Added `description` field to `BaseProvider` class
- All provider adapters updated with user-friendly descriptions
- Better TUI menu integration
- Improved provider discoverability

### 📦 New Files

- **`interactive_menu.py`** (1,771 lines) - Complete TUI implementation
  - Context-aware menus
  - Interactive init flow
  - Environment variable detection
  - API key configuration
  
- **`project_utils.py`** (90 lines) - Unified project path resolution
  - `--project` flag support
  - `FRAMEWORK_PROJECT` env var handling
  - Path validation and resolution

### ✨ Benefits Summary

1. **Lower Barrier to Entry**: New users can get started with guided interactive menus
2. **Faster Workflows**: Common tasks now take seconds with TUI
3. **Better Discoverability**: Browse features and options interactively
4. **Multi-Project Ready**: Switch between projects seamlessly
5. **Power User Friendly**: All direct CLI commands still work unchanged
6. **Professional UX**: Rich formatting and beautiful interfaces throughout
7. **Smart Defaults**: Auto-detection of API keys and environment variables
8. **Zero Breaking Changes**: Complete backward compatibility maintained

## Migration Notes

**No breaking changes.** This release is fully backward compatible.

### New Users
Simply run `framework` to see the new interactive menu!

### Existing Users
Continue using direct CLI commands as before, or try the new interactive menu:
```bash
framework  # Launch TUI
```

### Multi-Project Users
Use the new `--project` flag or `FRAMEWORK_PROJECT` environment variable to work with multiple projects efficiently.

## Upgrade Instructions

```bash
pip install --upgrade alpha-berkeley-framework
```

Or with specific extras:

```bash
pip install --upgrade "alpha-berkeley-framework[memory,docs]"
```

---

**Full Changelog**: See [CHANGELOG.md](CHANGELOG.md) for detailed commit history
