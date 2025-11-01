"""Project initialization command.

This module provides the 'framework init' command which creates new
projects from templates. It offers a streamlined way to scaffold complete
agent applications with proper structure and configuration.
"""

import click
from pathlib import Path
from rich.console import Console

from .templates import TemplateManager


console = Console()


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
    """Create a new Framework project.
    
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
      - compact (default): Uses extend_framework_registry() helper (~10 lines)
      - explicit: Full framework + app components visible (~500 lines)
    
    The generated project includes:
    
    \b
      - Application code (capabilities, registry, context classes)
      - Service configurations (Jupyter, OpenWebUI, Pipelines)
      - Configuration file with framework imports
      - Environment template (.env.example)
      - Dependencies file (pyproject.toml)
      - Documentation (README.md)
    
    Examples:
    
    \b
      # Create minimal project (compact registry style)
      $ framework init my-assistant
      
      # Create with explicit registry (advanced users)
      $ framework init my-assistant --registry-style explicit
      
      # Create from specific template
      $ framework init my-assistant --template hello_world_weather
      
      # Create in specific location
      $ framework init my-assistant --output-dir /projects
      
      # Force overwrite if directory exists
      $ framework init my-assistant --force
    """
    console.print(f"🚀 Creating project: [bold cyan]{project_name}[/bold cyan]")
    
    try:
        # Create template manager
        manager = TemplateManager()
        
        # Show available templates
        available_templates = manager.list_app_templates()
        if template not in available_templates:
            console.print(
                f"❌ Template '{template}' not found.\n"
                f"Available templates: {', '.join(available_templates)}",
                style="red"
            )
            raise click.Abort()
        
        console.print(f"  📋 Using template: [cyan]{template}[/cyan]")
        console.print(f"  📝 Registry style: [cyan]{registry_style}[/cyan]")
        
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
                console.print(
                    f"  ⚠️  [yellow]Removing existing directory:[/yellow] {project_path}",
                )
                import shutil
                shutil.rmtree(project_path)
                console.print(f"  ✓ Removed existing directory", style="green")
            else:
                console.print(
                    f"❌ Directory '{project_path}' already exists.\n"
                    f"   Use --force to overwrite, or choose a different name.",
                    style="red"
                )
                raise click.Abort()
        
        # Create project
        project_path = manager.create_project(
            project_name=project_name,
            output_dir=output_path,
            template_name=template,
            registry_style=registry_style
        )
        
        console.print(f"  ✓ Creating application code...", style="green")
        console.print(f"  ✓ Creating service configurations...", style="green")
        console.print(f"  ✓ Creating project configuration...", style="green")
        
        # Check if API keys were detected and .env was created
        api_keys = ['CBORG_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
        has_api_keys = any(key in detected_env for key in api_keys)
        
        if has_api_keys:
            console.print(f"  ✓ Created .env with detected API keys", style="green")
        
        console.print(
            f"\n✅ Project created successfully at: [bold]{project_path}[/bold]"
        )
        
        # Show next steps
        console.print("\n📋 [bold]Next steps:[/bold]")
        console.print(f"  1. [cyan]cd {project_name}[/cyan]")
        
        if has_api_keys:
            console.print("  2. # .env already configured with detected API keys")
            console.print("  3. [cyan]framework deploy up[/cyan]")
            console.print("  4. [cyan]framework chat[/cyan]")
        else:
            console.print("  2. [cyan]cp .env.example .env[/cyan]")
            console.print("  3. # Edit .env with your API keys (OPENAI_API_KEY, etc.)")
            console.print("  4. [cyan]framework deploy up[/cyan]")
            console.print("  5. [cyan]framework chat[/cyan]")
        
    except ValueError as e:
        console.print(f"❌ Error: {e}", style="red")
        raise click.Abort()
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        import traceback
        console.print(traceback.format_exc(), style="dim")
        raise click.Abort()


if __name__ == "__main__":
    init()

