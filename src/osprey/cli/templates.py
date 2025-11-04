"""Template management for project scaffolding.

This module provides the TemplateManager class which handles:
- Discovery of bundled templates in the osprey package
- Rendering Jinja2 templates with project-specific context
- Creating complete project structures from templates
- Copying service configurations to user projects
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from osprey.cli.styles import console


class TemplateManager:
    """Manages project templates and scaffolding.

    This class handles all template-related operations for creating new
    projects from bundled templates. It uses Jinja2 for template rendering
    and provides methods for project structure creation.

    Attributes:
        template_root: Path to osprey's bundled templates directory
        jinja_env: Jinja2 environment for template rendering
    """

    def __init__(self):
        """Initialize template manager with osprey templates.

        Discovers the template directory from the installed osprey package
        using importlib, which works both in development and after pip install.
        """
        self.template_root = self._get_template_root()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_root)),
            autoescape=select_autoescape(['html', 'xml']),
            keep_trailing_newline=True
        )

    def _get_template_root(self) -> Path:
        """Get path to osprey templates directory.

        Returns:
            Path to the templates directory in the osprey package

        Raises:
            RuntimeError: If templates directory cannot be found
        """
        try:
            # Try to import osprey.templates to find its location
            import osprey.templates
            template_path = Path(osprey.templates.__file__).parent
            if template_path.exists():
                return template_path
        except (ImportError, AttributeError):
            pass

        # Fallback for development: relative to this file
        fallback_path = Path(__file__).parent.parent / "templates"
        if fallback_path.exists():
            return fallback_path

        raise RuntimeError(
            "Could not locate osprey templates directory. "
            "Ensure osprey is properly installed."
        )

    def _detect_environment_variables(self) -> Dict[str, str]:
        """Detect environment variables from the system for use in templates.

        This method checks for common environment variables that are typically
        needed in .env files (API keys, paths, etc.) and returns those that are
        currently set in the system.

        Returns:
            Dictionary of detected environment variables with their values.
            Only includes variables that are actually set (non-empty).

        Examples:
            >>> manager = TemplateManager()
            >>> env_vars = manager._detect_environment_variables()
            >>> env_vars.get('OPENAI_API_KEY')  # Returns key if set, None otherwise
        """
        # List of environment variables we want to detect and potentially use
        env_vars_to_check = [
            'CBORG_API_KEY',
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'GOOGLE_API_KEY',
            'PROJECT_ROOT',
            'LOCAL_PYTHON_VENV',
            'TZ',
        ]

        detected = {}
        for var in env_vars_to_check:
            value = os.environ.get(var)
            if value:  # Only include if the variable is set and non-empty
                detected[var] = value

        return detected

    def list_app_templates(self) -> List[str]:
        """List available application templates.

        Returns:
            List of template names (directory names in templates/apps/)

        Examples:
            >>> manager = TemplateManager()
            >>> manager.list_app_templates()
            ['minimal', 'hello_world_weather', 'wind_turbine']
        """
        apps_dir = self.template_root / "apps"
        if not apps_dir.exists():
            return []

        return sorted([
            d.name for d in apps_dir.iterdir() 
            if d.is_dir() and not d.name.startswith('_')
        ])

    def render_template(self, template_path: str, context: Dict[str, Any], output_path: Path):
        """Render a single template file.

        Args:
            template_path: Relative path to template within templates directory
            context: Dictionary of variables for template rendering
            output_path: Path where rendered output should be written

        Raises:
            jinja2.TemplateNotFound: If template file doesn't exist
            IOError: If output file cannot be written
        """
        template = self.jinja_env.get_template(template_path)
        rendered = template.render(**context)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered)

    def create_project(
        self,
        project_name: str,
        output_dir: Path,
        template_name: str = "minimal",
        registry_style: str = "compact",
        context: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Create complete project from template.

        This is the main entry point for project creation. It:
        1. Validates template exists
        2. Creates project directory structure
        3. Renders and copies project files
        4. Copies service configurations
        5. Creates application code from template

        Args:
            project_name: Name of the project (e.g., "my-assistant")
            output_dir: Parent directory where project will be created
            template_name: Application template to use (default: "minimal")
            registry_style: Registry style - "compact" (uses helper) or "explicit" (full listing)
            context: Additional template context variables

        Returns:
            Path to created project directory

        Raises:
            ValueError: If template doesn't exist or project directory exists

        Examples:
            >>> manager = TemplateManager()
            >>> project_dir = manager.create_project(
            ...     "my-assistant",
            ...     Path("/projects"),
            ...     template_name="minimal",
            ...     registry_style="compact"
            ... )
            >>> print(project_dir)
            /projects/my-assistant
        """
        # 1. Validate template exists
        app_templates = self.list_app_templates()
        if template_name not in app_templates:
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available templates: {', '.join(app_templates)}"
            )

        # 2. Setup project directory
        project_dir = output_dir / project_name
        if project_dir.exists():
            raise ValueError(
                f"Directory '{project_dir}' already exists. "
                "Please choose a different project name or location."
            )

        project_dir.mkdir(parents=True)

        # 3. Prepare template context
        package_name = project_name.replace("-", "_").lower()
        class_name = self._generate_class_name(package_name)

        # Detect current Python environment
        import sys
        current_python = sys.executable

        # Detect environment variables from the system
        detected_env_vars = self._detect_environment_variables()

        ctx = {
            "project_name": project_name,
            "package_name": package_name,
            "app_display_name": project_name,  # Used in templates for display/documentation
            "app_class_name": class_name,  # Used in templates for class names
            "registry_class_name": class_name,  # Backward compatibility
            "project_description": f"{project_name} - Osprey Agent Application",
            "framework_version": self._get_framework_version(),
            "project_root": str(project_dir.absolute()),
            "venv_path": "${LOCAL_PYTHON_VENV}",
            "current_python_env": current_python,  # Actual path to current Python
            "default_provider": "cborg",
            "default_model": "anthropic/claude-haiku",
            # Add detected environment variables
            "env": detected_env_vars,
            **(context or {})
        }

        # 4. Create project structure
        self._create_project_structure(project_dir, template_name, ctx)

        # 5. Copy services
        self.copy_services(project_dir)

        # 6. Create src directory and application code
        src_dir = project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        self._create_application_code(src_dir, package_name, template_name, ctx, registry_style)

        # 7. Create _agent_data directory structure
        self._create_agent_data_structure(project_dir, ctx)

        return project_dir

    def _create_project_structure(self, project_dir: Path, template_name: str, ctx: Dict):
        """Create base project files (config, README, pyproject.toml, etc.).

        Args:
            project_dir: Root directory of the project
            template_name: Name of the application template being used
            ctx: Template context variables
        """
        project_template_dir = self.template_root / "project"

        # Render template files
        files_to_render = [
            ("config.yml.j2", "config.yml"),
            ("env.example.j2", ".env.example"),
            ("README.md.j2", "README.md"),
            ("pyproject.toml.j2", "pyproject.toml"),
            ("requirements.txt", "requirements.txt"),  # Render to replace framework_version
        ]

        # Copy static files
        static_files = [
            # requirements.txt moved to rendered templates to handle {{ framework_version }}
        ]

        for template_file, output_file in files_to_render:
            template_path = project_template_dir / template_file
            if template_path.exists():
                self.render_template(
                    f"project/{template_file}",
                    ctx,
                    project_dir / output_file
                )

        # Create .env file only if API keys are detected
        detected_env_vars = ctx.get('env', {})
        api_keys = ['CBORG_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
        has_api_keys = any(key in detected_env_vars for key in api_keys)

        if has_api_keys:
            env_template = project_template_dir / "env.j2"
            if env_template.exists():
                self.render_template(
                    "project/env.j2",
                    ctx,
                    project_dir / ".env"
                )
                # Set proper permissions (owner read/write only)
                import os
                os.chmod(project_dir / ".env", 0o600)

        # Copy static files
        for src_name, dst_name in static_files:
            src_file = project_template_dir / src_name
            if src_file.exists():
                shutil.copy(src_file, project_dir / dst_name)

        # Copy gitignore (renamed from 'gitignore' to '.gitignore')
        gitignore_source = project_template_dir / "gitignore"
        if gitignore_source.exists():
            shutil.copy(gitignore_source, project_dir / ".gitignore")

    def copy_services(self, project_dir: Path):
        """Copy service configurations to project (flattened structure).

        Services are copied with a flattened structure (not nested under osprey/).
        This makes the user's project structure cleaner.

        Args:
            project_dir: Root directory of the project
        """
        src_services = self.template_root / "services"
        dst_services = project_dir / "services"

        if not src_services.exists():
            return

        dst_services.mkdir(parents=True, exist_ok=True)

        # Copy each service directory individually (flattened)
        for item in src_services.iterdir():
            if item.is_dir():
                shutil.copytree(item, dst_services / item.name, dirs_exist_ok=True)
            elif item.is_file() and item.suffix in ['.j2', '.yml', '.yaml']:
                # Copy docker-compose template/config files
                shutil.copy(item, dst_services / item.name)

    def _create_application_code(
        self, 
        project_dir: Path, 
        package_name: str, 
        template_name: str, 
        ctx: Dict,
        registry_style: str = "compact"
    ):
        """Create application code from template.

        Args:
            project_dir: Root directory of the project
            package_name: Python package name (e.g., "my_assistant")
            template_name: Name of the application template
            ctx: Template context variables
            registry_style: Registry style - "compact" or "explicit"

        Note:
            Currently, both compact and explicit styles use the same template.
            Future enhancement: Generate explicit registry.py dynamically with
            all framework components listed when registry_style=="explicit".
        """
        app_template_dir = self.template_root / "apps" / template_name
        app_dir = project_dir / package_name
        app_dir.mkdir(parents=True)

        # Add registry_style to context for templates that might use it
        ctx['registry_style'] = registry_style

        # Process all files in the template
        for template_file in app_template_dir.rglob("*"):
            if not template_file.is_file():
                continue

            rel_path = template_file.relative_to(app_template_dir)

            # Determine output path
            if template_file.suffix == ".j2":
                # Template file - render it
                output_name = template_file.stem  # Remove .j2 extension
                output_path = app_dir / rel_path.parent / output_name

                # TODO: For explicit style, generate registry.py dynamically
                # if registry_style == "explicit" and output_name == "registry.py":
                #     self._generate_explicit_registry(output_path, ctx)
                # else:
                #     self.render_template(...)

                self.render_template(
                    f"apps/{template_name}/{rel_path}",
                    ctx,
                    output_path
                )
            else:
                # Static file - copy directly
                output_path = app_dir / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(template_file, output_path)

    def _get_framework_version(self) -> str:
        """Get current osprey version.

        Returns:
            Version string (e.g., "0.7.0")
        """
        try:
            from osprey import __version__
            return __version__
        except (ImportError, AttributeError):
            return "0.7.0"

    def _generate_class_name(self, package_name: str) -> str:
        """Generate a PascalCase class name prefix from package name.

        Args:
            package_name: Python package name (e.g., "my_assistant")

        Returns:
            PascalCase class name prefix (e.g., "MyAssistant")
            Note: The template adds "RegistryProvider" suffix

        Examples:
            >>> TemplateManager()._generate_class_name("my_assistant")
            'MyAssistant'
            >>> TemplateManager()._generate_class_name("weather_app")
            'WeatherApp'
        """
        # Convert snake_case to PascalCase
        words = package_name.split('_')
        class_name = ''.join(word.capitalize() for word in words)
        return class_name

    def _create_agent_data_structure(self, project_dir: Path, ctx: Dict):
        """Create _agent_data directory structure for the project.

        This method creates the agent data directory and all standard subdirectories
        based on osprey's default configuration. This ensures that container
        deployments won't fail due to missing mount points.

        Args:
            project_dir: Root directory of the project
            ctx: Template context variables (unused but kept for consistency)
        """
        # Create main _agent_data directory
        agent_data_dir = project_dir / "_agent_data"
        agent_data_dir.mkdir(parents=True, exist_ok=True)

        # Create standard subdirectories based on default framework configuration
        subdirs = [
            "executed_scripts",
            "execution_plans", 
            "user_memory",
            "registry_exports",
            "prompts",
            "checkpoints"
        ]

        for subdir in subdirs:
            subdir_path = agent_data_dir / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)

        console.print(f"  [success]✓[/success] Created agent data structure at [path]{agent_data_dir}[/path]")

        # Create a README to explain the directory structure
        readme_content = """# Agent Data Directory

This directory contains runtime data generated by the Osprey Framework:

- `executed_scripts/`: Python scripts executed by the framework
- `execution_plans/`: Orchestrator execution plans (JSON format)
- `user_memory/`: User memory data and conversation history
- `registry_exports/`: Exported registry information
- `prompts/`: Generated prompts (when debug mode enabled)
- `checkpoints/`: LangGraph checkpoints for conversation state

This directory is excluded from git (see .gitignore) but is required for
proper framework operation, especially when using containerized services.
"""

        readme_path = agent_data_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)

