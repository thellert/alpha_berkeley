"""Anthropic Provider Adapter Implementation."""

from typing import Optional, Any, Union
import httpx
import anthropic
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider as PydanticAnthropicProvider

from .base import BaseProvider


class AnthropicProviderAdapter(BaseProvider):
    """Anthropic AI provider implementation."""

    # Metadata (single source of truth)
    name = "anthropic"
    description = "Anthropic (Claude models)"
    requires_api_key = True
    requires_base_url = False
    requires_model_id = True
    supports_proxy = True
    default_base_url = None
    default_model_id = "claude-sonnet-4-5"
    health_check_model_id = "claude-sonnet-4-5" 
    available_models = [
        "claude-opus-4-1",
        "claude-sonnet-4-5",
        "claude-haiku-4-5"
    ]

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
        system_prompt: Optional[str] = None,
        output_format: Optional[Any] = None,
        **kwargs
    ) -> Union[str, list]:
        """Execute Anthropic chat completion with extended thinking support."""
        # Get http_client if provided (for proxy support)
        http_client = kwargs.get("http_client")

        client = anthropic.Anthropic(
            api_key=api_key,
            http_client=http_client,
        )

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
        timeout: float = 5.0,
        model_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """Check Anthropic API health with minimal test call.

        Makes a minimal API call (~10 tokens, ~$0.0001) to verify the API key works.
        An API key that can't handle a penny's worth of tokens is a critical issue.
        """
        if not api_key:
            return False, "API key not set"

        # Check for placeholder/template values
        if api_key.startswith("${") or api_key.startswith("sk-ant-xxx"):
            return False, "API key not configured (placeholder value detected)"

        # Use provided model or cheapest default from metadata
        test_model = model_id or self.health_check_model_id

        try:
            client = anthropic.Anthropic(api_key=api_key)

            # Minimal test: 1 token in, 1 token out (~$0.0001 cost)
            response = client.messages.create(
                model=test_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}],
                timeout=timeout
            )

            # If we got here, API key works
            return True, "API accessible and authenticated"

        except anthropic.AuthenticationError:
            return False, "Authentication failed (invalid API key)"
        except anthropic.PermissionDeniedError:
            return False, "Permission denied (check API key permissions)"
        except anthropic.RateLimitError:
            # Rate limited = API key works, just hitting limits
            return True, "API key valid (rate limited, but functional)"
        except anthropic.NotFoundError as e:
            # Model not found - API key works but model doesn't exist
            return False, f"Model '{test_model}' not found (check model ID)"
        except anthropic.BadRequestError as e:
            return False, f"Bad request: {str(e)[:50]}"
        except anthropic.APIConnectionError as e:
            return False, f"Connection failed: {str(e)[:50]}"
        except anthropic.APITimeoutError:
            return False, "Request timeout"
        except anthropic.InternalServerError as e:
            return False, f"Anthropic server error: {str(e)[:50]}"
        except anthropic.APIError as e:
            return False, f"API error: {str(e)[:50]}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)[:50]}"

