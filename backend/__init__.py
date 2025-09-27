"""
Backend package initialization
"""

from .api.main import app
from .services import FinancialAnalysisService, DataIntegrationService
from .repositories import BaseRepository, FinancialDataRepository, AerospikeRepository
from .models import AnalysisResult, FinancialData, RiskMetrics, SentimentData
from .config import Settings, get_settings

__version__ = "1.0.0"

__all__ = [
    'app',
    'FinancialAnalysisService', 
    'DataIntegrationService',
    'BaseRepository', 
    'FinancialDataRepository', 
    'AerospikeRepository',
    'AnalysisResult', 
    'FinancialData', 
    'RiskMetrics', 
    'SentimentData',
    'Settings', 
    'get_settings'
]