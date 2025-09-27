"""
Data management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ..main import get_data_service
from ...services import DataIntegrationService


router = APIRouter()


class MigrationRequest(BaseModel):
    """Request model for data migration"""
    from_repo: str = "fallback"  # "primary" or "fallback"
    to_repo: str = "primary"     # "primary" or "fallback"


@router.get("/status")
async def get_data_status(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Get data repository status"""
    
    try:
        stats = await data_service.get_repository_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/migrate")
async def migrate_data(
    request: MigrationRequest,
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Migrate data between repositories"""
    
    if request.from_repo not in ["primary", "fallback"]:
        raise HTTPException(status_code=400, detail="from_repo must be 'primary' or 'fallback'")
    
    if request.to_repo not in ["primary", "fallback"]:
        raise HTTPException(status_code=400, detail="to_repo must be 'primary' or 'fallback'")
    
    if request.from_repo == request.to_repo:
        raise HTTPException(status_code=400, detail="from_repo and to_repo must be different")
    
    try:
        migration_result = await data_service.migrate_data(
            from_repo=request.from_repo,
            to_repo=request.to_repo
        )
        
        return {
            "success": migration_result.get("success", False),
            "data": migration_result,
            "message": f"Migration from {request.from_repo} to {request.to_repo} completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.post("/sync")
async def sync_repositories(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Synchronize data between repositories"""
    
    try:
        sync_result = await data_service.sync_repositories()
        
        return {
            "success": sync_result.get("success", False),
            "data": sync_result,
            "message": "Repository synchronization completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {str(e)}")


@router.post("/switch/primary")
async def switch_to_primary(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Switch to primary repository (Aerospike)"""
    
    try:
        success = await data_service.switch_to_primary()
        
        if success:
            return {
                "success": True,
                "message": "Switched to primary repository (Aerospike)",
                "active_repository": "primary"
            }
        else:
            return {
                "success": False,
                "message": "Failed to switch to primary repository",
                "active_repository": "fallback"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Switch failed: {str(e)}")


@router.post("/switch/fallback") 
async def switch_to_fallback(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Switch to fallback repository (in-memory)"""
    
    try:
        await data_service.switch_to_fallback()
        
        return {
            "success": True,
            "message": "Switched to fallback repository (in-memory)",
            "active_repository": "fallback"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Switch failed: {str(e)}")


@router.get("/repositories/stats")
async def get_repository_statistics(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Get detailed repository statistics"""
    
    try:
        stats = await data_service.get_repository_stats()
        
        # Add additional computed stats
        total_symbols = 0
        for repo_name, repo_data in stats.get("repositories", {}).items():
            if "symbols_count" in repo_data:
                total_symbols += repo_data["symbols_count"]
        
        stats["computed"] = {
            "total_unique_symbols": total_symbols,
            "estimated_data_size": "calculated based on repository type"
        }
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.delete("/repository/{repo_type}/symbol/{symbol}")
async def delete_symbol_data(
    repo_type: str,
    symbol: str,
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Delete all data for a symbol from specified repository"""
    
    if repo_type not in ["primary", "fallback"]:
        raise HTTPException(status_code=400, detail="repo_type must be 'primary' or 'fallback'")
    
    try:
        # Get the repository
        if repo_type == "primary":
            repository = data_service.primary_repository
        else:
            repository = data_service.fallback_repository
        
        # Get all records for the symbol
        records = await repository.get_latest_by_symbol(symbol.upper(), limit=1000)
        
        deleted_count = 0
        for record in records:
            if record.analysis_id:
                success = await repository.delete(record.analysis_id)
                if success:
                    deleted_count += 1
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} records for {symbol.upper()} from {repo_type} repository",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.get("/backup/export")
async def export_data(
    format: str = Query(default="json", regex="^(json|csv)$"),
    symbol: str = Query(default=None),
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Export data from active repository"""
    
    try:
        # Get data to export
        if symbol:
            records = await data_service.get_analysis_history(symbol.upper(), limit=1000)
        else:
            # Get all symbols and their latest records
            symbols = await data_service.get_all_symbols()
            records = []
            for sym in symbols:
                sym_records = await data_service.get_analysis_history(sym, limit=10)
                records.extend(sym_records)
        
        if format == "json":
            export_data = [record.to_dict() for record in records]
        else:  # CSV format would need pandas
            # For now, return JSON with a note
            export_data = {
                "note": "CSV export requires pandas - returning JSON format",
                "data": [record.to_dict() for record in records]
            }
        
        return {
            "success": True,
            "data": export_data,
            "format": format,
            "record_count": len(records),
            "exported_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")