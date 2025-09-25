"""ALS Assistant Application Registry Configuration.

This module defines the component registry for the Advanced Light Source (ALS) Expert application.
All ALS-specific capabilities, context classes, and data sources are declared here.
"""

from framework.registry import (
    CapabilityRegistration,
    ContextClassRegistration, 
    DataSourceRegistration,
    FrameworkPromptProviderRegistration,
    RegistryConfig,
    RegistryConfigProvider
)

class ALSExpertRegistryProvider(RegistryConfigProvider):
    """Registry provider for ALS Assistant application."""
    
    def get_registry_config(self) -> RegistryConfig:
        """Get ALS Assistant v2 application registry configuration.
        
        Returns:
            RegistryConfig: Registry configuration for ALS Assistant v2 application
        """
        return RegistryConfig(
        
        # Exclude framework components that conflict with specialized implementations  
        framework_exclusions={
            "capabilities": ["python"]  # Use specialized data_analysis instead
        },
        
        capabilities=[
            CapabilityRegistration(
                name="pv_address_finding",
                module_path="applications.als_assistant.capabilities.pv_address_finding",
                class_name="PVAddressFindingCapability",
                description="Find Process Variable addresses based on descriptions",
                provides=["PV_ADDRESSES"],
                requires=[]
            ),

            CapabilityRegistration(
                name="pv_value_retrieval",
                module_path="applications.als_assistant.capabilities.pv_value_retrieval",
                class_name="PVValueRetrievalCapability",
                description="Retrieve current values from Process Variables",
                provides=["PV_VALUES"],
                requires=["PV_ADDRESSES"]
            ),
            CapabilityRegistration(
                name="get_archiver_data",
                module_path="applications.als_assistant.capabilities.get_archiver_data",
                class_name="ArchiverDataCapability",
                description="Retrieve historical data from EPICS archiver",
                provides=["ARCHIVER_DATA"],
                requires=["PV_ADDRESSES", "TIME_RANGE"]
            ),

            CapabilityRegistration(
                name="data_analysis",
                module_path="applications.als_assistant.capabilities.data_analysis",
                class_name="DataAnalysisCapability",
                description="Perform statistical and numerical analysis on data",
                provides=["ANALYSIS_RESULTS"],
                requires=[]
            ),

            CapabilityRegistration(
                name="data_visualization",
                module_path="applications.als_assistant.capabilities.data_visualization",
                class_name="DataVisualizationCapability",
                description="Create plots and visualizations of data",
                provides=["VISUALIZATION_RESULTS"],
                requires=[]
            ),

            CapabilityRegistration(
                name="machine_operations",
                module_path="applications.als_assistant.capabilities.machine_operations",
                class_name="MachineOperationsCapability",
                description="Monitor and control accelerator operations",
                provides=["OPERATION_RESULTS"],
                requires=[]
            ),

            CapabilityRegistration(
                name="live_monitoring",
                module_path="applications.als_assistant.capabilities.live_monitoring",
                class_name="LiveMonitoringCapability",
                description="Launch Phoebus Data Browser for real-time PV monitoring",
                provides=[],
                requires=["PV_ADDRESSES"]
            )
        ],

        context_classes=[
            ContextClassRegistration(
                context_type="PV_ADDRESSES",
                module_path="applications.als_assistant.context_classes",
                class_name="PVAddresses"
            ),

            ContextClassRegistration(
                context_type="PV_VALUES",
                module_path="applications.als_assistant.context_classes",
                class_name="PVValues"
            ),
            ContextClassRegistration(
                context_type="ARCHIVER_DATA",
                module_path="applications.als_assistant.context_classes",
                class_name="ArchiverDataContext"
            ),
            ContextClassRegistration(
                context_type="ANALYSIS_RESULTS",
                module_path="applications.als_assistant.context_classes",
                class_name="AnalysisResultsContext"
            ),
            ContextClassRegistration(
                context_type="VISUALIZATION_RESULTS",
                module_path="applications.als_assistant.context_classes",
                class_name="VisualizationResultsContext"
            ),
            ContextClassRegistration(
                context_type="OPERATION_RESULTS",
                module_path="applications.als_assistant.context_classes",
                class_name="OperationResultsContext"
            ),
            ContextClassRegistration(
                context_type="LAUNCHER_RESULTS",
                module_path="applications.als_assistant.context_classes",
                class_name="LauncherResultsContext"
            )
        ],
        
        # ============================================================
        # Optional fields - only specify if different from defaults
        # ============================================================
        
        data_sources=[
            DataSourceRegistration(
                name="experiment_database",
                module_path="applications.als_assistant.database.als_knowledge.experiment_database",
                class_name="ExperimentDatabaseProvider",
                description="Provides access to experiment database",
                health_check_required=True
            )
        ],
        
        framework_prompt_providers=[
            FrameworkPromptProviderRegistration(
                application_name="als_assistant",
                module_path="applications.als_assistant.framework_prompts",
                description="ALS-specific framework prompt provider for all infrastructure prompts",
                prompt_builders={
                    "orchestrator": "ALSOrchestratorPromptBuilder",
                    "task_extraction": "ALSTaskExtractionPromptBuilder", 
                    "response_generation": "ALSResponseGenerationPromptBuilder",
                    "classification": "ALSClassificationPromptBuilder",
                    "error_analysis": "ALSErrorAnalysisPromptBuilder",
                    "clarification": "ALSClarificationPromptBuilder",
                    "memory_extraction": "ALSMemoryExtractionPromptBuilder"
                }
            )
        ]
        )