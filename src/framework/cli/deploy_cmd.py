"""Service deployment command.

This module provides the 'framework deploy' command which wraps the existing
container_manager functionality. It preserves 100% of the original behavior
while providing a cleaner CLI interface.

IMPORTANT: This is a thin wrapper around framework.deployment.container_manager.
All existing functionality is preserved without modification.
"""

import click
from pathlib import Path
from rich.console import Console

# Import existing container manager functions (Phase 1.5 refactored)
from framework.deployment.container_manager import (
    deploy_up,
    deploy_down,
    deploy_restart,
    show_status,
    clean_deployment,
    rebuild_deployment,
    prepare_compose_files
)


console = Console()


@click.command()
@click.argument(
    "action",
    type=click.Choice(["up", "down", "restart", "status", "clean", "rebuild"]),
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    default="config.yml",
    help="Configuration file (default: config.yml)"
)
@click.option(
    "--detached", "-d",
    is_flag=True,
    help="Run services in detached mode (for up, restart, rebuild)"
)
def deploy(action: str, config: str, detached: bool):
    """Manage Docker/Podman services for Framework projects.
    
    This command wraps the existing container management functionality,
    providing control over service deployment, status, and cleanup.
    
    Actions:
    
    \b
      up       - Start all configured services
      down     - Stop all services
      restart  - Restart all services
      status   - Show service status
      clean    - Remove containers and volumes (WARNING: destructive)
      rebuild  - Clean, rebuild, and restart services
    
    The services to deploy are defined in your config.yml under
    the 'deployed_services' key.
    
    Examples:
    
    \b
      # Start services
      $ framework deploy up
      
      # Start in background (detached mode)
      $ framework deploy up -d
      
      # Stop services
      $ framework deploy down
      
      # Check status
      $ framework deploy status
      
      # Use custom config
      $ framework deploy up --config my-config.yml
      
      # Clean everything (removes data!)
      $ framework deploy clean
    """
    console.print(f"🔧 Service management: [bold]{action}[/bold]")
    
    try:
        # Convert config path to Path object (some functions may expect string or Path)
        config_path = config  # Keep as string - original functions accept strings
        
        # Dispatch to existing container_manager functions
        # These are the ORIGINAL functions from Phase 1.5, behavior unchanged
        if action == "up":
            deploy_up(config_path, detached=detached)
            
        elif action == "down":
            deploy_down(config_path)
            
        elif action == "restart":
            deploy_restart(config_path, detached=detached)
            
        elif action == "status":
            show_status(config_path)
            
        elif action == "clean":
            # clean_deployment expects compose_files list, so prepare them first
            _, compose_files = prepare_compose_files(config_path)
            clean_deployment(compose_files)
            
        elif action == "rebuild":
            rebuild_deployment(config_path, detached=detached)
        
        # Note: The original functions handle all output and error messaging
        # We don't add extra output to avoid changing user experience
        
    except KeyboardInterrupt:
        console.print("\n⚠️  Operation cancelled by user", style="yellow")
        raise click.Abort()
    except Exception as e:
        console.print(f"❌ Deployment failed: {e}", style="red")
        # Show more details in verbose mode
        import os
        if os.environ.get("DEBUG"):
            import traceback
            console.print(traceback.format_exc(), style="dim")
        raise click.Abort()


if __name__ == "__main__":
    deploy()

