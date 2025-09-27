"""
API routes package
"""

from .analysis_routes import router as analysis_router
from .data_routes import router as data_router
from .health_routes import router as health_router

__all__ = ['analysis_router', 'data_router', 'health_router']