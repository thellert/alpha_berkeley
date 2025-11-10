"""{{ app_display_name }} Application Package.

This is a minimal Osprey Framework application template designed for
easy integration of external APIs, workflows, and custom functionality.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Define your data structures:
   → Edit context_classes.py
   → Use the provided examples as templates

2. Implement your capabilities:
   → Copy capabilities/example_capability.py.j2
   → Add your API calls and logic

3. Register your components:
   → Edit registry.py
   → Add CapabilityRegistration and ContextClassRegistration entries

4. Configure and run:
   → Edit config.yml with your settings
   → Run: osprey chat

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEMPLATE CONTENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

context_classes.py
    Complete examples of how to define data structures for your API responses,
    analysis results, and any data your capabilities work with. Includes:
    - Full implementation examples
    - Multiple patterns for different use cases
    - Detailed documentation of required methods
    - LLM-friendly access pattern generation

registry.py
    Configuration file that registers your components with the framework.
    Includes:
    - Step-by-step inline documentation
    - Examples for all registration types
    - Troubleshooting guide
    - Patterns for excluding/overriding framework components

capabilities/
    Directory for your capability implementations. Includes:
    - example_capability.py.j2: Complete 200+ line template
    - __init__.py: Overview of patterns and best practices
    - Clear guidance on where to put your API calls and logic

README.md
    Comprehensive guide covering:
    - Integration patterns (API, analysis, knowledge retrieval)
    - Development workflow
    - Testing and debugging
    - Links to working examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN PHILOSOPHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This template is optimized for:

✓ LLM/Agent Understanding
  - Clear, descriptive names
  - Comprehensive inline documentation
  - Self-documenting code patterns

✓ Human Understanding
  - Progressive disclosure (simple → advanced)
  - Complete examples before abstractions
  - Clear separation of concerns

✓ Easy Integration
  - Minimal boilerplate
  - Copy-paste friendly templates
  - Clear "put your code here" markers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEARNING PATH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Read README.md for overview
2. Study example_capability.py.j2 for capability patterns
3. Study context_classes.py for data structure patterns
4. Review registry.py to understand component registration
5. Generate working examples: osprey init --template hello_world_weather
6. Implement your integration following the patterns

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For detailed documentation, see README.md in this directory.
"""
