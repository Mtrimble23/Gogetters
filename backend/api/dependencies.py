"""
Dependency injection for services
"""

from ..services import FinancialAnalysisService, DataIntegrationService
from ..repositories import FinancialDataRepository, AerospikeRepository


# Global service instances
_data_service: DataIntegrationService = None
_analysis_service: FinancialAnalysisService = None


def get_data_service() -> DataIntegrationService:
    """Get or create data integration service instance"""
    global _data_service
    if _data_service is None:
        repository = FinancialDataRepository()
        _data_service = DataIntegrationService(repository)
    return _data_service


def get_analysis_service() -> FinancialAnalysisService:
    """Get or create financial analysis service instance"""
    global _analysis_service
    if _analysis_service is None:
        aerospike_repo = AerospikeRepository()
        _analysis_service = FinancialAnalysisService(aerospike_repo)
    return _analysis_service


def get_aerospike_repository() -> AerospikeRepository:
    """Get aerospike repository instance"""
    return AerospikeRepository()