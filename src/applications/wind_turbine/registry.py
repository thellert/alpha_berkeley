"""Wind Turbine Application Registry Configuration.

This module defines the component registry for the Wind Turbine Monitoring application.
All wind turbine-specific capabilities, context classes, and data sources are declared here.
"""

from framework.registry import (
    CapabilityRegistration, 
    ContextClassRegistration, 
    DataSourceRegistration,
    RegistryConfig,
    RegistryConfigProvider
)

class WindTurbineRegistryProvider(RegistryConfigProvider):
    """Registry provider for Wind Turbine application."""
    
    def get_registry_config(self) -> RegistryConfig:
        """Get wind turbine application registry configuration.
        
        Returns:
            RegistryConfig: Registry configuration for wind turbine monitoring application
        """
        return RegistryConfig(
        core_nodes=[],  # Applications don't define core nodes
        
        # Exclude framework components that conflict with specialized implementations
        framework_exclusions={
            "capabilities": ["python"]  # Use specialized turbine_analysis instead
        },
        
        capabilities=[
            CapabilityRegistration(
                name="weather_data_retrieval",
                module_path="applications.wind_turbine.capabilities.weather_data_retrieval",
                class_name="WeatherDataRetrievalCapability", 
                description="Retrieve weather data for wind analysis",
                provides=["WEATHER_DATA"],
                requires=["TIME_RANGE"]
            ),
            CapabilityRegistration(
                name="knowledge_retrieval",
                module_path="applications.wind_turbine.capabilities.knowledge_retrieval",
                class_name="KnowledgeRetrievalCapability",
                description="Retrieve technical standards and performance benchmarks from knowledge base",
                provides=["TURBINE_KNOWLEDGE"],
                requires=[]
            ),
            CapabilityRegistration(
                name="turbine_data_archiver",
                module_path="applications.wind_turbine.capabilities.turbine_data_archiver",
                class_name="TurbineDataArchiverCapability",
                description="Retrieve historical turbine performance data",
                provides=["TURBINE_DATA"],
                requires=["TIME_RANGE"]
            ),
            CapabilityRegistration(
                name="turbine_analysis",
                module_path="applications.wind_turbine.capabilities.turbine_analysis",
                class_name="TurbineAnalysisCapability",
                description="Analyze turbine performance against industry benchmarks",
                provides=["ANALYSIS_RESULTS"],
                requires=["TURBINE_DATA", "WEATHER_DATA", "TURBINE_KNOWLEDGE"]
            )
        ],
        
        context_classes=[
            ContextClassRegistration(
                context_type="TURBINE_DATA",
                module_path="applications.wind_turbine.context_classes", 
                class_name="TurbineDataContext"
            ),
            ContextClassRegistration(
                context_type="WEATHER_DATA",
                module_path="applications.wind_turbine.context_classes",
                class_name="WeatherDataContext"
            ),
            ContextClassRegistration(
                context_type="ANALYSIS_RESULTS",
                module_path="applications.wind_turbine.context_classes",
                class_name="AnalysisResultsContext"
            ),
            ContextClassRegistration(
                context_type="TURBINE_KNOWLEDGE",
                module_path="applications.wind_turbine.context_classes",
                class_name="TurbineKnowledgeContext"
            ),
        ],
        
        data_sources=[
            DataSourceRegistration(
                name="wind_farm_knowledge",
                module_path="applications.wind_turbine.data_sources.knowledge_provider",
                class_name="WindFarmKnowledgeProvider",
                description="Mock RAG-style knowledge base for wind farm domain expertise"
            )
        ],
        
        framework_prompt_providers=[
            # If wind turbine needs custom framework prompts
        ],
        
        initialization_order=[
            "context_classes",
            "data_sources", 
            "capabilities",
            "framework_prompt_providers"
        ]
        ) 
