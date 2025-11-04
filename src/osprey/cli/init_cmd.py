"""Project initialization command.

This module provides the 'osprey init' command which creates new
projects from templates. It offers a streamlined way to scaffold complete
agent applications with proper structure and configuration.
"""

import click
from pathlib import Path

from .templates import TemplateManager
from .styles import console, Messages, Styles


@click.command()
@click.argument("project_name")
@click.option(
    "--template", "-t",
    default="minimal",
    help="Application template to use (minimal, hello_world_weather, wind_turbine)"
)
@click.option(
    "--registry-style", "-r",
    type=click.Choice(["compact", "explicit"], case_sensitive=False),
    default="compact",
    help="Registry style: compact (uses helper, ~10 lines) or explicit (full listing, ~500 lines)"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(),
    default=".",
    help="Output directory for project (default: current directory)"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Force overwrite if project directory already exists"
)
def init(project_name: str, template: str, registry_style: str, output_dir: str, force: bool):
    """Create a new Osprey project.

    Creates a complete self-contained project with application code,
    service configurations, and documentation. The project will be
    ready to run immediately after adding API keys.

    PROJECT_NAME: Name of your project (e.g., my-assistant, beamline-agent)

    Available templates:

    \b
      - minimal: Bare-bones project with TODO placeholders
      - hello_world_weather: Simple weather query example
      - wind_turbine: Complex multi-capability example

    Registry styles:

    \b
      - compact (default): Uses extend_osprey_registry() helper (~10 lines)
      - explicit: Full osprey + app components visible (~500 lines)

    The generated project includes:

    \b
      - Application code (capabilities, registry, context classes)
      - Service configurations (Jupyter, OpenWebUI, Pipelines)
      - Configuration file with osprey imports
      - Environment template (.env.example)
      - Dependencies file (pyproject.toml)
      - Documentation (README.md)

    Examples:

    \b
      # Create minimal project (compact registry style)
      $ osprey init my-assistant

      # Create with explicit registry (advanced users)
      $ osprey init my-assistant --registry-style explicit

      # Create from specific template
      $ osprey init my-assistant --template hello_world_weather

      # Create in specific location
      $ osprey init my-assistant --output-dir /projects

      # Force overwrite if directory exists
      $ osprey init my-assistant --force
    """
    console.print(f"🚀 Creating project: [header]{project_name}[/header]")

    try:
        # Create template manager
        manager = TemplateManager()

        # Show available templates
        available_templates = manager.list_app_templates()
        if template not in available_templates:
            console.print(
                f"❌ Template '{template}' not found.\n"
                f"Available templates: {', '.join(available_templates)}",
                style=Styles.ERROR
            )
            raise click.Abort()

        console.print(f"  📋 Using template: [accent]{template}[/accent]")
        console.print(f"  📝 Registry style: [accent]{registry_style}[/accent]")

        # Detect environment variables
        detected_env = manager._detect_environment_variables()
        if detected_env:
            console.print(f"  🔑 Detected {len(detected_env)} environment variable(s) from system:")
            for env_var in detected_env.keys():
                console.print(f"     • {env_var}", style="dim")

        # Handle existing directory
        output_path = Path(output_dir).resolve()
        project_path = output_path / project_name

        if project_path.exists():
            if force:
                msg = Messages.warning(f'Removing existing directory: {project_path}')
                console.print(f"  ⚠️  {msg}")
                import shutil
                shutil.rmtree(project_path)
                console.print(f"  {Messages.success('Removed existing directory')}")
            else:
                console.print(
                    f"❌ Directory '{project_path}' already exists.\n"
                    f"   Use --force to overwrite, or choose a different name.",
                    style=Styles.ERROR
                )
                raise click.Abort()

        # Create project
        project_path = manager.create_project(
            project_name=project_name,
            output_dir=output_path,
            template_name=template,
            registry_style=registry_style
        )

        console.print(f"  ✓ Creating application code...", style=Styles.SUCCESS)
        console.print(f"  ✓ Creating service configurations...", style=Styles.SUCCESS)
        console.print(f"  ✓ Creating project configuration...", style=Styles.SUCCESS)

        # Check if API keys were detected and .env was created
        api_keys = ['CBORG_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
        has_api_keys = any(key in detected_env for key in api_keys)

        if has_api_keys:
            console.print(f"  ✓ Created .env with detected API keys", style=Styles.SUCCESS)

        console.print(
            f"\n✅ Project created successfully at: [bold]{project_path}[/bold]"
        )

        # Show next steps
        console.print("\n📋 [bold]Next steps:[/bold]")
        console.print(f"  1. {Messages.command(f'cd {project_name}')}")

        if has_api_keys:
            console.print("  2. # .env already configured with detected API keys")
            console.print(f"  3. {Messages.command('osprey deploy up')}")
            console.print(f"  4. {Messages.command('osprey chat')}")
        else:
            console.print(f"  2. {Messages.command('cp .env.example .env')}")
            console.print("  3. # Edit .env with your API keys (OPENAI_API_KEY, etc.)")
            console.print(f"  4. {Messages.command('osprey deploy up')}")
            console.print(f"  5. {Messages.command('osprey chat')}")

    except ValueError as e:
        console.print(f"❌ Error: {e}", style=Styles.ERROR)
        raise click.Abort()
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style=Styles.ERROR)
        import traceback
        console.print(traceback.format_exc(), style="dim")
        raise click.Abort()


if __name__ == "__main__":
    init()

