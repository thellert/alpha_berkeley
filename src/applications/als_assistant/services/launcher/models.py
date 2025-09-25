"""Launcher Service Models

Data models for the launcher service including state, requests, and results.
Kept simple and focused on the core functionality.
"""

from typing import Dict, Any, Optional, List, TypedDict
from pydantic import BaseModel, Field
import shlex


class ExecutableCommand(TypedDict):
    """Represents a command that can be executed on the user's machine.
    
    Simple TypedDict for LangGraph serialization compatibility.
    """
    name: str  # Human-readable name for the command
    executable: str  # Path to the executable (shell-quoted)
    args: List[str]  # Command arguments (shell-quoted)
    description: str  # Description of what this command does


class LauncherServiceRequest(BaseModel):
    """Request to the launcher service.
    
    Enhanced request structure with explicit PV support and optional context.
    """
    query: str = Field(description="Natural language query for application launching")
    pv_addresses: Optional[List[str]] = Field(default=None, description="Explicit PV addresses provided by the agent")
    runtime_config: Optional[Dict[str, Any]] = Field(default=None, description="Complete configurable dictionary with all configs")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class LauncherServiceResult(BaseModel):
    """Result from the launcher service.
    
    Contains everything needed to present the launch option to the user.
    """
    success: bool = Field(description="Whether the request was processed successfully")
    launch_uri: Optional[str] = Field(default=None, description="URI to launch the application")
    command_name: Optional[str] = Field(default=None, description="Human-readable command name")
    command_description: Optional[str] = Field(default=None, description="Description of what will be launched")
    error_message: Optional[str] = Field(default=None, description="Error message if unsuccessful")
    
    @classmethod
    def success_result(cls, command: ExecutableCommand, launch_uri: str) -> 'LauncherServiceResult':
        """Create a successful result."""
        return cls(
            success=True,
            launch_uri=launch_uri,
            command_name=command["name"],
            command_description=command["description"]
        )
    
    @classmethod
    def error_result(cls, error_message: str) -> 'LauncherServiceResult':
        """Create an error result."""
        return cls(
            success=False,
            error_message=error_message
        )


