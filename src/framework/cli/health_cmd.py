"""Health check command for Alpha Berkeley Framework.

This module provides the 'framework health' command which performs comprehensive
diagnostics on the framework installation and application configuration. It checks
configuration validity, file system structure, container status, API providers,
and Python environment without actually running the framework.
"""

import click
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


class HealthCheckResult:
    """Result of a health check with status and details."""
    
    def __init__(self, name: str, status: str, message: str = "", details: str = ""):
        self.name = name
        self.status = status  # "ok", "warning", "error"
        self.message = message
        self.details = details
    
    def __repr__(self):
        return f"HealthCheckResult({self.name}, {self.status})"


class HealthChecker:
    """Comprehensive health checker for Alpha Berkeley Framework."""
    
    def __init__(self, verbose: bool = False, full: bool = False):
        self.verbose = verbose
        self.full = full
        self.results: List[HealthCheckResult] = []
        self.cwd = Path.cwd()
        
        # Load .env file early so environment variables are available for all checks
        self._load_env_file()
        
    def add_result(self, name: str, status: str, message: str = "", details: str = ""):
        """Add a health check result."""
        self.results.append(HealthCheckResult(name, status, message, details))
    
    def _load_env_file(self):
        """Load .env file from current directory if it exists."""
        try:
            from dotenv import load_dotenv
            dotenv_path = self.cwd / ".env"
            if dotenv_path.exists():
                load_dotenv(dotenv_path, override=False)  # Don't override existing env vars
        except ImportError:
            # python-dotenv not available, skip loading
            pass
    
    def check_all(self) -> bool:
        """Run all health checks and return True if all passed."""
        console.print("\n[bold cyan]🏥 Alpha Berkeley Framework - Health Check[/bold cyan]\n")
        
        # Phase 1: Core checks (always run)
        self.check_configuration()
        self.check_file_system()
        self.check_python_environment()
        
        # Phase 2: Container and provider checks (always run)
        self.check_containers()
        self.check_api_providers()
        
        # Phase 3: Full model testing (only in full mode)
        if self.full:
            self.check_model_chat_completions()
        
        # Display results
        self.display_results()
        
        # Return overall status
        errors = sum(1 for r in self.results if r.status == "error")
        return errors == 0
    
    def check_configuration(self):
        """Check configuration file validity and structure."""
        console.print("[bold]Configuration[/bold]")
        
        # Check if config.yml exists
        config_path = self.cwd / "config.yml"
        if not config_path.exists():
            self.add_result(
                "config_file_exists",
                "error",
                "config.yml not found in current directory",
                f"Looking in: {self.cwd}\n"
                "Please run this command from a project directory containing config.yml"
            )
            console.print("  [red]❌ config.yml not found[/red]")
            return
        
        self.add_result("config_file_exists", "ok", f"Found at {config_path}")
        console.print(f"  [green]✅ config.yml found[/green]")
        
        # Try to load and parse YAML
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                self.add_result("yaml_valid", "error", "Config file is empty")
                console.print("  [red]❌ Config file is empty[/red]")
                return
            
            if not isinstance(config, dict):
                self.add_result("yaml_valid", "error", "Config must be a dictionary")
                console.print("  [red]❌ Invalid YAML structure[/red]")
                return
            
            self.add_result("yaml_valid", "ok", "Valid YAML syntax")
            console.print("  [green]✅ Valid YAML syntax[/green]")
            
            # Check required sections
            self._check_config_structure(config)
            
            # Check environment variables
            self._check_environment_variables(config)
            
        except yaml.YAMLError as e:
            self.add_result("yaml_valid", "error", f"YAML parsing error: {e}")
            console.print(f"  [red]❌ YAML parsing error: {e}[/red]")
        except Exception as e:
            self.add_result("yaml_valid", "error", f"Failed to read config: {e}")
            console.print(f"  [red]❌ Failed to read config: {e}[/red]")
    
    def _check_config_structure(self, config: Dict):
        """Check configuration structure and required sections."""
        
        # Check required framework models (8 total)
        required_models = [
            "orchestrator", "response", "classifier", "approval",
            "task_extraction", "memory", "python_code_generator", "time_parsing"
        ]
        
        models = config.get("models", {})
        missing_models = [m for m in required_models if m not in models]
        
        if missing_models:
            self.add_result(
                "required_models",
                "error",
                f"Missing required models: {', '.join(missing_models)}",
                "Framework requires 8 models: " + ", ".join(required_models)
            )
            console.print(f"  [red]❌ Missing required models: {', '.join(missing_models)}[/red]")
        else:
            self.add_result("required_models", "ok", f"All {len(required_models)} required models defined")
            console.print(f"  [green]✅ All {len(required_models)} required models defined[/green]")
        
        # Check model configurations
        invalid_models = []
        for model_name, model_config in models.items():
            if not isinstance(model_config, dict):
                invalid_models.append(model_name)
                continue
            if "provider" not in model_config:
                invalid_models.append(f"{model_name} (missing provider)")
            if "model_id" not in model_config:
                invalid_models.append(f"{model_name} (missing model_id)")
        
        if invalid_models:
            self.add_result(
                "model_configs_valid",
                "warning",
                f"Invalid model configurations: {', '.join(invalid_models)}"
            )
            console.print(f"  [yellow]⚠️  Invalid model configs: {', '.join(invalid_models)}[/yellow]")
        else:
            self.add_result("model_configs_valid", "ok", "All model configurations valid")
            console.print("  [green]✅ All model configurations valid[/green]")
        
        # Check deployed_services
        deployed_services = config.get("deployed_services", [])
        if not deployed_services:
            self.add_result(
                "deployed_services",
                "warning",
                "No deployed services configured"
            )
            console.print("  [yellow]⚠️  No deployed services configured[/yellow]")
        else:
            self.add_result(
                "deployed_services",
                "ok",
                f"{len(deployed_services)} services configured: {', '.join(deployed_services)}"
            )
            console.print(f"  [green]✅ {len(deployed_services)} services configured[/green]")
        
        # Check if services defined in deployed_services exist in services section
        services = config.get("services", {})
        undefined_services = [s for s in deployed_services if s not in services]
        if undefined_services:
            self.add_result(
                "service_definitions",
                "error",
                f"Services not defined: {', '.join(undefined_services)}"
            )
            console.print(f"  [red]❌ Undefined services: {', '.join(undefined_services)}[/red]")
        else:
            self.add_result("service_definitions", "ok", "All deployed services defined")
            if deployed_services:  # Only print if there are services
                console.print("  [green]✅ All deployed services defined[/green]")
        
        # Check API providers
        api_providers = config.get("api", {}).get("providers", {})
        if not api_providers:
            self.add_result(
                "api_providers",
                "warning",
                "No API providers configured"
            )
            console.print("  [yellow]⚠️  No API providers configured[/yellow]")
        else:
            self.add_result(
                "api_providers",
                "ok",
                f"{len(api_providers)} providers configured: {', '.join(api_providers.keys())}"
            )
            console.print(f"  [green]✅ {len(api_providers)} API providers configured[/green]")
    
    def _check_environment_variables(self, config: Dict):
        """Check if environment variables referenced in config are set."""
        import re
        
        # Find all ${VAR_NAME} patterns in config
        config_str = str(config)
        env_vars = re.findall(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}', config_str)
        env_vars = list(set(env_vars))  # Remove duplicates
        
        missing_vars = [var for var in env_vars if var not in os.environ]
        
        if missing_vars:
            self.add_result(
                "environment_variables",
                "warning",
                f"Missing environment variables: {', '.join(missing_vars)}",
                "These variables are referenced in config.yml but not set in environment"
            )
            console.print(f"  [yellow]⚠️  Missing env vars: {', '.join(missing_vars)}[/yellow]")
        else:
            if env_vars:
                self.add_result(
                    "environment_variables",
                    "ok",
                    f"All {len(env_vars)} environment variables set"
                )
                console.print(f"  [green]✅ All {len(env_vars)} environment variables set[/green]")
    
    def check_file_system(self):
        """Check file system structure and permissions."""
        console.print("\n[bold]File System[/bold]")
        
        # Check project root
        project_root_env = os.environ.get("PROJECT_ROOT")
        if project_root_env:
            project_root = Path(project_root_env)
            if project_root.exists():
                self.add_result("project_root", "ok", f"PROJECT_ROOT set and exists: {project_root}")
                console.print(f"  [green]✅ PROJECT_ROOT: {project_root}[/green]")
            else:
                self.add_result(
                    "project_root",
                    "warning",
                    f"PROJECT_ROOT set but path does not exist: {project_root}"
                )
                console.print(f"  [yellow]⚠️  PROJECT_ROOT path not found: {project_root}[/yellow]")
        else:
            self.add_result("project_root", "warning", "PROJECT_ROOT not set")
            console.print("  [yellow]⚠️  PROJECT_ROOT environment variable not set[/yellow]")
        
        # Check .env file
        env_file = self.cwd / ".env"
        if env_file.exists():
            self.add_result("env_file", "ok", f".env file found")
            console.print("  [green]✅ .env file found[/green]")
        else:
            self.add_result("env_file", "warning", ".env file not found")
            console.print("  [yellow]⚠️  .env file not found[/yellow]")
        
        # Check registry file (if specified in config)
        try:
            config_path = self.cwd / "config.yml"
            if config_path.exists():
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                registry_path_str = config.get("registry_path")
                if registry_path_str:
                    # Resolve environment variables in path
                    registry_path_str = os.path.expandvars(registry_path_str)
                    registry_path = self.cwd / registry_path_str
                    
                    if registry_path.exists():
                        self.add_result("registry_file", "ok", f"Registry file found: {registry_path}")
                        console.print(f"  [green]✅ Registry file found[/green]")
                    else:
                        self.add_result(
                            "registry_file",
                            "error",
                            f"Registry file not found: {registry_path}"
                        )
                        console.print(f"  [red]❌ Registry file not found: {registry_path}[/red]")
        except Exception as e:
            # Don't fail if we can't check registry
            pass
        
        # Check agent data directory
        agent_data_dir = self.cwd / "_agent_data"
        if agent_data_dir.exists():
            if os.access(agent_data_dir, os.W_OK):
                self.add_result("agent_data_dir", "ok", "Agent data directory exists and is writable")
                console.print("  [green]✅ Agent data directory writable[/green]")
            else:
                self.add_result(
                    "agent_data_dir",
                    "warning",
                    "Agent data directory exists but is not writable"
                )
                console.print("  [yellow]⚠️  Agent data directory not writable[/yellow]")
        else:
            self.add_result(
                "agent_data_dir",
                "warning",
                "Agent data directory does not exist yet (will be created on first run)"
            )
            console.print("  [yellow]⚠️  Agent data directory not created yet[/yellow]")
        
        # Check disk space
        try:
            stat = shutil.disk_usage(self.cwd)
            free_gb = stat.free / (1024**3)
            
            if free_gb < 1.0:
                self.add_result("disk_space", "warning", f"Low disk space: {free_gb:.1f} GB free")
                console.print(f"  [yellow]⚠️  Low disk space: {free_gb:.1f} GB free[/yellow]")
            else:
                self.add_result("disk_space", "ok", f"{free_gb:.1f} GB free")
                console.print(f"  [green]✅ Disk space: {free_gb:.1f} GB free[/green]")
        except Exception as e:
            self.add_result("disk_space", "warning", f"Could not check disk space: {e}")
    
    def check_python_environment(self):
        """Check Python version and dependencies."""
        console.print("\n[bold]Python Environment[/bold]")
        
        # Check Python version
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            self.add_result(
                "python_version",
                "warning",
                f"Python {version_str} (recommended: 3.11+)"
            )
            console.print(f"  [yellow]⚠️  Python {version_str} (recommended: 3.11+)[/yellow]")
        else:
            self.add_result("python_version", "ok", f"Python {version_str}")
            console.print(f"  [green]✅ Python {version_str}[/green]")
        
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            self.add_result("virtual_environment", "ok", "Virtual environment active")
            console.print("  [green]✅ Virtual environment active[/green]")
        else:
            self.add_result(
                "virtual_environment",
                "warning",
                "Not in a virtual environment"
            )
            console.print("  [yellow]⚠️  Not in a virtual environment[/yellow]")
        
        # Check core dependencies
        core_deps = [
            "click", "rich", "yaml", "jinja2",
            "pydantic_ai", "langgraph", "langchain_core"
        ]
        
        missing_deps = []
        for dep in core_deps:
            # Handle special cases
            import_name = dep
            if dep == "yaml":
                import_name = "yaml"
            elif dep == "pydantic_ai":
                import_name = "pydantic_ai"
            elif dep == "langchain_core":
                import_name = "langchain_core"
            
            try:
                __import__(import_name)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            self.add_result(
                "core_dependencies",
                "error",
                f"Missing dependencies: {', '.join(missing_deps)}"
            )
            console.print(f"  [red]❌ Missing dependencies: {', '.join(missing_deps)}[/red]")
        else:
            self.add_result("core_dependencies", "ok", f"All {len(core_deps)} core dependencies installed")
            console.print(f"  [green]✅ Core dependencies installed ({len(core_deps)}/{len(core_deps)})[/green]")
    
    def check_containers(self):
        """Check container runtime and deployed services."""
        console.print("\n[bold]Container Infrastructure[/bold]")
        
        # Check if podman is available
        try:
            result = subprocess.run(
                ["podman", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.add_result("podman_available", "ok", version)
                console.print(f"  [green]✅ {version}[/green]")
                
                # Check container status
                self._check_container_status()
            else:
                self.add_result("podman_available", "error", "Podman command failed")
                console.print("  [red]❌ Podman not working properly[/red]")
        except FileNotFoundError:
            self.add_result("podman_available", "warning", "Podman not found in PATH")
            console.print("  [yellow]⚠️  Podman not installed or not in PATH[/yellow]")
        except Exception as e:
            self.add_result("podman_available", "warning", f"Could not check Podman: {e}")
            console.print(f"  [yellow]⚠️  Could not check Podman: {e}[/yellow]")
    
    def _check_container_status(self):
        """Check status of deployed containers."""
        try:
            # Load config to get deployed services
            config_path = self.cwd / "config.yml"
            if not config_path.exists():
                return
            
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            deployed_services = config.get("deployed_services", [])
            if not deployed_services:
                return
            
            # Get all containers
            result = subprocess.run(
                ["podman", "ps", "-a", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return
            
            containers = json.loads(result.stdout) if result.stdout.strip() else []
            
            # Check each expected service
            for service in deployed_services:
                # Look for containers matching the service name
                matching = [c for c in containers if service.lower() in str(c.get("Names", [])).lower()]
                
                if matching:
                    container = matching[0]
                    state = container.get("State", "unknown")
                    
                    if state == "running":
                        self.add_result(
                            f"container_{service}",
                            "ok",
                            f"{service}: running"
                        )
                        console.print(f"  [green]✅ {service}: running[/green]")
                    else:
                        self.add_result(
                            f"container_{service}",
                            "warning",
                            f"{service}: {state}"
                        )
                        console.print(f"  [yellow]⚠️  {service}: {state}[/yellow]")
                else:
                    self.add_result(
                        f"container_{service}",
                        "warning",
                        f"{service}: not found"
                    )
                    console.print(f"  [yellow]⚠️  {service}: not deployed[/yellow]")
        
        except Exception as e:
            # Don't fail the health check if container status can't be determined
            if self.verbose:
                console.print(f"  [dim]Could not check container status: {e}[/dim]")
    
    def check_api_providers(self):
        """Check API provider configurations and connectivity."""
        console.print("\n[bold]API Providers[/bold]")
        
        try:
            config_path = self.cwd / "config.yml"
            if not config_path.exists():
                return
            
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            api_config = config.get("api", {}).get("providers", {})
            
            for provider_name, provider_config in api_config.items():
                self._check_provider(provider_name, provider_config)
        
        except Exception as e:
            if self.verbose:
                console.print(f"  [dim]Could not check API providers: {e}[/dim]")
    
    def _check_provider(self, provider_name: str, provider_config: Dict):
        """Check a specific API provider."""
        # Check if API key is set
        api_key = provider_config.get("api_key", "")
        
        # Check if it's an environment variable reference
        if api_key.startswith("${") and api_key.endswith("}"):
            var_name = api_key[2:-1]
            api_key = os.environ.get(var_name, "")
        
        if provider_name == "ollama":
            # Ollama doesn't need an API key, always test connectivity (it's free)
            base_url = provider_config.get("base_url")
            if base_url:
                # Try to test Ollama connection
                try:
                    from framework.models.factory import _test_ollama_connection
                    if _test_ollama_connection(base_url):
                        self.add_result(
                            f"provider_{provider_name}",
                            "ok",
                            f"{provider_name}: accessible at {base_url}"
                        )
                        console.print(f"  [green]✅ {provider_name}: accessible[/green]")
                    else:
                        self.add_result(
                            f"provider_{provider_name}",
                            "warning",
                            f"{provider_name}: not accessible at {base_url}"
                        )
                        console.print(f"  [yellow]⚠️  {provider_name}: not accessible[/yellow]")
                except Exception as e:
                    self.add_result(
                        f"provider_{provider_name}",
                        "warning",
                        f"{provider_name}: could not test connection"
                    )
                    console.print(f"  [yellow]⚠️  {provider_name}: could not test[/yellow]")
            else:
                self.add_result(
                    f"provider_{provider_name}",
                    "warning",
                    f"{provider_name}: no base_url configured"
                )
                console.print(f"  [yellow]⚠️  {provider_name}: no base_url[/yellow]")
        else:
            # For other providers, check if API key is set first
            if not api_key or api_key == "your-api-key-here" or api_key.startswith("${"):
                self.add_result(
                    f"provider_{provider_name}",
                    "warning",
                    f"{provider_name}: API key not set"
                )
                console.print(f"  [yellow]⚠️  {provider_name}: API key not set[/yellow]")
                return
            
            # API key is set - always test connectivity (it's fast and essentially free)
            self._test_provider_connectivity(provider_name, provider_config, api_key)
    
    def _test_provider_connectivity(self, provider_name: str, provider_config: Dict, api_key: str):
        """Test API endpoint connectivity (lightweight check, always runs)."""
        try:
            import requests
            
            base_url = provider_config.get("base_url")
            
            # Provider-specific connectivity tests
            if provider_name in ["openai", "cborg"]:
                # OpenAI-compatible API: test /v1/models endpoint
                if not base_url:
                    base_url = "https://api.openai.com/v1" if provider_name == "openai" else None
                
                if base_url:
                    test_url = base_url.rstrip('/') + '/models'
                    headers = {"Authorization": f"Bearer {api_key}"}
                    
                    response = requests.get(test_url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        self.add_result(
                            f"provider_{provider_name}",
                            "ok",
                            f"{provider_name}: API accessible and authenticated"
                        )
                        console.print(f"  [green]✅ {provider_name}: API accessible ✓[/green]")
                    elif response.status_code == 401:
                        self.add_result(
                            f"provider_{provider_name}",
                            "warning",
                            f"{provider_name}: Authentication failed (invalid API key?)"
                        )
                        console.print(f"  [yellow]⚠️  {provider_name}: Authentication failed[/yellow]")
                    else:
                        self.add_result(
                            f"provider_{provider_name}",
                            "warning",
                            f"{provider_name}: API returned status {response.status_code}"
                        )
                        console.print(f"  [yellow]⚠️  {provider_name}: Status {response.status_code}[/yellow]")
                else:
                    # No base_url, skip connectivity test
                    self.add_result(
                        f"provider_{provider_name}",
                        "ok",
                        f"{provider_name}: API key set (connectivity not tested)"
                    )
                    console.print(f"  [green]✅ {provider_name}: API key set[/green]")
            
            elif provider_name == "anthropic":
                # Anthropic: use a lightweight validation approach
                # Note: Anthropic doesn't have a free "list models" endpoint
                # We'll just check if the key format looks valid
                if api_key.startswith("sk-ant-"):
                    self.add_result(
                        f"provider_{provider_name}",
                        "ok",
                        f"{provider_name}: API key format valid (connectivity test skipped to avoid charges)"
                    )
                    console.print(f"  [green]✅ {provider_name}: API key format valid[/green]")
                else:
                    self.add_result(
                        f"provider_{provider_name}",
                        "warning",
                        f"{provider_name}: API key format unusual (expected to start with 'sk-ant-')"
                    )
                    console.print(f"  [yellow]⚠️  {provider_name}: Unusual key format[/yellow]")
            
            elif provider_name in ["google", "gemini"]:
                # Google: similar approach, avoid actual API call to prevent charges
                # Just confirm the key is set and looks reasonable
                if len(api_key) > 20:  # Google API keys are typically long
                    self.add_result(
                        f"provider_{provider_name}",
                        "ok",
                        f"{provider_name}: API key set (connectivity test skipped to avoid charges)"
                    )
                    console.print(f"  [green]✅ {provider_name}: API key set[/green]")
                else:
                    self.add_result(
                        f"provider_{provider_name}",
                        "warning",
                        f"{provider_name}: API key seems short (may be invalid)"
                    )
                    console.print(f"  [yellow]⚠️  {provider_name}: Key seems short[/yellow]")
            
            else:
                # Unknown provider: just confirm key is set
                self.add_result(
                    f"provider_{provider_name}",
                    "ok",
                    f"{provider_name}: API key set"
                )
                console.print(f"  [green]✅ {provider_name}: API key set[/green]")
        
        except requests.Timeout:
            self.add_result(
                f"provider_{provider_name}",
                "warning",
                f"{provider_name}: Connection timeout"
            )
            console.print(f"  [yellow]⚠️  {provider_name}: Timeout[/yellow]")
        except requests.RequestException as e:
            self.add_result(
                f"provider_{provider_name}",
                "warning",
                f"{provider_name}: Connection failed: {str(e)[:50]}"
            )
            console.print(f"  [yellow]⚠️  {provider_name}: Connection failed[/yellow]")
        except Exception as e:
            self.add_result(
                f"provider_{provider_name}",
                "warning",
                f"{provider_name}: Could not test connectivity: {str(e)[:50]}"
            )
            console.print(f"  [yellow]⚠️  {provider_name}: Test failed[/yellow]")
    
    def check_model_chat_completions(self):
        """Test actual chat completions with each unique model (full mode only)."""
        console.print("\n[bold]Model Chat Completions (Full Test)[/bold]")
        console.print("  [dim]Testing actual chat completion with each unique model...[/dim]")
        
        try:
            # Load config to get models
            config_path = self.cwd / "config.yml"
            if not config_path.exists():
                return
            
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            models = config.get("models", {})
            if not models:
                console.print("  [yellow]⚠️  No models configured[/yellow]")
                return
            
            # Extract unique (provider, model_id) pairs
            unique_models = set()
            for model_name, model_config in models.items():
                if not isinstance(model_config, dict):
                    continue
                
                provider = model_config.get("provider")
                model_id = model_config.get("model_id")
                
                if provider and model_id:
                    unique_models.add((provider, model_id))
            
            if not unique_models:
                console.print("  [yellow]⚠️  No valid models found[/yellow]")
                return
            
            console.print(f"  [dim]Found {len(unique_models)} unique model(s) to test[/dim]\n")
            
            # Test each unique model
            for provider, model_id in sorted(unique_models):
                self._test_model_chat(provider, model_id)
        
        except Exception as e:
            if self.verbose:
                console.print(f"  [dim]Could not test model completions: {e}[/dim]")
    
    def _test_model_chat(self, provider: str, model_id: str):
        """Test a single model with a minimal chat completion."""
        model_label = f"{provider}/{model_id}"
        
        # Show that we're testing this model
        console.print(f"  [dim]Testing {model_label}...[/dim]", end=" ")
        
        try:
            # Use the simple get_chat_completion function
            from framework.models.completion import get_chat_completion
            
            # Simple test prompt
            test_message = "Reply with exactly: OK"
            
            # Call get_chat_completion with a timeout
            try:
                response = get_chat_completion(
                    message=test_message,
                    provider=provider,
                    model_id=model_id,
                    max_tokens=50  # Keep it minimal
                )
                
                # If we got here without exception and have a response, the model works
                if response and isinstance(response, str) and len(response.strip()) > 0:
                    self.add_result(
                        f"model_chat_{provider}_{model_id}",
                        "ok",
                        f"{model_label}: Chat completion successful"
                    )
                    console.print(f"[green]✅ Working[/green]")
                else:
                    self.add_result(
                        f"model_chat_{provider}_{model_id}",
                        "warning",
                        f"{model_label}: Empty response"
                    )
                    console.print(f"[yellow]⚠️  Empty response[/yellow]")
            
            except Exception as e:
                # Check if it's a timeout-like error
                error_msg = str(e)
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    self.add_result(
                        f"model_chat_{provider}_{model_id}",
                        "warning",
                        f"{model_label}: Timeout"
                    )
                    console.print(f"[yellow]⚠️  Timeout[/yellow]")
                else:
                    # Some other error
                    display_msg = error_msg[:80] + "..." if len(error_msg) > 80 else error_msg
                    self.add_result(
                        f"model_chat_{provider}_{model_id}",
                        "error",
                        f"{model_label}: {error_msg}"
                    )
                    console.print(f"[red]❌ Failed[/red]")
                    console.print(f"     [dim]{display_msg}[/dim]")
                return
        
        except KeyboardInterrupt:
            # Re-raise keyboard interrupt so user can stop
            raise
        
        except Exception as e:
            error_msg = str(e)
            # Truncate for display
            display_msg = error_msg[:80] + "..." if len(error_msg) > 80 else error_msg
            
            self.add_result(
                f"model_chat_{provider}_{model_id}",
                "error",
                f"{model_label}: {error_msg}"
            )
            console.print(f"[red]❌ Failed[/red]")
            
            # Always show error details in full mode (not just verbose)
            console.print(f"     [dim]{display_msg}[/dim]")
    
    def display_results(self):
        """Display summary of health check results."""
        console.print()
        
        # Count results by status
        ok_count = sum(1 for r in self.results if r.status == "ok")
        warning_count = sum(1 for r in self.results if r.status == "warning")
        error_count = sum(1 for r in self.results if r.status == "error")
        total_count = len(self.results)
        
        # Build the content for the panel
        panel_content = []
        
        # Create summary line
        summary = f"Summary: {ok_count}/{total_count} checks passed"
        if warning_count > 0:
            summary += f" ({warning_count} warning{'s' if warning_count > 1 else ''})"
        if error_count > 0:
            summary += f" ({error_count} error{'s' if error_count > 1 else ''})"
        
        panel_content.append(summary)
        
        # Show detailed errors and warnings if verbose
        if self.verbose and (warning_count > 0 or error_count > 0):
            panel_content.append("")  # Empty line
            panel_content.append("Details:")
            for result in self.results:
                if result.status in ["warning", "error"]:
                    symbol = "⚠️ " if result.status == "warning" else "❌"
                    panel_content.append(f"  {symbol} {result.name}: {result.message}")
                    if result.details:
                        panel_content.append(f"     {result.details}")
        
        # Create and display the framed panel
        panel = Panel(
            "\n".join(panel_content),
            title="🏥 Framework Health Check Results",
            border_style="dim cyan",
            expand=False,
            padding=(1, 2)
        )
        console.print(panel)


@click.command()
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed information about warnings and errors"
)
@click.option(
    "--full", "-f",
    is_flag=True,
    help="Test actual chat completions with each unique model (may incur small API costs)"
)
def health(verbose: bool, full: bool):
    """Check the health of your Framework installation and configuration.
    
    This command performs comprehensive diagnostics without actually running
    the framework.
    
    Basic Mode (default):
    \b
      • Configuration file validity and structure
      • Required models and services configuration  
      • File system structure and permissions
      • Python version and dependencies
      • Container runtime availability
      • Container status (running/stopped)
      • API provider endpoint connectivity (lightweight tests)
        - Ollama: Connection test
        - OpenAI/CBORG: GET /v1/models endpoint
        - Anthropic/Google: Key format validation
    
    Full Mode (--full):
    \b
      • All basic checks, plus:
      • Actual chat completion tests with each unique model
      • Tests each unique (provider, model_id) pair only once
      • Sends minimal test prompt and verifies response
      • May incur small API costs (~$0.001-0.01 per model)
      • Takes longer (30s timeout per model)
    
    The health check must be run from a project directory containing
    config.yml (e.g., als_assistant, weather).
    
    Exit Codes:
    \b
      0 - All checks passed
      1 - Some warnings detected (non-critical)
      2 - Errors detected (critical issues)
    
    Examples:
    
    \b
      # Standard health check (includes endpoint tests)
      $ framework health
      
      # Verbose output with detailed error messages
      $ framework health --verbose
      
      # Full test with actual chat completions
      $ framework health --full
      
      # Full test with detailed output
      $ framework health --full --verbose
    """
    
    try:
        checker = HealthChecker(verbose=verbose, full=full)
        success = checker.check_all()
        
        # Determine exit code
        error_count = sum(1 for r in checker.results if r.status == "error")
        warning_count = sum(1 for r in checker.results if r.status == "warning")
        
        if error_count > 0:
            console.print("\n[red]❌ Health check failed with errors[/red]")
            sys.exit(2)
        elif warning_count > 0:
            console.print("\n[yellow]⚠️  Health check completed with warnings[/yellow]")
            sys.exit(1)
        else:
            console.print("\n[green]✅ All health checks passed![/green]")
            sys.exit(0)
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Health check interrupted[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]❌ Health check failed: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(3)

