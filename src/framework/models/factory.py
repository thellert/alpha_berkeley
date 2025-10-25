"""AI Model Factory for Structured Generation.

Creates and configures LLM model instances for use with PydanticAI agents and structured
generation workflows. This factory handles the complexity of provider-specific initialization,
credential management, HTTP client configuration, and proxy setup across multiple AI providers.

The factory supports enterprise-grade features including connection pooling, timeout management,
and automatic HTTP proxy detection through environment variables. Each provider has specific
requirements for API keys, base URLs, and model identifiers that are validated and enforced.

.. note::
   Model instances created here are optimized for structured generation with PydanticAI.
   For direct chat completions without structured outputs, consider using
   :func:`~completion.get_chat_completion` instead.

.. seealso::
   :func:`get_model` : Main factory function for creating model instances
   :func:`~completion.get_chat_completion` : Direct chat completion interface
   :mod:`configs.config` : Provider configuration and credential management
"""

import logging
import os
from typing import Optional, Union
from urllib.parse import urlparse
import httpx
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
import openai
from google import genai

from framework.utils.config import get_provider_config


def _create_openai_compatible_model(
    model_id: str,
    api_key: str,
    base_url: Optional[str],
    timeout_arg_from_get_model: Optional[float],
    shared_http_client: Optional[httpx.AsyncClient] = None
) -> OpenAIModel:
    """Create an OpenAI-compatible model instance with proper client configuration.
    
    This internal helper function handles the creation of OpenAI-compatible models
    for providers that use the OpenAI API format (OpenAI, Ollama, CBORG). It manages
    HTTP client configuration, timeout settings, and base URL handling with proper
    fallback behavior.
    
    :param model_id: Model identifier as recognized by the provider
    :type model_id: str
    :param api_key: API authentication key for the provider
    :type api_key: str
    :param base_url: Provider's API base URL, None for OpenAI's default endpoint
    :type base_url: str, optional
    :param timeout_arg_from_get_model: Request timeout in seconds, defaults to 60.0
    :type timeout_arg_from_get_model: float, optional
    :param shared_http_client: Pre-configured HTTP client with proxy/timeout settings
    :type shared_http_client: httpx.AsyncClient, optional
    :return: Configured OpenAI model instance ready for structured generation
    :rtype: OpenAIModel
    
    .. note::
       When a shared HTTP client is provided, timeout configuration is managed
       by the client rather than the OpenAI client constructor.
    
    .. seealso::
       :func:`get_model` : Main factory function that calls this helper
       :class:`pydantic_ai.models.openai.OpenAIModel` : PydanticAI OpenAI model wrapper
    """
    
    openai_client_instance: openai.AsyncOpenAI
    if shared_http_client:
        client_args = {
            "api_key": api_key,
            "http_client": shared_http_client
        }
        if base_url: # Pass base_url if provided
            client_args["base_url"] = base_url
        openai_client_instance = openai.AsyncOpenAI(**client_args)
    else:
        # No shared client.
        effective_timeout_for_openai = timeout_arg_from_get_model if timeout_arg_from_get_model is not None else 60.0
        client_args = {
            "api_key": api_key,
            "timeout": effective_timeout_for_openai
        }
        if base_url: # Pass base_url if provided
            client_args["base_url"] = base_url
        openai_client_instance = openai.AsyncOpenAI(**client_args)

    model = OpenAIModel(
        model_name=model_id,
        provider=OpenAIProvider(openai_client=openai_client_instance),
    )
    # Storing original model_id for clarity
    model.model_id = model_id 
    return model


logger = logging.getLogger(__name__)


def _validate_proxy_url(proxy_url: str) -> bool:
    """Validate HTTP proxy URL format and accessibility.
    
    Performs basic validation of proxy URL format to ensure it follows
    standard HTTP/HTTPS proxy URL patterns. This helps catch common
    configuration errors early and provides clear feedback.
    
    :param proxy_url: Proxy URL to validate
    :type proxy_url: str
    :return: True if proxy URL appears valid, False otherwise
    :rtype: bool
    """
    if not proxy_url:
        return False
    
    try:
        parsed = urlparse(proxy_url)
        # Check for valid scheme and netloc (host:port)
        if parsed.scheme not in ('http', 'https'):
            return False
        if not parsed.netloc:
            return False
        return True
    except Exception:
        return False


def _get_ollama_fallback_urls(base_url: str) -> list[str]:
    """Generate fallback URLs for Ollama based on the current base URL.
    
    This helper function generates appropriate fallback URLs to handle
    common development scenarios where the execution context (container vs local)
    doesn't match the configured Ollama URL.
    
    :param base_url: Current configured Ollama base URL
    :type base_url: str
    :return: List of fallback URLs to try in order
    :rtype: list[str]
    
    .. note::
       Fallback URLs are generated based on common patterns:
       - host.containers.internal -> localhost (container to local)
       - localhost -> host.containers.internal (local to container)
       - Generic fallbacks for other scenarios
    """
    fallback_urls = []
    
    if "host.containers.internal" in base_url:
        # Running in container but Ollama might be on localhost
        fallback_urls = [
            base_url.replace("host.containers.internal", "localhost"),
            "http://localhost:11434"
        ]
    elif "localhost" in base_url:
        # Running locally but Ollama might be in container context
        fallback_urls = [
            base_url.replace("localhost", "host.containers.internal"),
            "http://host.containers.internal:11434"
        ]
    else:
        # Generic fallbacks for other scenarios
        fallback_urls = [
            "http://localhost:11434",
            "http://host.containers.internal:11434"
        ]
    
    return fallback_urls


def _test_ollama_connection(base_url: str) -> bool:
    """Test if Ollama is accessible at the given URL.
    
    Performs a simple health check by attempting to connect to Ollama
    and calling the list models endpoint.
    
    :param base_url: Ollama base URL to test
    :type base_url: str
    :return: True if connection successful, False otherwise
    :rtype: bool
    """
    try:
        # Test with a simple synchronous request to avoid async complications
        import requests
        # Convert to OpenAI-compatible endpoint for testing
        test_url = base_url.rstrip('/') + '/v1/models'
        response = requests.get(test_url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _create_ollama_model_with_fallback(
    model_id: str,
    base_url: str,
    provider_config: dict,
    timeout: Optional[float],
    async_http_client: Optional[httpx.AsyncClient]
) -> OpenAIModel:
    """Create Ollama model with graceful fallback for development workflows.
    
    This function attempts to connect to Ollama at the configured URL first,
    then tries common fallback URLs if the initial connection fails. This
    handles the common development scenario where execution context (container
    vs local) doesn't match the configured Ollama endpoint.
    
    :param model_id: Ollama model identifier
    :type model_id: str
    :param base_url: Primary Ollama base URL from configuration
    :type base_url: str
    :param provider_config: Provider configuration dictionary
    :type provider_config: dict
    :param timeout: Request timeout in seconds
    :type timeout: float, optional
    :param async_http_client: Pre-configured HTTP client
    :type async_http_client: httpx.AsyncClient, optional
    :return: Configured OpenAI-compatible model for Ollama
    :rtype: OpenAIModel
    :raises ValueError: If no working Ollama endpoint is found
    """
    effective_base_url = base_url
    if not base_url.endswith('/v1'):
        effective_base_url = base_url.rstrip('/') + '/v1'
    
    used_fallback = False
    
    # Test primary URL first
    if _test_ollama_connection(base_url):
        logger.debug(f"Successfully connected to Ollama at {base_url}")
    else:
        logger.debug(f"Failed to connect to Ollama at {base_url}")
        
        # Try fallback URLs
        fallback_urls = _get_ollama_fallback_urls(base_url)
        working_url = None
        
        for fallback_url in fallback_urls:
            logger.debug(f"Attempting fallback connection to Ollama at {fallback_url}")
            if _test_ollama_connection(fallback_url):
                working_url = fallback_url
                used_fallback = True
                logger.warning(
                    f"⚠️  Ollama connection fallback: configured URL '{base_url}' failed, "
                    f"using fallback '{fallback_url}'. Consider updating your configuration "
                    f"for your current execution environment."
                )
                break
        
        if working_url:
            effective_base_url = working_url
            if not working_url.endswith('/v1'):
                effective_base_url = working_url.rstrip('/') + '/v1'
        else:
            # All connection attempts failed
            raise ValueError(
                f"Failed to connect to Ollama at configured URL '{base_url}' "
                f"and all fallback URLs {fallback_urls}. Please ensure Ollama is running "
                f"and accessible, or update your configuration."
            )
    
    return _create_openai_compatible_model(
        model_id=model_id,
        api_key=provider_config.get("api_key"),
        base_url=effective_base_url,
        timeout_arg_from_get_model=timeout,
        shared_http_client=async_http_client
    )


def get_model(
    provider: Optional[str] = None,
    model_config: Optional[dict] = None,
    model_id: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    max_tokens: int = 100000,
) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
    """Create a configured LLM model instance for structured generation with PydanticAI.
    
    This factory function creates and configures LLM model instances optimized for
    structured generation workflows using PydanticAI agents. It handles provider-specific
    initialization, credential validation, HTTP client configuration, and proxy setup
    automatically based on environment variables and configuration files.
    
    The function supports flexible configuration through multiple approaches:
    - Direct parameter specification for programmatic use
    - Model configuration dictionaries from YAML files
    - Automatic credential loading from configuration system
    - Environment-based HTTP proxy detection and configuration
    
    Provider-specific behavior:
    - **Anthropic**: Requires API key and model ID, supports HTTP proxy
    - **Google**: Requires API key and model ID, supports HTTP proxy  
    - **OpenAI**: Requires API key and model ID, supports HTTP proxy and custom base URLs
    - **Ollama**: Requires model ID and base URL, no API key needed, no proxy support
    - **CBORG**: Requires API key, model ID, and base URL, supports HTTP proxy
    
    :param provider: AI provider name ('anthropic', 'google', 'openai', 'ollama', 'cborg')
    :type provider: str, optional
    :param model_config: Configuration dictionary with provider, model_id, and other settings
    :type model_config: dict, optional
    :param model_id: Specific model identifier recognized by the provider
    :type model_id: str, optional
    :param api_key: API authentication key, auto-loaded from config if not provided
    :type api_key: str, optional
    :param base_url: Custom API endpoint URL, required for Ollama and CBORG
    :type base_url: str, optional
    :param timeout: Request timeout in seconds, defaults to provider configuration
    :type timeout: float, optional
    :param max_tokens: Maximum tokens for generation, defaults to 100000
    :type max_tokens: int
    :raises ValueError: If required provider, model_id, api_key, or base_url are missing
    :raises ValueError: If provider is not supported
    :return: Configured model instance ready for PydanticAI agent integration
    :rtype: Union[OpenAIModel, AnthropicModel, GeminiModel]
    
    .. note::
       HTTP proxy configuration is automatically detected from the HTTP_PROXY
       environment variable for supported providers. Timeout and connection
       pooling are managed through shared HTTP clients when proxies are enabled.
    
    .. warning::
       API keys and base URLs are validated before model creation. Ensure proper
       configuration is available through the config system or direct
       parameter specification.
    
    Examples:
        Basic model creation with direct parameters::
        
            >>> from framework.models import get_model
            >>> model = get_model(
            ...     provider="anthropic",
            ...     model_id="claude-3-sonnet-20240229",
            ...     api_key="your-api-key"
            ... )
            >>> # Use with PydanticAI Agent
            >>> agent = Agent(model=model, output_type=YourModel)
            
        Using configuration dictionary from YAML::
        
            >>> model_config = {
            ...     "provider": "cborg",
            ...     "model_id": "anthropic/claude-sonnet",
            ...     "max_tokens": 4096,
            ...     "timeout": 30.0
            ... }
            >>> model = get_model(model_config=model_config)
            
        Ollama local model setup::
        
            >>> model = get_model(
            ...     provider="ollama",
            ...     model_id="llama3.1:8b",
            ...     base_url="http://localhost:11434"
            ... )
    
    .. seealso::
       :func:`~completion.get_chat_completion` : Direct chat completion without structured output
       :func:`configs.config.get_provider_config` : Provider configuration loading
       :class:`pydantic_ai.Agent` : PydanticAI agent that uses these models
       :doc:`/developer-guides/01_understanding-the-framework/02_convention-over-configuration` : Complete model setup guide
    """
    if model_config:
        provider = model_config.get("provider", provider)
        model_id = model_config.get("model_id", model_id)
        max_tokens = model_config.get("max_tokens", max_tokens)
        timeout = model_config.get("timeout", timeout)

    if not provider:
        raise ValueError("Provider must be specified either directly or via model_config")

    provider_config = get_provider_config(provider)
    
    api_key = provider_config.get("api_key", api_key)
    base_url = provider_config.get("base_url", base_url)
    timeout = provider_config.get("timeout", timeout)
    
    # Define provider requirements
    provider_requirements = {
        "google":    {"model_id": True, "api_key": True,  "base_url": False, "use_proxy": True},
        "anthropic": {"model_id": True, "api_key": True,  "base_url": False, "use_proxy": True},
        "openai":    {"model_id": True, "api_key": True,  "base_url": False, "use_proxy": True},
        "ollama":    {"model_id": True, "api_key": False, "base_url": True,  "use_proxy": False},
        "cborg":     {"model_id": True, "api_key": True,  "base_url": True,  "use_proxy": True},
    }
    
    if provider not in provider_requirements:
        raise ValueError(f"Invalid provider: {provider}. Must be 'anthropic', 'cborg', 'google', 'ollama', or 'openai'.")
    
    requirements = provider_requirements[provider]
    
    # Common validation
    if requirements["model_id"] and not model_id:
        raise ValueError(f"Model ID for {provider} not provided.")
    
    if requirements["api_key"] and not api_key:
        raise ValueError(f"No API key provided for {provider}.")
    
    if requirements["base_url"] and not base_url:
        raise ValueError(f"No base URL provided for {provider}.")
   
    async_http_client: Optional[httpx.AsyncClient] = None
    
    # HTTP proxy is machine dependent and set up through environment variable
    proxy_url = os.getenv("HTTP_PROXY")
    should_use_proxy = False
    
    if requirements["use_proxy"] and proxy_url:
        if _validate_proxy_url(proxy_url):
            should_use_proxy = True
        else:
            logger.warning(f"Invalid HTTP_PROXY URL format '{proxy_url}', ignoring proxy configuration")

    # Create a custom client if a proxy is set (and should be used) or a specific timeout is requested
    if should_use_proxy or timeout is not None:
        client_params = {}
        if should_use_proxy:
            client_params["proxy"] = proxy_url
        if timeout is not None:
            client_params["timeout"] = timeout
        async_http_client = httpx.AsyncClient(**client_params)

    # Provider-specific implementation (validation already done above)
    if provider == "google":
        google_provider = GoogleGLAProvider(
            api_key=api_key, 
            http_client=async_http_client
        )
        return GeminiModel(model_name=model_id, provider=google_provider)

    elif provider == "anthropic":
        anthropic_provider = AnthropicProvider(
            api_key=api_key,
            http_client=async_http_client
        )
        return AnthropicModel(
            model_name=model_id, 
            provider=anthropic_provider, 
        )
    
    elif provider == "openai":
        return _create_openai_compatible_model(
            model_id=model_id,
            api_key=api_key,
            base_url=base_url,
            timeout_arg_from_get_model=timeout,
            shared_http_client=async_http_client
        )

    elif provider == "ollama":
        return _create_ollama_model_with_fallback(
            model_id=model_id,
            base_url=base_url,
            provider_config=provider_config,
            timeout=timeout,
            async_http_client=async_http_client
        )

    elif provider == "cborg":
        return _create_openai_compatible_model(
            model_id=model_id,
            api_key=api_key,
            base_url=base_url,
            timeout_arg_from_get_model=timeout,
            shared_http_client=async_http_client
        ) 