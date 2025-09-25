"""
ALS Assistant Observability Utilities

This module contains ALS Assistant-specific observability functions,
primarily for Langfuse integration and tracing.
"""

import base64
import logging
import os
from typing import Optional

from opentelemetry import trace
import logfire
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def scrubbing_callback(match: logfire.ScrubMatch):
    """Preserve the Langfuse session ID during log scrubbing."""
    if (
        match.path == ("attributes", "langfuse.session.id")
        and match.pattern_match.group(0) == "session"
    ):
        # Return the original value to prevent redaction
        return match.value


def configure_langfuse(langfuse_host: str = None):
    """
    Configure Langfuse for ALS Assistant agent observability.
    
    Args:
        langfuse_host: Optional override for Langfuse host URL
        
    Returns:
        OpenTelemetry tracer instance
    """

    
    # Check if Langfuse is enabled
    langfuse_enabled = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
    
    if not langfuse_enabled:
        # Return a regular tracer but don't configure any exporters or logfire
        # This will create spans locally but they won't be exported anywhere
        return trace.get_tracer("disabled_als_assistant_agent")
    
    # Get Langfuse credentials
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not langfuse_public_key or not langfuse_secret_key:
        raise ValueError("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set when Langfuse is enabled")
    
    # Determine Langfuse host with simple fallback logic
    if langfuse_host is None:
        langfuse_host = os.getenv("LANGFUSE_HOST")
        if not langfuse_host:
            # TODO: Clean this up - derive host/port from service configuration instead of hardcoding
            # Try langfuse-web first (inter-container), fallback to localhost (host access)
            langfuse_host = "http://langfuse-web:3000"
            try:
                import requests
                response = requests.get(f"{langfuse_host}/api/public/otel/v1/traces", timeout=2)
                # 405 Method Not Allowed is expected (GET on POST endpoint) and means connection works
                if response.status_code in [200, 405]:
                    logger.debug("Using inter-container Langfuse host: langfuse-web:3000")
                else:
                    raise requests.exceptions.RequestException(f"Unexpected status code: {response.status_code}")
            except Exception as e:
                langfuse_host = "http://localhost:3001"
                logger.debug(f"Falling back to localhost Langfuse host: localhost:3001 (reason: {e})")
    
    # Create authorization header
    langfuse_auth = base64.b64encode(f"{langfuse_public_key}:{langfuse_secret_key}".encode()).decode()

    # Configure OpenTelemetry environment
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{langfuse_host}/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"

    # Configure logfire with scrubbing
    logfire.configure(
        service_name='als-assistant-agents',
        send_to_logfire=False,
        scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback)
    )

    return trace.get_tracer("als_assistant_agent")


def get_tracer(name: str = "als_assistant_agent"):
    """
    Get an OpenTelemetry tracer for ALS Assistant services.
    
    Args:
        name: Tracer name
        
    Returns:
        OpenTelemetry tracer instance
    """
    return trace.get_tracer(name)