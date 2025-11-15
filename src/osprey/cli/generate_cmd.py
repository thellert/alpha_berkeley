"""Code generation commands for Osprey Framework.

This module provides the 'osprey generate' command group for creating
Osprey components from various sources.
"""

import asyncio
from pathlib import Path

import click

from .styles import Messages, Styles, console

# =============================================================================
# Project Detection (same logic as interactive_menu.py)
# =============================================================================

def is_project_initialized() -> bool:
    """Check if we're in an osprey project directory.

    Returns:
        True if config.yml exists in current directory
    """
    return (Path.cwd() / 'config.yml').exists()

# Lazy imports for heavy dependencies
def get_generator():
    """Lazy import of MCP generator."""
    from osprey.generators import MCPCapabilityGenerator
    return MCPCapabilityGenerator


def get_server_template():
    """Lazy import of MCP server template."""
    from osprey.generators.mcp_server_template import write_mcp_server_file
    return write_mcp_server_file


def initialize_registry():
    """Lazy import and initialize registry.

    Must be called from within a project directory (config.yml present).
    """
    from osprey.registry import initialize_registry
    from osprey.utils.log_filter import quiet_logger

    # Initialize registry (quiet mode to suppress logs)
    with quiet_logger(['REGISTRY', 'CONFIG']):
        initialize_registry()

    return True


@click.group()
def generate():
    """Generate Osprey components from various sources.

    This command group provides code generation utilities for creating
    Osprey capabilities, demo servers, and other components.

    Available generators:

    \b
      - capability: Generate Osprey capability from MCP server
      - mcp-server: Generate demo MCP server for testing

    Examples:

    \b
      # Generate capability from MCP server
      $ osprey generate capability --from-mcp http://localhost:3001 --name slack_mcp

      # Generate capability in simulated mode (no server needed)
      $ osprey generate capability --from-mcp simulated --name weather_mcp

      # Generate a demo MCP server
      $ osprey generate mcp-server --name my_server --output ./server.py
    """
    pass


@generate.command()
@click.option(
    '--from-mcp',
    'mcp_url',
    required=True,
    help='MCP server URL (e.g., http://localhost:3001) or "simulated" for demo mode'
)
@click.option(
    '--name', '-n',
    'capability_name',
    required=True,
    help='Name for the generated capability (e.g., slack_mcp, weather_mcp)'
)
@click.option(
    '--server-name',
    default=None,
    help='Human-readable server name (default: derived from capability name)'
)
@click.option(
    '--output', '-o',
    'output_file',
    default=None,
    help='Output file path (default: ./capabilities/<name>.py)'
)
@click.option(
    '--provider',
    default=None,
    help='LLM provider override (e.g., anthropic, openai, cborg)'
)
@click.option(
    '--model',
    'model_id',
    default=None,
    help='Model ID override (e.g., claude-sonnet-4-20250514, gpt-4o)'
)
@click.option(
    '--quiet', '-q',
    is_flag=True,
    help='Reduce output verbosity'
)
def capability(
    mcp_url: str,
    capability_name: str,
    server_name: str,
    output_file: str,
    provider: str,
    model_id: str,
    quiet: bool
):
    """Generate Osprey capability from MCP server.

    Creates a complete, production-ready Osprey capability that connects
    to an MCP (Model Context Protocol) server. The generated capability
    includes:

    \b
      - Capability class with ReAct agent execution
      - Classifier guide (when to activate)
      - Orchestrator guide (how to plan steps)
      - Context class for results
      - Error handling and logging
      - Registry registration snippet

    The capability uses a ReAct agent pattern where the orchestrator
    provides high-level task objectives, and the capability's internal
    agent autonomously selects and calls the appropriate MCP tools.

    Examples:

    \b
      # Generate from real MCP server
      $ osprey generate capability --from-mcp http://localhost:3001 -n slack_mcp

      # Simulated mode (no server needed, uses weather demo tools)
      $ osprey generate capability --from-mcp simulated -n weather_mcp

      # Custom output location
      $ osprey generate capability --from-mcp http://localhost:3001 \\
          -n slack_mcp --output ./my_app/capabilities/slack.py

      # Override LLM provider/model for guide generation
      $ osprey generate capability --from-mcp simulated -n weather_mcp \\
          --provider anthropic --model claude-sonnet-4-20250514

    After generation:

    \b
      1. Review and customize the generated code
      2. Customize the context class based on your data structure
      3. Add to your project's registry.py
      4. Test with: osprey chat
    """
    # Derive server name if not provided
    if not server_name:
        # Convert capability_name to title case (e.g., slack_mcp -> Slack Mcp)
        server_name = capability_name.replace('_', ' ').title().replace(' ', '')

    # Derive output file if not provided
    if not output_file:
        output_file = f"capabilities/{capability_name}.py"

    output_path = Path(output_file)

    # Check if simulated mode
    simulated = mcp_url.lower() == "simulated"
    if simulated:
        mcp_url = None

    # Check if we're in a project directory
    if not is_project_initialized():
        console.print(f"\n{Messages.error('Not in an Osprey project directory')}")
        console.print()
        console.print("  This command requires an Osprey project with [accent]config.yml[/accent]")
        console.print()
        console.print("  [bold]To create a new project:[/bold]")
        console.print("    " + Messages.command('osprey init my-project'))
        console.print()
        console.print("  [bold]Or navigate to an existing project:[/bold]")
        console.print("    " + Messages.command('cd my-project'))
        console.print("    " + Messages.command('osprey generate capability ...'))
        console.print()
        raise click.Abort()

    console.print("\n🎨 [header]Generating MCP Capability[/header]\n")
    console.print(f"  [{Styles.LABEL}]Capability:[/{Styles.LABEL}] [{Styles.VALUE}]{capability_name}[/{Styles.VALUE}]")
    console.print(f"  [{Styles.LABEL}]Server:[/{Styles.LABEL}] [{Styles.VALUE}]{server_name}[/{Styles.VALUE}]")
    console.print(f"  [{Styles.LABEL}]Mode:[/{Styles.LABEL}] [{Styles.VALUE}]{'Simulated' if simulated else f'Real MCP ({mcp_url})'}[/{Styles.VALUE}]")
    console.print(f"  [{Styles.LABEL}]Output:[/{Styles.LABEL}] [{Styles.VALUE}]{output_path}[/{Styles.VALUE}]\n")

    try:
        # Initialize registry (required for LLM providers)
        if not quiet:
            with console.status("[dim]Initializing registry...[/dim]"):
                initialize_registry()
            console.print(f"  {Messages.success('Registry initialized')}")
        else:
            initialize_registry()

        # Create generator
        MCPCapabilityGenerator = get_generator()
        generator = MCPCapabilityGenerator(
            capability_name=capability_name,
            server_name=server_name,
            verbose=not quiet,
            provider=provider,
            model_id=model_id
        )

        # Run async generation
        asyncio.run(_generate_capability_async(
            generator=generator,
            mcp_url=mcp_url,
            simulated=simulated,
            output_path=output_path,
            quiet=quiet
        ))

    except KeyboardInterrupt:
        console.print(f"\n{Messages.warning('Generation cancelled by user')}")
        raise click.Abort() from None
    except Exception as e:
        console.print(f"\n{Messages.error(f'Generation failed: {e}')}")
        if not quiet:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise click.Abort() from e


async def _offer_registry_integration(generator, classifier_analysis, orchestrator_analysis):
    """Offer to automatically add capability to registry.

    Args:
        generator: MCPCapabilityGenerator instance
        classifier_analysis: Generated classifier analysis
        orchestrator_analysis: Generated orchestrator analysis
    """
    try:
        import questionary

        from .styles import get_questionary_style
        from osprey.generators.registry_updater import (
            add_to_registry,
            find_registry_file,
            is_already_registered,
        )

        # Find registry file from config
        registry_path = find_registry_file()
        if not registry_path:
            console.print(f"\n[{Styles.DIM}]Note: Could not find registry.py from config. "
                         "Add capability manually.[/{Styles.DIM}]")
            return

        # Check if already registered
        if is_already_registered(registry_path, generator.capability_name):
            console.print(f"\n[{Styles.WARNING}]⚠️  Capability '{generator.capability_name}' "
                         f"is already registered in {registry_path}[/{Styles.WARNING}]")
            return

        # Ask user if they want to add it
        console.print()
        console.print(f"[{Styles.HEADER}]Registry Integration:[/{Styles.HEADER}]")
        console.print(f"  Found registry: [{Styles.VALUE}]{registry_path}[/{Styles.VALUE}]")
        console.print()

        add_to_reg = questionary.confirm(
            "Add this capability to your registry automatically?",
            default=True,
            style=get_questionary_style()
        ).ask()

        if not add_to_reg:
            console.print("\n  " + Messages.info('Skipped registry update. '
                         'Add manually using snippet at bottom of generated file.'))
            return

        # Generate class name and context type from generator
        class_name = ''.join(word.title() for word in generator.capability_name.split('_')) + 'Capability'
        context_class_name = ''.join(word.title() for word in generator.capability_name.split('_')) + 'ResultsContext'
        context_type = f"{generator.server_name.upper()}_RESULTS"
        description = f"{generator.server_name} operations via MCP server"

        # Add to registry
        new_content, preview = add_to_registry(
            registry_path,
            generator.capability_name,
            class_name,
            context_type,
            context_class_name,
            description
        )

        # Show preview
        console.print(f"\n[{Styles.HEADER}]Preview of changes:[/{Styles.HEADER}]")
        console.print(preview)

        # Confirm
        confirm = questionary.confirm(
            "Apply these changes to registry.py?",
            default=True,
            style=get_questionary_style()
        ).ask()

        if confirm:
            # Backup first
            backup_path = registry_path.with_suffix('.py.bak')
            backup_path.write_text(registry_path.read_text())

            # Write new content
            registry_path.write_text(new_content)

            console.print(f"\n  {Messages.success(f'Updated {registry_path}')}")
            console.print(f"  [{Styles.DIM}]Backup saved to: {backup_path}[/{Styles.DIM}]")
            console.print()
            console.print("  " + Messages.info('Capability is now registered! '
                         'Test with: osprey chat'))
        else:
            console.print("\n  " + Messages.info('Changes not applied. '
                         'Add manually if needed.'))

    except ImportError:
        # questionary not available
        console.print(f"\n[{Styles.DIM}]Note: Install questionary for interactive registry updates[/{Styles.DIM}]")
    except Exception as e:
        console.print(f"\n[{Styles.WARNING}]⚠️  Could not update registry: {e}[/{Styles.WARNING}]")
        console.print("  " + Styles.DIM + "Add capability manually using snippet at bottom of generated file." + f"[/{Styles.DIM}]")


async def _generate_capability_async(
    generator,
    mcp_url: str,
    simulated: bool,
    output_path: Path,
    quiet: bool
):
    """Async helper for capability generation."""
    # Step 1: Discover tools
    if not quiet:
        console.print(f"\n📡 [{Styles.HEADER}]Step 1: Discovering MCP tools...[/{Styles.HEADER}]")

    with console.status("[dim]Connecting to MCP server...[/dim]" if not simulated else "[dim]Loading simulated tools...[/dim]"):
        tools = await generator.discover_tools(
            mcp_url=mcp_url,
            simulated=simulated
        )

    if not tools:
        console.print(f"  {Messages.error('No tools found')}")
        raise click.Abort()

    console.print(f"  {Messages.success(f'Found {len(tools)} tools')}")
    if not quiet:
        for tool in tools[:5]:
            console.print(f"    [{Styles.DIM}]•[/{Styles.DIM}] {tool['name']}")
        if len(tools) > 5:
            console.print(f"    [{Styles.DIM}]... and {len(tools) - 5} more[/{Styles.DIM}]")

    # Step 2: Generate guides
    if not quiet:
        console.print(f"\n🤖 [{Styles.HEADER}]Step 2: Generating guides with LLM...[/{Styles.HEADER}]")

    with console.status("[dim]Analyzing tools and generating examples...[/dim]"):
        classifier_analysis, orchestrator_analysis = await generator.generate_guides()

    num_examples = len(classifier_analysis.positive_examples) + len(classifier_analysis.negative_examples)
    console.print("  " + Messages.success(f'Generated {num_examples} classifier examples'))
    console.print("  " + Messages.success(f'Generated {len(orchestrator_analysis.example_steps)} orchestrator examples'))

    # Step 3: Generate code
    if not quiet:
        console.print(f"\n📝 [{Styles.HEADER}]Step 3: Generating capability code...[/{Styles.HEADER}]")

    with console.status("[dim]Creating capability class...[/dim]"):
        code = generator.generate_capability_code(classifier_analysis, orchestrator_analysis)

    console.print("  " + Messages.success('Code generated'))

    # Step 4: Write file
    if not quiet:
        console.print(f"\n💾 [{Styles.HEADER}]Step 4: Writing output file...[/{Styles.HEADER}]")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code)

    console.print(f"  {Messages.success(f'Written: {output_path} ({len(code):,} bytes)')}")

    # Success summary
    console.print("\n" + "=" * 70)
    console.print(f"[{Styles.BOLD_SUCCESS}]✅ SUCCESS! MCP Capability Generated[/{Styles.BOLD_SUCCESS}]")
    console.print("=" * 70 + "\n")

    console.print(f"[{Styles.HEADER}]What was created:[/{Styles.HEADER}]")
    console.print(f"  ✓ Capability class: {generator.capability_name}")
    console.print("  ✓ MCP client integration")
    console.print(f"  ✓ Classifier guide with {num_examples} examples")
    console.print(f"  ✓ Orchestrator guide with {len(orchestrator_analysis.example_steps)} examples")
    console.print("  ✓ Context class for results")
    console.print("  ✓ Error handling")
    console.print("  ✓ Registry registration snippet")

    console.print(f"\n[{Styles.HEADER}]Next Steps:[/{Styles.HEADER}]")
    console.print(f"  1. Review: [{Styles.VALUE}]{output_path}[/{Styles.VALUE}]")
    console.print("  2. Customize the context class based on your data structure")
    console.print("  3. Add to your registry.py (see snippet at bottom of file)")
    console.print(f"  4. Test with: [{Styles.ACCENT}]osprey chat[/{Styles.ACCENT}]")
    console.print()

    # Offer to add to registry automatically
    if not quiet:
        await _offer_registry_integration(
            generator,
            classifier_analysis,
            orchestrator_analysis
        )


@generate.command(name='mcp-server')
@click.option(
    '--name', '-n',
    'server_name',
    default='demo_mcp',
    help='Name for the server (default: demo_mcp)'
)
@click.option(
    '--output', '-o',
    'output_file',
    default=None,
    help='Output file path (default: ./<name>_server.py)'
)
@click.option(
    '--tools', '-t',
    type=click.Choice(['weather', 'slack', 'api'], case_sensitive=False),
    default='weather',
    help='Tool preset to include (default: weather)'
)
@click.option(
    '--port', '-p',
    default=3001,
    type=int,
    help='Server port (default: 3001)'
)
def mcp_server(
    server_name: str,
    output_file: str,
    tools: str,
    port: int
):
    """Generate demo MCP server for testing.

    Creates a demo MCP server that you can run locally to test
    Osprey's MCP capability generation. The server uses FastMCP
    for simple, Pythonic MCP server implementation.

    Tool presets available:

    \b
      - weather: Current conditions, forecasts, weather alerts
      - slack: Message sending, channel listing, history retrieval
      - api: Generic REST API operations (GET, POST, PUT)

    Examples:

    \b
      # Generate weather demo server
      $ osprey generate mcp-server

      # Generate Slack demo server on custom port
      $ osprey generate mcp-server --tools slack --port 3002

      # Custom output location
      $ osprey generate mcp-server --name my_server --output ./servers/mcp.py

    After generation:

    \b
      1. Install FastMCP: pip install fastmcp
      2. Run the server: python <output_file>
      3. Generate capability: osprey generate capability --from-mcp http://localhost:<port>
    """
    # Derive output file if not provided
    if not output_file:
        output_file = f"{server_name}_server.py"

    output_path = Path(output_file)

    console.print("\n🚀 [header]Generating MCP Server[/header]\n")
    console.print(f"  [{Styles.LABEL}]Server:[/{Styles.LABEL}] [{Styles.VALUE}]{server_name}[/{Styles.VALUE}]")
    console.print(f"  [{Styles.LABEL}]Tools:[/{Styles.LABEL}] [{Styles.VALUE}]{tools}[/{Styles.VALUE}]")
    console.print(f"  [{Styles.LABEL}]Port:[/{Styles.LABEL}] [{Styles.VALUE}]{port}[/{Styles.VALUE}]")
    console.print(f"  [{Styles.LABEL}]Output:[/{Styles.LABEL}] [{Styles.VALUE}]{output_path}[/{Styles.VALUE}]\n")

    try:
        with console.status("[dim]Generating server code...[/dim]"):
            write_mcp_server_file = get_server_template()
            output_path = write_mcp_server_file(
                output_path=output_path,
                server_name=server_name,
                port=port,
                tools=tools
            )

        console.print(f"  {Messages.success(f'Server generated: {output_path}')}\n")

        console.print(f"[{Styles.HEADER}]Next Steps:[/{Styles.HEADER}]")
        console.print(f"  1. Install dependencies: [{Styles.ACCENT}]pip install fastmcp[/{Styles.ACCENT}]")
        console.print(f"  2. Run the server: [{Styles.ACCENT}]python {output_path}[/{Styles.ACCENT}]")
        console.print(f"  3. Generate capability: [{Styles.ACCENT}]osprey generate capability --from-mcp http://localhost:{port} -n {server_name}[/{Styles.ACCENT}]")
        console.print()

    except Exception as e:
        console.print(f"\n{Messages.error(f'Generation failed: {e}')}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise click.Abort() from e


if __name__ == "__main__":
    generate()

