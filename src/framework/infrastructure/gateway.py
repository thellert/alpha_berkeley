"""
Gateway for Alpha Berkeley Agent Framework

This module provides the single entry point for all message processing.
All interfaces (CLI, OpenWebUI, etc.) should call Gateway.process_message().

The Gateway handles:
- State reset for new conversation turns
- Slash command parsing and application
- Approval response detection and resume commands
- Message preprocessing and state updates

Architecture:
- Gateway is the only component that creates state updates
- Interfaces handle presentation only
- Clean separation of concerns with single responsibility
"""

from __future__ import annotations
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple, Any, List, Union
from dataclasses import dataclass
import textwrap
import re

from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.types import Command

from configs.logger import get_logger
from configs.config import get_model_config
from framework.state import AgentState, StateManager
from framework.state.messages import MessageUtils
from framework.models import get_chat_completion


class ApprovalResponse(BaseModel):
    """Structured response for approval detection."""
    approved: bool

logger = get_logger("framework", "gateway")

@dataclass 
class GatewayResult:
    """Result of gateway message processing.
    
    This is the interface between Gateway and all other components.
    """
    # For normal conversation flow
    agent_state: Optional[Dict[str, Any]] = None
    
    # For interrupt/approval flow  
    resume_command: Optional[Command] = None
    
    # Processing metadata
    slash_commands_processed: List[str] = None
    approval_detected: bool = False
    is_interrupt_resume: bool = False
    
    # Error handling
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.slash_commands_processed is None:
            self.slash_commands_processed = []


class Gateway:
    """
    Gateway - Single Entry Point for All Message Processing
    
    This is the only component that interfaces should call for message processing.
    All state management, slash commands, and approval handling is centralized here.
    
    Usage::
    
        gateway = Gateway()
        result = await gateway.process_message(user_input, graph, config)
        
        # Execute the result
        if result.resume_command:
            await graph.ainvoke(result.resume_command, config=config)
        elif result.state_updates:
            await graph.ainvoke(result.state_updates, config=config)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the gateway.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logger
        
        # Initialize global configuration
        try:
            # Using config - no need to store config instance
            pass
        except Exception as e:
            self.logger.warning(f"Could not load config system: {e}")
        
        self.logger.info("Gateway initialized")
    
    async def process_message(
        self, 
        user_input: str,
        compiled_graph: Any = None,
        config: Optional[Dict[str, Any]] = None
    ) -> GatewayResult:
        """
        Single entry point for all message processing.
        
        This method handles the complete message processing flow:
        1. Check for pending interrupts (approval flow)
        2. Process new messages (normal flow)
        3. Apply state reset and slash commands
        4. Return complete result ready for execution
        
        Args:
            user_input: The raw user message
            compiled_graph: The compiled LangGraph instance
            config: LangGraph execution configuration
            
        Returns:
            GatewayResult: Complete processing result ready for execution
        """
        self.logger.info(f"Processing message: '{user_input[:50]}...'")
        
        try:
            # Check for pending interrupts first
            if self._has_pending_interrupts(compiled_graph, config):
                self.logger.info("Pending interrupt detected - processing as approval response")
                return await self._handle_interrupt_flow(user_input, compiled_graph, config)
            
            # Process as new conversation turn
            self.logger.info("Processing as new conversation turn")
            return await self._handle_new_message_flow(user_input, compiled_graph, config)
            
        except Exception as e:
            self.logger.exception(f"Error in message processing: {e}")
            return GatewayResult(error=str(e))
    
    async def _handle_interrupt_flow(
        self, 
        user_input: str, 
        compiled_graph: Any, 
        config: Dict[str, Any]
    ) -> GatewayResult:
        """Handle interrupt/approval flow generically.
        
        Gateway detects approval/rejection and uses Command(update=...) to inject 
        interrupt payload into agent state while resuming execution.
        """
        
        # Detect approval or rejection
        approval_data = self._detect_approval_response(user_input)
        
        if approval_data:
            self.logger.key_info(f"Detected {approval_data['type']} response")
            
            # Get interrupt payload and extract just the business data
            success, interrupt_payload = self._extract_resume_payload(compiled_graph, config)
            
            if success:
                resume_payload = interrupt_payload.get("resume_payload", {})
                
                # Create resume command that injects approval data into agent state
                resume_command = Command(
                    update={
                        "approval_approved": approval_data["approved"],
                        "approved_payload": resume_payload if approval_data["approved"] else None
                    }
                )
                
                return GatewayResult(
                    resume_command=resume_command,
                    approval_detected=True,
                    is_interrupt_resume=True
                )
            else:
                self.logger.warning("Could not extract resume payload, proceeding without resume command.")
                return GatewayResult(
                    error="Could not extract resume payload, please try again or provide a clear approval/rejection response."
                )
        else:
            self.logger.warning("No clear approval/rejection detected in interrupt context")
            return GatewayResult(
                error="Please provide a clear approval (yes/ok/approve) or rejection (no/cancel/reject) response"
            )
    
    async def _handle_new_message_flow(
        self, 
        user_input: str,
        compiled_graph: Any = None,
        config: Optional[Dict[str, Any]] = None
    ) -> GatewayResult:
        """Handle new message flow with fresh state creation."""
        
        # Parse slash commands first
        slash_commands, cleaned_message = self._parse_slash_commands(user_input)
        
        # Get current state if available to preserve persistent fields
        current_state = None
        if compiled_graph and config:
            try:
                graph_state = compiled_graph.get_state(config)
                current_state = graph_state.values if graph_state else None
                # Debug: Show what we're starting with
                if current_state:
                    exec_history = current_state.get("execution_history", [])
                    self.logger.info(f"DEBUG: Previous state has {len(exec_history)} execution records")
            except Exception as e:
                self.logger.warning(f"Could not get current state: {e}")
        
        # Create completely fresh state (not partial updates)
        message_content = cleaned_message.strip() if cleaned_message.strip() else user_input
        fresh_state = StateManager.create_fresh_state(
            user_input=message_content,
            current_state=current_state
        )
        
        # Debug: Show fresh state execution history
        fresh_exec_history = fresh_state.get("execution_history", [])
        self.logger.info(f"DEBUG: Fresh state created with {len(fresh_exec_history)} execution records")
        
        # Apply slash commands if any
        if slash_commands:
            # Create readable command list with options
            command_list = [f"/{cmd}:{opt}" if opt else f"/{cmd}" for cmd, opt in slash_commands.items()]
            self.logger.info(f"Processing slash commands: {command_list}")
            agent_control_updates = self._apply_slash_commands(slash_commands)
            fresh_state['agent_control'].update(agent_control_updates)
            self.logger.info(f"Applied slash commands {command_list} to agent_control")
        
        # Add execution metadata
        fresh_state["execution_start_time"] = time.time()
        
        self.logger.info("Created fresh state for new conversation turn")
        
        # Create readable command list for user feedback
        processed_commands = []
        if slash_commands:
            processed_commands = [f"/{cmd}:{opt}" if opt else f"/{cmd}" for cmd, opt in slash_commands.items()]
        
        return GatewayResult(
            agent_state=fresh_state,
            slash_commands_processed=processed_commands
        )
    
    def _has_pending_interrupts(self, compiled_graph: Any, config: Optional[Dict[str, Any]]) -> bool:
        """Check if there are pending interrupts.
        
        CRITICAL: Check state.interrupts (actual pending human approvals) 
        NOT state.next (scheduled nodes to execute).
        
        When graphs crash during routing, state.next can remain populated with 
        failed transitions, causing false interrupt detection.
        """
        if not compiled_graph or not config:
            return False
            
        try:
            graph_state = compiled_graph.get_state(config)
            return bool(graph_state and graph_state.interrupts)
        except Exception as e:
            self.logger.warning(f"Could not check graph interrupts: {e}")
            return False
    
    def _detect_approval_response(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Detect approval or rejection in user input using LLM classification."""
        try:
            # Get approval model configuration from framework config
            approval_config = get_model_config("framework", "approval")
            if not approval_config:
                self.logger.warning("No approval model configuration found - defaulting to not approved")
                return {
                    "type": "rejection",
                    "approved": False,
                    "message": user_input,
                    "timestamp": time.time()
                }
            
            # Create minimal prompt for approval detection
            prompt = f"""Analyze this user message and determine if it indicates approval or rejection of a request.

User message: "{user_input}"

Respond with true if the message indicates approval (yes, okay, proceed, continue, etc.) or false if it indicates rejection (no, cancel, stop, etc.) or is unclear."""

            # Get structured response from LLM
            result = get_chat_completion(
                message=prompt,
                model_config=approval_config,
                output_model=ApprovalResponse,
                max_tokens=10  # Very short response needed
            )
            
            # Convert to expected format
            return {
                "type": "approval" if result.approved else "rejection",
                "approved": result.approved,
                "message": user_input,
                "timestamp": time.time()
            }
                
        except Exception as e:
            self.logger.warning(f"Approval detection failed: {e} - defaulting to not approved")
            return {
                "type": "rejection",
                "approved": False,
                "message": user_input,
                "timestamp": time.time()
            }
    
    def _extract_resume_payload(self, compiled_graph: Any, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Extract interrupt payload from current LangGraph state.
        
        Gets the interrupt data from graph state and extracts the payload
        that contains the execution plan or other approval data.
        
        Args:
            compiled_graph: The compiled LangGraph instance
            config: LangGraph configuration
            
        Returns:
            Tuple of (success, payload) where success indicates if extraction worked
            and payload contains interrupt data or empty dict if failed
        """
        try:
            # Get current graph state
            graph_state = compiled_graph.get_state(config)
            
            if not graph_state or not hasattr(graph_state, 'interrupts'):
                self.logger.debug("No graph state or interrupts available")
                return False, {}
            
            # Check if there are any interrupts in the graph state
            if graph_state.interrupts:
                # Get the latest interrupt
                latest_interrupt = graph_state.interrupts[-1]
                
                if hasattr(latest_interrupt, 'value') and latest_interrupt.value:
                    interrupt_payload = latest_interrupt.value
                    
                    self.logger.info(f"Successfully extracted interrupt payload: {list(interrupt_payload.keys())}")
                    return True, interrupt_payload
                else:
                    self.logger.debug("No value found in interrupt data")
                    return False, {}
            
            self.logger.debug("No interrupts found in graph state")
            return False, {}
            
        except Exception as e:
            self.logger.error(f"Failed to extract resume payload: {e}")
            return False, {}

    def _clear_approval_state(self) -> Dict[str, Any]:
        """Clear approval state to prevent pollution in subsequent interrupts.
        
        This utility ensures that approval state from previous interrupts
        doesn't leak into subsequent operations, maintaining clean state hygiene.
        
        Returns:
            Dictionary with approval state fields set to None
        """
        return {
            "approval_approved": None,
            "approved_payload": None
        }
    
    def _parse_slash_commands(self, user_input: str) -> Tuple[Dict[str, Optional[str]], str]:
        """Parse slash commands from user input.
        
        Supported formats:
        - /command - command without option
        - /command:option - command with option
        
        Returns:
            Tuple of (commands_dict, remaining_message)
        """
        if not user_input.startswith('/'):
            return {}, user_input
        
        commands = {}
        remaining_parts = []
        
        # Split message into parts
        parts = user_input.split()
        
        for part in parts:
            if part.startswith('/'):
                if ':' in part:
                    # Format: /command:option
                    match = re.match(r'^/([a-zA-Z_]+):([a-zA-Z_]+)$', part)
                    if match:
                        command, option = match.groups()
                        commands[command] = option
                        self.logger.debug(f"Parsed command: /{command}:{option}")
                    else:
                        self.logger.warning(f"Invalid command format: {part}")
                        remaining_parts.append(part)
                else:
                    # Format: /command
                    match = re.match(r'^/([a-zA-Z_]+)$', part)
                    if match:
                        command = match.group(1)
                        commands[command] = None
                        self.logger.debug(f"Parsed command: /{command}")
                    else:
                        self.logger.warning(f"Invalid command format: {part}")
                        remaining_parts.append(part)
            else:
                remaining_parts.append(part)
        
        remaining_message = ' '.join(remaining_parts)
        return commands, remaining_message
    
    def _apply_slash_commands(self, commands: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Apply slash commands to agent control state.
        
        Returns only the changes from slash commands (will be merged with existing state).
        """
        # Only track changes from slash commands (not full state)
        agent_control_changes = {}
        
        # Apply slash commands  
        for command, option in commands.items():
            if command == "planning":
                if option in ["on", "enabled", "true"] or option is None:
                    agent_control_changes["planning_mode_enabled"] = True
                    self.logger.info("Enabled planning mode via slash command")
                elif option in ["off", "disabled", "false"]:
                    agent_control_changes["planning_mode_enabled"] = False
                    self.logger.info("Disabled planning mode via slash command")
            
            elif command == "approval":
                if option in ["on", "enabled", "true"] or option is None:
                    agent_control_changes["approval_mode"] = "enabled"
                    self.logger.info("Enabled approval mode via slash command")
                elif option in ["off", "disabled", "false"]:
                    agent_control_changes["approval_mode"] = "disabled"
                    self.logger.info("Disabled approval mode via slash command")
                elif option == "selective":
                    agent_control_changes["approval_mode"] = "selective"
                    self.logger.info("Set approval mode to selective via slash command")
            
            elif command == "debug":
                if option in ["on", "enabled", "true"] or option is None:
                    agent_control_changes["debug_mode"] = True
                    self.logger.info("Enabled debug mode via slash command")
                elif option in ["off", "disabled", "false"]:
                    agent_control_changes["debug_mode"] = False
                    self.logger.info("Disabled debug mode via slash command")
            
            # Task extraction bypass control
            elif command == "task":
                if option in ["off", "disabled", "false"]:
                    agent_control_changes["task_extraction_bypass_enabled"] = True
                    self.logger.info("Enabled task extraction bypass via slash command")
                elif option in ["on", "enabled", "true"]:
                    agent_control_changes["task_extraction_bypass_enabled"] = False
                    self.logger.info("Disabled task extraction bypass via slash command")
                else:
                    self.logger.warning(f"Invalid option for /task command: '{option}'. Use 'on' or 'off'")
            
            # Capability selection bypass control
            elif command == "caps":
                if option in ["off", "disabled", "false"]:
                    agent_control_changes["capability_selection_bypass_enabled"] = True
                    self.logger.info("Enabled capability selection bypass via slash command")
                elif option in ["on", "enabled", "true"]:
                    agent_control_changes["capability_selection_bypass_enabled"] = False
                    self.logger.info("Disabled capability selection bypass via slash command")
                else:
                    self.logger.warning(f"Invalid option for /caps command: '{option}'. Use 'on' or 'off'")
            
            else:
                self.logger.warning(f"Unknown slash command: /{command}")
        
        return agent_control_changes
    
 