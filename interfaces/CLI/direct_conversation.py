#!/usr/bin/env python3
"""
CLI Interface for Alpha Berkeley Agent Framework

This interface demonstrates the recommended architecture:
- Interface code focused on presentation only
- Gateway handles all preprocessing logic as single entry point
- Native LangGraph patterns for persistence and streaming
- Clean separation of concerns with single responsibility

The CLI is simple - it handles user interaction and delegates all processing to the Gateway.
"""

import asyncio
import sys
import os
import uuid
from typing import Dict, Any

# Load environment variables before any other imports
from dotenv import load_dotenv
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from framework.registry import initialize_registry, get_registry
from framework.graph import create_graph
from framework.infrastructure.gateway import Gateway
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from configs.logger import get_logger
from configs.unified_config import get_full_configuration
from rich.console import Console
from rich.text import Text

# Modern CLI dependencies
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.styles import Style

logger = get_logger("interface", "cli")


class CLI:
    """Command Line Interface for the Alpha Berkeley Agent Framework.
    
    This interface provides a clean, interactive command-line experience for users
    to communicate with the Alpha Berkeley Agent Framework. It demonstrates the
    recommended architecture pattern where the interface layer focuses solely on
    user interaction and presentation, while delegating all processing logic to
    the Gateway component.
    
    The CLI implements a real-time streaming interface with proper interrupt
    handling for approval workflows, status updates, and error management. It
    maintains conversation continuity through LangGraph's native checkpointing
    and provides rich console output using the Rich library.
    
    Key Features:
        - Interactive conversation loop with graceful exit handling
        - Real-time status updates during agent processing
        - Approval workflow integration with interrupt handling
        - Rich console formatting with colors and styling
        - Session-based conversation continuity
        - Comprehensive error handling and logging
    
    Architecture Pattern:
        - Interface handles user interaction and presentation only
        - Gateway manages all preprocessing as single entry point
        - Native LangGraph patterns for execution and persistence
        - Clean separation of concerns with single responsibility
    
    :param graph: LangGraph instance for agent execution
    :type graph: StateGraph, optional
    :param gateway: Gateway instance for message processing
    :type gateway: Gateway, optional
    :param thread_id: Unique thread identifier for conversation continuity
    :type thread_id: str, optional
    :param base_config: Base configuration dictionary for LangGraph execution
    :type base_config: dict, optional
    :param console: Rich console instance for formatted output
    :type console: Console
    
    .. note::
       The CLI creates a unique thread ID for each session to maintain
       conversation continuity across multiple interactions.
    
    .. warning::
       The CLI requires proper framework initialization before use. Ensure
       all dependencies are available before starting the interface.
    
    Examples:
        Basic CLI usage::
        
            >>> cli = CLI()
            >>> await cli.run()
            # Starts interactive CLI session
        
        Programmatic initialization::
        
            >>> cli = CLI()
            >>> await cli.initialize()
            >>> await cli._process_user_input("Hello, agent!")
    
    .. seealso::
       :class:`framework.infrastructure.gateway.Gateway` : Message processing gateway
       :class:`framework.graph.create_graph` : LangGraph instance creation
       :func:`configs.unified_config.get_full_configuration` : Configuration management
       :class:`rich.console.Console` : Rich console formatting
    """
    
    def __init__(self):
        """Initialize the CLI interface with default configuration.
        
        Sets up the CLI instance with empty framework components that will be
        initialized during startup. Creates a Rich console instance for formatted
        output and prepares the session state for framework initialization.
        
        The initialization is lightweight and defers heavy framework setup to
        the async initialize() method to avoid blocking the constructor.
        """
        self.graph = None
        self.gateway = None
        self.thread_id = None
        self.base_config = None
        self.console = Console()
        
        # Modern CLI components
        self.prompt_session = None
        self.history_file = os.path.expanduser("~/.alpha_berkeley_cli_history")
        
        # Create custom key bindings
        self.key_bindings = self._create_key_bindings()
        
        # Create custom style
        self.prompt_style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'suggestion': '#666666 italic',
        })
        
    def _create_key_bindings(self):
        """Create custom key bindings for advanced CLI functionality.
        
        Sets up key bindings that enhance the user experience with shortcuts
        and special commands. This method creates bindings for common operations
        like clearing the screen and handling multi-line input.
        
        :returns: KeyBindings instance with custom shortcuts
        :rtype: KeyBindings
        
        .. note::
           Key bindings are applied to the prompt session and work alongside
           default prompt_toolkit bindings for arrow keys, history, etc.
        
        Examples:
            - Ctrl+L: Clear screen
            - Ctrl+C: Interrupt (default behavior)
            - Tab: Auto-completion (when available)
        """
        bindings = KeyBindings()
        
        @bindings.add('c-l')  # Ctrl+L to clear screen
        def _(event):
            """Clear the screen."""
            clear()
            
        return bindings
        
    def _create_prompt_session(self):
        """Create a prompt_toolkit session with modern features.
        
        Initializes a PromptSession with advanced terminal features including
        command history, auto-suggestions, key bindings, and styled prompts.
        The session provides a modern CLI experience with arrow key navigation,
        command completion, and persistent history.
        
        :returns: Configured PromptSession instance
        :rtype: PromptSession
        
        .. note::
           The history file is stored in the user's home directory for
           persistence across sessions.
        
        Features enabled:
            - File-based command history
            - Auto-suggestions from history
            - Custom key bindings
            - Styled prompt with colors
            - Multi-line editing support
        """
        return PromptSession(
            history=FileHistory(self.history_file),
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=self.key_bindings,
            style=self.prompt_style,
            mouse_support=False,  # Disable to allow normal terminal scrolling
            complete_style='multi-column',
            enable_suspend=True,  # Allow Ctrl+Z
            reserve_space_for_menu=0  # Don't reserve space that could interfere with scrolling
        )
        
    async def initialize(self):
        """Initialize the CLI with framework components and display startup banner.
        
        Performs comprehensive framework initialization including configuration
        loading, registry setup, graph creation, and gateway initialization.
        Displays a rich ASCII banner and creates a unique thread ID for session
        continuity.
        
        This method handles the complete startup sequence:
        1. Display startup banner with framework branding
        2. Generate unique thread ID for conversation persistence
        3. Load and merge configuration from unified config system
        4. Initialize framework registry with all capabilities
        5. Create LangGraph instance with memory checkpointer
        6. Initialize Gateway for message processing
        7. Display initialization status and session information
        
        :raises Exception: If framework initialization fails due to missing
                          dependencies, configuration errors, or registry issues
        
        .. note::
           The thread ID format is 'cli_session_{8_char_hex}' for easy
           identification in logs and debugging.
        
        .. warning::
           This method must be called before processing any user input.
           Framework components will be None until initialization completes.
        
        Examples:
            Standalone initialization::
            
                >>> cli = CLI()
                >>> await cli.initialize()
                >>> print(f"Session ID: {cli.thread_id}")
                cli_session_a1b2c3d4
        
        .. seealso::
           :func:`framework.registry.initialize_registry` : Registry initialization
           :func:`framework.graph.create_graph` : Graph creation with checkpointing
           :class:`framework.infrastructure.gateway.Gateway` : Message processing
        """
        # Cool colored ASCII art banner
        self.console.print()
        
        # Create the banner with colors
        banner_text = """
    ╔═════════════════════════════════════════════════════════════════╗
    ║                                                                 ║
    ║                                                                 ║
    ║  ░█████╗░██╗░░░░░██████╗░██╗░░██╗░█████╗░  ░█████╗░██╗░░░░░██╗  ║
    ║  ██╔══██╗██║░░░░░██╔══██╗██║░░██║██╔══██╗  ██╔══██╗██║░░░░░██║  ║  
    ║  ███████║██║░░░░░██████╔╝███████║███████║  ██║░░╚═╝██║░░░░░██║  ║
    ║  ██╔══██║██║░░░░░██╔═══╝░██╔══██║██╔══██║  ██║░░██╗██║░░░░░██║  ║
    ║  ██║░░██║███████╗██║░░░░░██║░░██║██║░░██║  ╚█████╔╝███████╗██║  ║
    ║  ╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝  ░╚════╝░╚══════╝╚═╝  ║
    ║                                                                 ║
    ║                                                                 ║
    ║     Command Line Interface for the Alpha Berkeley Framework     ║
    ╚═════════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Text(banner_text, style="bold cyan"))
        self.console.print("💡 Type 'bye' or 'end' to exit", style="yellow")
        self.console.print()
        
        # Initialize configuration using LangGraph config
        self.console.print("🔄 Initializing configuration...", style="blue")
        
        # Create unique thread for this CLI session
        self.thread_id = f"cli_session_{uuid.uuid4().hex[:8]}"
        
        # Get base configurable and add session info
        configurable = get_full_configuration().copy()
        configurable.update({
            "user_id": "cli_user",
            "thread_id": self.thread_id,
            "chat_id": "cli_chat", 
            "session_id": self.thread_id
        })
        
        # Add recursion limit to runtime config
        from configs.unified_config import get_config_value
        recursion_limit = get_config_value("execution_limits.graph_recursion_limit")
        
        self.base_config = {
            "configurable": configurable,
            "recursion_limit": recursion_limit
        }
        
        # Initialize framework
        self.console.print("🔄 Initializing framework...", style="blue")
        initialize_registry()
        registry = get_registry()
        checkpointer = MemorySaver()
        
        # Create graph and gateway
        self.graph = create_graph(registry, checkpointer=checkpointer)
        self.gateway = Gateway()
        
        # Initialize modern prompt session
        self.prompt_session = self._create_prompt_session()
        
        self.console.print(f"✅ Framework initialized! Thread ID: {self.thread_id}", style="green")
        self.console.print("  • Use ↑/↓ arrow keys to navigate command history", style="dim cyan")
        self.console.print("  • Use ←/→ arrow keys to edit current line", style="dim cyan")
        self.console.print("  • Press Ctrl+L to clear screen", style="dim cyan")
        self.console.print("  • Type 'bye' or 'end' to exit, or press Ctrl+C", style="dim cyan")
        self.console.print()
        
    async def run(self):
        """Execute the main CLI interaction loop with graceful error handling.
        
        Runs the primary CLI interface loop that handles user input, processes
        messages through the framework, and manages the conversation flow. The
        loop continues until the user enters an exit command or interrupts the
        session.
        
        The main loop implements:
        - Automatic framework initialization on first run
        - Continuous user input processing with prompt display
        - Graceful exit handling for 'bye' and 'end' commands
        - Keyboard interrupt (Ctrl+C) and EOF handling
        - Comprehensive error handling with logging
        - Empty input filtering to avoid unnecessary processing
        
        Exit Conditions:
            - User enters 'bye' or 'end' (case-insensitive)
            - Keyboard interrupt (Ctrl+C)
            - End-of-file (Ctrl+D on Unix, Ctrl+Z on Windows)
            - Unhandled exceptions (logged and continued)
        
        :raises Exception: Critical errors are logged but don't terminate the loop
                          unless they occur during initialization
        
        .. note::
           The loop automatically calls initialize() if not already done,
           making this method suitable as a single entry point.
        
        .. warning::
           Long-running operations may block the CLI. Use Ctrl+C to interrupt
           if the agent becomes unresponsive.
        
        Examples:
            Start CLI session::
            
                >>> cli = CLI()
                >>> await cli.run()
                # Displays banner and starts interactive loop
                👤 You: Hello, agent!
                🔄 Processing: Hello, agent!
                🤖 Hello! How can I help you today?
        
        .. seealso::
           :meth:`initialize` : Framework initialization process
           :meth:`_process_user_input` : Individual message processing
        """
        
        await self.initialize()
        
        while True:
            try:
                # Use modern prompt with rich formatting and history
                user_input = await self.prompt_session.prompt_async(
                    HTML('<prompt>👤 You: </prompt>'),
                    style=self.prompt_style
                )
                user_input = user_input.strip()
                
                # Exit conditions
                if user_input.lower() in ["bye", "end"]:
                    self.console.print("👋 Goodbye!", style="yellow")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process user input
                await self._process_user_input(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="yellow")
                break
            except EOFError:
                self.console.print("\n👋 Goodbye!", style="yellow")
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")
                logger.exception("Unexpected error during interaction")
                continue
    
    async def _process_user_input(self, user_input: str):
        """Process user input through the Gateway and handle execution flow.
        
        Processes a single user message through the complete framework pipeline,
        handling both normal conversation flow and interrupt-based approval
        workflows. The method delegates all processing logic to the Gateway and
        manages the execution results appropriately.
        
        Processing Flow:
        1. Display processing status to user
        2. Send message to Gateway for preprocessing and routing
        3. Handle Gateway result based on type:
           - Error: Display error message and return
           - Resume command: Execute interrupt resumption with streaming
           - New conversation: Execute agent processing with streaming
           - No action: Display completion message
        4. Handle streaming execution with real-time status updates
        5. Check for additional interrupts or show final results
        
        :param user_input: Raw user message to process
        :type user_input: str
        :raises Exception: Processing errors are logged and displayed to user
        
        .. note::
           This method handles both synchronous and asynchronous execution
           patterns, adapting to the Gateway's response type.
        
        .. warning::
           Long-running operations may require user approval. The method
           will pause and wait for additional user input during interrupts.
        
        Examples:
            Process a simple query::
            
                >>> await cli._process_user_input("What is the weather?")
                🔄 Processing: What is the weather?
                🤖 I can help you check the weather...
            
            Handle approval workflow::
            
                >>> await cli._process_user_input("yes, approve")
                🔄 Resuming from interrupt...
                🤖 Operation approved and completed.
        
        .. seealso::
           :class:`framework.infrastructure.gateway.Gateway` : Message processing
           :meth:`_execute_result` : Agent execution with streaming
           :meth:`_show_final_result` : Final result display
        """
        
        self.console.print(f"🔄 Processing: {user_input}", style="blue")
        
        # Gateway handles all preprocessing
        result = await self.gateway.process_message(
            user_input, 
            self.graph, 
            self.base_config
        )
        
        # Handle result
        if result.error:
            self.console.print(f"❌ Error: {result.error}", style="red")
            return
        
        # Show slash command processing if any
        if result.slash_commands_processed:
            self.console.print(f"✅ Processed commands: {result.slash_commands_processed}", style="green")
        
        # Execute the result
        if result.resume_command:
            self.console.print("🔄 Resuming from interrupt...", style="blue")
            # Resume commands come from gateway - execute with streaming
            try:
                async for chunk in self.graph.astream(result.resume_command, config=self.base_config, stream_mode="custom"):
                    # Handle custom streaming events from get_stream_writer()
                    if chunk.get("event_type") == "status":
                        message = chunk.get("message", "Processing...")
                        progress = chunk.get("progress", 0)
                        # Show real-time status updates
                        if progress:
                            self.console.print(f"🔄 {message} ({progress*100:.0f}%)", style="blue")
                        else:
                            self.console.print(f"🔄 {message}", style="blue")
                
                # After resuming, check if there are more interrupts or if execution completed
                state = self.graph.get_state(config=self.base_config)
                
                # Check for additional interrupts
                if state.interrupts:
                    interrupt = state.interrupts[0]
                    user_message = interrupt.value.get('user_message', 'Additional approval required')
                    self.console.print(f"\n{user_message}", style="yellow")
                    
                    user_input = await self.prompt_session.prompt_async(
                        HTML('<prompt>👤 You: </prompt>'),
                        style=self.prompt_style
                    )
                    user_input = user_input.strip()
                    await self._process_user_input(user_input)
                else:
                    # Execution completed successfully
                    await self._show_final_result(state.values)
                    
            except Exception as e:
                self.console.print(f"❌ Resume error: {e}", style="red")
                logger.exception("Error during resume execution")
        elif result.agent_state:
            # Debug: Show execution step results count in fresh state  
            step_results = result.agent_state.get("execution_step_results", {})
            self.console.print(f"🔄 Starting new conversation turn (execution_step_results: {len(step_results)} records)...", style="blue")
            await self._execute_result(result.agent_state)
        else:
            self.console.print("⚠️  No action required", style="yellow")
    
    async def _execute_result(self, input_data: Any):
        """Execute agent processing with real-time streaming and interrupt handling.
        
        Executes the agent graph with the provided input data, streaming real-time
        status updates to the user and handling approval interrupts that may occur
        during processing. This method provides the core execution loop for new
        conversation turns.
        
        Execution Flow:
        1. Start streaming execution through LangGraph
        2. Process custom streaming events for status updates
        3. Display real-time progress with formatted messages
        4. Check final state for interrupts or completion
        5. Handle approval interrupts by collecting user input
        6. Display final results for completed executions
        
        The method handles LangGraph's custom streaming mode to capture status
        events generated by framework nodes during execution. Status updates
        include progress information, component names, and completion status.
        
        :param input_data: Preprocessed input data from Gateway for agent execution
        :type input_data: Any
        :raises Exception: Execution errors are logged and displayed to user
        
        .. note::
           Uses LangGraph's 'custom' stream mode to capture framework-specific
           status events while maintaining compatibility with standard streaming.
        
        .. warning::
           Execution may pause for user approval during sensitive operations.
           The method will recursively call _process_user_input for approvals.
        
        Examples:
            Normal execution flow::
            
                >>> await cli._execute_result(agent_state)
                🔄 Data Analysis - Loading dataset...
                🔄 Data Analysis - Processing 1000 records...
                🤖 Analysis complete! Found 3 key insights.
            
            Approval interrupt handling::
            
                >>> await cli._execute_result(agent_state)
                🔄 Python Executor - Generating analysis code...
                ⚠️ Approve Python execution? (yes/no)
                # Waits for user input and processes approval
        
        .. seealso::
           :meth:`_process_user_input` : Recursive approval handling
           :meth:`_show_final_result` : Final result display formatting
           :class:`langgraph.graph.StateGraph` : LangGraph streaming execution
        """
        
        try:
            # Use streaming for real-time updates
            async for chunk in self.graph.astream(input_data, config=self.base_config, stream_mode="custom"):
                # Handle custom streaming events from get_stream_writer()
                if chunk.get("event_type") == "status":
                    message = chunk.get("message", "Processing...")
                    progress = chunk.get("progress", 0)
                    # Show real-time status updates
                    if progress:
                        self.console.print(f"🔄 {message} ({progress*100:.0f}%)", style="white")
                    else:
                        self.console.print(f"🔄 {message}", style="white")
            
            # After streaming completes, check for interrupts
            state = self.graph.get_state(config=self.base_config)
            
            # Check for interrupts - in LangGraph, interrupts pause execution
            # and are available in state.interrupts or when state.next is not empty
            if state.interrupts:
                # Handle interrupt - show the interrupt message
                interrupt = state.interrupts[0]  # Get first interrupt
                interrupt_value = interrupt.value
                
                # Extract user message from interrupt data
                user_message = interrupt_value.get('user_message', 'Approval required')
                self.console.print(f"\n{user_message}", style="yellow")
                
                # Get user input for approval
                user_input = await self.prompt_session.prompt_async(
                    HTML('<prompt>👤 You: </prompt>'),
                    style=self.prompt_style
                )
                user_input = user_input.strip()
                
                # Process the approval response through gateway
                await self._process_user_input(user_input)
                return
            
            # No interrupt, show final result
            await self._show_final_result(state.values)
        
        except Exception as e:
            self.console.print(f"❌ Execution error: {e}", style="red")
            logger.exception("Error during graph execution")
    
    async def _show_final_result(self, result: Dict[str, Any]):
        """Display the final result from agent graph execution.
        
        Extracts and displays the final response from the completed agent
        execution, handling message extraction from the LangGraph state and
        providing debug information about execution metadata.
        
        Result Processing:
        1. Extract execution step results for debugging information
        2. Search messages list for the latest AI response
        3. Filter out human messages to find agent responses
        4. Display formatted response or fallback completion message
        5. Show execution statistics for debugging
        
        The method searches through the messages in reverse order to find the
        most recent assistant message, ensuring the latest response is displayed
        even in complex conversation flows.
        
        :param result: Complete agent state containing messages and execution data
        :type result: Dict[str, Any]
        
        .. note::
           The method displays execution step count for debugging purposes,
           helping track framework performance and execution complexity.
        
        .. warning::
           If no valid assistant message is found, displays a generic
           completion message rather than failing silently.
        
        Examples:
            Display agent response::
            
                >>> await cli._show_final_result({
                ...     "messages": [user_msg, assistant_msg],
                ...     "execution_step_results": {"step1": "data"}
                ... })
                📊 Execution completed (execution_step_results: 1 records)
                🤖 Here's the analysis you requested...
            
            Handle empty response::
            
                >>> await cli._show_final_result({"messages": []})
                📊 Execution completed (execution_step_results: 0 records)
                ✅ Execution completed
        
        .. seealso::
           :class:`langchain_core.messages.BaseMessage` : Message type handling
           :class:`rich.console.Console` : Console output formatting
        """
        
        # Debug: Show execution step results count after execution
        step_results = result.get("execution_step_results", {})
        self.console.print(f"📊 Execution completed (execution_step_results: {len(step_results)} records)", style="cyan")
        
        # Extract response from messages
        messages = result.get("messages", [])
        if messages:
            # Get the latest AI message
            for msg in reversed(messages):
                if hasattr(msg, 'content') and msg.content:
                    if not hasattr(msg, 'type') or msg.type != 'human':
                        self.console.print(f"🤖 {msg.content}", style="green")
                        return
        
        # Fallback if no messages found
        self.console.print("✅ Execution completed", style="green")
    
    async def _handle_stream_event(self, event: Dict[str, Any]):
        """Handle and display streaming events from LangGraph execution.
        
        Processes streaming events from the agent graph to extract and display
        responses from specific framework nodes. This method handles the event
        structure to find assistant messages from response-generating nodes.
        
        Event Processing:
        1. Iterate through event nodes to find response nodes
        2. Extract messages from nodes that generate responses
        3. Filter messages to find latest assistant response
        4. Display formatted response or completion message
        5. Handle cases where no response is found
        
        The method specifically looks for events from 'respond', 'clarify', and
        'error' nodes which are the primary response-generating components in
        the framework architecture.
        
        :param event: Streaming event dictionary from LangGraph execution
        :type event: Dict[str, Any]
        
        .. note::
           This method is designed for LangGraph's standard streaming mode
           and complements the custom streaming used in _execute_result.
        
        .. warning::
           If no response is found in the event, displays a generic
           completion message to avoid silent failures.
        
        Examples:
            Handle response event::
            
                >>> event = {
                ...     "respond": {
                ...         "messages": [assistant_message]
                ...     }
                ... }
                >>> await cli._handle_stream_event(event)
                🤖 Here's my response to your query...
            
            Handle empty event::
            
                >>> await cli._handle_stream_event({"other_node": {}})
                ✅ Execution completed
        
        .. seealso::
           :meth:`_show_final_result` : Alternative result display method
           :class:`langchain_core.messages.BaseMessage` : Message handling
        """
        
        # Extract response from the event
        for node_name, node_data in event.items():
            if node_name in ["respond", "clarify", "error"] and "messages" in node_data:
                messages = node_data["messages"]
                if messages:
                    # Get the latest AI message
                    for msg in reversed(messages):
                        if hasattr(msg, 'content') and msg.content:
                            if not hasattr(msg, 'type') or msg.type != 'human':
                                self.console.print(f"🤖 {msg.content}", style="green")
                                return

        
        # If no response found, show completion
        self.console.print("✅ Execution completed", style="green")


async def main():
    """Main entry point for the CLI application.
    
    Creates a CLI instance and starts the interactive session. This function
    serves as the primary entry point when the module is executed directly,
    providing a clean interface for starting the command-line application.
    
    The function handles the complete CLI lifecycle from initialization through
    user interaction to graceful shutdown. All error handling and session
    management is delegated to the CLI class.
    
    :raises Exception: Startup errors are propagated from CLI initialization
    
    Examples:
        Run from command line::
        
            $ python interfaces/CLI/direct_conversation.py
            # Starts interactive CLI session
        
        Programmatic usage::
        
            >>> import asyncio
            >>> asyncio.run(main())
            # Starts CLI in async context
    
    .. seealso::
       :class:`CLI` : Main CLI interface class
       :meth:`CLI.run` : Primary interaction loop
    """
    cli = CLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main()) 