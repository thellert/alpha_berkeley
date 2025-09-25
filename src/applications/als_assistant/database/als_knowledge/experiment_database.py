"""
ALS Assistant Experiment Database Provider

Data source for ALS experimental beam line and operational data.
"""

import os
import logging
from typing import Optional, Any, Dict, List

from framework.data_management.providers import DataSourceProvider, DataSourceContext
from framework.data_management.request import DataSourceRequest

logger = logging.getLogger(__name__)

class SimpleDatabase:
    """Mock database for demonstration - replace with real database connection."""
    
    def __init__(self):
        self.data = {
            "equipment_status": [
                # Current equipment status that could inform troubleshooting
                {"device": "SR:DCCT", "status": "operational", "last_calibration": "2025-01-15"},
            ],
            "baseline_data": [
                # Baseline measurements for comparative analysis
                {"parameter": "SR_beam_lifetime", "baseline_value": "12.2±0.5 hours", "date_established": "2025-01-10", "conditions": "normal operations"},
                {"parameter": "SR_beam_current", "baseline_value": "500±2 mA", "date_established": "2025-01-10", "measurement_device": "SR:DCCT"},
            ]
        }
    
    def query(self, table: str, filters: Dict = None) -> list:
        """Simple query method."""
        if table not in self.data:
            return []
        
        results = self.data[table]
        
        if filters:
            for key, value in filters.items():
                if isinstance(value, str):
                    results = [item for item in results if str(item.get(key, "")).lower() == value.lower()]
                else:
                    results = [item for item in results if item.get(key) == value]
        
        return results

class ExperimentDatabaseProvider(DataSourceProvider):
    """
    Application-specific data source provider for experimental data and maintenance logs.
    
    This demonstrates how to implement domain-specific data sources that integrate
    with the unified data source management system.
    """
    
    def __init__(self, db_connection=None):
        """Initialize with database connection."""
        self.db = db_connection or SimpleDatabase()
    
    @property
    def name(self) -> str:
        return "experiment_database"
    
    @property
    def context_type(self) -> str:
        return "EXPERIMENT_DATABASE_CONTEXT"
    
    @property
    def description(self) -> str:
        return "ALS experimental data and maintenance logs database"
    

    
    async def retrieve_data(self, request: DataSourceRequest) -> Optional[DataSourceContext]:
        """Retrieve relevant database records.
        
        Args:
            request: Data source request
            
        Returns:
            DataSourceContext with database records, or None if unavailable
        """
        try:
            # Get all database records
            equipment_status = self.db.query("equipment_status")
            baseline_data = self.db.query("baseline_data")
            
            if not (equipment_status or baseline_data):
                logger.debug("No database records found")
                return None
            
            # Create comprehensive data structure
            db_data = {
                "equipment_status": equipment_status,  # All current equipment status
                "baseline_data": baseline_data,  # All baseline measurements
            }
            
            logger.info(f"Retrieved {len(equipment_status)} equipment status entries, {len(baseline_data)} baselines")
            
            return DataSourceContext(
                source_name=self.name,
                context_type=self.context_type,
                data=db_data,
                metadata={
                    "equipment_count": len(equipment_status),
                    "baseline_count": len(baseline_data),
                    "source_description": "ALS experimental and maintenance database",
                    "is_application_provider": True
                },
                provider=self
            )
            
        except Exception as e:
            logger.warning(f"Database query failed: {e}")
            return None
    
    def should_respond(self, request: DataSourceRequest) -> bool:
        """Check if database is accessible.
        
        Returns:
            True if database connection is available
        """
        try:
            # Simple connectivity check
            return self.db is not None
        except:
            return False
    
    def format_for_prompt(self, context: DataSourceContext) -> str:
        """Custom formatting for database data with summary statistics."""
        if not context or not context.data:
            return ""
        
        db_data = context.data
        sections = []
        
        # Custom header with counts from metadata
        metadata = context.metadata
        equipment_count = metadata.get('equipment_count', 0)
        baseline_count = metadata.get('baseline_count', 0)
        sections.append(f"**🔬 ALS Equipment Database** ({equipment_count} devices, {baseline_count} baselines):")
        
        # Format critical equipment status
        if 'equipment_status' in db_data and db_data['equipment_status']:
            sections.append("  **📊 Critical Equipment Status:**")
            for eq in db_data['equipment_status']:
                status_emoji = "✅" if eq['status'] == 'operational' else "⚠️"
                extra_info = []
                if eq.get('current_limit'): extra_info.append(f"limit: {eq['current_limit']}")
                if eq.get('noise_level'): extra_info.append(f"noise: {eq['noise_level']}")
                if eq.get('cycle_schedule'): extra_info.append(f"schedule: {eq['cycle_schedule']}")
                extra = f" ({', '.join(extra_info)})" if extra_info else ""
                sections.append(f"    {status_emoji} {eq['device']}: {eq['status']}{extra}")
        
        # Format baseline data for comparisons
        if 'baseline_data' in db_data and db_data['baseline_data']:
            sections.append("  **📏 Baseline References:**")
            for baseline in db_data['baseline_data']:
                date_info = f" (est. {baseline.get('date_established', '')})" if baseline.get('date_established') else ""
                sections.append(f"    • {baseline['parameter']}: {baseline['baseline_value']}{date_info}")
        
        return "\n".join(sections)
    
    async def health_check(self) -> bool:
        """Verify database connectivity."""
        try:
            # Test basic query
            result = self.db.query("equipment_status")
            return isinstance(result, list)
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False

# Note: Registered in registry/config.py
experiment_db_provider = ExperimentDatabaseProvider() 