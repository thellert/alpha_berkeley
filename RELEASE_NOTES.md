# Alpha Berkeley Framework - Latest Release (v0.7.6)

🚀 **Architecture Enhancement Release** - Provider Registry System with extensible AI provider management.

## What's New in v0.7.6

### 🏗️ Provider Registry System

#### **Centralized Provider Management**
- **Registry Integration**: AI providers now managed through the same registry system as capabilities, services, and other components
- **Single Source of Truth**: All provider logic centralized in provider adapter classes
- **Lazy Loading**: Providers loaded on-demand with proper dependency management
- **Extensibility**: Applications can register custom providers (Azure OpenAI, institutional AI services, etc.)

#### **Provider Adapter Architecture**
- **New `BaseProvider` Abstract Class**: Defines consistent interface for all AI providers
- **Five Framework Providers**: Anthropic, OpenAI, Google, Ollama, CBORG adapters implemented
- **Provider Metadata**: Simple class attributes define requirements (API key, base URL, proxy support)
- **Health Check System**: Each provider implements connectivity testing with charge-aware logic

#### **Simplified Registration**
- **Minimal Registration**: Just `module_path` and `class_name` required
- **Metadata Introspection**: Registry reads provider metadata from class attributes
- **60% Less Code**: Provider registration reduced from 8-9 lines to 2 lines per provider
- **No Duplication**: Single source of truth eliminates metadata duplication

#### **Code Reduction & Maintainability**
- **~860 Lines Removed**: Eliminated provider-specific logic from factory.py, completion.py, health_cmd.py
- **~290 Lines Saved**: Factory module reduced from 472 to 206 lines (-56%)
- **~298 Lines Saved**: Completion module streamlined significantly
- **~290 Lines Saved**: Health check module simplified
- **Single Implementation**: Both PydanticAI models and direct completions use same adapter code

### 🔧 Critical Features Preserved

All existing functionality maintained:
- ✅ **HTTP Proxy Support**: `HTTP_PROXY` environment variable for enterprise deployments
- ✅ **Ollama Fallback Logic**: Automatic localhost ↔ host.containers.internal switching
- ✅ **Timeout Configuration**: Per-provider and per-request timeouts
- ✅ **Environment Variables**: `${VAR_NAME}` resolution in config files
- ✅ **Extended Thinking**: Anthropic and Google thinking modes fully supported
- ✅ **TypedDict Support**: Automatic conversion to Pydantic models
- ✅ **Charge-Aware Health Checks**: Format validation for paid APIs (Anthropic, Google)

### 🎯 Developer Experience Improvements

#### **Custom Provider Registration**
Applications can now register custom AI providers:

```python
from framework.registry import ProviderRegistration
from framework.models.providers.base import BaseProvider

# Define provider adapter
class AzureOpenAIProviderAdapter(BaseProvider):
    name = "azure_openai"
    requires_api_key = True
    requires_base_url = True
    # ... implementation ...

# Register in application registry
return extend_framework_registry(
    providers=[
        ProviderRegistration(
            module_path="my_app.providers.azure",
            class_name="AzureOpenAIProviderAdapter"
        )
    ]
)
```

Common use cases:
- Azure OpenAI enterprise deployments
- Institutional AI services (Stanford AI Playground, national lab endpoints)
- Commercial providers (Cohere, Mistral AI, Together AI)
- Self-hosted models with OpenAI-compatible APIs

#### **Provider Discovery**
```python
from framework.registry import get_registry

registry = get_registry()
providers = registry.list_providers()  # ['anthropic', 'openai', 'google', 'ollama', 'cborg']
provider = registry.get_provider('anthropic')  # Get provider class
```

### 🧪 Testing Infrastructure

#### **pytest Configuration**
- New `pytest.ini` with test markers (unit, integration, requires_api, etc.)
- Organized test categorization for better test management
- VCR cassette markers for recorded API interactions

#### **VCR Test Support**
- `tests/cassettes/` infrastructure for recording/replaying API interactions
- Cost-effective integration testing without repeated API charges
- Deterministic tests with recorded responses
- Comprehensive README documenting VCR usage and security

### 🛠️ Utilities & Infrastructure

#### **Log Filtering System**
- New `framework.utils.log_filter` module for dynamic log control
- `LoggerFilter` class for selective suppression by logger name, level, or pattern
- Context managers: `suppress_logger()`, `suppress_logger_level()`, `quiet_logger()`
- Used in health checks to suppress verbose registry initialization logs

#### **Memory Storage Improvements**
- Switched from root logger to framework logger for consistency
- Reduced log verbosity (INFO → DEBUG for initialization messages)
- Better integration with framework logging patterns

### 📚 Documentation Updates

#### **Provider Registry Documentation**
- New `ProviderRegistration` documentation in registry API reference
- Custom provider registration guide with Azure OpenAI example
- Updated component initialization order to include providers
- Provider access methods documented on `RegistryManager`

#### **Configuration Documentation**
- Updated provider extensibility information
- Direct link to custom provider registration guide
- GitHub issue creation guidance for community providers

### 🧹 Code Cleanup

#### **Removed Deprecated Code**
- Deleted `src/framework/interfaces/openwebui/` (deprecated interface)
- Removed `docs/ressources/other/EXECUTION_POLICY_SYSTEM.md` (outdated doc)
- Cleaned up unused provider logic from multiple files

#### **Test Updates**
- Fixed config import paths (moved from `configs.config` to `framework.utils.config`)
- Added minimal config.yml in tests to prevent config loading errors
- Updated integration tests for new architecture

## Benefits Summary

1. **Maintainability**: Single source of truth for provider logic
2. **Extensibility**: Applications can register custom providers easily
3. **Consistency**: Same adapter used by factory.py and completion.py
4. **Type Safety**: Strong typing throughout provider system
5. **Discoverability**: `registry.list_providers()` shows available providers
6. **Clean Architecture**: Clear separation between provider interface and implementation
7. **Reduced Code**: ~860 lines removed, ~1,090 lines of well-structured adapter code added
8. **Zero Breaking Changes**: All existing APIs work identically
9. **Better Testing**: VCR infrastructure for integration tests
10. **Enhanced Health Checks**: Provider-specific health validation through registry

## Technical Details

### Component Architecture
```
Registry System
├── ProviderRegistration (minimal metadata: module_path, class_name)
├── Provider Adapters (metadata as class attributes)
│   ├── BaseProvider (abstract interface)
│   ├── AnthropicProviderAdapter
│   ├── OpenAIProviderAdapter
│   ├── GoogleProviderAdapter
│   ├── OllamaProviderAdapter
│   └── CBorgProviderAdapter
└── RegistryManager (lazy loading, metadata introspection)
```

### Initialization Order
1. Context classes
2. Data sources
3. **Providers** (new in v0.7.6)
4. Core nodes
5. Services
6. Capabilities
7. Framework prompt providers

### Provider Interface
Each provider implements:
- `create_model()` - PydanticAI model creation
- `execute_completion()` - Direct API calls
- `check_health()` - Connectivity validation

## Migration Notes

**No breaking changes.** The provider registry is a backward-compatible internal refactoring. All existing code using `get_model()` and `get_chat_completion()` continues to work without modifications.

### For Advanced Users

If you need custom AI providers, you can now register them through the registry system. See documentation for complete examples.

### Configuration Changes

No configuration changes required. All existing `config.yml` provider configurations remain valid.

## Files Changed

- 12 atomic commits implementing provider registry system
- 3 documentation files updated
- 6 version files updated for v0.7.6 release

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
