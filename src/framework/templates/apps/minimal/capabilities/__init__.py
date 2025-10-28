"""{{ app_display_name }} Capabilities.

Add your capability implementations in this directory.

Each capability should:
1. Inherit from BaseCapability
2. Use the @capability_node decorator
3. Define name, description, provides, and requires attributes
4. Implement the execute() method
5. Optionally implement classify_error(), get_retry_policy(), 
   _create_orchestrator_guide(), and _create_classifier_guide()

Example:
    # capabilities/my_capability.py
    from framework.base import BaseCapability, capability_node
    from framework.state import AgentState
    
    @capability_node
    class MyCapability(BaseCapability):
        name = "my_capability"
        description = "What your capability does"
        provides = ["MY_CONTEXT_TYPE"]
        requires = []
        
        @staticmethod
        async def execute(state: AgentState, **kwargs):
            # Your implementation here
            pass
"""

