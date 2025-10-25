# Provider Registry Implementation Plan - UPDATED

## Executive Summary

Integrate AI provider management into the existing framework registry system. This creates a single source of truth for all provider operations while allowing applications to register custom providers, maintaining consistency with the framework's established architecture.

## Key Architectural Decision

**INTEGRATE with existing `framework.registry` system** rather than creating a parallel provider registry. This ensures:
- Consistency with existing component registration patterns
- Applications can register custom providers through their `RegistryConfigProvider`
- Single unified system for all framework extensibility
- Follows established lazy-loading and dependency management patterns

## Implementation Decisions (From Review)

1. **Naming Convention**: Use `*ProviderAdapter` suffix for provider classes to avoid conflicts with PydanticAI classes
   - `AnthropicProviderAdapter`, `GoogleProviderAdapter`, `OpenAIProviderAdapter`, etc.

2. **Provider Naming**: Use ONLY "google" - eliminate "gemini" alias (Google's official recommendation)

3. **Interface Design**: Simple class attributes approach for provider metadata

4. **Scope**: Centralize ALL provider logic - refactor both `factory.py` AND `completion.py` to use registry

5. **Configuration**: `config.yml` is source of truth - providers are stateless, receive config as parameters

6. **Health Checks**: Preserve charge-avoiding logic (format validation only for Anthropic/Google)

## Current State Analysis

### Existing Provider Logic Locations

1. **`factory.py` (lines 384-472)**
   - Provider requirements dict (lines 385-391)
   - Validation logic (lines 393-406)
   - Model creation logic (lines 430-472)
   - Proxy configuration (lines 410-427)
   - Ollama fallback logic (lines 134-273)

2. **`completion.py` (lines 411-627)**
   - Provider-specific completion handlers
   - Anthropic (lines 411-443)
   - Google (lines 444-464)
   - OpenAI (lines 465-504)
   - Ollama (lines 505-595)
   - CBORG (lines 596-627)

3. **`health_cmd.py` (lines 521-717)**
   - Provider connectivity tests
   - Different test strategies per provider
   - Some test endpoints, some only validate format

### Supported Providers

| Provider   | Requires API Key | Requires Base URL | Supports Proxy | Default Base URL |
|------------|-----------------|-------------------|----------------|------------------|
| anthropic  | Yes             | No                | Yes            | (default)        |
| google     | Yes             | No                | Yes            | (default)        |
| openai     | Yes             | No                | Yes            | api.openai.com   |
| ollama     | No              | Yes               | No             | (user-defined)   |
| cborg      | Yes             | Yes               | Yes            | (user-defined)   |

**Note**: "gemini" is no longer supported - use "google" as the official provider name per Google's recommendation.

### Critical Features to Preserve

1. **Proxy Support**: HTTP_PROXY environment variable for enterprise use
2. **Ollama Fallback**: Automatic localhost ↔ host.containers.internal switching
3. **Timeout Configuration**: Per-provider and per-request timeouts
4. **Environment Variable Resolution**: ${VAR_NAME} in config files
5. **Shared HTTP Client**: Connection pooling for performance
6. **TypedDict Support**: Conversion to Pydantic models
7. **Extended Thinking**: Anthropic and Google thinking modes
8. **Error Messages**: Clear, actionable error messages

## Registry Integration Architecture

### New Registry Components

Following the existing registry pattern, we'll add:

1. **`ProviderRegistration`** dataclass in `registry/base.py`:
   ```python
   @dataclass
   class ProviderRegistration:
       """Registration metadata for AI model providers."""
       name: str                    # Provider identifier (e.g., "anthropic")
       module_path: str             # Module for lazy loading
       class_name: str              # Provider class name
       requires_api_key: bool       # Whether API key is required
       requires_base_url: bool      # Whether base URL is required
       requires_model_id: bool      # Whether model ID is required
       supports_proxy: bool         # Whether HTTP proxy is supported
       default_base_url: Optional[str] = None  # Default API endpoint
   ```

2. **Provider Adapter classes** in `models/providers/`:
   ```
   models/providers/
   ├── __init__.py           # Provider registry and base classes
   ├── base.py               # BaseProvider abstract class
   ├── anthropic.py          # AnthropicProviderAdapter implementation
   ├── openai.py             # OpenAIProviderAdapter implementation
   ├── google.py             # GoogleProviderAdapter implementation
   ├── ollama.py             # OllamaProviderAdapter implementation
   └── cborg.py              # CBorgProviderAdapter implementation
   ```
   
   **Naming Note**: Use `*ProviderAdapter` suffix to avoid conflicts with PydanticAI's provider classes.

3. **Registry Manager Updates**:
   - Add `_providers: Dict[str, Type[BaseProvider]]` storage
   - Add `get_provider(name: str) -> Type[BaseProvider]` method
   - Add provider initialization to `_initialize_components()`

### Provider Class Interface

```python
from abc import ABC, abstractmethod
from typing import Optional, Any, Union
import httpx

class BaseProvider(ABC):
    """Base class for all AI model provider adapters.
    
    Provider adapters are stateless - they receive all configuration
    as method parameters. The source of truth for provider configuration
    is config.yml.
    
    Subclasses must define class-level metadata attributes that describe
    the provider's requirements.
    """
    
    # Metadata - subclasses must override these class attributes
    name: str = NotImplemented  # Provider identifier (e.g., "anthropic")
    requires_api_key: bool = NotImplemented
    requires_base_url: bool = NotImplemented
    requires_model_id: bool = NotImplemented
    supports_proxy: bool = NotImplemented
    default_base_url: Optional[str] = None
    
    @abstractmethod
    def create_model(
        self,
        model_id: str,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: Optional[float],
        http_client: Optional[httpx.AsyncClient]
    ) -> Any:
        """Create a model instance for PydanticAI.
        
        :param model_id: Model identifier for this provider
        :param api_key: API authentication key
        :param base_url: Custom API endpoint URL
        :param timeout: Request timeout in seconds
        :param http_client: Pre-configured HTTP client (caller owns lifecycle)
        :return: Configured model instance
        
        Note: If http_client is provided, the CALLER is responsible for
        closing it. Providers should not close or manage client lifecycle.
        """
        pass
    
    @abstractmethod
    def execute_completion(
        self,
        message: str,
        model_id: str,
        api_key: Optional[str],
        base_url: Optional[str],
        max_tokens: int = 1024,
        temperature: float = 0.0,
        thinking: Optional[dict] = None,
        system_prompt: Optional[str] = None,
        output_format: Optional[Any] = None,
        **kwargs
    ) -> Union[str, Any]:
        """Execute a direct chat completion (non-PydanticAI).
        
        :param message: User message to send
        :param model_id: Model identifier
        :param api_key: API authentication key
        :param base_url: Custom API endpoint URL
        :param max_tokens: Maximum tokens to generate
        :param temperature: Sampling temperature
        :param thinking: Extended thinking configuration (if supported)
        :param system_prompt: System prompt (if supported)
        :param output_format: Structured output format (Pydantic model or TypedDict)
        :param kwargs: Additional provider-specific arguments
        :return: Model response text or structured output
        """
        pass
    
    @abstractmethod
    def check_health(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: float = 5.0
    ) -> tuple[bool, str]:
        """Test provider connectivity and authentication.
        
        Important: For providers that charge for API calls (Anthropic, Google),
        this should do FORMAT VALIDATION ONLY to avoid incurring charges.
        For free endpoints (OpenAI /v1/models, Ollama), actual connectivity
        testing is acceptable.
        
        :param api_key: API authentication key
        :param base_url: Custom API endpoint URL
        :param timeout: Request timeout in seconds
        :return: (success, message) tuple
        """
        pass
```

### Example: Application-Specific Provider

Applications can register custom providers through their existing registry:

```python
# In applications/myapp/registry.py
from framework.registry import RegistryConfigProvider, RegistryConfig, ProviderRegistration

class MyAppRegistryProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[...],
            context_classes=[...],
            
            # NEW: Register custom provider
            providers=[
                ProviderRegistration(
                    name="azure_openai",
                    module_path="applications.myapp.providers.azure",
                    class_name="AzureOpenAIProvider",
                    requires_api_key=True,
                    requires_base_url=True,
                    requires_model_id=True,
                    supports_proxy=True,
                    default_base_url=None  # User must provide
                )
            ]
        )
```

## Implementation Plan

### Phase 1: Add Provider Support to Registry System (Foundation)

**Objective**: Extend registry system to support provider registration, zero impact on existing code.

#### Step 1.1: Add ProviderRegistration to base.py

Update `src/framework/registry/base.py`:

```python
@dataclass
class ProviderRegistration:
    """Registration metadata for AI model providers.
    
    Defines the metadata required for lazy loading of provider classes that
    implement AI model access across different API providers.
    
    :param name: Unique provider identifier (e.g., 'anthropic', 'openai')
    :type name: str
    :param module_path: Python module path for lazy import
    :type module_path: str
    :param class_name: Provider class name within the module
    :type class_name: str
    :param requires_api_key: Whether provider requires API key for authentication
    :type requires_api_key: bool
    :param requires_base_url: Whether provider requires custom base URL
    :type requires_base_url: bool
    :param requires_model_id: Whether provider requires model ID specification
    :type requires_model_id: bool
    :param supports_proxy: Whether provider supports HTTP proxy configuration
    :type supports_proxy: bool
    :param default_base_url: Default API endpoint URL if applicable
    :type default_base_url: str, optional
    """
    name: str
    module_path: str
    class_name: str
    requires_api_key: bool
    requires_base_url: bool
    requires_model_id: bool
    supports_proxy: bool
    default_base_url: Optional[str] = None
```

#### Step 1.2: Update RegistryConfig

Add providers field to `RegistryConfig` in `base.py`:

```python
@dataclass
class RegistryConfig:
    """Complete registry configuration with all component metadata."""
    
    # Existing fields...
    capabilities: List[CapabilityRegistration]
    context_classes: List[ContextClassRegistration]
    core_nodes: List[NodeRegistration] = field(default_factory=list)
    data_sources: List[DataSourceRegistration] = field(default_factory=list)
    services: List[ServiceRegistration] = field(default_factory=list)
    
    # NEW: Provider registrations
    providers: List[ProviderRegistration] = field(default_factory=list)
    
    # Update initialization order to include providers
    initialization_order: List[str] = field(default_factory=lambda: [
        "context_classes",
        "data_sources",
        "domain_analyzers",
        "execution_policy_analyzers",
        "providers",           # NEW: Initialize providers early
        "capabilities",
        "framework_prompt_providers",
        "core_nodes",
        "services"
    ])
```

#### Step 1.3: Update Registry Manager

Add provider support to `src/framework/registry/manager.py`:

```python
class RegistryManager:
    """Centralized registry for all framework components."""
    
    def __init__(self):
        # Existing storage...
        self._capabilities: Dict[str, 'BaseCapability'] = {}
        self._context_classes: Dict[str, Type] = {}
        self._data_sources: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        
        # NEW: Provider storage
        self._providers: Dict[str, Type['BaseProvider']] = {}
        self._provider_registrations: Dict[str, ProviderRegistration] = {}
    
    def get_provider(self, name: str) -> Optional[Type['BaseProvider']]:
        """Retrieve registered provider class by name.
        
        :param name: Unique provider name from registration
        :type name: str
        :return: Provider class if registered, None otherwise
        :rtype: Type[BaseProvider] or None
        """
        if not self._initialized:
            raise RegistryError("Registry not initialized. Call initialize_registry() first.")
        
        return self._providers.get(name)
    
    def get_provider_registration(self, name: str) -> Optional[ProviderRegistration]:
        """Get provider registration metadata.
        
        :param name: Provider name
        :type name: str
        :return: Provider registration if found, None otherwise
        :rtype: ProviderRegistration or None
        """
        return self._provider_registrations.get(name)
    
    def list_providers(self) -> List[str]:
        """Get list of all registered provider names.
        
        :return: List of provider names
        :rtype: list[str]
        """
        return list(self._providers.keys())
```

#### Step 1.4: Add Provider Initialization

Add provider initialization logic to `manager.py`:

```python
def _initialize_providers(self, config: RegistryConfig):
    """Initialize providers from registry configuration.
    
    :param config: Registry configuration with provider registrations
    :type config: RegistryConfig
    """
    logger.info(f"Initializing {len(config.providers)} provider(s)...")
    
    for registration in config.providers:
        try:
            # Store registration metadata
            self._provider_registrations[registration.name] = registration
            
            # Lazy load provider class
            module = importlib.import_module(registration.module_path)
            provider_class = getattr(module, registration.class_name)
            
            # Validate it's a provider
            from framework.models.providers.base import BaseProvider
            if not issubclass(provider_class, BaseProvider):
                raise RegistryError(
                    f"Provider {registration.name} class {registration.class_name} "
                    f"must inherit from BaseProvider"
                )
            
            # Store provider class
            self._providers[registration.name] = provider_class
            
            logger.info(f"  ✓ Registered provider: {registration.name}")
            
        except Exception as e:
            logger.error(f"  ✗ Failed to register provider {registration.name}: {e}")
            raise RegistryError(f"Provider registration failed for {registration.name}") from e
    
    logger.info(f"Provider initialization complete: {len(self._providers)} providers loaded")
```

Update `_initialize_components()` to call provider initialization:

```python
def _initialize_components(self, config: RegistryConfig):
    """Initialize all components in dependency order."""
    
    for component_type in config.initialization_order:
        if component_type == "context_classes":
            self._initialize_context_classes(config)
        elif component_type == "data_sources":
            self._initialize_data_sources(config)
        # NEW: Provider initialization
        elif component_type == "providers":
            self._initialize_providers(config)
        elif component_type == "capabilities":
            self._initialize_capabilities(config)
        # ... rest of initialization ...
```

**Files Modified**:
- `src/framework/registry/base.py` (add ProviderRegistration, update RegistryConfig)
- `src/framework/registry/manager.py` (add provider storage and methods)
- `src/framework/registry/__init__.py` (export ProviderRegistration)

**Testing Checkpoint**: Verify registry can be initialized with empty provider list

### Phase 2: Create Provider Base Class and Implementations

**Objective**: Create provider implementations following the BaseProvider interface.

#### Step 2.1: Create Provider Base Class

Create `src/framework/models/providers/base.py`:

```python
"""Base Provider Interface for AI Model Access."""

from abc import ABC, abstractmethod
from typing import Optional, Any, Union
import httpx
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel


class BaseProvider(ABC):
    """Abstract base class for AI model providers.
    
    All provider implementations must inherit from this class and implement
    the three core methods: create_model, execute_completion, and check_health.
    
    This interface ensures consistent provider behavior across the framework
    while allowing provider-specific implementations.
    """
    
    # Provider metadata (set by subclass)
    name: str
    requires_api_key: bool
    requires_base_url: bool
    requires_model_id: bool
    supports_proxy: bool
    default_base_url: Optional[str] = None
    
    @abstractmethod
    def create_model(
        self,
        model_id: str,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: Optional[float],
        http_client: Optional[httpx.AsyncClient]
    ) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
        """Create a model instance for PydanticAI.
        
        :param model_id: Model identifier for this provider
        :param api_key: API authentication key
        :param base_url: Custom API endpoint URL
        :param timeout: Request timeout in seconds
        :param http_client: Pre-configured HTTP client with proxy/timeout
        :return: Configured model instance
        """
        pass
    
    @abstractmethod
    def execute_completion(
        self,
        message: str,
        model_id: str,
        api_key: Optional[str],
        base_url: Optional[str],
        **kwargs
    ) -> str:
        """Execute a chat completion.
        
        :param message: User message to send
        :param model_id: Model identifier
        :param api_key: API authentication key
        :param base_url: Custom API endpoint URL
        :param kwargs: Additional provider-specific arguments
        :return: Model response text
        """
        pass
    
    @abstractmethod
    def check_health(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: float = 5.0
    ) -> tuple[bool, str]:
        """Test provider connectivity and authentication.
        
        :param api_key: API authentication key
        :param base_url: Custom API endpoint URL
        :param timeout: Request timeout in seconds
        :return: (success, message) tuple
        """
        pass
```

#### Step 2.2: Create Provider Implementations

Create `src/framework/models/providers/anthropic.py`:

```python
"""Anthropic Provider Adapter Implementation."""

from typing import Optional, Any
import httpx
import anthropic
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider as PydanticAnthropicProvider

from .base import BaseProvider


class AnthropicProviderAdapter(BaseProvider):
    """Anthropic AI provider implementation."""
    
    name = "anthropic"
    requires_api_key = True
    requires_base_url = False
    requires_model_id = True
    supports_proxy = True
    default_base_url = None
    
    def create_model(
        self,
        model_id: str,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: Optional[float],
        http_client: Optional[httpx.AsyncClient]
    ) -> AnthropicModel:
        """Create Anthropic model instance for PydanticAI."""
        provider = PydanticAnthropicProvider(
            api_key=api_key,
            http_client=http_client
        )
        return AnthropicModel(
            model_name=model_id,
            provider=provider
        )
    
    def execute_completion(
        self,
        message: str,
        model_id: str,
        api_key: Optional[str],
        base_url: Optional[str],
        max_tokens: int = 1024,
        temperature: float = 0.0,
        thinking: Optional[dict] = None,
        **kwargs
    ) -> Union[str, list]:
        """Execute Anthropic chat completion with extended thinking support."""
        client = anthropic.Anthropic(api_key=api_key)
        
        request_params = {
            "model": model_id,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add extended thinking if enabled
        enable_thinking = kwargs.get("enable_thinking", False)
        budget_tokens = kwargs.get("budget_tokens")
        
        if enable_thinking and budget_tokens is not None:
            if budget_tokens >= max_tokens:
                raise ValueError("budget_tokens must be less than max_tokens")
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": budget_tokens
            }
        
        response = client.messages.create(**request_params)
        
        if enable_thinking and "thinking" in request_params:
            return response.content  # Returns List[ContentBlock]
        else:
            # Concatenate text from all TextBlock instances
            text_parts = [
                block.text for block in response.content 
                if isinstance(block, anthropic.types.TextBlock)
            ]
            return "\n".join(text_parts)
    
    def check_health(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: float = 5.0
    ) -> tuple[bool, str]:
        """Check Anthropic API health (format validation only to avoid charges).
        
        Note: This does NOT make actual API calls to avoid incurring charges.
        It only validates the API key format.
        """
        if not api_key:
            return False, "API key not set"
        
        if not api_key.startswith("sk-ant-"):
            return False, "API key format unusual (expected 'sk-ant-...')"
        
        # Success - key format is valid
        # We don't test connectivity to avoid API charges
        return True, "API key format valid (connectivity not tested to avoid charges)"
```

Similar implementations for:
- `openai.py` (OpenAIProviderAdapter - tests /v1/models endpoint)
- `google.py` (GoogleProviderAdapter - format validation only, supports extended thinking)
- `ollama.py` (OllamaProviderAdapter - includes fallback logic, tests connectivity)
- `cborg.py` (CBorgProviderAdapter - tests /v1/models endpoint)

**Health Check Strategy**:
- **Anthropic**: Format validation only (avoid charges)
- **Google**: Format validation only (avoid charges)
- **OpenAI**: Test /v1/models endpoint (free, fast)
- **Ollama**: Test connectivity (free, local)
- **CBORG**: Test /v1/models endpoint (if available)

#### Step 2.3: Register Framework Providers

Update `src/framework/registry/registry.py` to include providers:

```python
class FrameworkRegistryProvider(RegistryConfigProvider):
    """Framework registry provider."""
    
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            # Existing registrations...
            core_nodes=[...],
            capabilities=[...],
            context_classes=[...],
            data_sources=[...],
            services=[...],
            
            # NEW: Framework providers (using *ProviderAdapter naming)
            providers=[
                ProviderRegistration(
                    name="anthropic",
                    module_path="framework.models.providers.anthropic",
                    class_name="AnthropicProviderAdapter",
                    requires_api_key=True,
                    requires_base_url=False,
                    requires_model_id=True,
                    supports_proxy=True,
                    default_base_url=None
                ),
                ProviderRegistration(
                    name="openai",
                    module_path="framework.models.providers.openai",
                    class_name="OpenAIProviderAdapter",
                    requires_api_key=True,
                    requires_base_url=False,
                    requires_model_id=True,
                    supports_proxy=True,
                    default_base_url="https://api.openai.com/v1"
                ),
                ProviderRegistration(
                    name="google",
                    module_path="framework.models.providers.google",
                    class_name="GoogleProviderAdapter",
                    requires_api_key=True,
                    requires_base_url=False,
                    requires_model_id=True,
                    supports_proxy=True,
                    default_base_url=None
                ),
                # NOTE: "gemini" is no longer supported - use "google" instead
                ProviderRegistration(
                    name="ollama",
                    module_path="framework.models.providers.ollama",
                    class_name="OllamaProviderAdapter",
                    requires_api_key=False,
                    requires_base_url=True,
                    requires_model_id=True,
                    supports_proxy=False,
                    default_base_url=None
                ),
                ProviderRegistration(
                    name="cborg",
                    module_path="framework.models.providers.cborg",
                    class_name="CBorgProviderAdapter",
                    requires_api_key=True,
                    requires_base_url=True,
                    requires_model_id=True,
                    supports_proxy=True,
                    default_base_url=None
                ),
            ],
            
            # ... rest of config ...
        )
```

**Files Created**:
- `src/framework/models/providers/__init__.py`
- `src/framework/models/providers/base.py`
- `src/framework/models/providers/anthropic.py` (AnthropicProviderAdapter)
- `src/framework/models/providers/openai.py` (OpenAIProviderAdapter)
- `src/framework/models/providers/google.py` (GoogleProviderAdapter)
- `src/framework/models/providers/ollama.py` (OllamaProviderAdapter)
- `src/framework/models/providers/cborg.py` (CBorgProviderAdapter)

**Files Modified**:
- `src/framework/registry/registry.py` (add provider registrations)

**Testing Checkpoint**:
```bash
python -c "from framework.registry import initialize_registry, get_registry; \
    initialize_registry(); \
    r = get_registry(); \
    print('Providers:', r.list_providers()); \
    p = r.get_provider('anthropic'); \
    print('Anthropic:', p)"
```

### Phase 3: Update Health Check to Use Registry

**Objective**: Simplify health_cmd.py to use provider registry.

#### Step 3.1: Update check_api_providers()

Update `src/framework/cli/health_cmd.py`:

```python
def check_api_providers(self):
    """Check API provider configurations and connectivity."""
    console.print("\n[bold]API Providers[/bold]")
    
    try:
        config_path = self.cwd / "config.yml"
        if not config_path.exists():
            return
        
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Get providers used in models
        used_providers = self._get_used_providers(config)
        
        if not used_providers:
            console.print("  [yellow]⚠️  No providers used in models[/yellow]")
            return
        
        console.print(f"  [dim]Testing {len(used_providers)} provider(s) used in current config...[/dim]\n")
        
        api_config = config.get("api", {}).get("providers", {})
        
        for provider_name in sorted(used_providers):
            if provider_name not in api_config:
                self.add_result(
                    f"provider_{provider_name}",
                    "error",
                    f"{provider_name}: Not configured in api.providers"
                )
                console.print(f"  [red]❌ {provider_name}: Not configured[/red]")
                continue
            
            provider_config = api_config[provider_name]
            self._check_provider(provider_name, provider_config)
    
    except Exception as e:
        if self.verbose:
            console.print(f"  [dim]Could not check API providers: {e}[/dim]")

def _get_used_providers(self, config: Dict) -> set:
    """Extract unique providers actually used in models section."""
    models = config.get("models", {})
    used_providers = set()
    
    for model_config in models.values():
        if isinstance(model_config, dict):
            provider = model_config.get("provider")
            if provider:
                used_providers.add(provider)
    
    return used_providers

def _check_provider(self, provider_name: str, provider_config: Dict):
    """Check a specific API provider using the provider registry."""
    from framework.registry import get_registry
    
    registry = get_registry()
    provider_class = registry.get_provider(provider_name)
    
    if not provider_class:
        self.add_result(
            f"provider_{provider_name}",
            "warning",
            f"{provider_name}: Unknown provider (not in registry)"
        )
        console.print(f"  [yellow]⚠️  {provider_name}: Unknown provider[/yellow]")
        return
    
    # Resolve API key from environment
    api_key = self._resolve_api_key(provider_config.get("api_key", ""))
    base_url = provider_config.get("base_url")
    
    # Instantiate provider and check health
    provider = provider_class()
    success, message = provider.check_health(api_key, base_url, timeout=5.0)
    
    if success:
        self.add_result(
            f"provider_{provider_name}",
            "ok",
            f"{provider_name}: {message}"
        )
        console.print(f"  [green]✅ {provider_name}: {message}[/green]")
    else:
        self.add_result(
            f"provider_{provider_name}",
            "warning",
            f"{provider_name}: {message}"
        )
        console.print(f"  [yellow]⚠️  {provider_name}: {message}[/yellow]")

def _resolve_api_key(self, api_key: str) -> str:
    """Resolve API key if it's an environment variable reference."""
    if api_key.startswith("${") and api_key.endswith("}"):
        var_name = api_key[2:-1]
        return os.environ.get(var_name, "")
    return api_key
```

#### Step 3.2: Remove Old Health Check Code

Delete old provider-specific code from `health_cmd.py`:
- Lines 543-600: Old `_check_provider()` logic
- Lines 602-717: Old `_test_provider_connectivity()` method

**Files Modified**:
- `src/framework/cli/health_cmd.py`

**Testing Checkpoint**:
```bash
framework health
framework health --full
```

### Phase 4: Update get_model() to Use Registry

**Objective**: Simplify factory.py to use provider registry.

#### Step 4.1: Update get_model()

Update `src/framework/models/factory.py`:

```python
def get_model(
    provider: Optional[str] = None,
    model_config: Optional[dict] = None,
    model_id: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    max_tokens: int = 100000,
) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
    """Create a configured LLM model instance."""
    
    # Load config
    if model_config:
        provider = model_config.get("provider", provider)
        model_id = model_config.get("model_id", model_id)
        max_tokens = model_config.get("max_tokens", max_tokens)
        timeout = model_config.get("timeout", timeout)
    
    if not provider:
        raise ValueError("Provider must be specified")
    
    # Get provider from registry
    from framework.registry import get_registry
    registry = get_registry()
    provider_class = registry.get_provider(provider)
    
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider}. Use registry.list_providers() to see available providers.")
    
    # Get provider config
    provider_config = get_provider_config(provider)
    api_key = provider_config.get("api_key", api_key)
    base_url = provider_config.get("base_url", base_url)
    timeout = provider_config.get("timeout", timeout)
    
    # Get provider registration for metadata
    registration = registry.get_provider_registration(provider)
    
    # Validate requirements
    if registration.requires_api_key and not api_key:
        raise ValueError(f"API key required for {provider}")
    if registration.requires_base_url and not base_url:
        raise ValueError(f"Base URL required for {provider}")
    if registration.requires_model_id and not model_id:
        raise ValueError(f"Model ID required for {provider}")
    
    # Setup HTTP client (proxy + timeout)
    http_client = None
    if registration.supports_proxy:
        proxy_url = os.getenv("HTTP_PROXY")
        if proxy_url and _validate_proxy_url(proxy_url):
            http_client = httpx.AsyncClient(proxy=proxy_url, timeout=timeout)
        elif timeout:
            http_client = httpx.AsyncClient(timeout=timeout)
    
    # Create model using provider
    provider_instance = provider_class()
    return provider_instance.create_model(
        model_id=model_id,
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        http_client=http_client
    )
```

#### Step 4.2: Remove Old Provider Logic

Delete from `factory.py`:
- Lines 385-406: Old provider_requirements dict and validation
- Lines 429-472: Old provider-specific if/elif blocks

Keep helper functions:
- `_validate_proxy_url()` - Still needed
- `_test_ollama_connection()` - Used by OllamaProvider
- `_get_ollama_fallback_urls()` - Used by OllamaProvider

**Files Modified**:
- `src/framework/models/factory.py`

**Testing Checkpoint**: Test all model creation scenarios

### Phase 5: Update get_chat_completion() to Use Registry

**Objective**: Centralize ALL provider logic by migrating completion.py to use provider registry.

**Rationale**: The goal is to have a single source of truth for provider logic. Both `factory.py` (PydanticAI models) and `completion.py` (direct API calls) should use the same provider adapters. This reduces maintenance burden and ensures consistency.

#### Step 5.1: Update get_chat_completion()

Update `src/framework/models/completion.py`:

```python
def get_chat_completion(
    message: str,
    provider: Optional[str] = None,
    model_id: Optional[str] = None,
    model_config: Optional[dict] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    thinking: Optional[dict] = None,
    system_prompt: Optional[str] = None,
    output_format: Optional[Union[Type[BaseModel], type]] = None,
) -> Union[str, BaseModel, dict]:
    """Get a chat completion from an LLM provider."""
    
    # Load config
    if model_config:
        provider = model_config.get("provider", provider)
        model_id = model_config.get("model_id", model_id)
    
    if not provider:
        raise ValueError("Provider must be specified")
    
    # Get provider from registry
    from framework.registry import get_registry
    registry = get_registry()
    provider_class = registry.get_provider(provider)
    
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider}")
    
    # Get provider config
    provider_config = get_provider_config(provider)
    api_key = provider_config.get("api_key", api_key)
    base_url = provider_config.get("base_url", base_url)
    
    # Execute completion using provider adapter
    provider_instance = provider_class()
    
    # Build kwargs for provider
    completion_kwargs = {
        "enable_thinking": enable_thinking,
        "budget_tokens": budget_tokens,
        "system_prompt": system_prompt,
        "output_format": output_model,  # Note: uses converted Pydantic model
    }
    
    result = provider_instance.execute_completion(
        message=message,
        model_id=model_id,
        api_key=api_key,
        base_url=base_url,
        max_tokens=max_tokens,
        temperature=temperature,
        **completion_kwargs
    )
    
    # Handle output conversion for TypedDict
    return _handle_output_conversion(result, is_typed_dict_output)
```

#### Step 5.2: Remove Old Completion Logic

Delete from `completion.py`:
- Lines 370-392: Old provider requirements dict and validation (now in registry)
- Lines 410-627: Old provider-specific if/elif blocks (now in provider adapters)

Keep helper functions:
- `_is_typed_dict()` - Type checking utility
- `_convert_typed_dict_to_pydantic()` - Type conversion
- `_handle_output_conversion()` - Result processing
- `_validate_proxy_url()` - Still needed for HTTP client setup
- `_get_ollama_fallback_urls()` - Move to OllamaProviderAdapter class

**Files Modified**:
- `src/framework/models/completion.py`

**Testing Checkpoint**: Test all completion scenarios including:
- Simple text completions
- Structured outputs (Pydantic and TypedDict)
- Extended thinking (Anthropic and Google)
- All provider types

### Phase 6: Documentation and Testing

#### Step 6.1: Update Module Exports

Update `src/framework/models/__init__.py`:

```python
from .factory import get_model
from .completion import get_chat_completion
from .providers.base import BaseProvider

__all__ = [
    'get_model',
    'get_chat_completion',
    'BaseProvider',
]
```

Update `src/framework/registry/__init__.py`:

```python
from .base import (
    # ... existing exports ...
    ProviderRegistration,  # NEW
)

__all__ = [
    # ... existing exports ...
    'ProviderRegistration',
]
```

#### Step 6.2: Example: Application Custom Provider

Document how applications register custom providers:

```python
# applications/myapp/providers/azure.py
from framework.models.providers.base import BaseProvider

class AzureOpenAIProvider(BaseProvider):
    """Azure OpenAI provider."""
    
    name = "azure_openai"
    requires_api_key = True
    requires_base_url = True
    requires_model_id = True
    supports_proxy = True
    
    def create_model(self, ...):
        # Azure-specific logic
        pass
    
    def execute_completion(self, ...):
        # Azure-specific logic
        pass
    
    def check_health(self, ...):
        # Azure-specific logic
        pass
```

```python
# applications/myapp/registry.py
from framework.registry import RegistryConfigProvider, ProviderRegistration

class MyAppRegistryProvider(RegistryConfigProvider):
    def get_registry_config(self):
        return RegistryConfig(
            capabilities=[...],
            
            # Register custom provider
            providers=[
                ProviderRegistration(
                    name="azure_openai",
                    module_path="applications.myapp.providers.azure",
                    class_name="AzureOpenAIProvider",
                    requires_api_key=True,
                    requires_base_url=True,
                    requires_model_id=True,
                    supports_proxy=True
                )
            ]
        )
```

#### Step 6.3: Testing

Create comprehensive tests as outlined in original plan, plus:

```python
# Test provider registry integration
def test_provider_registry():
    """Test provider registration and access."""
    from framework.registry import initialize_registry, get_registry
    
    initialize_registry()
    registry = get_registry()
    
    # Check framework providers are registered
    providers = registry.list_providers()
    assert "anthropic" in providers
    assert "openai" in providers
    assert "ollama" in providers
    
    # Check provider access
    anthropic = registry.get_provider("anthropic")
    assert anthropic is not None
    assert anthropic.name == "anthropic"
    assert anthropic.requires_api_key is True
```

## Migration Checklist

### Phase 1: Registry Foundation
- [ ] Add ProviderRegistration to base.py
- [ ] Update RegistryConfig with providers field
- [ ] Add provider storage to RegistryManager
- [ ] Add get_provider() and list_providers() methods
- [ ] Add _initialize_providers() method
- [ ] Update initialization order
- [ ] Export ProviderRegistration
- [ ] Test registry initialization

### Phase 2: Provider Implementations
- [ ] Create BaseProvider abstract class
- [ ] Implement AnthropicProvider
- [ ] Implement OpenAIProvider
- [ ] Implement GoogleProvider
- [ ] Implement OllamaProvider (with fallback logic)
- [ ] Implement CBorgProvider
- [ ] Register providers in FrameworkRegistryProvider
- [ ] Test provider loading from registry

### Phase 3: Health Check Migration
- [ ] Add _get_used_providers() method
- [ ] Update check_api_providers() to filter
- [ ] Update _check_provider() to use registry
- [ ] Add _resolve_api_key() helper
- [ ] Remove old health check code
- [ ] Test framework health command

### Phase 4: Model Factory Migration
- [ ] Update get_model() to use registry
- [ ] Remove old provider requirements dict
- [ ] Remove old provider creation logic
- [ ] Test model creation with all providers

### Phase 5: Completion Migration
- [ ] Update get_chat_completion() to use registry
- [ ] Remove old completion logic
- [ ] Test completions with all providers
- [ ] Test structured outputs

### Phase 6: Documentation & Testing
- [ ] Update module exports
- [ ] Document custom provider registration
- [ ] Create unit tests for providers
- [ ] Create integration tests
- [ ] Run regression tests
- [ ] Manual testing checklist
- [ ] Update CHANGELOG.md

## Benefits Summary

1. **Centralized Logic**: ALL provider logic in one place (both factory and completion use same adapters)
2. **Consistency**: Provider registration follows same pattern as capabilities, services, etc.
3. **Extensibility**: Applications can register custom providers (Azure, Cohere, etc.)
4. **Single Registry**: All framework extensibility in one system
5. **Type Safety**: Strong typing throughout
6. **Lazy Loading**: Providers loaded only when needed
7. **Discoverability**: `registry.list_providers()` shows what's available
8. **Testing**: Easy to test provider implementations independently
9. **Clean Architecture**: Separates provider interface from implementation
10. **Reduced Maintenance**: Single source of truth for provider requirements and behavior
11. **Config-Driven**: `config.yml` is source of truth, providers are stateless

## Timeline Estimate

- Phase 1: 3-4 hours (registry foundation)
- Phase 2: 6-8 hours (provider implementations)
- Phase 3: 2-3 hours (health check)
- Phase 4: 2-3 hours (factory)
- Phase 5: 2-3 hours (completion)
- Phase 6: 4-6 hours (testing & docs)

**Total**: 19-27 hours over 4-6 days
