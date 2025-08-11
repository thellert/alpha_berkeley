"""
Unified Execution Wrapper System

Consolidates wrapper logic between container and local execution.
Both execution methods create the same wrapper infrastructure with 
environment-specific adaptations.
"""

import textwrap
from pathlib import Path
from typing import Optional, Dict, Any
from configs.logger import get_logger

logger = get_logger("framework", "execution_wrapper")


class ExecutionWrapper:
    """
    Unified wrapper system for both container and local Python execution.
    
    Creates wrapped Python scripts with:
    - Standard imports and setup
    - Context loading 
    - Output capture
    - Results export
    - Error handling
    
    Environment-specific adaptations handled via parameters.
    """
    
    def __init__(self, execution_mode: str = "container"):
        """
        Initialize wrapper for specific execution environment.
        
        Args:
            execution_mode: "container" or "local"
        """
        self.execution_mode = execution_mode
    
    def create_wrapper(
        self, 
        user_code: str, 
        execution_folder: Optional[Path] = None
    ) -> str:
        """
        Create complete wrapped Python script.
        
        Args:
            user_code: Clean user code to execute
            execution_folder: Optional execution directory
            
        Returns:
            Complete wrapped Python script
        """
        
        # Build wrapper components
        imports = self._get_imports()
        environment_setup = self._get_environment_setup(execution_folder)
        metadata_init = self._get_metadata_init()
        context_loading = self._get_context_loading()
        output_capture_start = self._get_output_capture_start()
        user_code_section = self._wrap_user_code(user_code)
        cleanup_and_export = self._get_cleanup_and_export()
        
        # Assemble complete wrapper
        wrapped_code = "\n".join([
            imports,
            environment_setup,
            metadata_init, 
            context_loading,
            output_capture_start,
            user_code_section,
            cleanup_and_export
        ])
        
        return wrapped_code
    
    def _get_imports(self) -> str:
        """Get standard imports for both environments."""
        imports = """
# Standard imports for agent execution
import sys
import json
import os
import time
import traceback
from pathlib import Path
from io import StringIO
from datetime import datetime, timedelta
import pickle

# Initialize registry for context loading
print("🔧 [DEBUG] Starting registry initialization...", file=sys.stderr)
try:
    from framework.registry import initialize_registry, get_registry
    print("🔧 [DEBUG] Imported registry functions", file=sys.stderr)
    
    initialize_registry(auto_export=False)  # Initialize without export for performance
    print("🔧 [DEBUG] Registry initialization completed", file=sys.stderr)
    
    # Debug: Check if TIME_RANGE context class is properly registered
    registry = get_registry()
    print("🔧 [DEBUG] Got registry instance", file=sys.stderr)
    
    time_range_class = registry.get_context_class("TIME_RANGE")
    if time_range_class:
        print(f"✓ [DEBUG] TIME_RANGE context class registered: {time_range_class.__name__}", file=sys.stderr)
    else:
        print("❌ [DEBUG] TIME_RANGE context class NOT found in registry", file=sys.stderr)
        # List all registered context classes for debugging
        try:
            all_contexts = registry._registries.get('contexts', {})
            print(f"🔧 [DEBUG] All registered contexts: {list(all_contexts.keys())}", file=sys.stderr)
        except Exception as debug_e:
            print(f"🔧 [DEBUG] Failed to list contexts: {debug_e}", file=sys.stderr)
        
except Exception as e:
    print(f"❌ [DEBUG] Registry initialization failed: {e}", file=sys.stderr)
    print("Context loading may not work properly", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

# Scientific libraries
try:
    import numpy as np
except ImportError:
    print("NumPy not available")
    
try:
    import pandas as pd
except ImportError:
    print("Pandas not available")

try:
    import matplotlib.pyplot as plt
    # Configure matplotlib for non-interactive use
    plt.switch_backend('Agg')
except ImportError:
    print("Matplotlib not available")
"""
        
        # Container-specific Jupyter magic
        if self.execution_mode == "container":
            imports += """
# Jupyter-specific optimizations (container only)
try:
    get_ipython().run_line_magic('matplotlib', 'inline')
except:
    pass  # Not in IPython environment
"""
        
        return textwrap.dedent(imports).strip()
    
    def _get_environment_setup(self, execution_folder: Optional[Path]) -> str:
        """Get environment-specific setup code."""
        
        if self.execution_mode == "local":
            # Local execution needs sys.path setup and directory changes
            setup = f"""
# Local execution environment setup
import sys
from pathlib import Path

# Add framework src directory to Python path (FIXES THE CURRENT BUG!)
current_path = Path.cwd()
project_root = None

# Find project root by looking for src/framework
for parent in [current_path] + list(current_path.parents):
    src_dir = parent / "src"
    if src_dir.exists() and (src_dir / "framework").exists():
        project_root = parent
        break

if project_root:
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"✅ Added framework path to sys.path: {{src_path}}")
else:
    print("⚠️ Could not locate framework src directory")
"""
            
            # Add directory change for local execution
            if execution_folder:
                setup += f"""
# Change to execution directory
execution_dir = Path(r"{execution_folder}")
if execution_dir.exists():
    os.chdir(execution_dir)
    print(f"Changed to execution directory: {{execution_dir}}")
else:
    print(f"Warning: Execution directory {{execution_dir}} does not exist")
"""
        
        else:  # Container execution
            # Container handles path mounting, just needs directory info
            if execution_folder:
                # Convert host path to container path
                container_path = self._convert_host_path_to_container_path(execution_folder)
                setup = f"""
# Container execution directory setup  
execution_dir = Path("{container_path}")
print(f"Container working directory: {{Path.cwd()}}")
print(f"Target execution directory: {{execution_dir}}")

if execution_dir.exists():
    print(f"Changing to execution directory: {{execution_dir}}")
    os.chdir(execution_dir)
    print(f"Current working directory: {{Path.cwd()}}")
else:
    print(f"ERROR: Execution directory {{execution_dir}} does not exist!")
"""
            else:
                setup = """
# Container execution - using current directory
print(f"Container working directory: {{Path.cwd()}}")
"""
        
        return textwrap.dedent(setup).strip()
    
    def _get_metadata_init(self) -> str:
        """Initialize execution metadata tracking."""
        return textwrap.dedent(f"""
            # Execution metadata
            execution_metadata = {{
                "start_time": datetime.now().isoformat(),
                "success": True,
                "error": None,
                "traceback": None,
                "stdout": "",
                "stderr": "",
                "error_type": "CODE_ERROR",  # Default to code error
                "results_saved": False,
                "figures_saved": [],
                "figure_count": 0,
                "execution_mode": "{self.execution_mode}"
            }}
        """).strip()
    
    def _get_context_loading(self) -> str:
        """Get context loading code with error handling."""
        return textwrap.dedent("""
            # Load execution context
            try:
                print(f"Looking for context.json at: {{Path.cwd() / 'context.json'}}")
                print(f"context.json exists: {{(Path.cwd() / 'context.json').exists()}}")
                
                from framework.context import load_context
                context = load_context('context.json')
                
                if context:
                    print("✅ Agent context loaded successfully!")
                    print(f"Context available with {{len([k for k in dir(context) if not k.startswith('_')])}} context categories")
                    available_types = [k for k in dir(context) if not k.startswith('_')]
                    print(f"Available context types: {{available_types}}")
                else:
                    print("⚠️ No execution context available")
                    context = None
                    
            except Exception as e:
                print(f"❌ Context loading failed: {{e}}")
                import traceback
                traceback.print_exc()
                execution_metadata["error_type"] = "INFRASTRUCTURE_ERROR"
                execution_metadata["infrastructure_error"] = f"Context loading failed: {{str(e)}}"
                context = None
        """).strip()
    
    def _get_output_capture_start(self) -> str:
        """Start output capture for both environments."""
        return textwrap.dedent("""
            # Capture stdout/stderr
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            try:
                # Redirect output streams
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
        """).strip()
    
    def _wrap_user_code(self, user_code: str) -> str:
        """Wrap user code with proper indentation."""
        indented_code = "\n".join("    " + line for line in user_code.split("\n"))
        return f"""
    # Execute user code
{indented_code}
    
    # Mark successful execution
    execution_metadata["success"] = True
    execution_metadata["end_time"] = datetime.now().isoformat()
"""
    
    def _get_cleanup_and_export(self) -> str:
        """Get cleanup and results export code - consolidated for both execution modes."""
        
        # Environment-specific differences
        if self.execution_mode == "local":
            # Local execution needs to output captured content to host process
            host_output_section = textwrap.dedent("""
                # Output captured content so host process can see it (LOCAL ONLY)
                captured_stdout = stdout_capture.getvalue()
                captured_stderr = stderr_capture.getvalue()
                
                if captured_stdout:
                    print(captured_stdout, end='')
                if captured_stderr:
                    print(captured_stderr, file=sys.stderr, end='')
            """).strip()
            
            # Local execution is more forgiving about metadata save failures
            metadata_error_handling = textwrap.dedent("""
                    print(f"ERROR: Failed to save execution metadata: {e}", file=sys.stderr)
                    # Don't raise for local execution - just log the error
            """).strip()
        
        else:  # Container execution
            # Container doesn't need host output (Jupyter handles this)
            host_output_section = ""
            
            # Container execution is strict about metadata save failures
            metadata_error_handling = textwrap.dedent("""
                    print(f"CRITICAL ERROR: Failed to save execution metadata: {e}", file=sys.stderr)
                    raise RuntimeError(f"Failed to save execution metadata: {e}")
            """).strip()
        
        # Build the complete code block properly
        base_cleanup = textwrap.dedent("""
            except Exception as e:
                execution_metadata["success"] = False
                execution_metadata["error"] = str(e)
                execution_metadata["traceback"] = traceback.format_exc()
                
                # Print detailed error information to console for immediate debugging
                print(f"\\n{'='*60}", file=sys.stderr)
                print(f"PYTHON EXECUTION ERROR", file=sys.stderr)
                print(f"{'='*60}", file=sys.stderr)
                print(f"Error Type: {{type(e).__name__}}", file=sys.stderr)
                print(f"Error Message: {{str(e)}}", file=sys.stderr)
                print(f"\\nFull Traceback:", file=sys.stderr)
                print(f"{{traceback.format_exc()}}", file=sys.stderr)
                print(f"{'='*60}\\n", file=sys.stderr)
                
            finally:
                # Restore stdout/stderr and capture output
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                
                execution_metadata["stdout"] = stdout_capture.getvalue()
                execution_metadata["stderr"] = stderr_capture.getvalue()
                execution_metadata["end_time"] = datetime.now().isoformat()
        """).strip()
        
        middle_section = textwrap.dedent("""
                # Custom JSON encoder for datetime/numpy objects (defined once for reuse)
                class DateTimeEncoder(json.JSONEncoder):
                    def default(self, obj):
                        if isinstance(obj, datetime):
                            return obj.isoformat()
                        elif hasattr(obj, 'item'):  # numpy scalars
                            return obj.item()
                        elif hasattr(obj, 'tolist'):  # numpy arrays
                            return obj.tolist()
                        return super().default(obj)
                
                # Save results dictionary if it exists
                if 'results' in globals() and results is not None:
                    try:
                        with open('results.json', 'w', encoding='utf-8') as f:
                            json.dump(results, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
                        execution_metadata["results_saved"] = True
                    except Exception as e:
                        execution_metadata["results_save_error"] = str(e)
                
                # Save matplotlib figures
                try:
                    figure_nums = plt.get_fignums()
                    if figure_nums:
                        figures_dir = Path('figures')
                        figures_dir.mkdir(exist_ok=True)
                        
                        for i, fig_num in enumerate(figure_nums):
                            try:
                                fig = plt.figure(fig_num)
                                figure_path = figures_dir / f'figure_{{i+1:02d}}.png'
                                fig.savefig(figure_path, dpi=150, bbox_inches='tight', facecolor='white')
                                execution_metadata["figures_saved"].append(str(figure_path))
                            except Exception as fig_error:
                                if "figure_errors" not in execution_metadata:
                                    execution_metadata["figure_errors"] = []
                                execution_metadata["figure_errors"].append(f"Figure {{i+1}}: {{str(fig_error)}}")
                        
                        execution_metadata["figure_count"] = len(execution_metadata["figures_saved"])
                except Exception as e:
                    execution_metadata["figure_save_error"] = str(e)
                
                # Save execution metadata for debugging
                try:
                    with open('execution_metadata.json', 'w', encoding='utf-8') as f:
                        json.dump(execution_metadata, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
                    print(f"DEBUG: Successfully saved execution_metadata.json", file=sys.stderr)
                except Exception as e:
        """).strip()
        
        # Combine all parts properly
        parts = [base_cleanup]
        
        # Add host output section if needed (with proper indentation)
        if host_output_section:
            # Add proper indentation for the host output section (4 spaces to match finally block)
            indented_host_section = "\n".join("    " + line if line.strip() else line 
                                            for line in host_output_section.split("\n"))
            parts.append(indented_host_section)
        
        parts.append(middle_section)
        
        # Add proper indentation for metadata error handling
        if metadata_error_handling:
            indented_error_handling = "\n".join("    " + line if line.strip() else line 
                                              for line in metadata_error_handling.split("\n"))
            parts.append(indented_error_handling)
        
        return "\n".join(parts)
    
    def _convert_host_path_to_container_path(self, host_path: Path) -> str:
        """Convert host path to container path (for container execution)."""
        # Use the convenient get_agent_dir function to get the configured executed scripts directory
        from configs.config import get_agent_dir
        
        # Get the full path to the executed scripts directory as configured
        executed_scripts_base_path = get_agent_dir("executed_python_scripts_dir")
        executed_scripts_base = Path(executed_scripts_base_path)
        
        host_path_str = str(host_path)
        executed_scripts_base_str = str(executed_scripts_base)
        
        # Check if the host path is under the configured executed scripts directory
        if host_path_str.startswith(executed_scripts_base_str):
            # Extract the relative path from the executed scripts base directory
            try:
                relative_path = host_path.relative_to(executed_scripts_base)
                return f"/home/jovyan/work/executed_scripts/{relative_path.as_posix()}"
            except ValueError:
                # Should not happen if startswith check passed, but handle gracefully
                logger.warning(f"Could not get relative path from {host_path} to {executed_scripts_base}")
        
        # Fallback: log the issue and use the folder name
        logger.warning(f"Host path {host_path} is not under configured executed scripts directory {executed_scripts_base}")
        logger.warning(f"Using fallback container path mapping")
        return f"/home/jovyan/work/executed_scripts/{host_path.name}" 