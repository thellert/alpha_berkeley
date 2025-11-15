"""Registry auto-update helper for MCP capability generation.

Automatically adds generated capabilities to project registry with user confirmation.
"""

import re
from pathlib import Path
from typing import Optional


def find_registry_file() -> Optional[Path]:
    """Find the registry.py file from config.yml.

    Reads registry_path from config.yml in current directory.

    Returns:
        Path to registry.py or None if not found or config missing
    """
    from osprey.utils.config import get_config_value

    try:
        # Get registry path from config
        registry_path = get_config_value("registry_path")
        if not registry_path:
            return None

        # Convert to Path and resolve relative to current directory
        registry_file = Path(registry_path)
        if not registry_file.is_absolute():
            registry_file = Path.cwd() / registry_file

        if registry_file.exists():
            return registry_file

    except Exception:
        pass

    return None


def get_project_module_name(registry_path: Path) -> str:
    """Extract the project module name from registry path.

    Args:
        registry_path: Path to registry.py

    Returns:
        Module name (e.g., 'my_control_assistant')
    """
    return registry_path.parent.name


def generate_capability_registration(
    capability_name: str,
    class_name: str,
    module_name: str,
    context_type: str,
    description: str = ""
) -> str:
    """Generate CapabilityRegistration code.

    Args:
        capability_name: Name of the capability (e.g., 'slack_mcp')
        class_name: Class name (e.g., 'SlackMcpCapability')
        module_name: Project module name
        context_type: Context type produced
        description: Human-readable description

    Returns:
        Formatted registration code
    """
    if not description:
        description = f"{capability_name} operations via MCP server"

    return f'''                CapabilityRegistration(
                    name="{capability_name}",
                    module_path="{module_name}.capabilities.{capability_name}",
                    class_name="{class_name}",
                    description="{description}",
                    provides=["{context_type}"],
                    requires=[]
                ),'''


def generate_context_registration(
    context_type: str,
    context_class_name: str,
    module_name: str,
    capability_name: str
) -> str:
    """Generate ContextClassRegistration code.

    Args:
        context_type: Context type (e.g., 'SLACK_RESULTS')
        context_class_name: Context class name
        module_name: Project module name
        capability_name: Capability name (for module path)

    Returns:
        Formatted registration code
    """
    return f'''                ContextClassRegistration(
                    context_type="{context_type}",
                    module_path="{module_name}.capabilities.{capability_name}",
                    class_name="{context_class_name}"
                ),'''


def add_to_registry(
    registry_path: Path,
    capability_name: str,
    class_name: str,
    context_type: str,
    context_class_name: str,
    description: str = ""
) -> tuple[str, str]:
    """Add capability to registry file.

    Args:
        registry_path: Path to registry.py
        capability_name: Capability name
        class_name: Capability class name
        context_type: Context type
        context_class_name: Context class name
        description: Capability description

    Returns:
        Tuple of (new_content, preview) where preview shows what was added
    """
    module_name = get_project_module_name(registry_path)
    content = registry_path.read_text()

    # Generate registration code
    cap_reg = generate_capability_registration(
        capability_name, class_name, module_name, context_type, description
    )
    ctx_reg = generate_context_registration(
        context_type, context_class_name, module_name, capability_name
    )

    # Find the capabilities list and add before the closing ]
    # Look for the pattern: capabilities=[...], and insert before the last item's comma or ]
    capabilities_pattern = r'(capabilities=\s*\[)(.*?)(\s*\],)'

    def add_to_capabilities(match):
        prefix = match.group(1)
        existing = match.group(2)
        suffix = match.group(3)

        # Add new capability registration
        return f"{prefix}{existing}\n{cap_reg}{suffix}"

    new_content = re.sub(capabilities_pattern, add_to_capabilities, content, flags=re.DOTALL)

    # Find the context_classes list and add
    context_pattern = r'(context_classes=\s*\[)(.*?)(\s*\]\s*\))'

    def add_to_contexts(match):
        prefix = match.group(1)
        existing = match.group(2)
        suffix = match.group(3)

        # Add new context registration
        return f"{prefix}{existing}\n{ctx_reg}{suffix}"

    new_content = re.sub(context_pattern, add_to_contexts, new_content, flags=re.DOTALL)

    # Create preview showing what was added
    preview = f"""
[bold]Capability Registration:[/bold]
{cap_reg}

[bold]Context Class Registration:[/bold]
{ctx_reg}
"""

    return new_content, preview


def is_already_registered(registry_path: Path, capability_name: str) -> bool:
    """Check if capability is already registered.

    Args:
        registry_path: Path to registry.py
        capability_name: Capability name to check

    Returns:
        True if already registered
    """
    content = registry_path.read_text()
    # Look for name="{capability_name}"
    pattern = rf'name\s*=\s*["\']'+ re.escape(capability_name) + r'["\']'
    return bool(re.search(pattern, content))

