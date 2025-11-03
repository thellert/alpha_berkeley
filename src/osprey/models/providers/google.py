"""Google Provider Adapter Implementation."""

from typing import Optional, Any, Union
import httpx
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from google import genai
from google.genai import types as genai_types
from .base import BaseProvider


class GoogleProviderAdapter(BaseProvider):
    """Google AI (Gemini) provider implementation."""

    # Metadata (single source of truth)
    name = "google"
    description = "Google (Gemini models)"
    requires_api_key = True
    requires_base_url = False
    requires_model_id = True
    supports_proxy = True
    default_base_url = None
    default_model_id = "gemini-2.5-flash"  # Latest Flash for general use
    health_check_model_id = "gemini-2.5-flash-lite"  # Cheapest/fastest for health checks
    available_models = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ]

    def create_model(
        self,
        model_id: str,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: Optional[float],
        http_client: Optional[httpx.AsyncClient]
    ) -> GeminiModel:
        """Create Google Gemini model instance for PydanticAI."""
        provider = GoogleGLAProvider(
            api_key=api_key, 
            http_client=http_client
        )
        return GeminiModel(model_name=model_id, provider=provider)

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
    ) -> str:
        """Execute Google Gemini chat completion with thinking support."""
        # Suppress Google library's INFO logs (AFC messages, etc.)
        import logging
        google_logger = logging.getLogger('google.genai')
        original_level = google_logger.level
        google_logger.setLevel(logging.WARNING)
        
        try:
            client = genai.Client(api_key=api_key)
        finally:
            # Restore original log level
            google_logger.setLevel(original_level)

        # Handle thinking configuration
        enable_thinking = kwargs.get("enable_thinking", False)
        budget_tokens = kwargs.get("budget_tokens", 0)

        if not enable_thinking:
            budget_tokens = 0

        if budget_tokens >= max_tokens:
            raise ValueError("budget_tokens must be less than max_tokens.")

        response = client.models.generate_content(
            model=model_id,
            contents=[message],
            config=genai_types.GenerateContentConfig(
                **({"thinking_config": genai_types.ThinkingConfig(thinking_budget=budget_tokens)}),
                max_output_tokens=max_tokens
            )
        )

        return response.text

    def check_health(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: float = 5.0,
        model_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """Check Google API health with minimal test call.

        Makes a minimal API call (~10 tokens, ~$0.0001) to verify the API key works.
        An API key that can't handle a penny's worth of tokens is a critical issue.
        """
        if not api_key:
            return False, "API key not set"

        # Check for placeholder/template values
        if api_key.startswith("${") or "YOUR_API_KEY" in api_key.upper():
            return False, "API key not configured (placeholder value detected)"

        # Use provided model or cheapest default from metadata
        test_model = model_id or self.health_check_model_id

        try:
            # Suppress Google library's INFO logs (AFC messages, etc.)
            import logging
            google_logger = logging.getLogger('google.genai')
            original_level = google_logger.level
            google_logger.setLevel(logging.WARNING)
            
            try:
                client = genai.Client(api_key=api_key)
            finally:
                # Restore original log level
                google_logger.setLevel(original_level)

            # Minimal test: 1 token in, 1 token out (~$0.0001 cost)
            response = client.models.generate_content(
                model=test_model,
                contents=["Hi"],
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=1
                )
            )

            # If we got here, API key works
            return True, "API accessible and authenticated"

        except Exception as e:
            error_msg = str(e).lower()

            # Check for common error types
            if "authentication" in error_msg or "api key" in error_msg or "invalid" in error_msg:
                return False, "Authentication failed (invalid API key)"
            elif "permission" in error_msg or "denied" in error_msg:
                return False, "Permission denied (check API key permissions)"
            elif "quota" in error_msg or "rate" in error_msg:
                # Rate limited = API key works, just hitting limits
                return True, "API key valid (rate limited, but functional)"
            elif "timeout" in error_msg:
                return False, "Request timeout"
            else:
                return False, f"API error: {str(e)[:50]}"

