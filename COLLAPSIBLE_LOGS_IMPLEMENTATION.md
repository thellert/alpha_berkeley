# Collapsible Logs Implementation Guide

## Overview

This guide shows how to implement collapsible initialization logs in the Osprey CLI. Users will see a clean progress indicator during startup, with all detailed logs captured and accessible via `Ctrl+O`.

**Design Philosophy**: This is a pure presentation layer feature - we don't suppress logs, we **redirect them to memory** during initialization, then make them available on-demand. All logs are preserved for debugging.

**Compatibility**: This feature works independently of the logging system architecture. It will work with the current logger and will continue to work seamlessly when unified logging is implemented, since it captures at the Python `logging.root` level.

## The Problem

Currently, the CLI initialization spams ~20+ registry log messages:
```
INFO     Registry: Configured 1 application registry(ies)
INFO     Registry: Added /path/to/registry.py
INFO     Registry: Loaded application registry from: ...
INFO     Registry: Built merged registry with 1 application(s)
INFO     Registry: Initializing registry system...
INFO     Registry: Registered 4 context classes
... (15+ more lines)
```

This is **important for debugging** but **clutters the UX** for normal use. We want to preserve all these logs for troubleshooting while keeping the screen clean.

## The Solution

### User Experience

**During Initialization:**
```
🔄 Initializing framework...
⠋ Loading registry and providers...
Press Ctrl+O anytime to view logs
```

**After Initialization:**
```
✅ Framework initialized! Thread ID: cli_session_a1b2c3d4
  • 21 log messages captured (press Ctrl+O to view)
  • Use ↑/↓ arrow keys to navigate command history
  • Press Ctrl+L to clear screen
  • Type 'bye' or 'end' to exit
```

**When User Presses Ctrl+O:**
```
╭──────────────── 📋 Initialization Logs ────────────────╮
│ [INFO    ] Loading configuration from: config.yml      │
│ [INFO    ] Registry: Configured 1 application registry │
│ [INFO    ] Registry: Added /path/to/registry.py        │
│ [INFO    ] Registry: Built merged registry             │
│ ... (all 21 messages)                                   │
╰────────────────────── 21 messages ─────────────────────╯

💡 Press Ctrl+O again to hide logs
```

## Implementation Strategy

### Step 1: Create a Log Capture System

Create `src/osprey/cli/log_capture.py`:

```python
"""Log capture system for collapsible CLI logs.

This module provides a thread-safe log capture mechanism that redirects
console output during CLI initialization. All logs are preserved in memory
and can be displayed on-demand via keyboard shortcuts.

Design:
- Captures at logging.root level (works with any logging API)
- Thread-safe using locks
- Memory-bounded (keeps only recent N logs)
- Preserves logger names and context
- Non-intrusive - can be toggled anytime
"""

import logging
import threading
from typing import List, Dict, Any
from rich.panel import Panel
from rich.text import Text


class CaptureHandler(logging.Handler):
    """Custom logging handler that captures records to memory.
    
    This handler is designed to replace RichHandler temporarily during
    initialization to prevent console spam while preserving all log data.
    """
    
    def __init__(self, capture_list: List[Dict[str, Any]], lock: threading.Lock, max_logs: int = 1000):
        """Initialize the capture handler.
        
        Args:
            capture_list: Shared list to store captured log records
            lock: Thread lock for safe concurrent access
            max_logs: Maximum number of logs to retain (oldest removed first)
        """
        super().__init__()
        self.capture_list = capture_list
        self.lock = lock
        self.max_logs = max_logs
    
    def emit(self, record: logging.LogRecord):
        """Capture a log record to the list.
        
        Args:
            record: The LogRecord to capture
        """
        try:
            with self.lock:
                # Keep only recent logs to prevent unbounded memory growth
                if len(self.capture_list) >= self.max_logs:
                    self.capture_list.pop(0)
                
                # Format with logger name for context (e.g., "REGISTRY", "orchestrator")
                # Preserve the logger name to help users understand where logs come from
                formatted = f"[{record.name:15}] [{record.levelname:8}] {record.getMessage()}"
                
                self.capture_list.append({
                    'level': record.levelname,
                    'name': record.name,
                    'message': record.getMessage(),
                    'formatted': formatted,
                    'timestamp': record.created
                })
        except Exception:
            # Never let logging errors break the application
            # Silently fail - logging is not critical to app function
            pass


class CLILogCapture:
    """Captures logs during initialization for later display.
    
    This class temporarily redirects logging output from the console to memory
    during CLI initialization, then restores normal logging. Users can view
    captured logs anytime via keyboard shortcuts (Ctrl+O).
    
    Thread-safe and memory-bounded for production use.
    """
    
    def __init__(self, max_logs: int = 1000):
        """Initialize the log capture system.
        
        Args:
            max_logs: Maximum number of logs to retain in memory
        """
        self.logs: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.is_visible = False
        self.capture_handler: CaptureHandler | None = None
        self.saved_handlers: List[logging.Handler] = []
        self.max_logs = max_logs
        
    def start_capture(self):
        """Start capturing logs and suppress console output.
        
        Temporarily removes all existing handlers (including RichHandler)
        and replaces them with our capture handler. This prevents logs
        from cluttering the console during initialization.
        
        All logs are preserved in memory for later viewing.
        """
        # Save existing handlers so we can restore them later
        self.saved_handlers = logging.root.handlers[:]
        
        # Remove all handlers to prevent console output
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Add our capture handler to collect logs in memory
        self.capture_handler = CaptureHandler(self.logs, self.lock, self.max_logs)
        self.capture_handler.setLevel(logging.DEBUG)  # Capture everything
        logging.root.addHandler(self.capture_handler)
        
    def stop_capture(self):
        """Stop capturing logs and restore normal logging.
        
        Removes the capture handler and restores all original handlers
        (including RichHandler) so normal console logging resumes.
        """
        # Remove capture handler
        if self.capture_handler:
            logging.root.removeHandler(self.capture_handler)
            self.capture_handler = None
        
        # Restore original handlers for normal operation
        for handler in self.saved_handlers:
            logging.root.addHandler(handler)
        
        self.saved_handlers = []
        
    def toggle_visibility(self) -> bool:
        """Toggle log visibility and return new state.
        
        Returns:
            True if logs are now visible, False if hidden
        """
        self.is_visible = not self.is_visible
        return self.is_visible
        
    def get_summary(self) -> str:
        """Get a brief summary of captured logs.
        
        Returns:
            Human-readable summary string (e.g., "21 log messages captured, 2 warnings")
        """
        with self.lock:
            if not self.logs:
                return "No logs captured"
            
            total = len(self.logs)
            errors = sum(1 for log in self.logs if log['level'] == 'ERROR')
            warnings = sum(1 for log in self.logs if log['level'] in ['WARNING', 'WARN'])
            
            parts = [f"{total} log messages captured"]
            if errors:
                parts.append(f"{errors} errors")
            if warnings:
                parts.append(f"{warnings} warnings")
                
            return ", ".join(parts)
        
    def render_panel(self) -> Panel:
        """Render logs in a Rich panel with color-coded levels.
        
        Returns:
            Rich Panel object ready to print to console
        """
        with self.lock:
            if not self.logs:
                return Panel(
                    "No logs available",
                    title="📋 Initialization Logs",
                    border_style="dim"
                )
            
            # Create Rich Text object for proper formatting
            text = Text()
            
            for log in self.logs:
                # Color by severity level
                if log['level'] == 'ERROR':
                    style = "red"
                elif log['level'] in ['WARNING', 'WARN']:
                    style = "yellow"
                elif log['level'] == 'DEBUG':
                    style = "dim cyan"
                else:
                    style = "cyan"
                
                text.append(log['formatted'] + "\n", style=style)
            
            return Panel(
                text,
                title="📋 Initialization Logs",
                subtitle=f"[dim]{len(self.logs)} messages[/dim]",
                border_style="cyan"
            )
```

### Step 2: Modify CLI Initialization

In `src/osprey/interfaces/cli/direct_conversation.py`, update the `CLI` class:

```python
from osprey.cli.log_capture import CLILogCapture
from rich.spinner import Spinner
from rich.live import Live

class CLI:
    def __init__(self, config_path="config.yml"):
        # ... existing code ...
        
        # Add log capture system
        self.log_capture = CLILogCapture()
        
    def _create_key_bindings(self):
        """Create custom key bindings."""
        bindings = KeyBindings()
        
        @bindings.add('c-l')  # Ctrl+L to clear screen
        def _(event):
            """Clear the screen."""
            clear()
        
        # NEW: Add Ctrl+O for log toggle
        @bindings.add('c-o')  # Ctrl+O to toggle logs
        def _(event):
            """Toggle initialization logs display."""
            is_showing = self.log_capture.toggle_visibility()
            
            # Force a newline to avoid prompt rendering issues
            event.app.output.write('\n')
            event.app.output.flush()
            
            if is_showing:
                self.console.print(self.log_capture.render_panel())
                self.console.print()
                self.console.print("[dim]💡 Press Ctrl+O again to hide logs[/dim]")
            else:
                self.console.print("[dim]📋 Logs hidden. Press Ctrl+O to show.[/dim]")
            
            self.console.print()
        
        return bindings
    
    async def initialize(self):
        """Initialize the CLI with framework components."""
        # Simple startup message (no banner in chat)
        self.console.print()
        self.console.print(f"[{Styles.PRIMARY}]Osprey Chat Interface[/{Styles.PRIMARY}]", style="bold")
        self.console.print(f"[{Styles.DIM}]Type 'bye' or 'end' to exit[/{Styles.DIM}]")
        self.console.print(f"[{Styles.DIM}]Use slash commands (/) for quick actions - try /help[/{Styles.DIM}]")
        self.console.print()

        # Initialize configuration
        self.console.print(f"[{Styles.INFO}]🔄 Initializing configuration...[/{Styles.INFO}]")
        
        # Create unique thread for this CLI session
        self.thread_id = f"cli_session_{uuid.uuid4().hex[:8]}"
        
        # Get base configurable and add session info
        configurable = get_full_configuration(config_path=self.config_path).copy()
        configurable.update({
            "user_id": "cli_user",
            "thread_id": self.thread_id,
            "chat_id": "cli_chat",
            "session_id": self.thread_id,
            "interface_context": "cli"
        })
        
        # Add recursion limit to runtime config
        from osprey.utils.config import get_config_value
        recursion_limit = get_config_value("execution_limits.graph_recursion_limit")
        
        self.base_config = {
            "configurable": configurable,
            "recursion_limit": recursion_limit
        }
        
        # Start capturing logs to prevent console spam
        self.log_capture.start_capture()
        
        # Show animated spinner during initialization
        self.console.print(f"[{Styles.INFO}]🔄 Initializing framework...[/{Styles.INFO}]")
        
        # Use Rich spinner for visual feedback
        spinner = Spinner("dots", text=f"[{Styles.DIM}]Loading registry and providers... (Press Ctrl+O to view logs)[/{Styles.DIM}]")
        
        try:
            with Live(spinner, console=self.console, transient=True):
                # All framework initialization happens here
                # Logs are captured silently in the background
                initialize_registry(config_path=self.config_path)
                registry = get_registry()
                checkpointer = MemorySaver()
                self.graph = create_graph(registry, checkpointer=checkpointer)
                self.gateway = Gateway()
                self.prompt_session = self._create_prompt_session()
        finally:
            # Always restore normal logging, even if init fails
            self.log_capture.stop_capture()
        
        # Success message with helpful info
        self.console.print(f"[{Styles.SUCCESS}]✅ Framework initialized! Thread ID: {self.thread_id}[/{Styles.SUCCESS}]")
        self.console.print(f"[{Styles.DIM}]  • {self.log_capture.get_summary()} (press Ctrl+O to view)[/{Styles.DIM}]")
        self.console.print(f"[{Styles.DIM}]  • Use ↑/↓ arrow keys to navigate command history[/{Styles.DIM}]")
        self.console.print(f"[{Styles.DIM}]  • Use ←/→ arrow keys to edit current line[/{Styles.DIM}]")
        self.console.print(f"[{Styles.DIM}]  • Press Ctrl+L to clear screen[/{Styles.DIM}]")
        self.console.print(f"[{Styles.DIM}]  • Type 'bye' or 'end' to exit, or press Ctrl+C[/{Styles.DIM}]")
        self.console.print()
```

### Step 3: Optional - Also Add /logs Command

For users who prefer typing commands, you can also add a `/logs` slash command in the existing command system.

## Benefits

1. **Clean UX**: Users see a simple animated spinner instead of log spam
2. **Debugging Preserved**: All logs are captured and accessible on-demand with Ctrl+O
3. **Non-Intrusive**: Logs are hidden by default but always available
4. **Familiar Pattern**: Uses Ctrl+O (similar to Ctrl+L for clear screen)
5. **Works Anywhere**: Can toggle logs before, during, or after conversation
6. **Thread-Safe**: Production-ready with proper locking for concurrent access
7. **Memory-Bounded**: Automatically manages memory by limiting retained logs
8. **Context-Rich**: Preserves logger names (REGISTRY, orchestrator, etc.) for debugging
9. **Future-Proof**: Works with current logger and will work with unified logging
10. **Robust**: Error-safe implementation that never breaks the application

## Alternative: Use Existing /debug Command

If you want to leverage the existing slash command system:

```python
# In the command registry
@command("logs", "Show/hide initialization logs")
def show_logs_command(context: CommandContext) -> CommandResult:
    """Toggle initialization logs display."""
    cli = context.cli_instance
    is_showing = cli.log_capture.toggle_visibility()
    
    if is_showing:
        cli.console.print()
        cli.console.print(cli.log_capture.render_panel())
        cli.console.print()
        return CommandResult(
            success=True,
            message="Showing initialization logs (type /logs again to hide)"
        )
    else:
        return CommandResult(
            success=True,
            message="Logs hidden (type /logs to show)"
        )
```

## Testing

After implementation, test:

### Functional Tests
1. ✅ Start CLI - should see clean initialization with spinner
2. ✅ Press Ctrl+O during chat - should show all captured logs
3. ✅ Press Ctrl+O again - should hide logs
4. ✅ Verify all registry logs are captured (check count matches expectation)
5. ✅ Test that log levels are color-coded correctly (ERROR=red, WARNING=yellow, INFO=cyan)
6. ✅ Verify log capture doesn't interfere with normal logging after init

### Edge Cases
7. ✅ Test with initialization errors - logs should still be captured and viewable
8. ✅ Test Ctrl+O before initialization completes - should work
9. ✅ Test rapid Ctrl+O toggling - no crashes or rendering issues
10. ✅ Test with long-running sessions - verify memory doesn't grow unbounded
11. ✅ Test logger names are preserved (e.g., "REGISTRY", "orchestrator")
12. ✅ Test with empty logs (start CLI, immediately Ctrl+O)

### Integration Tests
13. ✅ Verify prompt still works correctly after toggling logs
14. ✅ Test compatibility with Ctrl+L (clear screen)
15. ✅ Test compatibility with arrow keys (history navigation)
16. ✅ Test in different terminal emulators (iTerm, Terminal.app, etc.)
17. ✅ Test that handlers are properly restored after capture

## Key Implementation Fixes

This updated implementation addresses several critical issues from the original plan:

### 1. **Proper Handler Implementation** ✅
- **Before**: Tried to assign `emit` method to handler instance (doesn't work)
- **After**: Proper `logging.Handler` subclass with overridden `emit()` method

### 2. **Console Output Suppression** ✅
- **Before**: Captured logs but RichHandler still printed to console
- **After**: Temporarily removes RichHandler, adds capture handler, then restores
- **Result**: Clean console during init, all logs preserved in memory

### 3. **Thread Safety** ✅
- **Before**: No locking mechanism
- **After**: Uses `threading.Lock` for safe concurrent access
- **Result**: Production-ready for multi-threaded environments

### 4. **Memory Management** ✅
- **Before**: Unbounded log list could grow indefinitely
- **After**: Configurable `max_logs` with automatic oldest-log removal
- **Result**: Bounded memory usage even in long-running sessions

### 5. **Logger Context Preservation** ✅
- **Before**: Only captured message text
- **After**: Preserves logger name (e.g., "REGISTRY", "orchestrator")
- **Result**: Better debugging with component identification

### 6. **Spinner Implementation** ✅
- **Before**: Mock UI only, no implementation
- **After**: Rich `Spinner` with `Live` context manager
- **Result**: Professional animated feedback during init

### 7. **Prompt Rendering Safety** ✅
- **Before**: Could break prompt rendering when toggling logs
- **After**: Explicit newline and flush before printing
- **Result**: Clean rendering without artifacts

### 8. **Error Handling** ✅
- **Before**: No error handling in capture
- **After**: Try-except in `emit()` to prevent logging errors from breaking app
- **Result**: Robust even if logging fails

## Architecture Notes

### Why This Works Independently

This feature operates at the **presentation layer** and is independent of the logging API:

```
Application Layer
    ↓
Logger API (current or unified)
    ↓
Python logging.root  ← Log capture happens here
    ↓
Handlers (RichHandler / CaptureHandler)
    ↓
Console Output
```

**Key insight**: By capturing at `logging.root`, we're below the API layer. Whether you use:
- Current: `logger = get_logger("component")` 
- Future: `logger = get_stateful_logger("component", state)`

Both send logs to `logging.root`, so capture works the same way.

### Compatibility with Unified Logging

When unified logging is implemented:
1. `UnifiedLogger` will still use Python's logging system
2. Messages will still flow through `logging.root`
3. Our `CaptureHandler` will still intercept them
4. **No changes needed** to the collapsible logs feature

The only potential enhancement: unified logging's metadata could be displayed in the log panel for richer debugging context.

## Implementation Checklist

Ready to implement? Follow these steps:

### Phase 1: Core Implementation
- [ ] Create `src/osprey/cli/log_capture.py` with corrected implementation
  - [ ] `CaptureHandler` class with proper `logging.Handler` subclass
  - [ ] `CLILogCapture` class with thread safety and memory management
  - [ ] All methods implemented (start_capture, stop_capture, toggle, render)

### Phase 2: CLI Integration
- [ ] Update `src/osprey/interfaces/cli/direct_conversation.py`
  - [ ] Import log capture and Rich components
  - [ ] Add `self.log_capture = CLILogCapture()` to `__init__`
  - [ ] Add Ctrl+O key binding to `_create_key_bindings()`
  - [ ] Wrap initialization in log capture with spinner

### Phase 3: Testing
- [ ] Run all functional tests (12 test cases)
- [ ] Test edge cases (initialization errors, rapid toggling, etc.)
- [ ] Integration testing (prompt compatibility, handler restoration)
- [ ] Cross-platform testing (different terminal emulators)

### Phase 4: Documentation
- [ ] Update CLI user documentation with Ctrl+O shortcut
- [ ] Add troubleshooting section for common issues
- [ ] Document memory limits and configuration options

## Estimated Implementation Time

- **Core Implementation**: 30-45 minutes
- **CLI Integration**: 15-20 minutes  
- **Testing**: 30-45 minutes
- **Documentation**: 15-20 minutes

**Total: ~2 hours** for a complete, production-ready implementation

## Next Steps

1. **Immediate**: Implement collapsible logs using this updated guide
2. **Future**: When unified logging is implemented, optionally enhance the log panel with:
   - Filtering by component name
   - Filtering by log level
   - Display of streaming metadata
   - Export logs to file

The collapsible logs feature is **ready for implementation** and will work seamlessly with both current and future logging systems. 🚀
