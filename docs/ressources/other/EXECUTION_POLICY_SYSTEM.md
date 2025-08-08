# Execution Policy Analyzer System

## Overview

The Execution Policy Analyzer system provides a clean, configurable approach to both **domain analysis** and **execution policy decisions** for Python code execution. It separates **hard-coded safety checks** (syntax, security) from **configurable business logic** (domain patterns, execution mode, approval requirements).

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Static Code Analyzer                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Basic Analysis (Hard-coded Framework Safety)               │
│     • Syntax validation                                        │
│     • Security analysis                                        │
│     • Import validation                                        │
│     • Structure validation                                     │
├─────────────────────────────────────────────────────────────────┤
│  2. Domain Analysis (Registry-Based)                           │
│     • Registry-based domain analyzers                         │
│     • Priority-based selection                                │
│     • Fallback to framework EPICS defaults                    │
├─────────────────────────────────────────────────────────────────┤
│  3. Execution Policy Decision (Registry-Based)                 │
│     • Registry-based policy analyzers                         │
│     • Priority-based selection                                │
│     • Fallback to framework defaults                          │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Basic Analysis** → `BasicAnalysisResult`
2. **Domain Analysis** → `DomainAnalysisResult` (Registry-Based)
3. **Policy Analysis** → `ExecutionPolicyDecision` (Registry-Based)
4. **Legacy Conversion** → `AnalysisResult` (backward compatibility)

## Key Benefits

### ✅ **Complete Configurability**
- Both domain analysis AND policy decisions are configurable
- Applications can customize code pattern detection
- Applications can customize execution decisions
- Framework provides sensible defaults for both

### ✅ **Simple & Focused**
- Hard-coded safety checks remain in framework
- Only domain analysis and decision logic are configurable
- Clear separation of concerns

### ✅ **Type-Safe Integration**
- Well-defined data classes for all interfaces
- Structured input/output for both analyzer types
- Compile-time validation of custom implementations

### ✅ **Registry-Based Flexibility**
- Applications register custom domain analyzers
- Applications register custom policy analyzers
- Priority-based selection (lower numbers = higher priority)
- Automatic fallback to framework defaults

### ✅ **Backward Compatibility**
- Existing code continues to work unchanged
- Legacy `AnalysisResult` format preserved
- Gradual migration path available

## Usage Examples

### Framework Default Behavior
```python
# No custom configuration needed
# Framework automatically uses:
# - DefaultFrameworkDomainAnalyzer (EPICS detection)
# - DefaultFrameworkPolicyAnalyzer (EPICS-based decisions)
```

### Application Customization

#### 1. Custom Domain Analyzer
```python
# src/applications/als_expert/domain_analysis.py
class ALSExpertDomainAnalyzer(DomainAnalyzer):
    def get_priority(self) -> int:
        return 10  # Higher priority than default
    
    async def analyze_domain(self, basic_analysis):
        # Detect ALS-specific patterns
        detected_operations = []
        if "beam_size" in basic_analysis.code:
            detected_operations.append("beam_diagnostics")
        if "orbit_correction" in basic_analysis.code:
            detected_operations.append("orbit_control")
        
        return DomainAnalysisResult(
            detected_operations=detected_operations,
            risk_categories=["accelerator_physics"],
            domain_data={"als_specific": True}
        )
```

#### 2. Custom Policy Analyzer  
```python
# src/applications/als_expert/execution_policy.py
class ALSExpertExecutionPolicyAnalyzer(ExecutionPolicyAnalyzer):
    def get_priority(self) -> int:
        return 10  # Higher priority than default
    
    async def analyze_policy(self, basic_analysis, domain_analysis):
        # Custom ALS-specific logic based on domain analysis
        if "beam_diagnostics" in domain_analysis.detected_operations:
            return ExecutionPolicyDecision(
                execution_mode="read_only",
                needs_approval=False,
                approval_reasoning="Beam diagnostics are safe for automatic execution"
            )
        
        # Standard logic for other cases...
```

#### 3. Register Both in Application
```python
# src/applications/als_expert/registry.py
domain_analyzers=[
    DomainAnalyzerRegistration(
        name="als_expert_domain",
        module_path="applications.als_expert.domain_analysis",
        class_name="ALSExpertDomainAnalyzer",
        description="ALS Expert domain pattern detection",
        priority=10
    )
],

execution_policy_analyzers=[
    ExecutionPolicyAnalyzerRegistration(
        name="als_expert_policy",
        module_path="applications.als_expert.execution_policy",
        class_name="ALSExpertExecutionPolicyAnalyzer",
        description="ALS Expert execution policies",
        priority=10
    )
]
```

## Implementation Details

### BasicAnalysisResult
```python
@dataclass
class BasicAnalysisResult:
    syntax_valid: bool
    syntax_issues: List[str]
    security_issues: List[str]
    security_risk_level: str  # "low", "medium", "high"
    import_issues: List[str]
    prohibited_imports: List[str]
    has_result_structure: bool
    code: str
    code_length: int
    user_context: Optional[Dict[str, Any]]
    execution_context: Optional[Dict[str, Any]]
```

### DomainAnalysisResult
```python
@dataclass 
class DomainAnalysisResult:
    detected_operations: List[str]  # e.g., ["epics_writes", "beam_diagnostics"]
    risk_categories: List[str]      # e.g., ["accelerator_control", "beam_safety"]
    domain_data: Dict[str, Any]     # Extensible for custom data
```

### ExecutionPolicyDecision
```python
class ExecutionPolicyDecision(NamedTuple):
    execution_mode: str           # "read_only", "write_access", "simulation"
    needs_approval: bool
    approval_reasoning: str
    additional_issues: List[str]
    recommendations: List[str]
    analysis_passed: bool
    additional_context: Optional[Dict[str, Any]]
```

## Configuration Examples

### Simple Application Override
```yaml
# config.yml - No changes needed!
# Applications register analyzers through registry system
```

### Advanced Custom Analysis Pipeline
```python
class CustomDomainAnalyzer(DomainAnalyzer):
    async def analyze_domain(self, basic_analysis):
        # Custom domain pattern detection:
        # - Machine learning model patterns
        # - Database query patterns  
        # - Scientific computation patterns
        # - Domain-specific libraries
        pass

class CustomPolicyAnalyzer(ExecutionPolicyAnalyzer):
    async def analyze_policy(self, basic_analysis, domain_analysis):
        # Custom policy logic based on:
        # - Custom domain patterns from domain_analysis
        # - Time of day
        # - User permissions  
        # - Equipment status
        # - Code complexity
        pass
```

## Migration Guide

### For Framework Users
**No changes required** - existing behavior preserved through default analyzers

### For Application Developers

#### Phase 1: Keep Current Behavior
- No immediate changes needed
- Framework handles everything automatically using defaults

#### Phase 2: Add Custom Domain Analysis
- Implement `DomainAnalyzer` interface for custom pattern detection
- Register in application's registry configuration
- Test alongside framework defaults

#### Phase 3: Add Custom Policy Logic
- Implement `ExecutionPolicyAnalyzer` interface
- Use results from custom domain analysis
- Register in application's registry configuration

#### Phase 4: Advanced Integration
- Combine custom domain and policy analyzers
- Integrate with external systems
- Implement complex approval workflows

## Conclusion

The enhanced Execution Policy Analyzer system provides the perfect balance of:
- **Complete Flexibility** through registry-based domain AND policy analysis
- **Safety** through hard-coded framework checks
- **Simplicity** through focused, single-responsibility interfaces  
- **Compatibility** through legacy format preservation

Applications can now customize both **what patterns they detect** and **how they respond to those patterns** without compromising safety or requiring framework modifications. 