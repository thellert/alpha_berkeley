# Documentation Cleanup Guide

This guide documents common issues found in the Alpha Berkeley Framework documentation and how to fix them systematically.

---

## 1. RST Header Formatting Issues

### Problem
Many `.rst` files throughout the repository use Markdown-style headers (`#` and `##`) instead of proper reStructuredText format. This causes Sphinx rendering issues including:
- Documents showing as "<no title>" in navigation
- Corrupted content with strange characters in rendered output
- Broken cross-references and table of contents
- Inconsistent section hierarchy

### Detection
Look for files with `.rst` extension containing:
```markdown
# Title
## Section Header
### Subsection
```

### Solution
Convert to proper RST format with underlined headers:
```rst
Title
=====

Section Header
==============

Subsection
----------
```

### RST Header Hierarchy
```rst
Document Title
==============

Major Section
=============

Subsection
----------

Sub-subsection
~~~~~~~~~~~~~~

Paragraph
^^^^^^^^^
```

### Quick Fix Commands
Find all affected files:
```bash
grep -r "^#\+ " docs/source/ --include="*.rst"
```

### Files Fixed (Example)
- `docs/source/developer-guides/understanding-the-framework/infrastructure-architecture.rst`
- `docs/source/developer-guides/understanding-the-framework/langgraph-integration.rst`
- `docs/source/developer-guides/understanding-the-framework/orchestrator-first-philosophy.rst`
- `docs/source/developer-guides/understanding-the-framework/convention-over-configuration.rst`

### Validation
After fixing, verify:
1. Document titles appear correctly in navigation
2. Cross-references work properly
3. Table of contents renders with proper hierarchy
4. No corrupted content in rendered output

---

## 2. Python Code Block Formatting Issues

### Problem
Python code snippets in `.rst` files are not properly formatted as code blocks, causing them to render as plain text instead of syntax-highlighted code. This makes documentation harder to read and reduces professional appearance.

### Detection
Look for Python code that appears as regular text, often preceded by:
```rst
```python
# Code here but not in proper RST code block
```
```

### Solution
Use proper RST code block directive:
```rst
.. code-block:: python

   from framework.infrastructure.gateway import Gateway
   
   # All interfaces use Gateway as single entry point
   gateway = Gateway()
   result = await gateway.process_message(
       user_input="Find beam current PV addresses",
       compiled_graph=graph,
       config=config
   )
```

### RST Code Block Syntax
```rst
.. code-block:: language

   # Code content here
   # Must be indented (3 or 4 spaces recommended)
   # Blank line required after directive
```

### Common Languages
- `python` - Python code
- `bash` - Shell commands
- `yaml` - YAML configuration
- `json` - JSON data
- `text` - Plain text output

### Example Fix
**Before (broken):**
```rst
```python
gateway = Gateway()
result = await gateway.process_message()
```
```

**After (correct):**
```rst
.. code-block:: python

   gateway = Gateway()
   result = await gateway.process_message()
```

### Validation
After fixing, verify:
1. Code appears with syntax highlighting
2. Proper indentation is preserved
3. Code blocks are visually distinct from regular text

---

## 3. Broken Cross-References

### Problem
Many `.rst` files contain `:doc:` references pointing to files that don't exist, causing links to render as plain text instead of clickable hyperlinks. This breaks navigation and user experience.

### Detection
Look for plain text that should be links, particularly:
- References in "Next Steps" sections
- API reference cross-links
- Navigation between guide sections

Find broken references:
```bash
# Search for :doc: references
grep -r ":doc:" docs/source/ --include="*.rst"

# Check if referenced files exist
# Example: :doc:`quick-start-patterns/state-and-context-essentials`
# Should correspond to: docs/source/developer-guides/quick-start-patterns/state-and-context-essentials.rst
```

### Common Issues
1. **Missing Files**: Referenced file doesn't exist yet
2. **Wrong Paths**: File exists but path is incorrect
3. **Naming Mismatches**: File exists with different name

### Solution
**For Missing Files:**
```rst
# Remove or comment out until file exists
.. TODO: Add link when file is created
.. :doc:`missing-file-name`
```

**For Wrong Paths:**
```rst
# Fix the path
# Before: :doc:`../wrong-path/file`
# After:  :doc:`../correct-path/file`
```

### Validation
After fixing:
1. Links appear as clickable hyperlinks (not plain text)
2. Links navigate to correct pages
3. No Sphinx warnings about missing references

---

*More cleanup patterns will be added to this guide as they are discovered and resolved.*
