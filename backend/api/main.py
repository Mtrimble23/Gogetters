"""
FastAPI main application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .routes.analysis_routes import router as analysis_router
from .routes.data_routes import router as data_router  
from .routes.health_routes import router as health_router
from ..services import FinancialAnalysisService, DataIntegrationService
from ..repositories import FinancialDataRepository, AerospikeRepository


# Global service instances
data_service: DataIntegrationService = None
analysis_service: FinancialAnalysisService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global data_service, analysis_service
    
    print("Starting Financial Risk Analyzer Backend...")
    
    # Initialize repositories and services
    aerospike_repo = AerospikeRepository()
    fallback_repo = FinancialDataRepository()
    
    data_service = DataIntegrationService(
        primary_repository=aerospike_repo,
        fallback_repository=fallback_repo
    )
    
    # Initialize data service (will try Aerospike, fallback to in-memory)
    await data_service.initialize()
    
    # Initialize analysis service with active repository
    analysis_service = FinancialAnalysisService(
        repository=data_service.get_active_repository()
    )
    
    print("Backend initialization complete!")
    
    yield
    
    # Cleanup
    print("Shutting down Financial Risk Analyzer Backend...")


# Create FastAPI app
app = FastAPI(
    title="Financial Risk Analyzer API",
    description="Comprehensive financial risk analysis with sentiment analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(data_router, prefix="/api/v1/data", tags=["Data"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial Risk Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


def get_data_service() -> DataIntegrationService:
    """Get data integration service instance"""
    global data_service
    if data_service is None:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return data_service


def get_analysis_service() -> FinancialAnalysisService:
    """Get financial analysis service instance"""
    global analysis_service
    if analysis_service is None:
        raise HTTPException(status_code=500, detail="Analysis service not initialized")
    return analysis_service


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )