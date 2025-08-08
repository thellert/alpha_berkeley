"""
Data Source Manager

Unified data source management system that replaces both the registry and integration service
with a cleaner approach supporting core and application-specific data sources.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time

from .providers import DataSourceContext, DataSourceProvider
from .request import DataSourceRequest

logger = logging.getLogger(__name__)

@dataclass
class DataRetrievalResult:
    """Result of data retrieval from multiple sources."""
    context_data: Dict[str, DataSourceContext] = field(default_factory=dict)
    successful_sources: List[str] = field(default_factory=list)
    failed_sources: List[str] = field(default_factory=list)
    total_sources_attempted: int = 0
    retrieval_time_ms: Optional[float] = None
    
    @property
    def has_data(self) -> bool:
        """Check if any data was successfully retrieved."""
        return bool(self.context_data)
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of data retrieval."""
        if self.total_sources_attempted == 0:
            return 0.0
        return len(self.successful_sources) / self.total_sources_attempted
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the retrieval results."""
        return {
            'sources_attempted': self.total_sources_attempted,
            'sources_successful': len(self.successful_sources),
            'sources_failed': len(self.failed_sources),
            'success_rate': self.success_rate,
            'context_types_retrieved': list(set(ctx.context_type for ctx in self.context_data.values())),
            'retrieval_time_ms': self.retrieval_time_ms
        }

class DataSourceManager:
    """
    Unified data source management system.
    
    Replaces both DataSourceRegistry and DataSourceIntegrationService with a
    cleaner architecture that supports core and application-specific data sources.
    """
    
    def __init__(self):
        self._providers: Dict[str, DataSourceProvider] = {}
        self._initialized = False
    
    def register_provider(self, provider: DataSourceProvider) -> None:
        """
        Register a data source provider.
        
        Providers are queried in registration order (framework providers first,
        then application providers).
        """
        self._providers[provider.name] = provider
        logger.info(f"Registered data source: {provider.name}")
    

    def get_responding_providers(self, request: DataSourceRequest) -> List[DataSourceProvider]:
        """
        Get all providers that should respond to the current request in registration order.
        
        Args:
            request: Data source request with requester information
            
        Returns:
            List of providers that should respond in registration order (framework first, then applications)
        """
        return [p for p in self._providers.values() if p.should_respond(request)]
    
    async def retrieve_all_context(self, request: DataSourceRequest, 
                                  timeout_seconds: float = 30.0) -> DataRetrievalResult:
        """
        Retrieve context from all responding data sources.
        
        Args:
            request: Data source request with requester information
            timeout_seconds: Maximum time to wait for all data sources
            
        Returns:
            DataRetrievalResult containing all successfully retrieved data
        """
        start_time = time.time()
        
        # Get responding providers in registration order
        providers = self.get_responding_providers(request)
        
        if not providers:
            logger.info("No data sources available for current context")
            return DataRetrievalResult(total_sources_attempted=0)
        
        logger.info(f"Retrieving context from {len(providers)} data sources")
        
        # Create retrieval tasks for all providers
        tasks = []
        for provider in providers:
            task = asyncio.create_task(
                self._retrieve_from_provider(provider, request),
                name=f"retrieve_{provider.name}"
            )
            tasks.append((provider.name, task))
        
        # Wait for all tasks with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.warning(f"Data source retrieval timed out after {timeout_seconds}s")
            # Cancel remaining tasks
            for _, task in tasks:
                if not task.done():
                    task.cancel()
            results = [None] * len(tasks)  # Treat all as failed
        
        # Process results
        context_data = {}
        successful_sources = []
        failed_sources = []
        
        for (provider_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.warning(f"Data retrieval failed for {provider_name}: {result}")
                failed_sources.append(provider_name)
            elif result is not None:
                context_data[provider_name] = result
                successful_sources.append(provider_name)
                logger.debug(f"Successfully retrieved data from {provider_name}")
            else:
                failed_sources.append(provider_name)
        
        retrieval_time_ms = (time.time() - start_time) * 1000
        
        retrieval_result = DataRetrievalResult(
            context_data=context_data,
            successful_sources=successful_sources,
            failed_sources=failed_sources,
            total_sources_attempted=len(providers),
            retrieval_time_ms=retrieval_time_ms
        )
        
        logger.info(f"Data retrieval complete: {retrieval_result.get_summary()}")
        return retrieval_result
    
    def get_provider(self, provider_name: str) -> Optional[DataSourceProvider]:
        """
        Get a specific data source provider by name.
        
        Args:
            provider_name: Name of the data source provider to retrieve
            
        Returns:
            DataSourceProvider if found, None otherwise
        """
        return self._providers.get(provider_name)
    
    async def retrieve_from_provider(self, provider_name: str, request: DataSourceRequest) -> Optional[DataSourceContext]:
        """
        Retrieve data from a specific provider by name.
        
        Args:
            provider_name: Name of the data source provider
            request: Data source request
            
        Returns:
            DataSourceContext if successful, None if provider not found or retrieval failed
        """
        provider = self.get_provider(provider_name)
        if not provider:
            logger.warning(f"Data source provider '{provider_name}' not found")
            return None
        
        if not provider.should_respond(request):
            logger.debug(f"Provider '{provider_name}' chose not to respond to request")
            return None
            
        return await self._retrieve_from_provider(provider, request)
    
    async def _retrieve_from_provider(self, provider: DataSourceProvider, 
                                     request: DataSourceRequest) -> Optional[DataSourceContext]:
        """
        Retrieve data from a single provider with error handling.
        
        Args:
            provider: The data source provider to retrieve from
            request: Data source request
            
        Returns:
            DataSourceContext if successful, None if failed
        """
        try:
            logger.debug(f"Retrieving data from {provider.name}")
            return await provider.retrieve_data(request)
        except Exception as e:
            logger.warning(f"Failed to retrieve data from {provider.name}: {e}")
            return None
    




# Global manager instance
_data_source_manager: Optional[DataSourceManager] = None

def get_data_source_manager() -> DataSourceManager:
    """
    Get the global data source manager instance.
    
    Loads all data sources from the registry system. Providers are queried
    in registration order (framework first, then applications).
    """
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
        
        # Load all data sources from registry
        try:
            from framework.registry import get_registry
            registry = get_registry()
            
            # Get all data sources from registry
            registry_data_sources = registry.get_all_data_sources()
            
            for provider in registry_data_sources:
                _data_source_manager.register_provider(provider)
                
            logger.info(f"Loaded {len(registry_data_sources)} data sources from registry")
            
        except Exception as e:
            logger.warning(f"Failed to load data sources from registry: {e}")
    
    return _data_source_manager 