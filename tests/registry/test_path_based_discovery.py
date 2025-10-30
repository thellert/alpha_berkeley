"""Tests for path-based registry discovery.

This test module validates the new path-based registry loading mechanism
introduced in Phase 4, including:
- Loading registries from file paths (absolute/relative)
- Error handling for missing/invalid files
- Support for multiple config formats
- Helper functions (extend_framework_registry, get_framework_defaults)
"""

import pytest
from pathlib import Path
import tempfile
import sys

from framework.registry.manager import RegistryManager
from framework.registry.base import (
    RegistryConfigProvider,
    RegistryConfig,
    CapabilityRegistration,
    ContextClassRegistration
)
from framework.registry.helpers import (
    extend_framework_registry,
    get_framework_defaults
)


class TestPathBasedLoading:
    """Test _load_registry_from_path() method."""
    
    def test_load_from_relative_path(self, tmp_path):
        """Test loading registry from relative path."""
        # Create test registry file
        registry_dir = tmp_path / "test_app"
        registry_dir.mkdir(parents=True)
        registry_file = registry_dir / "registry.py"
        
        registry_file.write_text("""
from framework.registry import (
    RegistryConfigProvider,
    RegistryConfig,
    CapabilityRegistration
)

class TestRegistryProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[
                CapabilityRegistration(
                    name="test_capability",
                    module_path="test_app.capabilities.test",
                    class_name="TestCapability",
                    description="Test capability",
                    provides=[],
                    requires=[]
                )
            ],
            context_classes=[]
        )
""")
        
        # Change to temp directory to test relative paths
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            
            # Load registry using relative path
            manager = RegistryManager(registry_paths=["./test_app/registry.py"])
            
            # Should not raise - initialization happens in _build_merged_configuration
            assert manager.registry_paths == ["./test_app/registry.py"]
            
        finally:
            os.chdir(original_cwd)
    
    def test_load_from_absolute_path(self, tmp_path):
        """Test loading registry from absolute path."""
        # Create test registry file
        registry_dir = tmp_path / "test_app"
        registry_dir.mkdir(parents=True)
        registry_file = registry_dir / "registry.py"
        
        registry_file.write_text("""
from framework.registry import (
    RegistryConfigProvider,
    RegistryConfig
)

class TestRegistryProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[],
            context_classes=[]
        )
""")
        
        # Load registry using absolute path
        absolute_path = str(registry_file.absolute())
        manager = RegistryManager(registry_paths=[absolute_path])
        
        # Should not raise
        assert manager.registry_paths == [absolute_path]
    
    def test_load_missing_file_raises_error(self, tmp_path):
        """Test that missing registry file raises clear error."""
        from framework.registry.manager import RegistryError
        
        # Error is raised during __init__ when config is built
        with pytest.raises(RegistryError, match="Registry file not found"):
            manager = RegistryManager(registry_paths=["./nonexistent/registry.py"])
    
    def test_load_invalid_python_raises_error(self, tmp_path):
        """Test that invalid Python file raises clear error."""
        from framework.registry.manager import RegistryError
        
        # Create invalid Python file
        registry_file = tmp_path / "bad_registry.py"
        registry_file.write_text("this is not valid python syntax{{{")
        
        # Error is raised during __init__
        with pytest.raises(RegistryError, match="Failed to load Python module"):
            manager = RegistryManager(registry_paths=[str(registry_file)])
    
    def test_load_no_provider_raises_error(self, tmp_path):
        """Test that registry without RegistryConfigProvider raises error."""
        from framework.registry.manager import RegistryError
        
        # Create valid Python file but no provider
        registry_file = tmp_path / "no_provider.py"
        registry_file.write_text("""
# Valid Python but no RegistryConfigProvider
def some_function():
    pass
""")
        
        # Error is raised during __init__
        with pytest.raises(RegistryError, match="No RegistryConfigProvider implementation found"):
            manager = RegistryManager(registry_paths=[str(registry_file)])
    
    def test_load_multiple_providers_raises_error(self, tmp_path):
        """Test that registry with multiple providers raises error."""
        from framework.registry.manager import RegistryError
        
        # Create file with two providers
        registry_file = tmp_path / "multi_provider.py"
        registry_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig

class Provider1(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])

class Provider2(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])
""")
        
        # Error is raised during __init__
        with pytest.raises(RegistryError, match="Multiple RegistryConfigProvider"):
            manager = RegistryManager(registry_paths=[str(registry_file)])
    
    def test_load_multiple_registries(self, tmp_path):
        """Test loading multiple application registries."""
        # Create two registry files
        app1_dir = tmp_path / "app1"
        app1_dir.mkdir(parents=True)
        app1_file = app1_dir / "registry.py"
        app1_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig, CapabilityRegistration

class App1Provider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[
                CapabilityRegistration(
                    name="app1_cap",
                    module_path="app1.capabilities.test",
                    class_name="App1Capability",
                    description="App1 capability",
                    provides=[],
                    requires=[]
                )
            ],
            context_classes=[]
        )
""")
        
        app2_dir = tmp_path / "app2"
        app2_dir.mkdir(parents=True)
        app2_file = app2_dir / "registry.py"
        app2_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig, CapabilityRegistration

class App2Provider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[
                CapabilityRegistration(
                    name="app2_cap",
                    module_path="app2.capabilities.test",
                    class_name="App2Capability",
                    description="App2 capability",
                    provides=[],
                    requires=[]
                )
            ],
            context_classes=[]
        )
""")
        
        # Load both registries
        manager = RegistryManager(registry_paths=[
            str(app1_file),
            str(app2_file)
        ])
        
        # Both should be registered
        assert len(manager.registry_paths) == 2
        
        # Config should include both app capabilities
        # Note: We can't easily test this without initializing, which requires modules to exist
        # This validates the constructor and path handling


class TestHelperFunctions:
    """Test registry helper functions."""
    
    def test_get_framework_defaults(self):
        """Test that get_framework_defaults returns framework config."""
        framework = get_framework_defaults()
        
        # Should be a RegistryConfig
        assert isinstance(framework, RegistryConfig)
        
        # Should have framework components
        assert len(framework.core_nodes) > 0
        assert len(framework.capabilities) > 0
        assert len(framework.context_classes) > 0
        
        # Should have specific framework capabilities
        cap_names = [c.name for c in framework.capabilities]
        assert "memory" in cap_names
        assert "time_range_parsing" in cap_names
        assert "python" in cap_names
        assert "respond" in cap_names
        assert "clarify" in cap_names
    
    def test_extend_framework_registry_simple(self):
        """Test extending framework with simple capability."""
        config = extend_framework_registry(
            capabilities=[
                CapabilityRegistration(
                    name="my_capability",
                    module_path="my_app.capabilities.test",
                    class_name="MyCapability",
                    description="Test capability",
                    provides=[],
                    requires=[]
                )
            ]
        )
        
        # Returns application components only
        cap_names = [c.name for c in config.capabilities]
        assert "my_capability" in cap_names
        
        # Framework capabilities are not included (merged by RegistryManager)
        assert "memory" not in cap_names
        
        # Contains only specified capabilities
        assert len(config.capabilities) == 1
    
    def test_extend_framework_registry_with_exclusions(self):
        """Test excluding framework components."""
        config = extend_framework_registry(
            capabilities=[
                CapabilityRegistration(
                    name="custom_python",
                    module_path="my_app.capabilities.python",
                    class_name="CustomPythonCapability",
                    description="Custom Python capability",
                    provides=["PYTHON_RESULTS"],
                    requires=[]
                )
            ],
            exclude_capabilities=["python"]
        )
        
        # Returns application components only
        cap_names = [c.name for c in config.capabilities]
        assert "custom_python" in cap_names
        
        # Framework capabilities not included
        assert "python" not in cap_names
        assert "memory" not in cap_names
        
        # Exclusions stored in framework_exclusions field
        assert config.framework_exclusions is not None
        assert "capabilities" in config.framework_exclusions
        assert "python" in config.framework_exclusions["capabilities"]
    
    def test_extend_framework_registry_with_overrides(self):
        """Test overriding framework components."""
        custom_memory = CapabilityRegistration(
            name="memory",  # Same name as framework
            module_path="my_app.capabilities.custom_memory",
            class_name="CustomMemoryCapability",
            description="Custom memory implementation",
            provides=["MEMORY_CONTEXT"],
            requires=[]
        )
        
        config = extend_framework_registry(
            override_capabilities=[custom_memory]
        )
        
        # Returns application config with override capability
        cap_names = [c.name for c in config.capabilities]
        assert "memory" in cap_names
        
        # Verify it's the custom implementation
        memory_cap = next(c for c in config.capabilities if c.name == "memory")
        assert memory_cap.module_path == "my_app.capabilities.custom_memory"
        assert memory_cap.class_name == "CustomMemoryCapability"
        
        # Contains only the specified override
        assert len(config.capabilities) == 1
    
    def test_extend_framework_registry_all_parameters(self):
        """Test using multiple parameters together."""
        config = extend_framework_registry(
            capabilities=[
                CapabilityRegistration(
                    name="new_cap",
                    module_path="app.cap",
                    class_name="Cap",
                    description="New",
                    provides=[],
                    requires=[]
                )
            ],
            context_classes=[
                ContextClassRegistration(
                    context_type="NEW_CONTEXT",
                    module_path="app.context",
                    class_name="NewContext"
                )
            ],
            exclude_capabilities=["python"],
            exclude_nodes=["error"]
        )
        
        # Contains application components
        assert any(c.name == "new_cap" for c in config.capabilities)
        assert any(c.context_type == "NEW_CONTEXT" for c in config.context_classes)
        
        # Exclusions stored in framework_exclusions field
        assert config.framework_exclusions is not None
        assert "python" in config.framework_exclusions.get("capabilities", [])
        assert "error" in config.framework_exclusions.get("nodes", [])
        
        # Framework components not included in application config
        assert not any(c.name == "memory" for c in config.capabilities)
        assert not any(n.name == "router" for n in config.core_nodes)


class TestConfigFormats:
    """Test different configuration format support."""
    
    def test_framework_only_config(self):
        """Test registry with no applications (framework only)."""
        manager = RegistryManager(registry_paths=[])
        
        # Should create framework-only registry
        assert len(manager.registry_paths) == 0
        
        # Config should have framework components
        assert len(manager.config.capabilities) > 0
        assert len(manager.config.core_nodes) > 0
    
    def test_single_application_path(self, tmp_path):
        """Test with single application registry path."""
        # Create simple registry
        registry_file = tmp_path / "app" / "registry.py"
        registry_file.parent.mkdir(parents=True)
        registry_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig

class AppProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])
""")
        
        manager = RegistryManager(registry_paths=[str(registry_file)])
        
        assert len(manager.registry_paths) == 1
        assert manager.registry_paths[0] == str(registry_file)
    
    def test_multiple_application_paths(self, tmp_path):
        """Test with multiple application registry paths."""
        # Create two registries
        app1_file = tmp_path / "app1" / "registry.py"
        app1_file.parent.mkdir(parents=True)
        app1_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig

class App1Provider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])
""")
        
        app2_file = tmp_path / "app2" / "registry.py"
        app2_file.parent.mkdir(parents=True)
        app2_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig

class App2Provider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])
""")
        
        manager = RegistryManager(registry_paths=[
            str(app1_file),
            str(app2_file)
        ])
        
        assert len(manager.registry_paths) == 2


class TestErrorHandling:
    """Test error handling and messages."""
    
    def test_missing_file_error_message(self, tmp_path):
        """Test error message for missing registry file."""
        from framework.registry.manager import RegistryError
        
        # Error is raised during __init__
        with pytest.raises(RegistryError) as exc_info:
            manager = RegistryManager(registry_paths=["./does_not_exist.py"])
        
        error_msg = str(exc_info.value)
        assert "Registry file not found" in error_msg
        assert "does_not_exist.py" in error_msg
    
    def test_no_provider_error_message(self, tmp_path):
        """Test error message when no provider found."""
        from framework.registry.manager import RegistryError
        
        registry_file = tmp_path / "registry.py"
        registry_file.write_text("# No provider here\n")
        
        # Error is raised during __init__
        with pytest.raises(RegistryError) as exc_info:
            manager = RegistryManager(registry_paths=[str(registry_file)])
        
        error_msg = str(exc_info.value)
        assert "No RegistryConfigProvider implementation found" in error_msg
        assert "Example:" in error_msg  # Should include helpful example
    
    def test_invalid_directory_path_raises_error(self, tmp_path):
        """Test that passing a directory instead of file raises error."""
        from framework.registry.manager import RegistryError
        
        # Create a directory
        registry_dir = tmp_path / "app"
        registry_dir.mkdir(parents=True)
        
        # Error is raised during __init__
        with pytest.raises(RegistryError, match="not a file"):
            manager = RegistryManager(registry_paths=[str(registry_dir)])


class TestBackwardCompatibility:
    """Test that old patterns still work with warnings."""
    
    def test_framework_only_registry(self):
        """Test creating framework-only registry (empty list)."""
        manager = RegistryManager(registry_paths=[])
        
        # Should work - creates framework-only registry
        assert len(manager.registry_paths) == 0
        assert isinstance(manager.config, RegistryConfig)
        
        # Should have framework capabilities
        cap_names = [c.name for c in manager.config.capabilities]
        assert "memory" in cap_names
        assert "python" in cap_names


class TestHelperIntegration:
    """Test helpers work in real registry scenarios."""
    
    def test_helper_in_registry_provider(self, tmp_path):
        """Test that helper function works when used in a registry provider."""
        # Create registry using helper
        registry_file = tmp_path / "app" / "registry.py"
        registry_file.parent.mkdir(parents=True)
        registry_file.write_text("""
from framework.registry import (
    RegistryConfigProvider,
    RegistryConfig,
    extend_framework_registry,
    CapabilityRegistration
)

class AppProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return extend_framework_registry(
            capabilities=[
                CapabilityRegistration(
                    name="my_cap",
                    module_path="app.cap",
                    class_name="MyCap",
                    description="Test",
                    provides=[],
                    requires=[]
                )
            ]
        )
""")
        
        # Load using path-based discovery
        manager = RegistryManager(registry_paths=[str(registry_file)])
        
        # After merge, should include both framework and application capabilities
        cap_names = [c.name for c in manager.config.capabilities]
        assert "memory" in cap_names  # Framework (merged)
        assert "my_cap" in cap_names  # Application
    
    def test_helper_with_exclusions_in_provider(self, tmp_path):
        """Test helper with exclusions in a registry provider."""
        registry_file = tmp_path / "app" / "registry.py"
        registry_file.parent.mkdir(parents=True)
        registry_file.write_text("""
from framework.registry import (
    RegistryConfigProvider,
    RegistryConfig,
    extend_framework_registry,
    CapabilityRegistration
)

class AppProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return extend_framework_registry(
            capabilities=[
                CapabilityRegistration(
                    name="custom_python",
                    module_path="app.python",
                    class_name="CustomPython",
                    description="Custom Python",
                    provides=["PYTHON_RESULTS"],
                    requires=[]
                )
            ],
            exclude_capabilities=["python"]
        )
""")
        
        manager = RegistryManager(registry_paths=[str(registry_file)])
        
        # After merge with framework_exclusions applied
        cap_names = [c.name for c in manager.config.capabilities]
        assert "python" not in cap_names  # Framework Python should be excluded
        assert "custom_python" in cap_names  # Custom version included
        assert "memory" in cap_names  # Other framework capabilities present


class TestSysPathManagement:
    """Test sys.path configuration for application module imports.
    
    These tests verify that the registry manager correctly configures sys.path
    to enable imports of application modules (context_classes, capabilities, etc.)
    following the industry-standard pattern used by pytest, sphinx, and airflow.
    """
    
    def test_syspath_configured_for_src_structure(self, tmp_path):
        """Test that src/ directory is added to sys.path for src/app structure."""
        # Create typical generated project structure: ./src/app_name/
        src_dir = tmp_path / "src"
        app_dir = src_dir / "my_app"
        app_dir.mkdir(parents=True)
        
        # Create registry that references app modules
        registry_file = app_dir / "registry.py"
        registry_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig, ContextClassRegistration

class TestProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[],
            context_classes=[
                ContextClassRegistration(
                    context_type="TEST_CONTEXT",
                    module_path="my_app.context_classes",  # Requires src/ on sys.path
                    class_name="TestContext"
                )
            ]
        )
""")
        
        # Create the referenced module
        context_file = app_dir / "context_classes.py"
        context_file.write_text("""
from framework.context import BaseContext

class TestContext(BaseContext):
    def __init__(self):
        super().__init__("TEST_CONTEXT")
""")
        
        # Store original sys.path
        original_syspath = sys.path.copy()
        
        try:
            # Load registry - should automatically add src/ to sys.path
            manager = RegistryManager(registry_paths=[str(registry_file)])
            
            # Verify src/ was added to sys.path
            src_dir_str = str(src_dir.resolve())
            assert src_dir_str in sys.path, f"Expected {src_dir_str} in sys.path"
            
            # Verify it was added at the beginning (higher priority)
            assert sys.path.index(src_dir_str) < 10, "src/ should be near beginning of sys.path"
            
        finally:
            # Clean up sys.path
            sys.path[:] = original_syspath
    
    def test_syspath_configured_for_flat_structure(self, tmp_path):
        """Test that app directory is added to sys.path for flat structure."""
        # Create flat structure: ./app_name/ (no src/)
        app_dir = tmp_path / "my_app"
        app_dir.mkdir(parents=True)
        
        registry_file = app_dir / "registry.py"
        registry_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig

class TestProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])
""")
        
        original_syspath = sys.path.copy()
        
        try:
            # Load registry - should add app directory to sys.path
            manager = RegistryManager(registry_paths=[str(registry_file)])
            
            # Verify app directory was added (since no src/ exists)
            app_dir_str = str(app_dir.resolve())
            assert app_dir_str in sys.path, f"Expected {app_dir_str} in sys.path"
            
        finally:
            sys.path[:] = original_syspath
    
    def test_syspath_not_duplicated(self, tmp_path):
        """Test that sys.path entries aren't duplicated on repeated loads."""
        src_dir = tmp_path / "src"
        app_dir = src_dir / "my_app"
        app_dir.mkdir(parents=True)
        
        registry_file = app_dir / "registry.py"
        registry_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig

class TestProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])
""")
        
        original_syspath = sys.path.copy()
        
        try:
            # Load registry multiple times
            manager1 = RegistryManager(registry_paths=[str(registry_file)])
            initial_syspath_len = len(sys.path)
            
            manager2 = RegistryManager(registry_paths=[str(registry_file)])
            
            # sys.path should not grow (deduplication working)
            assert len(sys.path) == initial_syspath_len, "sys.path should not have duplicates"
            
            # Verify only one occurrence of src_dir
            src_dir_str = str(src_dir.resolve())
            count = sys.path.count(src_dir_str)
            assert count == 1, f"Expected 1 occurrence of {src_dir_str}, found {count}"
            
        finally:
            sys.path[:] = original_syspath
    
    def test_application_modules_can_import_after_syspath_setup(self, tmp_path, monkeypatch):
        """Test that application modules can actually be imported after sys.path setup."""
        # Create realistic project structure
        src_dir = tmp_path / "src"
        app_dir = src_dir / "weather_app"
        app_dir.mkdir(parents=True)
        
        # Create a minimal config.yml to avoid config loading errors
        config_file = tmp_path / "config.yml"
        config_file.write_text("""
project_root: .
models:
  orchestrator:
    provider: openai
    model_id: gpt-4
""")
        
        # Set CONFIG_FILE environment variable
        monkeypatch.setenv('CONFIG_FILE', str(config_file))
        
        # Create context_classes module
        context_file = app_dir / "context_classes.py"
        context_file.write_text("""
from framework.context.base import CapabilityContext

class WeatherContext(CapabilityContext):
    def __init__(self):
        super().__init__("WEATHER_DATA")
        self.temperature = None
""")
        
        # Create registry that references it
        registry_file = app_dir / "registry.py"
        registry_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig, ContextClassRegistration

class WeatherProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(
            capabilities=[],
            context_classes=[
                ContextClassRegistration(
                    context_type="WEATHER_DATA",
                    module_path="weather_app.context_classes",
                    class_name="WeatherContext"
                )
            ]
        )
""")
        
        original_syspath = sys.path.copy()
        
        try:
            # Load registry - sys.path should be configured
            manager = RegistryManager(registry_paths=[str(registry_file)])
            manager.initialize()  # Initialize to load context classes
            
            # Verify we can now import the application module
            import weather_app.context_classes
            assert hasattr(weather_app.context_classes, 'WeatherContext')
            
            # Verify the context class was loaded correctly
            assert "WEATHER_DATA" in manager._registries['contexts']
            
        finally:
            # Clean up
            sys.path[:] = original_syspath
            if 'weather_app' in sys.modules:
                del sys.modules['weather_app']
            if 'weather_app.context_classes' in sys.modules:
                del sys.modules['weather_app.context_classes']
    
    def test_syspath_detection_with_explicit_src_dir(self, tmp_path):
        """Test Pattern 2: Registry not in src/ but src/ exists."""
        # Create structure: ./config/registry.py and ./src/ exists
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)
        
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True)
        
        registry_file = config_dir / "registry.py"
        registry_file.write_text("""
from framework.registry import RegistryConfigProvider, RegistryConfig

class TestProvider(RegistryConfigProvider):
    def get_registry_config(self) -> RegistryConfig:
        return RegistryConfig(capabilities=[], context_classes=[])
""")
        
        original_syspath = sys.path.copy()
        
        try:
            manager = RegistryManager(registry_paths=[str(registry_file)])
            
            # Should detect src/ directory and add it
            src_dir_str = str(src_dir.resolve())
            assert src_dir_str in sys.path, f"Expected {src_dir_str} in sys.path (Pattern 2)"
            
        finally:
            sys.path[:] = original_syspath


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

