"""
Static Analysis Node - LangGraph Architecture

Analyzes generated Python code for potential issues before execution.
Enhanced with EPICS operation detection and execution mode selection.
Transformed for LangGraph integration with TypedDict state management.
"""

import ast
import re
from typing import Dict, Any, List, Optional


from .exceptions import (
    CodeSyntaxError, CodeGenerationError, ContainerConfigurationError,
    MaxAttemptsExceededError, PythonExecutorException
)
from framework.approval.approval_system import create_code_approval_interrupt
from .models import PythonExecutionState, AnalysisResult, validate_result_structure, get_execution_mode_config_from_configurable
from .services import FileManager, NotebookManager
from .execution_control import ExecutionMode
from .execution_policy_analyzer import BasicAnalysisResult, DomainAnalysisManager, ExecutionPolicyManager
from configs.logger import get_logger
from configs.streaming import get_streamer
from configs.config import get_full_configuration
from framework.approval.approval_manager import get_python_execution_evaluator

logger = get_logger("framework", "python_analyzer")


class StaticCodeAnalyzer:
    """Clean code analyzer with proper exception handling"""
    
    def __init__(self, configurable):
        self.configurable = configurable
    
    async def analyze_code(self, code: str, context: Any) -> AnalysisResult:
        """Perform comprehensive static analysis using configurable execution policy analyzers"""
        
        try:
            # ========================================
            # BASIC ANALYSIS (Hard-coded Framework Safety Checks)
            # ========================================
            
            # 1. Syntax validation
            syntax_issues = self._check_syntax(code)
            syntax_valid = len(syntax_issues) == 0
            
            # Critical syntax errors should fail immediately
            if not syntax_valid:
                raise CodeSyntaxError(
                    "Code contains syntax errors",
                    syntax_issues=syntax_issues,
                    technical_details={"code_preview": code[:200] + "..." if len(code) > 200 else code}
                )
            
            # 2. Security analysis
            security_issues = self._check_security(code)
            security_risk_level = self._determine_security_risk_level(security_issues)
            
            # 3. Import validation
            import_issues = self._check_imports(code)
            prohibited_imports = self._get_prohibited_imports(import_issues)
            
            # 4. Result structure validation
            has_result_structure = validate_result_structure(code)
            
            # Create basic analysis result
            basic_analysis = BasicAnalysisResult(
                syntax_valid=syntax_valid,
                syntax_issues=syntax_issues,
                security_issues=security_issues,
                security_risk_level=security_risk_level,
                import_issues=import_issues,
                prohibited_imports=prohibited_imports,
                has_result_structure=has_result_structure,
                code=code,
                code_length=len(code),
                user_context=None,  # Could be populated from context if needed
                execution_context=None
            )
            
            # ========================================
            # DOMAIN ANALYSIS (Framework-provided EPICS analysis)
            # ========================================
            
            domain_manager = DomainAnalysisManager(self.configurable)
            domain_analysis = await domain_manager.analyze_domain(basic_analysis)
            
            # ========================================
            # EXECUTION POLICY DECISION (Configurable)
            # ========================================
            
            policy_manager = ExecutionPolicyManager(self.configurable)
            policy_decision = await policy_manager.analyze_policy(basic_analysis, domain_analysis)
           
            
            # Combine all issues
            all_issues = []
            all_issues.extend(basic_analysis.syntax_issues)
            all_issues.extend(basic_analysis.security_issues)
            all_issues.extend(basic_analysis.import_issues)
            all_issues.extend(policy_decision.additional_issues)
            
            # Determine severity and pass/fail status
            critical_issues = [issue for issue in all_issues if any(word in issue.lower() for word in ["error", "invalid", "blocked"])]
            passed = len(critical_issues) == 0 and policy_decision.analysis_passed
            severity = "error" if critical_issues else ("warning" if all_issues else "info")
            
            # Get execution mode configuration
            execution_mode_config = None
            try:
                mode_config = get_execution_mode_config_from_configurable(self.configurable, policy_decision.execution_mode.value)
                execution_mode_config = mode_config.__dict__
            except Exception as e:
                logger.warning(f"Failed to load execution mode config: {e}")
            
            # Extract EPICS flags from domain analysis for backward compatibility
            has_epics_writes = "epics_writes" in domain_analysis.detected_operations
            has_epics_reads = "epics_reads" in domain_analysis.detected_operations
            
            analysis_result = AnalysisResult(
                passed=passed,
                issues=all_issues,
                recommendations=policy_decision.recommendations,
                severity=severity,
                has_epics_writes=has_epics_writes,
                has_epics_reads=has_epics_reads,
                recommended_execution_mode=policy_decision.execution_mode,
                needs_approval=policy_decision.needs_approval,
                approval_reasoning=policy_decision.approval_reasoning,
                execution_mode_config=execution_mode_config
            )
            
            if passed:
                logger.info(f"Static analysis passed: {len(all_issues)} non-critical issues, execution mode: {policy_decision.execution_mode.value}")
            else:
                logger.warning(f"Static analysis found critical issues: {len(critical_issues)} critical, {len(all_issues)} total")
            
            return analysis_result
            
        except CodeSyntaxError:
            # Re-raise syntax errors
            raise
        except Exception as e:
            # Convert unexpected errors to configuration errors
            raise ContainerConfigurationError(
                f"Static analysis failed: {str(e)}",
                technical_details={"original_error": str(e)}
            )
    
    def _check_syntax(self, code: str) -> List[str]:
        """Check Python syntax validity"""
        issues = []
        try:
            ast.parse(code)
            logger.debug("Syntax validation passed")
        except SyntaxError as e:
            issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
            logger.warning(f"Syntax error found: {e.msg}")
        except Exception as e:
            issues.append(f"Syntax parsing error: {str(e)}")
            logger.warning(f"Syntax parsing failed: {str(e)}")
        
        return issues
    
    def _check_security(self, code: str) -> List[str]:
        """Basic security checks for dangerous operations"""
        issues = []
        
        # Check for potentially dangerous operations
        dangerous_patterns = [
            ("exec(", "Use of exec() function"),
            ("eval(", "Use of eval() function"),
            ("__import__", "Dynamic import usage"),
            ("open(", "File operations - ensure proper handling"),
            ("subprocess", "Subprocess usage - potential security risk"),
            ("os.system", "System command execution"),
        ]
        
        for pattern, warning in dangerous_patterns:
            if pattern in code:
                if pattern in ["open(", "subprocess"]:
                    # These might be legitimate, just warn
                    issues.append(f"Warning: {warning}")
                else:
                    # These are more concerning
                    issues.append(f"Security risk: {warning}")
        
        return issues
    
    def _check_imports(self, code: str) -> List[str]:
        """Check for prohibited imports - returns list of issues"""
        issues = []
        
        prohibited_imports = ["subprocess", "os.system", "eval", "exec"]
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in prohibited_imports:
                            issues.append(f"Prohibited import detected: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module in prohibited_imports:
                        issues.append(f"Prohibited import detected: {node.module}")
                        
        except SyntaxError:
            # Syntax errors are handled elsewhere
            pass
            
        return issues
    
    def _determine_security_risk_level(self, security_issues: List[str]) -> str:
        """Determine security risk level based on security issues"""
        if not security_issues:
            return "low"
        
        high_risk_keywords = ["subprocess", "os.system", "eval", "exec", "shell"]
        for issue in security_issues:
            if any(keyword in issue.lower() for keyword in high_risk_keywords):
                return "high"
        
        return "medium"
    
    def _get_prohibited_imports(self, import_issues: List[str]) -> List[str]:
        """Extract list of prohibited imports from import issues"""
        prohibited = []
        for issue in import_issues:
            if "Prohibited import detected:" in issue:
                import_name = issue.split(": ", 1)[1]
                prohibited.append(import_name)
        return prohibited


def create_analyzer_node():
    """Create the static analysis node function."""
    
    async def analyzer_node(state: PythonExecutionState) -> Dict[str, Any]:
        """Perform static analysis and package approval data to avoid double execution."""
        
        # Define streaming helper here for step awareness
        streamer = get_streamer("python_executor", "analyzer", state)
        streamer.status("Analyzing Python code...")
        
        # Check if we have code to analyze
        generated_code = state.get("generated_code")
        if not generated_code:
            error_message = "No code available for static analysis"
            error_chain = state.get("error_chain", []) + [error_message]
            
            return {
                "analysis_failed": True,
                "error_chain": error_chain,
                "current_stage": "generation"
            }
        
        # Use existing analyzer logic - access request data via state.request
        # Get config from LangGraph configurable
        configurable = get_full_configuration()
        
        analyzer = StaticCodeAnalyzer(configurable)
        
        try:
            # Perform analysis using existing logic
            analysis_result = await analyzer.analyze_code(
                state["generated_code"],  # From service state
                state["request"]  # Original request context as dictionary
            )
            
            if not analysis_result.passed:
                # Analysis failed - need to regenerate
                error_message = f"Static analysis failed: {', '.join(analysis_result.issues)}"
                error_chain = state.get("error_chain", []) + [error_message]
                
                # Create attempt notebook for debugging static analysis failures
                await _create_analysis_failure_attempt_notebook(
                    state, configurable, generated_code, error_message, analysis_result.issues
                )
                
                return {
                    "analysis_result": analysis_result,
                    "analysis_failed": True,
                    "error_chain": error_chain,
                    "current_stage": "generation"
                }
            
            # Analysis passed - check if approval needed
            requires_approval = analysis_result.needs_approval
            
            status_msg = "Code requires approval" if requires_approval else "Code analysis passed"
            streamer.status(status_msg)
            
            if requires_approval:
                # CRITICAL: Create approval interrupt data here to avoid double execution
                # Use the new LangGraph-native approval system
                approval_interrupt_data = create_code_approval_interrupt(
                    code=state["generated_code"],
                    analysis_details=analysis_result.__dict__ if analysis_result else {},
                    execution_mode=analysis_result.recommended_execution_mode.value if hasattr(analysis_result.recommended_execution_mode, 'value') else str(analysis_result.recommended_execution_mode),
                    safety_concerns=analysis_result.issues + analysis_result.recommendations,
                    notebook_path=None,  # Will be set during execution setup
                    notebook_link=None,  # Will be set during execution setup
                    execution_request=state["request"],
                    expected_results=state["request"].expected_results,
                    execution_folder_path=None,  # Will be set during execution setup
                    step_objective=state["request"].task_objective
                )
                
                return {
                    "analysis_result": analysis_result,
                    "analysis_failed": False,
                    "requires_approval": True,
                    "approval_interrupt_data": approval_interrupt_data,  # Use new LangGraph-native system
                    "current_stage": "approval"
                }
            else:
                return {
                    "analysis_result": analysis_result,
                    "analysis_failed": False,
                    "requires_approval": False,
                    "approval_interrupt_data": None,
                    "current_stage": "execution"
                }
            
        except (CodeSyntaxError, CodeGenerationError) as e:
            # Expected code quality issues - treat as analysis failure, not system error
            logger.warning(f"⚠️  Code analysis failed: {e}")
            error_message = f"Code quality issue: {str(e)}"
            error_chain = state.get("error_chain", []) + [error_message]
            
            # Create attempt notebook for debugging syntax errors
            await _create_syntax_error_attempt_notebook(
                state, configurable, generated_code, str(e)
            )
            
            return {
                "analysis_failed": True,  # Retry with regeneration
                "error_chain": error_chain,
                "failure_reason": str(e),
                "current_stage": "generation"
            }
            
        except Exception as e:
            # Truly unexpected analyzer crashes are critical system errors
            # This should only happen due to framework bugs, not code quality issues
            logger.error(f"❌ Critical system error: Analyzer crashed unexpectedly: {e}")
            logger.error(f"This indicates a framework bug, not a code quality issue")
            
            return {
                "analysis_failed": False,  # Don't retry - this is a system bug
                "is_failed": True,         # Mark as permanently failed
                "failure_reason": f"Critical analyzer error: {str(e)}",
                "error_chain": state.get("error_chain", []) + [f"System error: {str(e)}"],
                "current_stage": "failed"
            }
    
    return analyzer_node


async def _create_analysis_failure_attempt_notebook(
    state: PythonExecutionState,
    configurable: Dict[str, Any], 
    code: str,
    error_message: str,
    issues: List[str]
) -> None:
    """Create attempt notebook for static analysis failures."""
    try:
        # Set up file and notebook managers
        file_manager = FileManager(configurable)
        notebook_manager = NotebookManager(configurable)
        
        # Ensure execution folder exists
        execution_folder = state.get("execution_folder")
        if not execution_folder:
            execution_folder = file_manager.create_execution_folder(
                state["request"].execution_folder_name
            )
            state["execution_folder"] = execution_folder
        
        # Create detailed error context for the notebook
        error_context = f"""**Static Analysis Failed**

**Error:** {error_message}

**Issues Found:**
{chr(10).join(f'- {issue}' for issue in issues)}

**Debug Information:**
- Stage: Static analysis
- Generated Code Length: {len(code)} characters
- Analysis Result: Failed validation

**Note:** This notebook contains the code that failed static analysis. Review the issues above and regenerate the code accordingly."""

        # Create attempt notebook
        notebook_path = notebook_manager.create_attempt_notebook(
            context=execution_folder,
            code=code,
            stage="static_analysis_failed",
            error_context=error_context,
            silent=True  # Don't log creation as we'll log it below
        )
        
        logger.info(f"📝 Created attempt notebook for static analysis failure: {notebook_path}")
        
    except Exception as e:
        logger.warning(f"Failed to create attempt notebook for static analysis failure: {e}")
        # Don't fail the entire analysis just because notebook creation failed


async def _create_syntax_error_attempt_notebook(
    state: PythonExecutionState,
    configurable: Dict[str, Any],
    code: str, 
    error_message: str
) -> None:
    """Create attempt notebook for syntax errors."""
    try:
        # Set up file and notebook managers
        file_manager = FileManager(configurable)
        notebook_manager = NotebookManager(configurable)
        
        # Ensure execution folder exists
        execution_folder = state.get("execution_folder")
        if not execution_folder:
            execution_folder = file_manager.create_execution_folder(
                state["request"].execution_folder_name
            )
            state["execution_folder"] = execution_folder
        
        # Create detailed error context for the notebook
        error_context = f"""**Syntax Error Detected**

**Error:** {error_message}

**Debug Information:**
- Stage: Code syntax validation
- Generated Code Length: {len(code)} characters
- Error Type: Syntax validation failed

**Note:** This notebook contains the code that has syntax errors. The code below will not execute properly and needs to be corrected."""

        # Create attempt notebook
        notebook_path = notebook_manager.create_attempt_notebook(
            context=execution_folder,
            code=code,
            stage="syntax_error",
            error_context=error_context,
            silent=True  # Don't log creation as we'll log it below
        )
        
        logger.info(f"📝 Created attempt notebook for syntax error: {notebook_path}")
        
    except Exception as e:
        logger.warning(f"Failed to create attempt notebook for syntax error: {e}")
        # Don't fail the entire analysis just because notebook creation failed
 