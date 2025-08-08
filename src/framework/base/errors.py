"""Error Classification Framework - Comprehensive Error Handling System

This module provides the complete error classification and handling infrastructure
for the ALS Expert framework. It implements a sophisticated error management system
that enables intelligent error classification, recovery strategy selection, and
comprehensive error tracking throughout the entire framework ecosystem.

The error classification system serves as the foundation for robust error handling
by providing structured error analysis, severity classification, and recovery
strategy coordination. It integrates seamlessly with both capability execution
and infrastructure operations to ensure consistent error handling patterns.

Key Error Management Components:
    1. **ErrorSeverity Enum**: Defines classification levels and recovery strategies
    2. **ErrorClassification**: Structured error analysis with recovery information
    3. **ExecutionError**: Comprehensive error data for execution failures
    4. **Framework Exceptions**: Custom exception hierarchy for system errors

Error Classification Levels:
    - **CRITICAL**: End execution immediately - unrecoverable errors
    - **RETRIABLE**: Retry execution with same parameters - transient failures
    - **REPLANNING**: Create new execution plan - strategy failures
    - **FATAL**: System-level failure - immediate termination required

The error system integrates with LangGraph's execution model while providing
manual retry coordination through the router system. This ensures consistent
error handling behavior across all framework components while maintaining
compatibility with LangGraph's checkpoint and streaming systems.

.. note::
   The framework uses manual retry handling rather than LangGraph's native
   retry policies to ensure consistent behavior and sophisticated error
   classification across all components.

.. warning::
   FATAL errors immediately terminate execution to prevent system corruption.
   Use FATAL severity only for errors that indicate serious system issues.

.. seealso::
   :mod:`framework.base.decorators` : Decorator integration with error handling
   :mod:`framework.base.results` : Result types and execution tracking
   :class:`BaseCapability` : Capability error classification methods
"""

from enum import Enum
from typing import Optional, List, Any
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Enumeration of error severity levels with comprehensive recovery strategies.
    
    This enum defines the complete spectrum of error severity classifications
    and their corresponding recovery strategies used throughout the ALS Expert
    framework. Each severity level triggers specific recovery behavior designed
    to maintain robust system operation while enabling intelligent error handling
    and graceful degradation.
    
    The severity levels form a hierarchy of recovery strategies from simple
    retries to complete execution termination. The framework's error handling
    system uses these classifications to coordinate recovery efforts between
    capabilities, infrastructure nodes, and the overall execution system.
    
    Recovery Strategy Hierarchy:
    1. **Automatic Recovery**: RETRIABLE errors with retry mechanisms
    2. **Strategy Adjustment**: REPLANNING for execution plan adaptation
    3. **Execution Control**: CRITICAL for graceful termination
    4. **System Protection**: FATAL for immediate termination
    
    :param CRITICAL: End execution immediately - unrecoverable errors requiring termination
    :type CRITICAL: str
    :param RETRIABLE: Retry current execution step with same parameters - transient failures
    :type RETRIABLE: str
    :param REPLANNING: Create new execution plan with different strategy - approach failures
    :type REPLANNING: str
    :param FATAL: System-level failure requiring immediate termination - corruption prevention
    :type FATAL: str
    
    .. note::
       The framework uses manual retry coordination rather than automatic retries
       to ensure consistent behavior and sophisticated error analysis across all
       components.
    
    .. warning::
       FATAL errors immediately raise exceptions to terminate execution and prevent
       system corruption. Use FATAL only for errors that indicate serious system
       issues that could compromise framework integrity.
    
    Examples:
        Network error classification::
        
            if isinstance(exc, ConnectionError):
                return ErrorClassification(severity=ErrorSeverity.RETRIABLE, ...)
            elif isinstance(exc, AuthenticationError):
                return ErrorClassification(severity=ErrorSeverity.CRITICAL, ...)
        
        Data validation error handling::
        
            if isinstance(exc, ValidationError):
                return ErrorClassification(severity=ErrorSeverity.REPLANNING, ...)
            elif isinstance(exc, CorruptedDataError):
                return ErrorClassification(severity=ErrorSeverity.FATAL, ...)
    
    .. seealso::
       :class:`ErrorClassification` : Structured error analysis with severity
       :class:`ExecutionError` : Comprehensive error information container
    """
    CRITICAL = "critical"           # End execution
    RETRIABLE = "retriable"         # Retry execution step
    REPLANNING = "replanning"       # Replan the execution plan
    FATAL = "fatal"                 # System-level failure - raise exception immediately


@dataclass
class ErrorClassification:
    """Comprehensive error classification result with recovery strategy coordination.
    
    This dataclass provides sophisticated error classification results that enable
    intelligent recovery strategy selection and coordination across the framework.
    It serves as the primary interface between error analysis and recovery systems,
    supporting both automated recovery mechanisms and human-guided error resolution.
    
    ErrorClassification enables comprehensive error handling by providing:
    1. **Severity Assessment**: Clear classification of error impact and recovery strategy
    2. **User Communication**: Human-readable error descriptions for interfaces
    3. **Technical Context**: Detailed debugging information for developers
    
    The classification system supports multiple recovery approaches including
    automatic retries, execution replanning, and graceful degradation patterns.
    The severity field determines the recovery strategy while user_message and
    technical_details provide contextual information for logging and debugging.
    
    :param severity: Error severity level determining recovery strategy
    :type severity: ErrorSeverity
    :param user_message: Human-readable error description for user interfaces and logs
    :type user_message: Optional[str]
    :param technical_details: Detailed technical information for debugging and logging
    :type technical_details: Optional[str]
    
    .. note::
       The framework uses this classification to coordinate recovery strategies
       across multiple system components. Different severity levels trigger
       different recovery workflows through the router system.
    
    .. warning::
       Ensure severity levels are chosen carefully as they directly impact
       system behavior and recovery strategies. Inappropriate classifications
       can lead to ineffective error handling.
    
    Examples:
        Network timeout classification::
        
            classification = ErrorClassification(
                severity=ErrorSeverity.RETRIABLE,
                user_message="Network connection timeout, retrying...",
                technical_details="HTTP request timeout after 30 seconds"
            )
        
        Missing step input requiring replanning::
        
            classification = ErrorClassification(
                severity=ErrorSeverity.REPLANNING,
                user_message="Required data not available, need different approach",
                technical_details="Step expected 'SENSOR_DATA' context but found None"
            )
        
        Critical validation failure::
        
            classification = ErrorClassification(
                severity=ErrorSeverity.CRITICAL,
                user_message="Invalid configuration detected",
                technical_details="Missing required parameter 'api_key' in capability config"
            )
        

    
    .. seealso::
       :class:`ErrorSeverity` : Severity levels and recovery strategies
       :class:`ExecutionError` : Complete error information container
    """
    severity: ErrorSeverity
    user_message: Optional[str] = None
    technical_details: Optional[str] = None


@dataclass
class ExecutionError:
    """Comprehensive execution error container with recovery coordination support.
    
    This dataclass provides a complete representation of execution errors including
    severity classification, recovery suggestions, technical debugging information,
    and context for coordinating recovery strategies. It serves as the primary
    error data structure used throughout the framework for error handling,
    logging, and recovery coordination.
    
    ExecutionError enables sophisticated error management by providing:
    1. **Error Classification**: Severity-based recovery strategy determination
    2. **User Communication**: Clear, actionable error messages for interfaces
    3. **Developer Support**: Technical details and debugging context
    4. **Recovery Guidance**: Specific suggestions for error resolution
    5. **System Integration**: Context for automated recovery systems
    
    The error structure supports both automated error handling workflows and
    human-guided error resolution processes. It integrates seamlessly with
    the framework's classification system and retry mechanisms to provide
    comprehensive error management.
    
    :param severity: Error severity classification for recovery strategy selection
    :type severity: ErrorSeverity
    :param message: Clear, human-readable description of the error condition
    :type message: str
    :param capability_name: Name of the capability or component that generated this error
    :type capability_name: Optional[str]
    :param suggestions: Domain-specific suggestions for error resolution and recovery
    :type suggestions: Optional[List[str]]
    :param technical_details: Detailed technical information for debugging and analysis
    :type technical_details: Optional[str]

    
    .. note::
       ExecutionError instances are typically created by error classification
       methods in capabilities and infrastructure nodes. The framework's
       decorators automatically handle the creation and routing of these errors.
    
    .. warning::
       The severity field directly impacts system behavior through recovery
       strategy selection. Ensure appropriate severity classification to avoid
       ineffective error handling or unnecessary system termination.
    
    Examples:
        Database connection error::
        
            error = ExecutionError(
                severity=ErrorSeverity.RETRIABLE,
                message="Database connection failed",
                capability_name="database_query",
                suggestions=[
                    "Check database server status",
                    "Verify connection credentials",
                    "Ensure network connectivity"
                ],
                technical_details="PostgreSQL connection timeout after 30 seconds"
            )
        

        
        Data corruption requiring immediate attention::
        
            error = ExecutionError(
                severity=ErrorSeverity.FATAL,
                message="Critical data corruption detected",
                capability_name="data_processor",
                technical_details="Checksum validation failed on primary data store",
                suggestions=[
                    "Initiate emergency backup procedures",
                    "Contact system administrator immediately",
                    "Do not proceed with further operations"
                ]
            )
    
    .. seealso::
       :class:`ErrorSeverity` : Severity levels and recovery strategies
       :class:`ErrorClassification` : Error analysis and classification system
       :class:`ExecutionResult` : Result containers with error integration
    """
    severity: ErrorSeverity
    message: str
    capability_name: Optional[str] = None  # Which capability generated this error
    suggestions: Optional[List[str]] = None  # Capability-specific recovery suggestions
    technical_details: Optional[str] = None  # Additional technical context for debugging



# Framework-specific exception classes
class FrameworkError(Exception):
    """Base exception for all framework-related errors.
    
    This is the root exception class for all custom exceptions within the
    ALS Expert framework. It provides a common base for framework-specific
    error handling and categorization.
    """
    pass


class RegistryError(FrameworkError):
    """Exception for registry-related errors.
    
    Raised when issues occur with component registration, lookup, or
    management within the framework's registry system.
    """
    pass


class ConfigurationError(FrameworkError):
    """Exception for configuration-related errors.
    
    Raised when configuration files are invalid, missing required settings,
    or contain incompatible values that prevent proper system operation.
    """
    pass
