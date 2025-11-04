"""Service deployment command.

This module provides the 'osprey deploy' command which wraps the existing
container_manager functionality. It preserves 100% of the original behavior
while providing a cleaner CLI interface.

IMPORTANT: This is a thin wrapper around osprey.deployment.container_manager.
All existing functionality is preserved without modification.
"""

import click
from pathlib import Path
from rich.console import Console

# Import existing container manager functions (Phase 1.5 refactored)
from osprey.deployment.container_manager import (
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
    type=click.Choice(["up", "down", "restart", "status", "build", "clean", "rebuild"]),
)
@click.option(
    "--project", "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Project directory (default: current directory or OSPREY_PROJECT env var)"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    default="config.yml",
    help="Configuration file (default: config.yml in project directory)"
)
@click.option(
    "--detached", "-d",
    is_flag=True,
    help="Run services in detached mode (for up, restart, rebuild)"
)
@click.option(
    "--dev",
    is_flag=True,
    help="Development mode: copy local osprey package to containers instead of using PyPI version. Use this when testing local osprey changes."
)
def deploy(action: str, project: str, config: str, detached: bool, dev: bool):
    """Manage Docker/Podman services for Osprey projects.

    This command wraps the existing container management functionality,
    providing control over service deployment, status, and cleanup.

    Actions:

    \b
      up       - Start all configured services
      down     - Stop all services
      restart  - Restart all services
      status   - Show service status
      build    - Build/prepare compose files without starting services
      clean    - Remove containers and volumes (WARNING: destructive)
      rebuild  - Clean, rebuild, and restart services

    The services to deploy are defined in your config.yml under
    the 'deployed_services' key.

    Examples:

    \b
      # Start services in current directory
      $ osprey deploy up

      # Start services in specific project
      $ osprey deploy up --project ~/projects/my-agent

      # Start in background (detached mode)
      $ osprey deploy up -d

      # Start with local osprey for development/testing
      $ osprey deploy up --dev

      # Stop services
      $ osprey deploy down

      # Check status
      $ osprey deploy status

      # Build compose files without starting services
      $ osprey deploy build

      # Use environment variable
      $ export OSPREY_PROJECT=~/projects/my-agent
      $ osprey deploy up

      # Use custom config
      $ osprey deploy up --config my-config.yml

      # Clean everything (removes data!)
      $ osprey deploy clean

      # Rebuild with local osprey for development
      $ osprey deploy rebuild --dev
    """
    from .project_utils import resolve_config_path

    console.print(f"Service management: [bold]{action}[/bold]")

    try:
        # Resolve config path from project and config args
        config_path = resolve_config_path(project, config)

        # Dispatch to existing container_manager functions
        # These are the ORIGINAL functions from Phase 1.5, behavior unchanged
        if action == "up":
            deploy_up(config_path, detached=detached, dev_mode=dev)

        elif action == "down":
            deploy_down(config_path, dev_mode=dev)

        elif action == "restart":
            deploy_restart(config_path, detached=detached)

        elif action == "status":
            show_status(config_path)

        elif action == "build":
            # Just prepare compose files without starting services
            console.print("🔨 Building compose files...")
            _, compose_files = prepare_compose_files(config_path, dev_mode=dev)
            console.print("\n✅ Compose files built successfully:")
            for compose_file in compose_files:
                console.print(f"  • {compose_file}")

        elif action == "clean":
            # clean_deployment expects compose_files list, so prepare them first
            _, compose_files = prepare_compose_files(config_path, dev_mode=dev)
            clean_deployment(compose_files)

        elif action == "rebuild":
            rebuild_deployment(config_path, detached=detached, dev_mode=dev)

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

