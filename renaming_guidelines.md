# Renaming Guidelines: Framework to Osprey (AI Agent Instructions)

**Context**: The codebase is being renamed from "Alpha Berkeley Framework" to "Osprey Framework". The source directory has already been renamed from `src/framework/` to `src/osprey/`, but many files still contain old references.

## Critical Rules

### ✅ MUST CHANGE (Code References)

These are **code-level references** that must be updated:

1. **Import statements**: `from framework.X` → `from osprey.X`
   ```python
   # CHANGE THIS
   from framework.state import AgentState
   from framework.base.capability import BaseCapability
   
   # TO THIS
   from osprey.state import AgentState
   from osprey.base.capability import BaseCapability
   ```

2. **String module paths**: `"framework.X"` → `"osprey.X"`
   ```python
   # CHANGE THIS
   module_path = "framework.capabilities.my_capability"
   
   # TO THIS
   module_path = "osprey.capabilities.my_capability"
   ```

3. **Sphinx cross-references**: `:class:\`framework.X\`` → `:class:\`osprey.X\``
   ```python
   # CHANGE THIS
   :class:`framework.state.StateManager`
   :mod:`framework.base.planning`
   
   # TO THIS
   :class:`osprey.state.StateManager`
   :mod:`osprey.base.planning`
   ```

4. **Logger names**: `get_logger("framework")` → `get_logger("osprey")`
   ```python
   # CHANGE THIS
   logger = get_logger("framework")
   
   # TO THIS
   logger = get_logger("osprey")
   ```

5. **Brand name**: "Alpha Berkeley Framework" → "Osprey Framework"
   ```python
   # CHANGE THIS
   """Registry Manager for Alpha Berkeley Agentic Framework Components."""
   
   # TO THIS
   """Registry Manager for Osprey Agentic Framework Components."""
   ```

### ❌ MUST NOT CHANGE (Generic Architecture References)

These are **common noun uses** describing the architecture - KEEP AS-IS:

1. **"the framework"** - when describing what the software does
   ```python
   # KEEP AS-IS
   """The framework provides a capability-based architecture."""
   "This is true throughout the framework."
   "The framework is designed for on-demand imports."
   ```

2. **"framework capabilities"** - generic architectural term
   ```python
   # KEEP AS-IS
   """Base class for framework capabilities."""
   "Integration with framework systems."
   ```

3. **"framework's"** - possessive describing features
   ```python
   # KEEP AS-IS
   "The framework's lazy loading pattern prevents circular imports."
   ```

4. **Historical references** in CHANGELOG.md

5. **Copyright notices** - keep legal text as-is

## Decision Test

**Ask yourself**: "Is this referring to the **package/module name** or describing the **architectural concept**?"

- If you can replace "framework" with "system" or "architecture" and it still makes sense → **KEEP IT**
- If it's an import, module path, or brand name → **CHANGE IT**

## Examples

### Example 1: Module Docstring (Mixed)

```python
# BEFORE
"""Registry Manager for Alpha Berkeley Agentic Framework Components.

This module provides the centralized registry management system for the Alpha Berkeley
framework, serving as the single point of access for all framework components
including capabilities, nodes, and services.

The registry uses the framework's lazy loading pattern to prevent circular imports.
"""

from framework.state import AgentState
from framework.registry.base import RegistryBase
```

```python
# AFTER
"""Registry Manager for Osprey Agentic Framework Components.

This module provides the centralized registry management system for the Osprey
framework, serving as the single point of access for all framework components
including capabilities, nodes, and services.

The registry uses the framework's lazy loading pattern to prevent circular imports.
"""

from osprey.state import AgentState
from osprey.registry.base import RegistryBase
```

**What changed**:
- "Alpha Berkeley Agentic Framework" → "Osprey Agentic Framework" (brand name)
- "Alpha Berkeley framework" → "Osprey framework" (brand name with lowercase)
- `from framework.` → `from osprey.` (imports)

**What stayed the same**:
- "all framework components" (generic - describing what belongs to the system)
- "framework's lazy loading" (generic - describing a feature)

### Example 2: Capability Docstring (Mostly Generic)

```python
# KEEP AS-IS (no changes needed)
"""Base class for framework capabilities using convention-based configuration.

This class provides the foundation for all capabilities in the framework.
Capabilities integrate seamlessly with the framework's execution model.
"""
```

**Why no changes**: All uses of "framework" here are generic architectural descriptions.

### Example 3: Import Block

```python
# BEFORE
from framework.base.errors import ErrorClassification, ErrorSeverity

if TYPE_CHECKING:
    from framework.state import AgentState
    from framework.base.planning import PlannedStep
```

```python
# AFTER
from osprey.base.errors import ErrorClassification, ErrorSeverity

if TYPE_CHECKING:
    from osprey.state import AgentState
    from osprey.base.planning import PlannedStep
```

### Example 4: Registry String References

```python
# BEFORE
module = importlib.import_module("framework.capabilities.memory")
path = "framework.state.AgentState"
```

```python
# AFTER
module = importlib.import_module("osprey.capabilities.memory")
path = "osprey.state.AgentState"
```

## Validation Checklist

After making changes, verify:

1. ✅ All `from framework.` changed to `from osprey.`
2. ✅ All `"framework.` (string module paths) changed to `"osprey.`
3. ✅ All Sphinx `:class:\`framework.` changed to `:class:\`osprey.`
4. ✅ Brand name "Alpha Berkeley" changed to "Osprey"
5. ✅ Generic "framework" (lowercase, describing architecture) kept as-is
6. ✅ File still makes sense and reads naturally

## Report Format

When you complete a file, report:
```
Completed: [filename]
Changes made:
- X import statements updated (framework → osprey)
- X string module references updated
- X brand name references updated
- X Sphinx cross-references updated
Kept as-is:
- X generic "framework" references (architectural descriptions)
```
