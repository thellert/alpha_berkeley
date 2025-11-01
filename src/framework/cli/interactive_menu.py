"""Interactive Terminal UI (TUI) for Alpha Berkeley Framework CLI.

This module provides the interactive menu system that launches when the user
runs 'framework' with no arguments. It provides a context-aware interface that
adapts based on whether the user is in a project directory.

Key Features:
- Context-aware main menu (different for "no project" vs "existing project")
- Interactive init flow with template, provider, and model selection
- Automatic environment variable detection (API keys from shell)
- Secure API key configuration with password input
- Smooth transitions between menu and direct commands
- Integration with existing Click commands (no duplication)

Architecture:
- Uses questionary for interactive prompts with custom styling
- Uses rich for terminal output and formatting
- Integrates with existing TemplateManager for project creation
- Integrates with registry system for provider metadata
- Calls underlying functions directly (not Click commands)

The TUI is optional - users can still use direct commands like:
    framework init my-project
    framework chat
    framework deploy up

"""

import os
import sys
import asyncio
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

try:
    import questionary
    from questionary import Style, Choice
except ImportError:
    questionary = None
    Style = None
    Choice = None


# ============================================================================
# CONSOLE AND STYLING
# ============================================================================

console = Console()

# Custom style matching the framework theme
custom_style = Style([
    ('qmark', 'fg:#00aa00 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#00aa00 bold'),
    ('pointer', 'fg:#00aa00 bold'),
    ('highlighted', 'fg:#00aa00 bold bg:#2d2d2d'),
    ('selected', 'fg:#00aa00'),
    ('separator', 'fg:#666666'),
    ('instruction', 'fg:#666666 italic'),
    ('text', 'fg:#888888'),
    ('disabled', 'fg:#666666'),
]) if Style else None


# ============================================================================
# BANNER AND BRANDING
# ============================================================================

def show_banner(context: str = "interactive"):
    """Display the unified framework banner with ASCII art.
    
    Args:
        context: Display context - "interactive", "chat", or "welcome"
    """
    from rich.text import Text
    
    console.print()
    
    # Unified ASCII art banner used across all CLI interfaces
    banner_text = """
    ╔═════════════════════════════════════════════════════════════════╗
    ║                                                                 ║
    ║                                                                 ║
    ║  ░█████╗░██╗░░░░░██████╗░██╗░░██╗░█████╗░  ░█████╗░██╗░░░░░██╗  ║
    ║  ██╔══██╗██║░░░░░██╔══██╗██║░░██║██╔══██╗  ██╔══██╗██║░░░░░██║  ║  
    ║  ███████║██║░░░░░██████╔╝███████║███████║  ██║░░╚═╝██║░░░░░██║  ║
    ║  ██╔══██║██║░░░░░██╔═══╝░██╔══██║██╔══██║  ██║░░██╗██║░░░░░██║  ║
    ║  ██║░░██║███████╗██║░░░░░██║░░██║██║░░██║  ╚█████╔╝███████╗██║  ║
    ║  ╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝  ░╚════╝░╚══════╝╚═╝  ║
    ║                                                                 ║
    ║                                                                 ║
    ║     Command Line Interface for the Alpha Berkeley Framework     ║
    ╚═════════════════════════════════════════════════════════════════╝
    """
    
    console.print(Text(banner_text, style="bold cyan"))
    
    # Context-specific subtitle
    if context == "interactive":
        console.print("    [bold cyan]Interactive Menu System[/bold cyan]")
        console.print("    [dim]Use arrow keys to navigate • Press Ctrl+C to exit[/dim]")
    elif context == "chat":
        console.print("    [yellow]💡 Type 'bye' or 'end' to exit[/yellow]")
        console.print("    [bright_blue]⚡ Use slash commands (/) for quick actions - try /help[/bright_blue]")
    
    console.print()


def show_success_art():
    """Display success ASCII art."""
    art = """
    ┌─────────────────────────────┐
    │   ✓  SUCCESS  ✓             │
    └─────────────────────────────┘
    """
    console.print(art, style="green bold")


# ============================================================================
# PROJECT DETECTION
# ============================================================================

def is_project_initialized() -> bool:
    """Check if we're in a framework project directory.
    
    Returns:
        True if config.yml exists in current directory
    """
    return (Path.cwd() / 'config.yml').exists()


def get_project_info(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and parse config.yml for project metadata.
    
    Args:
        config_path: Optional path to config.yml (defaults to current directory)
    
    Returns:
        Dictionary with project information (provider, model, etc.)
        Returns empty dict if no project found or error parsing
    """
    if config_path is None:
        config_path = Path.cwd() / 'config.yml'
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate config.yml structure after parsing
        if config is None:
            if os.environ.get('DEBUG'):
                console.print(f"[dim]Warning: Empty config.yml at {config_path}[/dim]")
            return {}
        
        if not isinstance(config, dict):
            if os.environ.get('DEBUG'):
                console.print(f"[dim]Warning: Invalid config.yml structure (not a dict) at {config_path}[/dim]")
            return {}
        
        # Extract relevant information with safe defaults
        info = {
            'project_root': config.get('project_root', str(config_path.parent)),
            'registry_path': config.get('registry_path', ''),
        }
        
        # Extract provider and model from models.orchestrator section
        models_config = config.get('models', {})
        if not isinstance(models_config, dict):
            models_config = {}
        
        orchestrator = models_config.get('orchestrator', {})
        if not isinstance(orchestrator, dict):
            orchestrator = {}
        
        if orchestrator:
            info['provider'] = orchestrator.get('provider', 'unknown')
            info['model'] = orchestrator.get('model_id', 'unknown')
        
        return info
        
    except yaml.YAMLError as e:
        console.print(f"[yellow]Warning:[/yellow] Invalid YAML in config.yml: {e}")
        return {}
    except UnicodeDecodeError as e:
        console.print(f"[yellow]Warning:[/yellow] Encoding error in config.yml: {e}")
        return {}
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Could not parse config.yml: {e}")
        return {}


def discover_nearby_projects(max_dirs: int = 50, max_time_ms: int = 100) -> List[Tuple[str, Path]]:
    """Discover framework projects in immediate subdirectories.
    
    This performs a SHALLOW, non-recursive search (1 level deep only) for 
    config.yml files in subdirectories of the current working directory.
    
    Performance safeguards:
    - Only checks immediate subdirectories (not recursive)
    - Stops after checking max_dirs subdirectories
    - Has timeout protection (max_time_ms)
    - Ignores hidden directories and common non-project directories
    
    Args:
        max_dirs: Maximum number of subdirectories to check (default: 50)
        max_time_ms: Maximum time to spend searching in milliseconds (default: 100)
        
    Returns:
        List of tuples: (project_name, project_path)
        Sorted alphabetically by project name
        
    Examples:
        >>> discover_nearby_projects()
        [('my-agent', Path('/current/dir/my-agent')),
         ('weather-app', Path('/current/dir/weather-app'))]
    """
    import time
    
    projects = []
    start_time = time.time()
    max_time_seconds = max_time_ms / 1000.0
    
    # Directories to ignore (common non-project directories)
    ignore_dirs = {
        'node_modules', 'venv', '.venv', 'env', '.env', 
        '__pycache__', '.git', '.svn', '.hg',
        'build', 'dist', '.egg-info', 'site-packages',
        '.pytest_cache', '.mypy_cache', '.tox',
        'docs', '_agent_data', '.cache'
    }
    
    try:
        cwd = Path.cwd()
        checked_count = 0
        
        # Get all immediate subdirectories
        subdirs = []
        try:
            for item in cwd.iterdir():
                # Check timeout
                if time.time() - start_time > max_time_seconds:
                    if os.environ.get('DEBUG'):
                        console.print(f"[dim]Project discovery timeout after {max_time_ms}ms[/dim]")
                    break
                
                # Only check directories
                if not item.is_dir():
                    continue
                
                # Skip hidden directories (start with .)
                if item.name.startswith('.'):
                    continue
                
                # Skip common non-project directories
                if item.name in ignore_dirs:
                    continue
                
                subdirs.append(item)
                
        except (PermissionError, OSError) as e:
            # Skip directories we can't read
            if os.environ.get('DEBUG'):
                console.print(f"[dim]Warning: Could not read directory: {e}[/dim]")
            return projects
        
        # Sort subdirectories alphabetically for consistent ordering
        subdirs.sort(key=lambda p: p.name.lower())
        
        # Check each subdirectory for config.yml
        for subdir in subdirs:
            # Check limits
            if checked_count >= max_dirs:
                if os.environ.get('DEBUG'):
                    console.print(f"[dim]Project discovery stopped after checking {max_dirs} directories[/dim]")
                break
            
            if time.time() - start_time > max_time_seconds:
                if os.environ.get('DEBUG'):
                    console.print(f"[dim]Project discovery timeout after {max_time_ms}ms[/dim]")
                break
            
            try:
                config_file = subdir / 'config.yml'
                
                if config_file.exists() and config_file.is_file():
                    # Found a project!
                    projects.append((subdir.name, subdir))
                    
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
            
            checked_count += 1
    
    except Exception as e:
        # Fail gracefully - return whatever we found so far
        if os.environ.get('DEBUG'):
            console.print(f"[dim]Warning during project discovery: {e}[/dim]")
    
    # Return sorted list
    return sorted(projects, key=lambda x: x[0].lower())


# ============================================================================
# PROVIDER METADATA (from Registry)
# ============================================================================

# Cache for provider metadata (loaded once per TUI session)
_provider_cache: Optional[Dict[str, Dict[str, Any]]] = None

def get_provider_metadata() -> Dict[str, Dict[str, Any]]:
    """Get provider information from framework registry.
    
    Loads providers directly from the framework registry configuration
    without requiring a project config.yml. This reads the framework's
    provider registrations and introspects provider class attributes
    for metadata (single source of truth).
    
    This approach works whether or not you're in a project directory,
    making it perfect for the TUI init flow.
    
    Results are cached for the TUI session to avoid repeated registry loading.
    
    Returns:
        Dictionary mapping provider names to their metadata:
        {
            'anthropic': {
                'name': 'anthropic',
                'description': 'Anthropic (Claude models)',
                'requires_key': True,
                'requires_base_url': False,
                'models': ['claude-sonnet-4-5', ...],
                'default_model': 'claude-sonnet-4-5',
                'health_check_model': 'claude-haiku-4-5'
            },
            ...
        }
    """
    global _provider_cache
    
    # Return cached data if available
    if _provider_cache is not None:
        return _provider_cache
    
    import importlib
    
    try:
        # Import framework registry provider directly (no config.yml needed!)
        from framework.registry.registry import FrameworkRegistryProvider
        
        # Get framework registry config (doesn't require project config)
        framework_registry = FrameworkRegistryProvider()
        config = framework_registry.get_registry_config()
        
        providers = {}
        
        # Load each provider registration from framework config
        for provider_reg in config.providers:
            try:
                # Import the provider module
                module = importlib.import_module(provider_reg.module_path)
                
                # Get the provider class
                provider_class = getattr(module, provider_reg.class_name)
                
                # Extract metadata from class attributes (single source of truth)
                providers[provider_class.name] = {
                    'name': provider_class.name,
                    'description': provider_class.description,
                    'requires_key': provider_class.requires_api_key,
                    'requires_base_url': provider_class.requires_base_url,
                    'models': provider_class.available_models,
                    'default_model': provider_class.default_model_id,
                    'health_check_model': provider_class.health_check_model_id
                }
            except Exception as e:
                # Skip providers that fail to load, but log for debugging
                if os.environ.get('DEBUG'):
                    console.print(f"[dim]Warning: Could not load provider {provider_reg.class_name}: {e}[/dim]")
                continue
        
        if not providers:
            console.print("[yellow]Warning:[/yellow] No providers could be loaded from framework registry")
        
        # Cache the result for future calls
        _provider_cache = providers
        return providers
        
    except Exception as e:
        # This should rarely happen - framework registry should always be available
        console.print(f"[red]Error:[/red] Could not load providers from framework registry: {e}")
        console.print("[yellow]The TUI requires access to provider information to initialize projects.[/yellow]")
        if os.environ.get('DEBUG'):
            import traceback
            traceback.print_exc()
        
        # Return empty dict but don't cache failures
        return {}


# ============================================================================
# MAIN MENU
# ============================================================================

def show_main_menu() -> Optional[str]:
    """Show context-aware main menu.
    
    Returns:
        Selected action string, or None if user cancels
    """
    if not questionary:
        console.print("[red]Error:[/red] questionary package not installed.")
        console.print("Install with: pip install questionary")
        return None
    
    if not is_project_initialized():
        # No project in current directory - discover nearby projects
        console.print("\n[dim]No project detected in current directory[/dim]")
        
        # Quick shallow search for projects in subdirectories
        nearby_projects = discover_nearby_projects()
        
        # Build menu choices
        choices = []
        
        # If we found nearby projects, add them to the menu
        if nearby_projects:
            console.print(f"[dim]Found {len(nearby_projects)} project(s) in subdirectories[/dim]\n")
            
            for project_name, project_path in nearby_projects:
                # Get project info for display
                project_info = get_project_info(project_path / 'config.yml')
                
                if project_info and 'provider' in project_info:
                    display = f"[→] {project_name:20} ({project_info['provider']} / {project_info.get('model', 'unknown')[:20]})"
                else:
                    display = f"[→] {project_name:20} (framework project)"
                
                # Value is tuple so we can distinguish from other actions
                choices.append(Choice(display, value=('select_project', project_path)))
            
            # Add separator
            choices.append(Choice("─" * 60, value=None, disabled=True))
        
        # Standard menu options
        choices.extend([
            Choice("[+] Create new project (interactive)", value='init_interactive'),
            Choice("[?] Show init command syntax", value='init_help'),
            Choice("[?] Show main help", value='help'),
            Choice("[x] Exit", value='exit')
        ])
        
        return questionary.select(
            "What would you like to do?",
            choices=choices,
            style=custom_style,
            instruction="(Use arrow keys to navigate)"
        ).ask()
    else:
        # Project menu
        project_info = get_project_info()
        project_name = Path.cwd().name
        
        console.print(f"\n[bold cyan]Project:[/bold cyan] {project_name}")
        if project_info:
            console.print(f"[dim]Provider: {project_info.get('provider', 'unknown')} | "
                         f"Model: {project_info.get('model', 'unknown')}[/dim]")
        
        return questionary.select(
            "Select command:",
            choices=[
                Choice("[>] chat        - Start CLI conversation", value='chat'),
                Choice("[>] deploy      - Manage services (web UIs)", value='deploy'),
                Choice("[>] health      - Run system health check", value='health'),
                Choice("[>] config      - Show configuration", value='config'),
                Choice("[+] init        - Create new project", value='init_interactive'),
                Choice("[?] help        - Show all commands", value='help'),
                Choice("[x] exit        - Exit CLI", value='exit')
            ],
            style=custom_style,
            instruction="(Use arrow keys to navigate)"
        ).ask()


# ============================================================================
# DIRECTORY SAFETY CHECKS
# ============================================================================

def check_directory_has_active_mounts(directory: Path) -> Tuple[bool, List[str]]:
    """Check if a directory has active Docker/Podman volume mounts.
    
    This helps prevent accidentally deleting directories that contain running
    services with active volume mounts, which can lead to corrupted containers.
    
    Args:
        directory: Directory path to check
        
    Returns:
        Tuple of (has_mounts, mount_details)
        - has_mounts: True if active mounts detected
        - mount_details: List of mount descriptions
        
    Examples:
        >>> has_mounts, details = check_directory_has_active_mounts(Path("my-project"))
        >>> if has_mounts:
        ...     print(f"Active mounts: {details}")
    """
    import subprocess
    
    mount_details = []
    
    # Normalize the directory path
    dir_str = str(directory.resolve())
    
    # Check for Docker mounts
    try:
        # Try docker first (more common)
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=1
        )
        
        if result.returncode == 0:
            containers = result.stdout.strip().split('\n')
            containers = [c for c in containers if c]  # Remove empty strings
            
            for container in containers:
                # Inspect each container for mounts
                inspect_result = subprocess.run(
                    ["docker", "inspect", "--format", "{{json .Mounts}}", container],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if inspect_result.returncode == 0:
                    import json
                    try:
                        mounts = json.loads(inspect_result.stdout)
                        for mount in mounts:
                            source = mount.get('Source', '')
                            if dir_str in source or source.startswith(dir_str):
                                mount_details.append(
                                    f"Container '{container}' has mount: {source}"
                                )
                    except json.JSONDecodeError:
                        pass
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        # Docker not available or timeout - try Podman
        pass
    
    # Check for Podman mounts (if docker check didn't find anything)
    if not mount_details:
        try:
            result = subprocess.run(
                ["podman", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                containers = [c for c in containers if c]
                
                for container in containers:
                    inspect_result = subprocess.run(
                        ["podman", "inspect", "--format", "{{json .Mounts}}", container],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if inspect_result.returncode == 0:
                        import json
                        try:
                            mounts = json.loads(inspect_result.stdout)
                            for mount in mounts:
                                source = mount.get('Source', '')
                                if dir_str in source or source.startswith(dir_str):
                                    mount_details.append(
                                        f"Container '{container}' has mount: {source}"
                                    )
                        except json.JSONDecodeError:
                            pass
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            # Podman also not available - assume no mounts
            pass
    
    return len(mount_details) > 0, mount_details


# ============================================================================
# TEMPLATE SELECTION
# ============================================================================

def select_template(templates: List[str]) -> Optional[str]:
    """Interactive template selection.
    
    Args:
        templates: List of available template names
        
    Returns:
        Selected template name, or None if cancelled
    """
    # Template descriptions (could also come from template metadata)
    descriptions = {
        'minimal': 'Empty project structure with TODO placeholders',
        'hello_world_weather': 'Single capability weather example (tutorial)',
        'wind_turbine': 'Multi-capability with RAG and custom prompts (advanced)'
    }
    
    choices = []
    for template in templates:
        desc = descriptions.get(template, 'No description available')
        display = f"{template:20} - {desc}"
        choices.append(Choice(display, value=template))
    
    return questionary.select(
        "Select project template:",
        choices=choices,
        style=custom_style,
        instruction="(Use arrow keys to navigate)"
    ).ask()


def get_default_name_for_template(template: str) -> str:
    """Get a sensible default project name for the template.
    
    Args:
        template: Template name
        
    Returns:
        Default project name suggestion
    """
    defaults = {
        'minimal': 'my-agent',
        'hello_world_weather': 'weather-agent',
        'wind_turbine': 'turbine-agent'
    }
    return defaults.get(template, 'my-project')


# ============================================================================
# PROVIDER AND MODEL SELECTION
# ============================================================================

def select_provider(providers: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """Interactive provider selection.
    
    Args:
        providers: Provider metadata dictionary
        
    Returns:
        Selected provider name, or None if cancelled
    """
    # Validate providers dict before selection menus (fail gracefully if empty)
    if not providers:
        console.print("\n[red]Error:[/red] No providers available")
        console.print("[yellow]The framework could not load any AI providers.[/yellow]")
        console.print("[dim]Check that framework is properly installed: pip install -e .[all][/dim]\n")
        return None
    
    choices = []
    for key, p in sorted(providers.items()):
        try:
            # Validate provider metadata structure
            if not isinstance(p, dict):
                continue
            if 'name' not in p or 'description' not in p:
                if os.environ.get('DEBUG'):
                    console.print(f"[dim]Warning: Provider {key} missing required metadata[/dim]")
                continue
                
            # Description comes directly from provider class attribute
            key_info = " [requires API key]" if p.get('requires_key', True) else " [no API key]"
            display = f"{p['name']:12} - {p['description']}{key_info}"
            choices.append(Choice(display, value=key))
        except Exception as e:
            if os.environ.get('DEBUG'):
                console.print(f"[dim]Warning: Error processing provider {key}: {e}[/dim]")
            continue
    
    if not choices:
        console.print("\n[red]Error:[/red] No valid providers found")
        console.print("[yellow]All providers failed validation.[/yellow]\n")
        return None
    
    return questionary.select(
        "Select default AI provider:",
        choices=choices,
        style=custom_style,
        instruction="(This sets default provider in config.yml)"
    ).ask()


def select_model(provider: str, providers: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """Interactive model selection for chosen provider.
    
    Args:
        provider: Provider name
        providers: Provider metadata dictionary
        
    Returns:
        Selected model ID, or None if cancelled
    """
    provider_info = providers[provider]
    
    choices = [
        Choice(model, value=model) 
        for model in provider_info['models']
    ]
    
    default = provider_info.get('default_model')
    
    return questionary.select(
        f"Select default model for {provider}:",
        choices=choices,
        style=custom_style,
        default=default if default in provider_info['models'] else None
    ).ask()


# ============================================================================
# API KEY MANAGEMENT
# ============================================================================

def get_api_key_name(provider: str) -> Optional[str]:
    """Get environment variable name for provider API key.
    
    Args:
        provider: Provider name (e.g., 'anthropic', 'openai')
        
    Returns:
        Environment variable name, or None if provider doesn't need API key
    """
    key_names = {
        'cborg': 'CBORG_API_KEY',
        'stanford': 'STANFORD_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'google': 'GOOGLE_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'ollama': None  # Ollama doesn't need API key
    }
    return key_names.get(provider, f'{provider.upper()}_API_KEY')


def configure_api_key(provider: str, project_path: Path, 
                     providers: Dict[str, Dict[str, Any]]) -> bool:
    """Configure API key for the selected provider.
    
    Args:
        provider: Provider name (e.g., 'anthropic', 'openai')
        project_path: Path to project directory
        providers: Provider metadata dictionary
        
    Returns:
        True if API key configured successfully, False otherwise
    """
    console.print("\n[bold cyan]API Key Configuration[/bold cyan]\n")
    
    # Get key name
    key_name = get_api_key_name(provider)
    
    if not key_name:
        console.print(f"[green]✓[/green] Provider '{provider}' does not require an API key")
        return True
    
    console.print(f"Provider: [cyan]{provider}[/cyan]")
    console.print(f"Required: [cyan]{key_name}[/cyan]\n")
    
    # Check if already detected from environment
    from framework.cli.templates import TemplateManager
    manager = TemplateManager()
    detected_env = manager._detect_environment_variables()
    
    if key_name in detected_env:
        console.print(f"[green]✓[/green] API key already detected from environment")
        console.print(f"[dim]Value: {detected_env[key_name][:10]}...[/dim]\n")
        
        use_detected = questionary.confirm(
            "Use detected API key?",
            default=True,
            style=custom_style
        ).ask()
        
        if use_detected:
            write_env_file(project_path, key_name, detected_env[key_name])
            return True
    
    # Give user options
    action = questionary.select(
        "How would you like to configure the API key?",
        choices=[
            Choice("[#] Paste API key now (secure input)", value='paste'),
            Choice("[-] Configure later (edit .env manually)", value='later'),
            Choice("[?] Where do I get an API key?", value='help'),
        ],
        style=custom_style
    ).ask()
    
    if action == 'help':
        show_api_key_help(provider)
        return configure_api_key(provider, project_path, providers)  # Ask again
    
    elif action == 'paste':
        console.print(f"\n[dim]Enter your {key_name} (input will be hidden)[/dim]")
        
        api_key = questionary.password(
            f"{key_name}:",
            style=custom_style
        ).ask()
        
        if api_key and len(api_key.strip()) > 0:
            write_env_file(project_path, key_name, api_key.strip())
            console.print(f"\n[green]✓[/green] {key_name} configured securely\n")
            return True
        else:
            console.print("\n[yellow]Warning:[/yellow] No API key provided\n")
            return False
    
    elif action == 'later':
        show_manual_config_instructions(provider, key_name, project_path)
        return False
    
    return False


def write_env_file(project_path: Path, key_name: str, api_key: str):
    """Write API key to .env file with proper permissions.
    
    Args:
        project_path: Path to project directory
        key_name: Environment variable name
        api_key: API key value
    """
    from dotenv import set_key
    
    env_file = project_path / ".env"
    
    # Copy from .env.example if doesn't exist
    if not env_file.exists():
        env_example = project_path / ".env.example"
        if env_example.exists():
            shutil.copy(env_example, env_file)
        else:
            env_file.touch()
    
    # Set the key
    set_key(str(env_file), key_name, api_key)
    
    # Set permissions to 600 (owner read/write only)
    os.chmod(env_file, 0o600)
    
    console.print(f"  [green]✓[/green] Wrote {key_name} to .env")
    console.print(f"  [green]✓[/green] Set file permissions to 600")


def show_api_key_help(provider: str):
    """Show provider-specific instructions for getting API keys.
    
    Args:
        provider: Provider name
    """
    console.print()
    
    if provider == 'cborg':
        console.print("[bold]Getting a CBorg API Key:[/bold]")
        console.print("  1. Visit: https://cborg.lbl.gov")
        console.print("  2. As a Berkeley Lab employee, click 'Request API Key'")
        console.print("  3. Create an API key ($50/month per user allocation)")
        console.print("  4. Copy the key provided\n")
        
    elif provider == 'stanford':
        console.print("[bold]Getting a Stanford API Key:[/bold]")
        console.print("  1. Contact Stanford AI team for access information")
        console.print("  2. Sign in with Stanford credentials")
        console.print("  3. Request API key for your project")
        console.print("  4. Copy the key provided\n")
        console.print("[dim]Note: This may require Stanford affiliation[/dim]\n")
        
    elif provider == 'anthropic':
        console.print("[bold]Getting an Anthropic API Key:[/bold]")
        console.print("  1. Visit: https://console.anthropic.com/")
        console.print("  2. Sign up or log in with your account")
        console.print("  3. Navigate to 'API Keys' in the settings")
        console.print("  4. Click 'Create Key' and name your key")
        console.print("  5. Copy the key (shown only once!)\n")
        
    elif provider == 'openai':
        console.print("[bold]Getting an OpenAI API Key:[/bold]")
        console.print("  1. Visit: https://platform.openai.com/api-keys")
        console.print("  2. Sign up or log in to your OpenAI account")
        console.print("  3. Add billing information if not already set up")
        console.print("  4. Click '+ Create new secret key'")
        console.print("  5. Name your key and copy it (shown only once!)\n")
        
    elif provider == 'google':
        console.print("[bold]Getting a Google API Key (Gemini):[/bold]")
        console.print("  1. Visit: https://aistudio.google.com/app/apikey")
        console.print("  2. Sign in with your Google account")
        console.print("  3. Click 'Create API key'")
        console.print("  4. Select a Google Cloud project or create a new one")
        console.print("  5. Copy the generated API key\n")
        
    else:
        console.print(f"[dim]Check {provider} documentation for API key instructions[/dim]\n")
    
    input("Press ENTER to continue...")


def show_manual_config_instructions(provider: str, key_name: str, project_path: Path):
    """Show instructions for manual API key configuration.
    
    Args:
        provider: Provider name
        key_name: Environment variable name
        project_path: Path to project directory
    """
    console.print("\n[yellow]Info:[/yellow] API key not configured")
    console.print("\n[bold]To configure manually:[/bold]")
    console.print(f"  1. Navigate to project: [cyan]cd {project_path.name}[/cyan]")
    console.print(f"  2. Copy template: [cyan]cp .env.example .env[/cyan]")
    console.print(f"  3. Edit .env and set {key_name}")
    console.print(f"  4. Set permissions: [cyan]chmod 600 .env[/cyan]\n")


# ============================================================================
# INTERACTIVE INIT FLOW
# ============================================================================

def run_interactive_init() -> str:
    """Interactive init flow with provider/model selection.
    
    Returns:
        Navigation action ('menu', 'exit', 'chat', etc.)
    """
    console.clear()
    show_banner(context="interactive")
    console.print("\n[bold cyan]Create New Project[/bold cyan]\n")
    
    # Get dynamic data with loading indicator
    from framework.cli.templates import TemplateManager
    from rich.spinner import Spinner
    from rich.live import Live
    
    manager = TemplateManager()
    
    try:
        # Show spinner while loading
        with console.status("[dim]Loading templates and providers...[/dim]", spinner="dots"):
            templates = manager.list_app_templates()
            providers = get_provider_metadata()
    except Exception as e:
        console.print(f"[red]✗ Error loading templates/providers:[/red] {e}")
        input("\nPress ENTER to continue...")
        return 'menu'
    
    # 1. Template selection
    console.print("[bold]Step 1: Select Template[/bold]\n")
    template = select_template(templates)
    if template is None:
        return 'menu'
    
    # 2. Project name
    console.print(f"\n[bold]Step 2: Project Name[/bold]\n")
    project_name = questionary.text(
        "Project name:",
        default=get_default_name_for_template(template),
        style=custom_style
    ).ask()
    
    if not project_name:
        return 'menu'
    
    # Check if project directory already exists (before other configuration steps)
    project_path = Path.cwd() / project_name
    if project_path.exists():
        console.print(f"\n[yellow]Warning:[/yellow] Directory '{project_path}' already exists.\n")
        
        # Check if directory exists immediately before deletion (safety check) and check for active Docker/Podman mounts before allowing deletion
        has_mounts, mount_details = check_directory_has_active_mounts(project_path)
        
        if has_mounts:
            console.print("[red]⚠️  DANGER:[/red] This directory has active container mounts!")
            console.print("[yellow]The following containers are using this directory:[/yellow]\n")
            for detail in mount_details:
                console.print(f"  • {detail}")
            console.print("\n[bold]You MUST stop containers before deleting this directory:[/bold]")
            console.print(f"  [cyan]cd {project_name} && framework deploy down[/cyan]\n")
            
            proceed_anyway = questionary.confirm(
                "⚠️  Delete anyway? (This may corrupt running containers!)",
                default=False,
                style=custom_style
            ).ask()
            
            if not proceed_anyway:
                console.print("\n[yellow]✗ Project creation cancelled[/yellow]")
                console.print("[dim]Tip: Stop containers first with 'framework deploy down'[/dim]")
                input("\nPress ENTER to continue...")
                return 'menu'
        
        action = questionary.select(
            "What would you like to do?",
            choices=[
                Choice("[!] Override - Delete existing directory and create new project", value='override'),
                Choice("[*] Rename - Choose a different project name", value='rename'),
                Choice("[-] Abort - Return to main menu", value='abort'),
            ],
            style=custom_style
        ).ask()
        
        if action == 'abort' or action is None:
            console.print("\n[yellow]✗ Project creation cancelled[/yellow]")
            input("\nPress ENTER to continue...")
            return 'menu'
        elif action == 'rename':
            # Go back to project name input
            console.print("\n[bold]Choose a different project name:[/bold]\n")
            new_project_name = questionary.text(
                "Project name:",
                default=f"{project_name}-2",
                style=custom_style
            ).ask()
            
            if not new_project_name:
                return 'menu'
            
            project_name = new_project_name
            project_path = Path.cwd() / project_name
            
            # Check again if new name exists
            if project_path.exists():
                console.print(f"\n[yellow]Warning:[/yellow] Directory '{project_path}' also exists.")
                override = questionary.confirm(
                    "Override existing directory?",
                    default=False,
                    style=custom_style
                ).ask()
                
                if not override:
                    console.print("\n[yellow]✗ Project creation cancelled[/yellow]")
                    input("\nPress ENTER to continue...")
                    return 'menu'
                
                # Delete existing directory
                console.print(f"\n[dim]Removing existing directory...[/dim]")
                
                # Check directory exists immediately before deletion (TOCTOU protection)
                if not project_path.exists():
                    console.print(f"[yellow]Warning:[/yellow] Directory was already deleted by another process")
                else:
                    try:
                        shutil.rmtree(project_path)
                        console.print(f"  [green]✓[/green] Removed existing directory")
                    except PermissionError as e:
                        console.print(f"\n[red]Error:[/red] Permission denied: {e}")
                        console.print("[yellow]Try running with appropriate permissions or stop any running processes[/yellow]")
                        input("\nPress ENTER to continue...")
                        return 'menu'
                    except OSError as e:
                        console.print(f"\n[red]Error:[/red] Could not delete directory: {e}")
                        input("\nPress ENTER to continue...")
                        return 'menu'
        elif action == 'override':
            # Delete existing directory
            console.print(f"\n[dim]Removing existing directory...[/dim]")
            
            # Check directory exists immediately before deletion (TOCTOU protection)
            if not project_path.exists():
                console.print(f"[yellow]Warning:[/yellow] Directory was already deleted by another process")
            else:
                try:
                    shutil.rmtree(project_path)
                    console.print(f"  [green]✓[/green] Removed existing directory")
                except PermissionError as e:
                    console.print(f"\n[red]Error:[/red] Permission denied: {e}")
                    console.print("[yellow]Try running with appropriate permissions or stop any running processes[/yellow]")
                    input("\nPress ENTER to continue...")
                    return 'menu'
                except OSError as e:
                    console.print(f"\n[red]Error:[/red] Could not delete directory: {e}")
                    input("\nPress ENTER to continue...")
                    return 'menu'
    
    # 3. Registry style
    console.print(f"\n[bold]Step 3: Registry Style[/bold]\n")
    registry_style = questionary.select(
        "Select registry style:",
        choices=[
            Choice("compact  - Uses extend_framework_registry() helper (~10 lines)", 
                   value='compact'),
            Choice("explicit - Full framework component listing (~500 lines)", 
                   value='explicit'),
        ],
        style=custom_style,
        default='compact',
        instruction="(compact is recommended for most projects)"
    ).ask()
    
    if registry_style is None:
        return 'menu'
    
    # 4. Provider selection
    console.print(f"\n[bold]Step 4: AI Provider[/bold]\n")
    provider = select_provider(providers)
    if provider is None:
        return 'menu'
    
    # 5. Model selection
    console.print(f"\n[bold]Step 5: Model Selection[/bold]\n")
    model = select_model(provider, providers)
    if model is None:
        return 'menu'
    
    # Summary
    console.print("\n[bold cyan]Configuration Summary:[/bold cyan]")
    console.print(f"  Project:  [green]{project_name}[/green]")
    console.print(f"  Template: [green]{template}[/green]")
    console.print(f"  Registry: [green]{registry_style}[/green]")
    console.print(f"  Provider: [green]{provider}[/green]")
    console.print(f"  Model:    [green]{model}[/green]\n")
    
    # Confirm
    proceed = questionary.confirm(
        "Create project with these settings?",
        default=True,
        style=custom_style
    ).ask()
    
    if not proceed:
        console.print("\n[yellow]✗ Project creation cancelled[/yellow]")
        input("\nPress ENTER to continue...")
        return 'menu'
    
    # Create project
    console.print("\n[bold]Creating project...[/bold]\n")
    
    try:
        project_path = manager.create_project(
            project_name=project_name,
            output_dir=Path.cwd(),
            template_name=template,
            registry_style=registry_style,
            context={
                'default_provider': provider,
                'default_model': model
            }
        )
        
        console.print(f"\n[green]✓ Project created at:[/green] {project_path}\n")
        
        # Check if API keys were detected and .env was created
        detected_env = manager._detect_environment_variables()
        api_keys = ['CBORG_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
        has_api_keys = any(key in detected_env for key in api_keys)
        
        if has_api_keys:
            env_file = project_path / ".env"
            if env_file.exists():
                console.print(f"[green]✓ Created .env with detected API keys[/green]")
                detected_keys = [key for key in api_keys if key in detected_env]
                console.print(f"[dim]  Detected: {', '.join(detected_keys)}[/dim]\n")
        
        # API key configuration
        if providers[provider]['requires_key']:
            api_configured = configure_api_key(provider, project_path, providers)
        else:
            api_configured = True
        
        # Success summary
        show_success_art()
        console.print("\n[bold green]Project created successfully![/bold green]\n")
        
        # Offer to launch chat immediately
        if api_configured:
            console.print("[bold]What would you like to do next?[/bold]\n")
            
            next_action = questionary.select(
                "Select action:",
                choices=[
                    Choice("[>] Start chat in this project now", value='chat'),
                    Choice("[<] Return to main menu", value='menu'),
                ],
                style=custom_style
            ).ask()
            
            if next_action == 'chat':
                console.print(f"\n[dim]Launching chat for project: {project_path.name}[/dim]\n")
                handle_chat_action(project_path=project_path)
                return 'menu'
        else:
            console.print("[bold]Next steps:[/bold]")
            console.print(f"  1. Navigate to project: [cyan]cd {project_path.name}[/cyan]")
            console.print(f"  2. Configure API key: [cyan]cp .env.example .env[/cyan] (then edit)")
            console.print(f"  3. Start chatting: [cyan]framework chat[/cyan]")
            console.print(f"  4. Start services: [cyan]framework deploy up[/cyan]")
            
            console.print("\n[dim]Press ENTER to continue...[/dim]")
            input()
        
        return 'menu'
        
    except ValueError as e:
        # This should not happen anymore since we check directory existence above
        # But catch it just in case
        console.print(f"\n[red]✗ Error creating project:[/red] {e}")
        input("\nPress ENTER to continue...")
        return 'menu'
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected error creating project:[/red] {e}")
        if os.environ.get('DEBUG'):
            import traceback
            traceback.print_exc()
        input("\nPress ENTER to continue...")
        return 'menu'


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

def handle_project_selection(project_path: Path):
    """Handle selection of a discovered project from subdirectory.
    
    Shows project-specific menu in a loop until user chooses to go back.
    
    Args:
        project_path: Path to the selected project directory
    """
    project_name = project_path.name
    project_info = get_project_info(project_path / 'config.yml')
    
    # Loop to keep showing project menu after actions complete
    while True:
        console.clear()
        show_banner(context="interactive")
        
        console.print(f"\n[bold cyan]Selected Project:[/bold cyan] {project_name}")
        console.print(f"[dim]Location: {project_path}[/dim]")
        
        if project_info:
            console.print(f"[dim]Provider: {project_info.get('provider', 'unknown')} | "
                         f"Model: {project_info.get('model', 'unknown')}[/dim]\n")
        
        # Offer actions for the selected project
        action = questionary.select(
            "What would you like to do with this project?",
            choices=[
                Choice("[>] chat        - Start CLI conversation", value='chat'),
                Choice("[>] deploy      - Manage services (web UIs)", value='deploy'),
                Choice("[>] health      - Run system health check", value='health'),
                Choice("[>] config      - Show configuration", value='config'),
                Choice("[<] back        - Return to main menu", value='back'),
            ],
            style=custom_style,
            instruction="(Use arrow keys to navigate)"
        ).ask()
        
        if action == 'back' or action is None:
            return  # Exit the loop and return to main menu
        
        # Execute the selected action with the project path
        if action == 'chat':
            handle_chat_action(project_path=project_path)
        elif action == 'deploy':
            handle_deploy_action(project_path=project_path)
        elif action == 'health':
            handle_health_action(project_path=project_path)
        elif action == 'config':
            handle_export_action(project_path=project_path)
        
        # After action completes, loop continues and shows project menu again


def handle_chat_action(project_path: Optional[Path] = None):
    """Start chat interface - calls underlying function directly.
    
    Args:
        project_path: Optional project directory path (defaults to current directory)
    """
    try:
        from framework.interfaces.cli.direct_conversation import run_cli
    except ImportError as e:
        console.print(f"\n[red]Import Error:[/red] Could not load chat interface")
        console.print(f"[dim]{e}[/dim]")
        input("\nPress ENTER to continue...")
        return
    except Exception as e:
        # Handle pydantic compatibility issues and other import errors
        error_msg = str(e)
        console.print(f"\n[red]Dependency Error:[/red] {error_msg}\n")
        
        if "TypedDict" in error_msg and "Python < 3.12" in error_msg:
            console.print("[yellow]This appears to be a pydantic/Python version compatibility issue.[/yellow]\n")
            console.print("[bold]Possible solutions:[/bold]")
            console.print("  1. Upgrade typing_extensions:")
            console.print("     [cyan]pip install --upgrade typing-extensions[/cyan]\n")
            console.print("  2. Upgrade pydantic:")
            console.print("     [cyan]pip install --upgrade pydantic pydantic-core[/cyan]\n")
            console.print("  3. Check pydantic-ai compatibility:")
            console.print("     [cyan]pip install --upgrade pydantic-ai[/cyan]\n")
            console.print("  4. Or upgrade to Python 3.12+\n")
        else:
            console.print("[yellow]There was an error loading the chat dependencies.[/yellow]")
            console.print("[dim]Try reinstalling framework dependencies: pip install -e .[all][/dim]\n")
        
        if os.environ.get('DEBUG'):
            console.print("\n[dim]Full traceback:[/dim]")
            import traceback
            traceback.print_exc()
        
        input("\nPress ENTER to continue...")
        return
    
    console.print("\n[bold cyan]Starting Framework CLI interface...[/bold cyan]")
    console.print("   [dim]Press Ctrl+C to exit[/dim]\n")
    
    try:
        if project_path:
            # When launching chat in a specific project, we need to:
            # 1. Set CONFIG_FILE env var so config loading works
            # 2. Change to project directory so relative paths work
            config_path = str(project_path / "config.yml")
            
            # Save original state
            original_dir = Path.cwd()
            original_config_env = os.environ.get('CONFIG_FILE')
            
            try:
                # Set up environment for the project
                os.environ['CONFIG_FILE'] = config_path
                
                # Add exception handling around os.chdir() operations
                try:
                    os.chdir(project_path)
                except (OSError, PermissionError) as e:
                    console.print(f"\n[red]Error:[/red] Cannot change to project directory: {e}")
                    return
                
                # Run chat
                asyncio.run(run_cli(config_path=config_path))
                
            finally:
                # Restore original state
                try:
                    os.chdir(original_dir)
                except (OSError, PermissionError) as e:
                    # If we can't restore, at least warn the user
                    console.print(f"\n[yellow]Warning:[/yellow] Could not restore original directory: {e}")
                    console.print(f"[dim]Current directory may have changed. Original was: {original_dir}[/dim]")
                
                if original_config_env is not None:
                    os.environ['CONFIG_FILE'] = original_config_env
                elif 'CONFIG_FILE' in os.environ:
                    del os.environ['CONFIG_FILE']
        else:
            # Default behavior - run in current directory
            asyncio.run(run_cli(config_path="config.yml"))
            
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Chat session ended.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
    
    # Automatically return to menu (no need for user to press ENTER)


def handle_deploy_action(project_path: Optional[Path] = None):
    """Manage deployment services menu.
    
    Args:
        project_path: Optional project directory path (defaults to current directory)
    """
    action = questionary.select(
        "Select deployment action:",
        choices=[
            Choice("[^] up      - Start all services", value='up'),
            Choice("[v] down    - Stop all services", value='down'),
            Choice("[*] restart - Restart all services", value='restart'),
            Choice("[+] build   - Build/prepare compose files only", value='build'),
            Choice("[i] status  - Show service status", value='status'),
            Choice("[<] back    - Back to main menu", value='back'),
        ],
        style=custom_style
    ).ask()
    
    if action == 'back' or action is None:
        return
    
    import subprocess
    import sys
    
    # Determine config path
    if project_path:
        config_path = str(project_path / "config.yml")
        # Save and change directory
        original_dir = Path.cwd()
        
        try:
            os.chdir(project_path)
        except (OSError, PermissionError) as e:
            console.print(f"\n[red]Error:[/red] Cannot change to project directory: {e}")
            input("\nPress ENTER to continue...")
            return
    else:
        config_path = "config.yml"
        original_dir = None
    
    try:
        # Build the framework deploy command
        # Use 'framework' command directly to avoid module import warnings
        cmd = ["framework", "deploy", action]
        
        if action in ['up', 'restart', 'rebuild']:
            cmd.append("-d")  # Run in detached mode
        
        cmd.extend(["--config", config_path])
        
        if action == 'up':
            console.print("\n[bold]Starting services...[/bold]")
        elif action == 'down':
            console.print("\n[bold]Stopping services...[/bold]")
        elif action == 'restart':
            console.print("\n[bold]Restarting services...[/bold]")
        elif action == 'build':
            console.print("\n[bold]Building compose files...[/bold]")
        elif action == 'status':
            console.print("\n[bold]Service Status:[/bold]")
        
        try:
            # Run subprocess with timeout (5 minutes for deploy operations)
            result = subprocess.run(cmd, cwd=project_path or Path.cwd(), timeout=300)
        except subprocess.TimeoutExpired:
            console.print(f"\n[red]Error:[/red] Command timed out after 5 minutes")
            console.print("[yellow]The operation took too long. Check your container runtime.[/yellow]")
            input("\nPress ENTER to continue...")
            if original_dir:
                try:
                    os.chdir(original_dir)
                except (OSError, PermissionError):
                    pass
            return
        
        if result.returncode == 0:
            if action == 'up':
                console.print("\n[green]✓ Services started[/green]")
            elif action == 'down':
                console.print("\n[green]✓ Services stopped[/green]")
            elif action == 'restart':
                console.print("\n[green]✓ Services restarted[/green]")
            elif action == 'build':
                console.print("\n[green]✓ Compose files built[/green]")
        else:
            console.print(f"\n[yellow]Command exited with code {result.returncode}[/yellow]")
            
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original directory
        if original_dir:
            try:
                os.chdir(original_dir)
            except (OSError, PermissionError) as e:
                console.print(f"\n[yellow]Warning:[/yellow] Could not restore directory: {e}")
    
    input("\nPress ENTER to continue...")


def handle_health_action(project_path: Optional[Path] = None):
    """Run health check.
    
    Args:
        project_path: Optional project directory path (defaults to current directory)
    """
    # Save and optionally change directory
    if project_path:
        original_dir = Path.cwd()
        
        try:
            os.chdir(project_path)
        except (OSError, PermissionError) as e:
            console.print(f"\n[red]Error:[/red] Cannot change to project directory: {e}")
            input("\nPress ENTER to continue...")
            return
    else:
        original_dir = None
    
    try:
        from framework.cli.health_cmd import HealthChecker
        
        # Create and run health checker
        checker = HealthChecker(verbose=False, full=False)
        success = checker.check_all()
        
        if success:
            console.print("\n[green]✓ Health check completed successfully[/green]")
        else:
            console.print("\n[yellow]Health check completed with warnings[/yellow]")
            
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
    finally:
        # Restore original directory
        if original_dir:
            try:
                os.chdir(original_dir)
            except (OSError, PermissionError) as e:
                console.print(f"\n[yellow]Warning:[/yellow] Could not restore directory: {e}")
    
    input("\nPress ENTER to continue...")


def handle_export_action(project_path: Optional[Path] = None):
    """Show configuration export.
    
    Args:
        project_path: Optional project directory path (defaults to current directory)
    """
    try:
        from pathlib import Path
        from jinja2 import Template
        import yaml
        from rich.syntax import Syntax
        
        # If project_path provided, show that project's config
        if project_path:
            config_path = project_path / "config.yml"
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                output_str = yaml.dump(
                    config_data,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True
                )
                
                console.print(f"\n[bold]Configuration for {project_path.name}:[/bold]\n")
                syntax = Syntax(
                    output_str,
                    "yaml",
                    theme="monokai",
                    line_numbers=False,
                    word_wrap=True
                )
                console.print(syntax)
            else:
                console.print(f"[red]Error:[/red] No config.yml found in {project_path}")
        else:
            # Load framework's configuration template
            template_path = Path(__file__).parent.parent / "templates" / "project" / "config.yml.j2"
            
            if not template_path.exists():
                console.print("[red]Error:[/red] Could not locate framework configuration template.")
                console.print(f"[dim]Expected at: {template_path}[/dim]")
            else:
                # Read and render the template with example values
                with open(template_path, 'r') as f:
                    template_content = f.read()
                
                template = Template(template_content)
                rendered_config = template.render(
                    project_name="example_project",
                    package_name="example_project",
                    project_root="/path/to/example_project",
                    hostname="localhost",
                    default_provider="cborg",
                    default_model="anthropic/claude-haiku"
                )
                
                # Parse the rendered config as YAML
                config_data = yaml.safe_load(rendered_config)
                
                # Format as YAML
                output_str = yaml.dump(
                    config_data,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True
                )
                
                # Print to console with syntax highlighting
                console.print("\n[bold]Framework Default Configuration:[/bold]\n")
                syntax = Syntax(
                    output_str,
                    "yaml",
                    theme="monokai",
                    line_numbers=False,
                    word_wrap=True
                )
                console.print(syntax)
                console.print("\n[dim]Tip: Use 'framework export-config --output file.yml' to save to file[/dim]")
        
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
    
    input("\nPress ENTER to continue...")


def handle_help_action():
    """Show CLI help."""
    help_text = """
# Alpha Berkeley Framework CLI

## Main Commands

- `framework` - Launch interactive menu (you are here!)
- `framework init <project>` - Create new project
- `framework chat` - Start CLI conversation
- `framework deploy up|down|status` - Manage services
- `framework health` - Run system health check
- `framework export-config` - View configuration

## Examples

Create a new project:
    framework init my-agent

Start a conversation (from project directory):
    framework chat

Deploy web services:
    framework deploy up

## Documentation

- Documentation: https://thellert.github.io/alpha_berkeley
- GitHub: https://github.com/thellert/alpha_berkeley
- Paper: https://arxiv.org/abs/2508.15066

"""
    console.print()
    console.print(Panel(
        Markdown(help_text),
        title="[bold cyan]Framework Help[/bold cyan]",
        border_style="cyan",
        width=80
    ))
    console.print()
    input("Press ENTER to continue...")


def handle_init_help_action():
    """Show init command syntax."""
    help_text = """
# Framework Init Command

## Syntax

    framework init <project-name> [options]

## Options

- `--template` - Template to use (minimal, hello_world_weather, wind_turbine)
- `--output-dir` - Output directory (default: current directory)
- `--registry-style` - Registry style (compact, explicit)

## Examples

Create minimal project:
    framework init my-agent

Create with specific template:
    framework init weather-app --template hello_world_weather

## Interactive Mode

For an interactive guided setup, use:
    framework

Then select "Create new project (interactive)"

"""
    console.print()
    console.print(Panel(
        Markdown(help_text),
        title="[bold cyan]Init Command Help[/bold cyan]",
        border_style="cyan",
        width=80
    ))
    console.print()
    input("Press ENTER to continue...")


# ============================================================================
# NAVIGATION LOOP
# ============================================================================

def navigation_loop():
    """Main navigation loop."""
    while True:
        console.clear()
        show_banner(context="interactive")
        
        action = show_main_menu()
        
        if action is None or action == 'exit':
            console.print("\n[cyan]👋 Goodbye![/cyan]\n")
            break
        
        # Handle tuple actions (project selection)
        if isinstance(action, tuple):
            action_type, action_data = action
            
            if action_type == 'select_project':
                project_path = action_data
                handle_project_selection(project_path)
                continue
        
        # Handle string actions (standard commands)
        if action == 'init_interactive':
            next_action = run_interactive_init()
            if next_action == 'exit':
                break
        elif action == 'chat':
            handle_chat_action()
        elif action == 'deploy':
            handle_deploy_action()
        elif action == 'health':
            handle_health_action()
        elif action == 'config':
            handle_export_action()
        elif action == 'help':
            handle_help_action()
        elif action == 'init_help':
            handle_init_help_action()


# ============================================================================
# ENTRY POINT
# ============================================================================

def launch_tui():
    """Entry point for TUI mode."""
    # Check dependencies
    if not questionary:
        console.print("[red]Error:[/red] Missing required dependency 'questionary'")
        console.print("\nInstall with:")
        console.print("  [cyan]pip install questionary[/cyan]")
        console.print("\nOr install full framework dependencies:")
        console.print("  [cyan]pip install -e .[all][/cyan]\n")
        sys.exit(1)
    
    try:
        navigation_loop()
    except KeyboardInterrupt:
        console.print("\n\n[cyan]👋 Goodbye![/cyan]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error:[/red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

