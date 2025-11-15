"""MCP Server Template Generator.

Generates demo MCP servers for testing Osprey MCP capabilities.
Uses FastMCP for simple, Pythonic MCP server implementation.
"""

from pathlib import Path


def generate_mcp_server(
    server_name: str = "demo_mcp",
    port: int = 3001,
    tools: str = "weather"
) -> str:
    """Generate MCP server Python code.

    Args:
        server_name: Name for the server
        port: Port to run on
        tools: Tool preset to include ('weather', 'slack', 'api')

    Returns:
        Complete Python source code for MCP server
    """

    # Get tool implementations based on preset
    if tools == "weather":
        tool_code = _get_weather_tools()
        description = "Weather Demo MCP Server"
    elif tools == "slack":
        tool_code = _get_slack_tools()
        description = "Slack Demo MCP Server"
    elif tools == "api":
        tool_code = _get_api_tools()
        description = "API Demo MCP Server"
    else:
        tool_code = _get_weather_tools()
        description = "Demo MCP Server"

    server_code = f'''#!/usr/bin/env python3
"""
{description}

A minimal MCP server for testing Osprey MCP capability generation.
Built with FastMCP - a Pythonic framework for MCP server development.

INSTALLATION:
    pip install fastmcp

USAGE:
    python {server_name}_server.py

    Server will run on http://localhost:{port}
    SSE endpoint: http://localhost:{port}/sse

TEST WITH OSPREY:
    osprey generate capability --from-mcp http://localhost:{port} --name {server_name}
"""

from typing import Optional, Literal
from fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("{description}")


# =============================================================================
# Tool Implementations
# =============================================================================

{tool_code}


# =============================================================================
# Server Startup
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("{description}")
    print("=" * 70)
    print(f"\\nStarting server on http://localhost:{port}")
    print(f"SSE endpoint: http://localhost:{port}/sse")
    print("\\nPress Ctrl+C to stop the server")
    print("=" * 70)
    print()

    # Run the server with SSE transport
    mcp.run(transport="sse", host="0.0.0.0", port={port})
'''

    return server_code


def _get_weather_tools() -> str:
    """Get Weather tool implementations."""
    return '''@mcp.tool()
def get_current_weather(
    location: str,
    units: Literal["celsius", "fahrenheit"] = "celsius"
) -> dict:
    """Get current weather conditions for a location."""
    # Mock weather data
    temp_c = 18
    temp_f = 64
    temp = temp_c if units == "celsius" else temp_f

    return {
        "location": location,
        "coordinates": {"lat": 37.7749, "lon": -122.4194},
        "current": {
            "timestamp": "2025-11-15T14:30:00Z",
            "temperature": temp,
            "feels_like": temp - 2,
            "conditions": "Partly Cloudy",
            "description": "Scattered clouds with mild temperatures",
            "humidity": 65,
            "wind_speed": 12,
            "wind_direction": "NW",
            "pressure": 1013,
            "visibility": 10,
            "uv_index": 5
        },
        "units": units,
        "success": True
    }


@mcp.tool()
def get_forecast(
    location: str,
    days: int = 5,
    units: Literal["celsius", "fahrenheit"] = "celsius"
) -> dict:
    """Get weather forecast for upcoming days."""
    # Mock forecast data
    forecast_data = []
    conditions_cycle = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]

    for i in range(min(days, 7)):
        temp_high_c = 20 + i
        temp_low_c = 12 + i
        temp_high_f = 68 + i * 2
        temp_low_f = 54 + i * 2

        forecast_data.append({
            "date": f"2025-11-{15+i:02d}",
            "day_of_week": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][i],
            "temperature_high": temp_high_c if units == "celsius" else temp_high_f,
            "temperature_low": temp_low_c if units == "celsius" else temp_low_f,
            "conditions": conditions_cycle[i % 5],
            "description": f"Expected {conditions_cycle[i % 5].lower()} conditions",
            "precipitation_chance": (i * 15) % 60,
            "humidity": 55 + (i * 5),
            "wind_speed": 8 + i,
            "uv_index": 6 - i if 6 - i > 0 else 1
        })

    return {
        "location": location,
        "coordinates": {"lat": 35.6762, "lon": 139.6503},
        "forecast_days": len(forecast_data),
        "daily": forecast_data,
        "units": units,
        "success": True
    }


@mcp.tool()
def get_weather_alerts(
    location: str,
    severity: Literal["all", "severe", "moderate", "minor"] = "all"
) -> dict:
    """Get active weather alerts and warnings for a location."""
    # Mock alert data - sometimes return alerts, sometimes empty
    # For demo purposes, locations with "Miami" or "Storm" return alerts
    has_alerts = "miami" in location.lower() or "storm" in location.lower()

    alerts = []
    if has_alerts:
        alerts = [
            {
                "id": "alert_001",
                "type": "Hurricane Warning",
                "severity": "severe",
                "headline": "Hurricane Warning in effect",
                "description": "Hurricane conditions expected within 36 hours. Prepare for severe weather.",
                "start_time": "2025-11-15T12:00:00Z",
                "end_time": "2025-11-17T18:00:00Z",
                "affected_areas": [f"{location} area"],
                "issued_by": "National Weather Service",
                "instructions": "Follow evacuation orders and prepare emergency supplies."
            }
        ]

    return {
        "location": location,
        "coordinates": {"lat": 25.7617, "lon": -80.1918},
        "alert_count": len(alerts),
        "alerts": alerts,
        "last_updated": "2025-11-15T14:30:00Z",
        "success": True
    }
'''


def _get_slack_tools() -> str:
    """Get Slack tool implementations."""
    return '''@mcp.tool()
def send_message(
    channel: str,
    text: str,
    thread_ts: Optional[str] = None
) -> dict:
    """Send a message to a Slack channel."""
    return {
        "ok": True,
        "channel": channel,
        "ts": "1234567890.123456",
        "message": {
            "text": text,
            "user": "U12345678",
            "ts": "1234567890.123456",
            "thread_ts": thread_ts
        }
    }


@mcp.tool()
def list_channels(
    types: str = "public_channel",
    limit: int = 100
) -> dict:
    """List channels in workspace."""
    return {
        "ok": True,
        "channels": [
            {"id": "C123", "name": "general", "is_member": True},
            {"id": "C456", "name": "random", "is_member": True},
            {"id": "C789", "name": "announcements", "is_member": False}
        ]
    }


@mcp.tool()
def get_channel_history(
    channel: str,
    limit: int = 10
) -> dict:
    """Get channel message history."""
    return {
        "ok": True,
        "messages": [
            {
                "type": "message",
                "user": "U12345",
                "text": "Hello world!",
                "ts": "1234567890.123456"
            }
        ]
    }
'''


def _get_api_tools() -> str:
    """Get generic API tool implementations."""
    return '''@mcp.tool()
def get_data(
    endpoint: str,
    params: Optional[dict] = None
) -> dict:
    """Make a GET request to an API endpoint."""
    return {
        "status": 200,
        "endpoint": endpoint,
        "params": params or {},
        "data": {"message": "Demo response", "items": [1, 2, 3]}
    }


@mcp.tool()
def post_data(
    endpoint: str,
    data: dict
) -> dict:
    """Make a POST request to an API endpoint."""
    return {
        "status": 201,
        "endpoint": endpoint,
        "created": True,
        "id": "demo-123",
        "data": data
    }


@mcp.tool()
def update_data(
    endpoint: str,
    id: str,
    data: dict
) -> dict:
    """Make a PUT/PATCH request to update data."""
    return {
        "status": 200,
        "endpoint": endpoint,
        "id": id,
        "updated": True,
        "data": data
    }
'''


def write_mcp_server_file(
    output_path: Path,
    server_name: str = "demo_mcp",
    port: int = 3001,
    tools: str = "weather"
) -> Path:
    """Generate and write MCP server file.

    Args:
        output_path: Where to write the server file
        server_name: Name for the server
        port: Port to run on
        tools: Tool preset to include

    Returns:
        Path to written file
    """
    code = generate_mcp_server(server_name, port, tools)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code)
    output_path.chmod(0o755)  # Make executable

    return output_path

