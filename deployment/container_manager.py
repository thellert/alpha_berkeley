"""Container Management and Service Orchestration System.

This module provides comprehensive container orchestration capabilities for the
deployment framework, handling service discovery, template rendering, build
directory management, and Podman Compose integration. The system supports
hierarchical service configurations with framework and application-specific
services that can be independently deployed and managed.

The container manager implements a sophisticated template processing pipeline
that converts Jinja2 templates into Docker Compose files, copies necessary
source code and configuration files, and orchestrates multi-service deployments
through Podman Compose with proper networking and dependency management.

Key Features:
    - Hierarchical service discovery (framework.service, applications.app.service)
    - Jinja2 template rendering with unified configuration context
    - Intelligent build directory management with selective file copying
    - Environment variable expansion and configuration flattening
    - Podman Compose orchestration with multi-file support
    - Kernel template processing for Jupyter notebook environments

Architecture:
    The system supports two service categories:
    
    1. Framework Services: Core infrastructure services like databases,
       web interfaces, and development tools (jupyter, open-webui, mem0)
    
    2. Application Services: Domain-specific services tied to particular
       applications (als_expert.mongo, als_expert.pv_finder)

Examples:
    Basic service deployment::
    
        $ python container_manager.py config.yml up -d
        # Deploys all services listed in deployed_services configuration
        
    Service discovery patterns::
    
        # Framework service (short name)
        deployed_services: ["jupyter", "mem0"]
        
        # Framework service (full path)
        deployed_services: ["framework.jupyter", "framework.mem0"]
        
        # Application service (full path required)
        deployed_services: ["applications.als_expert.mongo"]
        
    Template rendering workflow::
    
        1. Load unified configuration with imports and merging
        2. Discover services listed in deployed_services
        3. Process Jinja2 templates with configuration context
        4. Copy source code and additional directories as specified
        5. Flatten configuration files for container consumption
        6. Execute Podman Compose with generated files

.. seealso::
   :mod:`deployment.loader` : Configuration loading system used by this module
   :class:`configs.unified_config.UnifiedConfigBuilder` : Configuration management
   :func:`find_service_config` : Service discovery implementation
   :func:`render_template` : Template processing engine
"""

import os
import sys
import argparse
import subprocess
import shutil
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Add the src directory to Python path so we can import GlobalConfig
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from configs.unified_config import UnifiedConfigBuilder

SERVICES_DIR = "services"
SRC_DIR = "src"
OUT_SRC_DIR = "repo_src"

TEMPLATE_FILENAME = "docker-compose.yml.j2"
COMPOSE_FILE_NAME = "docker-compose.yml"

def find_service_config(config, service_name):
    """Locate service configuration and template path for deployment.
    
    This function implements the service discovery logic for the container
    management system, supporting both hierarchical service naming (full paths)
    and legacy short names for backward compatibility. The system searches
    through framework services and application-specific services to find
    the requested service configuration.
    
    Service naming supports three patterns:
    1. Framework services: "framework.service_name" or just "service_name"
    2. Application services: "applications.app_name.service_name"
    3. Legacy services: "service_name" (deprecated, for backward compatibility)
    
    The function returns both the service configuration object and the path
    to the Docker Compose template, enabling the caller to access service
    settings and initiate template rendering.
    
    :param config: Unified configuration containing service definitions
    :type config: dict
    :param service_name: Service identifier (short name or full dotted path)
    :type service_name: str
    :return: Tuple containing service configuration and template path,
        or (None, None) if service not found
    :rtype: tuple[dict, str] or tuple[None, None]
    
    Examples:
        Framework service discovery::
        
            >>> config = {'framework': {'services': {'jupyter': {'path': 'services/framework/jupyter'}}}}
            >>> service_config, template_path = find_service_config(config, 'framework.jupyter')
            >>> print(template_path)  # 'services/framework/jupyter/docker-compose.yml.j2'
            
        Application service discovery::
        
            >>> config = {'applications': {'als_expert': {'services': {'mongo': {'path': 'services/applications/als_expert/mongo'}}}}}
            >>> service_config, template_path = find_service_config(config, 'applications.als_expert.mongo')
            >>> print(template_path)  # 'services/applications/als_expert/mongo/docker-compose.yml.j2'
            
        Legacy service discovery::
        
            >>> config = {'services': {'legacy_service': {'path': 'services/legacy'}}}
            >>> service_config, template_path = find_service_config(config, 'legacy_service')
            >>> print(template_path)  # 'services/legacy/docker-compose.yml.j2'
    
    .. note::
       Legacy service support (services.* configuration) is deprecated and
       will be removed in future versions. Use framework.* or applications.*
       naming patterns for new services.
    
    .. seealso::
       :func:`get_templates` : Uses this function to build template lists
       :func:`setup_build_dir` : Processes discovered services for deployment
    """
    # Handle full path notation (framework.jupyter, applications.als_expert.mongo)
    if '.' in service_name:
        parts = service_name.split('.')
        
        if parts[0] == 'framework' and len(parts) == 2:
            # framework.service_name
            framework_services = config.get('framework', {}).get('services', {})
            service_config = framework_services.get(parts[1])
            if service_config:
                return service_config, os.path.join(service_config['path'], TEMPLATE_FILENAME)
                    
        elif parts[0] == 'applications' and len(parts) == 3:
            # applications.app_name.service_name
            app_name, service_name_short = parts[1], parts[2]
            applications = config.get('applications', {})
            app_config = applications.get(app_name, {})
            app_services = app_config.get('services', {})
            service_config = app_services.get(service_name_short)
            if service_config:
                return service_config, os.path.join(service_config['path'], TEMPLATE_FILENAME)
    
    # Handle short names - check legacy services first for backward compatibility
    # TODO: remove this once we have migrated all services to the new config structure
    legacy_services = config.get('services', {})
    service_config = legacy_services.get(service_name)
    if service_config:
        return service_config, os.path.join(service_config['path'], TEMPLATE_FILENAME)
    
    return None, None

def get_templates(config):
    """Collect template paths for all deployed services in the configuration.
    
    This function builds a comprehensive list of Docker Compose template paths
    based on the services specified in the deployed_services configuration.
    It processes both the root services template and individual service templates,
    providing the complete set of templates needed for deployment.
    
    The function always includes the root services template (services/docker-compose.yml.j2)
    which defines the shared network configuration and other global service settings.
    Individual service templates are then discovered through the service discovery
    system and added to the template list.
    
    :param config: Unified configuration containing deployed_services list
    :type config: dict
    :return: List of template file paths for processing
    :rtype: list[str]
    :raises Warning: Prints warning if deployed_services is not configured
    
    Examples:
        Template collection for mixed services::
        
            >>> config = {
            ...     'deployed_services': ['framework.jupyter', 'applications.als_expert.mongo'],
            ...     'framework': {'services': {'jupyter': {'path': 'services/framework/jupyter'}}},
            ...     'applications': {'als_expert': {'services': {'mongo': {'path': 'services/applications/als_expert/mongo'}}}}
            ... }
            >>> templates = get_templates(config)
            >>> print(templates)
            ['services/docker-compose.yml.j2',
             'services/framework/jupyter/docker-compose.yml.j2',
             'services/applications/als_expert/mongo/docker-compose.yml.j2']
    
    .. warning::
       If deployed_services is not configured or empty, only the root services
       template will be returned, which may not provide functional services.
    
    .. seealso::
       :func:`find_service_config` : Service discovery used by this function
       :func:`render_template` : Processes the templates returned by this function
    """
    templates = []

    # Add the services root template
    templates.append(os.path.join(SERVICES_DIR, TEMPLATE_FILENAME))

    # Get deployed services list
    deployed_services = config.get('deployed_services', [])
    if deployed_services:
        deployed_service_names = [str(service) for service in deployed_services]
    else:
        print("Warning: No deployed_services list found, no service templates will be processed")
        return templates
    
    # Add templates for deployed services
    for service_name in deployed_service_names:
        service_config, template_path = find_service_config(config, service_name)
        if template_path:
            templates.append(template_path)
        else:
            print(f"Warning: Service '{service_name}' not found in configuration")

    return templates
    
def render_template(template_path, config, out_dir):
    """Render Jinja2 template with configuration context to output directory.
    
    This function processes Jinja2 templates using the unified configuration
    as context, generating concrete configuration files for container deployment.
    The system supports multiple template types including Docker Compose files
    and Jupyter kernel configurations, with intelligent output filename detection.
    
    Template rendering uses the complete configuration dictionary as Jinja2 context,
    enabling templates to access any configuration value including environment
    variables, service settings, and application-specific parameters. Environment
    variables can be referenced directly in templates using ${VAR_NAME} syntax
    for deployment-specific configurations like proxy settings. The output
    directory is created automatically if it doesn't exist.
    
    :param template_path: Path to the Jinja2 template file to render
    :type template_path: str
    :param config: Configuration dictionary to use as template context
    :type config: dict
    :param out_dir: Output directory for the rendered file
    :type out_dir: str
    :return: Full path to the rendered output file
    :rtype: str
    
    Examples:
        Docker Compose template rendering::
        
            >>> config = {'database': {'host': 'localhost', 'port': 5432}}
            >>> output_path = render_template(
            ...     'services/mongo/docker-compose.yml.j2',
            ...     config,
            ...     'build/services/mongo'
            ... )
            >>> print(output_path)  # 'build/services/mongo/docker-compose.yml'
            
        Jupyter kernel template rendering::
        
            >>> config = {'project_root': '/home/user/project'}
            >>> output_path = render_template(
            ...     'services/jupyter/python3-epics/kernel.json.j2',
            ...     config,
            ...     'build/services/jupyter/python3-epics'
            ... )
            >>> print(output_path)  # 'build/services/jupyter/python3-epics/kernel.json'
    
    .. note::
       The function automatically determines output filenames based on template
       naming conventions: .j2 extension is removed, and specific patterns
       like docker-compose.yml.j2 and kernel.json.j2 are recognized.
    
    .. seealso::
       :func:`setup_build_dir` : Uses this function for service template processing
       :func:`render_kernel_templates` : Batch processing of kernel templates
    """
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(template_path)
    # Config is already a dict for Jinja2 template rendering
    config_dict = config
    rendered_content = template.render(config_dict)
    
    # Determine output filename based on template type
    if template_path.endswith('docker-compose.yml.j2'):
        output_filename = COMPOSE_FILE_NAME
    elif template_path.endswith('kernel.json.j2'):
        output_filename = 'kernel.json'
    else:
        # Generic fallback: remove .j2 extension
        output_filename = os.path.basename(template_path)[:-3]
    
    output_filepath = os.path.join(out_dir, output_filename)
    os.makedirs(out_dir, exist_ok=True)
    with open(output_filepath, "w") as f:
        f.write(rendered_content)
    return output_filepath

def render_kernel_templates(source_dir, config, out_dir):
    """Process all Jupyter kernel templates in a service directory.
    
    This function provides batch processing for Jupyter kernel configuration
    templates, automatically discovering all kernel.json.j2 files within a
    service directory and rendering them with the current configuration context.
    This is particularly useful for Jupyter services that provide multiple
    kernel environments with different configurations.
    
    The function recursively searches the source directory for kernel template
    files and processes each one, maintaining the relative directory structure
    in the output. This ensures that kernel configurations are placed in the
    correct locations for Jupyter to discover them.
    
    :param source_dir: Source directory to search for kernel templates
    :type source_dir: str
    :param config: Configuration dictionary for template rendering
    :type config: dict
    :param out_dir: Base output directory for rendered kernel files
    :type out_dir: str
    
    Examples:
        Kernel template processing for Jupyter service::
        
            >>> # Source structure:
            >>> # services/jupyter/
            >>> #   ├── python3-epics-readonly/kernel.json.j2
            >>> #   └── python3-epics-write/kernel.json.j2
            >>> 
            >>> render_kernel_templates(
            ...     'services/jupyter',
            ...     {'project_root': '/home/user/project'},
            ...     'build/services/jupyter'
            ... )
            >>> # Output structure:
            >>> # build/services/jupyter/
            >>> #   ├── python3-epics-readonly/kernel.json
            >>> #   └── python3-epics-write/kernel.json
    
    .. note::
       This function is typically called automatically by setup_build_dir when
       a service configuration includes 'render_kernel_templates: true'.
    
    .. seealso::
       :func:`render_template` : Core template rendering used by this function
       :func:`setup_build_dir` : Calls this function for kernel template processing
    """
    kernel_templates = []
    
    # Look for kernel.json.j2 files in subdirectories
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file == 'kernel.json.j2':
                template_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                kernel_templates.append(template_path)
    
    # Render each kernel template
    for template_path in kernel_templates:
        # Calculate relative output directory
        rel_template_dir = os.path.dirname(os.path.relpath(template_path, source_dir))
        kernel_out_dir = os.path.join(out_dir, rel_template_dir) if rel_template_dir != '.' else out_dir
        
        render_template(template_path, config, kernel_out_dir)
        print(f"Rendered kernel template: {template_path} -> {kernel_out_dir}/kernel.json")

def setup_build_dir(template_path, config, container_cfg):
    """Create complete build environment for service deployment.
    
    This function orchestrates the complete build directory setup process for
    a service, including template rendering, source code copying, configuration
    flattening, and additional directory management. It creates a self-contained
    build environment that contains everything needed for container deployment.
    
    The build process follows these steps:
    1. Create clean build directory for the service
    2. Render the Docker Compose template with configuration context
    3. Copy service-specific files (excluding templates)
    4. Copy source code if requested (copy_src: true)
    5. Copy additional directories as specified
    6. Create flattened configuration file for container use
    7. Process kernel templates if specified
    
    Source code copying includes intelligent handling of requirements files,
    automatically copying global requirements.txt to the container source
    directory to ensure dependency management works correctly in containers.
    
    :param template_path: Path to the service's Docker Compose template
    :type template_path: str
    :param config: Complete configuration dictionary for template rendering
    :type config: dict
    :param container_cfg: Service-specific configuration settings
    :type container_cfg: dict
    :return: Path to the rendered Docker Compose file
    :rtype: str
    
    Examples:
        Basic service build directory setup::
        
            >>> container_cfg = {
            ...     'copy_src': True,
            ...     'additional_dirs': ['docs', 'scripts'],
            ...     'render_kernel_templates': False
            ... }
            >>> compose_path = setup_build_dir(
            ...     'services/framework/jupyter/docker-compose.yml.j2',
            ...     config,
            ...     container_cfg
            ... )
            >>> print(compose_path)  # 'build/services/framework/jupyter/docker-compose.yml'
            
        Advanced service with custom directory mapping::
        
            >>> container_cfg = {
            ...     'copy_src': True,
            ...     'additional_dirs': [
            ...         'docs',  # Simple directory copy
            ...         {'src': 'external_data', 'dst': 'data'}  # Custom mapping
            ...     ],
            ...     'render_kernel_templates': True
            ... }
            >>> compose_path = setup_build_dir(template_path, config, container_cfg)
    
    .. note::
       The function automatically handles build directory cleanup, removing
       existing directories to ensure clean builds. Global requirements.txt
       is automatically copied to container source directories when present.
    
    .. warning::
       This function performs destructive operations on build directories.
       Ensure build_dir is properly configured to avoid data loss.
    
    .. seealso::
       :func:`render_template` : Template rendering used by this function
       :func:`render_kernel_templates` : Kernel template processing
       :class:`configs.unified_config.UnifiedConfigBuilder` : Configuration flattening
    """
    # Create the build directory for this service 
    source_dir = os.path.relpath(os.path.dirname(template_path), os.getcwd())
    
    # Clear the directory if it exists
    build_dir = config.get('build_dir', './build')
    out_dir = os.path.join(build_dir, source_dir)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    # Create the docker compose file from the template
    compose_filepath = render_template(template_path, config, out_dir)
        
    # Copy the contents of the services directory, except the template
    if source_dir != SERVICES_DIR: # ignore the top level dir
        # Deep copy everything in source directory except templates
        for file in os.listdir(source_dir):
            src_path = os.path.join(source_dir, file)
            dst_path = os.path.join(out_dir, file)
            # Skip template files (both docker-compose and kernel templates)
            if file != TEMPLATE_FILENAME and not file.endswith('.j2'):
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
    
        # Copy the source directory
        if container_cfg.get('copy_src', False):
            shutil.copytree(SRC_DIR, os.path.join(out_dir, OUT_SRC_DIR))
            
            # Copy global requirements.txt to repo_src if it exists
            # This handles consolidated requirements files
            global_requirements = "requirements.txt"
            if os.path.exists(global_requirements):
                repo_src_requirements = os.path.join(out_dir, OUT_SRC_DIR, "requirements.txt")
                shutil.copy2(global_requirements, repo_src_requirements)
                print(f"Copied global requirements.txt to {repo_src_requirements}")
            
        # Copy additional directories if specified in service configuration
        additional_dirs = container_cfg.get('additional_dirs', [])
        if additional_dirs:
            for dir_spec in additional_dirs:
                    if isinstance(dir_spec, str):
                        # Simple string: copy directory with same name
                        src_dir = dir_spec
                        dst_dir = os.path.join(out_dir, dir_spec)
                    elif isinstance(dir_spec, dict):
                        # Dictionary: allows custom source -> destination mapping
                        src_dir = dir_spec.get("src")
                        dst_dir = os.path.join(out_dir, dir_spec.get("dst", src_dir))
                    else:
                        continue
                        
                    if src_dir and os.path.exists(src_dir):
                        shutil.copytree(src_dir, dst_dir)
                        print(f"Copied {src_dir} to {dst_dir}")
                    elif src_dir:
                        print(f"Warning: Directory {src_dir} does not exist, skipping")
            
        # Create flattened configuration file for container
        # This merges all imports and creates a complete config without import directives
        try:
            global_config = UnifiedConfigBuilder()
            flattened_config = global_config.raw_config  # This contains the already-merged configuration
            
            config_yml_dst = os.path.join(out_dir, "config.yml")
            with open(config_yml_dst, 'w') as f:
                yaml.dump(flattened_config, f, default_flow_style=False, sort_keys=False)
            print(f"Created flattened config.yml at {config_yml_dst}")
        except Exception as e:
            print(f"Warning: Failed to create flattened config: {e}")
            # Fallback to copying original config
            config_yml_src = "config.yml"
            if os.path.exists(config_yml_src):
                config_yml_dst = os.path.join(out_dir, "config.yml")
                shutil.copy2(config_yml_src, config_yml_dst)
                print(f"Copied original config.yml to {config_yml_dst}")
        
        # Render kernel templates if specified in service configuration
        if container_cfg.get('render_kernel_templates', False):
            print(f"Processing kernel templates for {source_dir}")
            render_kernel_templates(source_dir, config, out_dir)
        
    return compose_filepath

def parse_args():
    """Parse command-line arguments for container management operations.
    
    This function defines and processes the command-line interface for the
    container management system, supporting configuration file specification,
    deployment commands (up/down), and operational flags like detached mode.
    
    The argument parser enforces logical constraints, such as requiring the
    'up' command when using detached mode, and provides clear error messages
    for invalid argument combinations.
    
    :return: Parsed command-line arguments
    :rtype: argparse.Namespace
    :raises SystemExit: If invalid argument combinations are provided
    
    Command-line Interface:
        python container_manager.py CONFIG [COMMAND] [OPTIONS]
        
        Positional Arguments:
            CONFIG: Path to the configuration file (required)
            COMMAND: Deployment command - 'up' or 'down' (optional)
            
        Options:
            -d, --detached: Run in detached mode (only with 'up')
    
    Examples:
        Generate compose files only::
        
            $ python container_manager.py config.yml
            # Creates build directory and compose files without deployment
            
        Deploy services in foreground::
        
            $ python container_manager.py config.yml up
            # Deploys services and shows output
            
        Deploy services in background::
        
            $ python container_manager.py config.yml up -d
            # Deploys services in detached mode
            
        Stop services::
        
            $ python container_manager.py config.yml down
            # Stops and removes deployed services
    
    .. seealso::
       :func:`main execution block` : Uses parsed arguments for deployment operations
    """
    parser = argparse.ArgumentParser(description="Run podman compose with config file.")
    
    # Mandatory config path
    parser.add_argument("config", help="Path to the config file")
    
    # Optional 'up' or 'down' command
    parser.add_argument(
        "command", nargs='?', choices=["up", "down"],
        help="Command to run (up/down). If not provided, then just generate "\
             "the compose files")

    # Optional -d / --detached flag
    parser.add_argument(
        "-d", "--detached", action="store_true",
        help="Run in detached mode. Only valid with 'up'.")

    args = parser.parse_args()

    # Validation
    if args.detached and args.command != "up":
        parser.error("The -d/--detached flag is only allowed with 'up'.")

    return args

if __name__ == "__main__":
    """Main execution block for container management operations.
    
    This section orchestrates the complete deployment workflow:
    1. Parse command-line arguments
    2. Load and validate configuration
    3. Discover and process services
    4. Generate build directories and compose files
    5. Execute Podman Compose commands if requested
    
    The execution block handles errors gracefully, providing clear feedback
    for configuration issues, missing services, or deployment failures.
    Exit codes indicate success (0) or various failure conditions (1).
    
    Workflow:
        1. Configuration Loading: Use UnifiedConfigBuilder to load and merge
           configuration files with proper error handling
        2. Service Discovery: Process deployed_services list to identify
           active services for deployment
        3. Template Processing: Generate build directories for root services
           and each deployed service
        4. Container Orchestration: Execute Podman Compose with generated
           files and environment configuration
    
    Examples:
        Successful deployment workflow::
        
            $ python container_manager.py config.yml up -d
            Deployed services: framework.jupyter, applications.als_expert.mongo
            Generated compose files:
             - build/services/docker-compose.yml
             - build/services/framework/jupyter/docker-compose.yml
             - build/services/applications/als_expert/mongo/docker-compose.yml
            Running command:
                podman compose -f build/services/docker-compose.yml \
                               -f build/services/framework/jupyter/docker-compose.yml \
                               -f build/services/applications/als_expert/mongo/docker-compose.yml \
                               --env-file .env up -d
    
    .. seealso::
       :func:`parse_args` : Command-line argument processing
       :class:`configs.unified_config.UnifiedConfigBuilder` : Configuration management
       :func:`find_service_config` : Service discovery implementation
    """
    args = parse_args()
    
    try:
        unified_config = UnifiedConfigBuilder(args.config)
        # Wrap the raw config in DotDict for compatibility with existing container manager code
        config = unified_config.raw_config
    except Exception as e:
        print(f"Error: Could not load config file {args.config}: {e}")
        sys.exit(1)
   
    # Get deployed services list
    deployed_services = config.get('deployed_services', [])
    if deployed_services:
        deployed_service_names = [str(service) for service in deployed_services]
        print(f"Deployed services: {', '.join(deployed_service_names)}")
    else:
        print("Warning: No deployed_services list found, no services will be processed")
        deployed_service_names = []

    compose_files = []

    # Create the top level compose file
    top_template = os.path.join(SERVICES_DIR, TEMPLATE_FILENAME)
    build_dir = config.get('build_dir', './build')
    out_dir = os.path.join(build_dir, SERVICES_DIR)
    top_template = render_template(top_template, config, out_dir)
    compose_files.append(top_template)
    
    # Create the service build directory for deployed services only
    for service_name in deployed_service_names:
        service_config, template_path = find_service_config(config, service_name)
        if service_config and template_path:
            if not os.path.isfile(template_path):
                print(f"Error: Template file {template_path} not found for service '{service_name}'")
                sys.exit(1)
            
            out = setup_build_dir(template_path, config, service_config)
            compose_files.append(out)
        else:
            print(f"Error: Service '{service_name}' not found in configuration")
            sys.exit(1)

    if args.command:
        # run the podman compose command up or down
        cmd = ["podman", "compose"]
        for compose_file in compose_files:
            cmd.extend(("-f", compose_file))

        # --------------------------------------
        # Add the env file
        # --------------------------------------
        cmd.append('--env-file')
        cmd.append('.env')
                
        cmd.append(args.command)
        
        if args.detached:
            cmd.append("-d")
    
       
        
        print(f"Running command:\n    {' '.join(cmd)}")
        os.execvp(cmd[0], cmd)
    else:
        print("Generated compose files:")
        for compose_file in compose_files:
            print(f" - {compose_file}")
        