"""Interactive chat command.

This module provides the 'framework chat' command which wraps the existing
direct_conversation CLI interface. It preserves 100% of the original behavior
while providing a cleaner CLI interface.

IMPORTANT: This is a thin wrapper around framework.interfaces.cli.direct_conversation.
All existing functionality is preserved without modification.
"""

import click
import asyncio
from rich.console import Console

# Import existing CLI interface (Phase 1.5 refactored)
from framework.interfaces.cli.direct_conversation import run_cli


console = Console()


@click.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    default="config.yml",
    help="Configuration file (default: config.yml)"
)
def chat(config: str):
    """Start interactive CLI conversation interface.
    
    Opens an interactive chat session with the agent. The interface
    provides command history, auto-suggestions, and real-time streaming
    of agent responses.
    
    This command wraps the existing direct_conversation interface,
    preserving all its functionality including:
    
    \b
      - Real-time status updates during agent processing
      - Approval workflow integration with interrupt handling
      - Rich console formatting with colors and styling
      - Session-based conversation continuity
      - Comprehensive error handling
    
    Commands within the chat:
    
    \b
      bye/end - Exit the chat
      Ctrl+L  - Clear screen
      Ctrl+C  - Exit
    
    Examples:
    
    \b
      # Start chat with default config
      $ framework chat
      
      # Use custom configuration
      $ framework chat --config my-config.yml
    
    Note: Ensure services are running first (framework deploy up)
    """
    console.print("🤖 Starting Framework CLI interface...")
    console.print("   Press Ctrl+C to exit\n")
    
    try:
        # Call the existing run_cli function with config_path
        # This is the ORIGINAL function from Phase 1.5, behavior unchanged
        asyncio.run(run_cli(config_path=config))
        
    except KeyboardInterrupt:
        console.print("\n\n👋 Goodbye!", style="yellow")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        # Show more details in verbose mode
        import os
        if os.environ.get("DEBUG"):
            import traceback
            console.print(traceback.format_exc(), style="dim")
        raise click.Abort()


if __name__ == "__main__":
    chat()

