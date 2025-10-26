"""Main CLI entry point for Alpha Berkeley Framework.

This module provides the main CLI group that organizes all framework
commands under the `framework` command namespace.

Note: This will become 'mentat' in Phase 8 of the migration.

Performance Note: Uses lazy imports to avoid loading heavy dependencies
(langgraph, langchain, etc.) until a command is actually invoked.
This keeps `framework --help` fast.
"""

import click
import sys

# Import version from framework package
try:
    from framework import __version__
except ImportError:
    __version__ = "0.7.3"


# PERFORMANCE OPTIMIZATION: Lazy command loading
# Commands are imported only when invoked, not at module load time.
# This keeps --help fast and avoids loading heavy dependencies unnecessarily.

class LazyGroup(click.Group):
    """Click group that lazily loads subcommands only when invoked."""
    
    def get_command(self, ctx, cmd_name):
        """Lazily import and return the command when it's invoked."""
        # Map command names to their module paths
        commands = {
            'init': 'framework.cli.init_cmd',
            'deploy': 'framework.cli.deploy_cmd',
            'chat': 'framework.cli.chat_cmd',
            'export-config': 'framework.cli.export_config_cmd',
            'health': 'framework.cli.health_cmd',
        }
        
        if cmd_name not in commands:
            return None
        
        # Lazy import - only loads when command is actually used
        import importlib
        mod = importlib.import_module(commands[cmd_name])
        
        # Get the command function from the module
        # Convention: module name without _cmd suffix
        if cmd_name == 'export-config':
            cmd_func = getattr(mod, 'export_config')
        else:
            cmd_func = getattr(mod, cmd_name)
        
        return cmd_func
    
    def list_commands(self, ctx):
        """Return list of available commands (for --help)."""
        return ['init', 'deploy', 'chat', 'export-config', 'health']


@click.group(cls=LazyGroup)
@click.version_option(version=__version__, prog_name="framework")
def cli():
    """Alpha Berkeley Framework CLI - Capability-Based Agentic Framework.
    
    A unified command-line interface for creating, deploying, and interacting
    with intelligent agents built on the Alpha Berkeley Framework.
    
    Use 'framework COMMAND --help' for more information on a specific command.
    
    Examples:
    
    \b
      framework init my-project       Create new project
      framework deploy up             Start services  
      framework chat                  Interactive conversation
      framework health                Check system health
      framework export-config         View framework defaults
    """
    pass


def main():
    """Entry point for the framework CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

