"""
Data integration service
Handles data flow between different components
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ..repositories import BaseRepository, FinancialDataRepository, AerospikeRepository
from ..models import AnalysisResult


class DataIntegrationService:
    """
    Service for managing data integration and migration
    Handles switching between repositories and data synchronization
    """
    
    def __init__(self, 
                 primary_repository: BaseRepository[AnalysisResult] = None,
                 fallback_repository: BaseRepository[AnalysisResult] = None):
        """Initialize data integration service"""
        self.primary_repository = primary_repository or AerospikeRepository()
        self.fallback_repository = fallback_repository or FinancialDataRepository()
        self.use_fallback = True  # Start with fallback until Aerospike is ready
    
    async def initialize(self):
        """Initialize repositories"""
        print("🔧 Initializing data integration service...")
        
        # First try to connect to Aerospike (primary repository)
        try:
            if isinstance(self.primary_repository, AerospikeRepository):
                print("   Attempting to connect to Aerospike...")
                await self.primary_repository.connect()
                
                # Test the connection with a simple operation
                symbols = await self.primary_repository.get_all_symbols()
                
                self.use_fallback = False
                print("   ✅ Connected to Aerospike successfully!")
                print(f"   📦 Using namespace: VTHacks, set: finance")
                print(f"   🎯 Primary repository active")
                
        except Exception as e:
            print(f"   ⚠️  Failed to connect to Aerospike: {e}")
            print(f"   🔄 Falling back to in-memory repository")
            self.use_fallback = True
        
        # Initialize fallback repository (always available)
        if self.use_fallback:
            print("   ✅ In-memory repository initialized")
        
        active_repo = "Aerospike (primary)" if not self.use_fallback else "In-memory (fallback)"
        print(f"   🎯 Active repository: {active_repo}")
    
    def get_active_repository(self) -> BaseRepository[AnalysisResult]:
        """Get the currently active repository"""
        return self.fallback_repository if self.use_fallback else self.primary_repository
    
    async def save_analysis(self, analysis: AnalysisResult) -> str:
        """Save analysis to active repository"""
        repository = self.get_active_repository()
        return await repository.save(analysis)
    
    async def get_analysis(self, symbol: str) -> Optional[AnalysisResult]:
        """Get latest analysis for symbol"""
        repository = self.get_active_repository()
        return await repository.get_by_symbol(symbol)
    
    async def get_analysis_history(self, symbol: str, limit: int = 10) -> List[AnalysisResult]:
        """Get analysis history"""
        repository = self.get_active_repository()
        return await repository.get_latest_by_symbol(symbol, limit)
    
    async def search_analyses(self, filters: Dict[str, Any]) -> List[AnalysisResult]:
        """Search analyses with filters"""
        repository = self.get_active_repository()
        return await repository.search(filters)
    
    async def get_all_symbols(self) -> List[str]:
        """Get all symbols from active repository"""
        repository = self.get_active_repository()
        return await repository.get_all_symbols()
    
    async def migrate_data(self, from_repo: str = "fallback", to_repo: str = "primary") -> Dict[str, Any]:
        """
        Migrate data between repositories
        
        Args:
            from_repo: Source repository ("primary" or "fallback")
            to_repo: Destination repository ("primary" or "fallback")
            
        Returns:
            Migration results
        """
        source_repo = self.primary_repository if from_repo == "primary" else self.fallback_repository
        dest_repo = self.primary_repository if to_repo == "primary" else self.fallback_repository
        
        migration_stats = {
            "started_at": datetime.now().isoformat(),
            "symbols_processed": 0,
            "records_migrated": 0,
            "errors": []
        }
        
        try:
            # Get all symbols from source
            symbols = await source_repo.get_all_symbols()
            migration_stats["symbols_processed"] = len(symbols)
            
            print(f"Starting migration of {len(symbols)} symbols from {from_repo} to {to_repo}")
            
            for symbol in symbols:
                try:
                    # Get all records for this symbol
                    records = await source_repo.get_latest_by_symbol(symbol, limit=1000)  # Get all
                    
                    for record in records:
                        # Save to destination
                        await dest_repo.save(record)
                        migration_stats["records_migrated"] += 1
                    
                    print(f"Migrated {len(records)} records for {symbol}")
                    
                except Exception as e:
                    error_msg = f"Error migrating {symbol}: {e}"
                    print(error_msg)
                    migration_stats["errors"].append(error_msg)
            
            migration_stats["completed_at"] = datetime.now().isoformat()
            migration_stats["success"] = True
            
        except Exception as e:
            migration_stats["error"] = str(e)
            migration_stats["success"] = False
            print(f"Migration failed: {e}")
        
        return migration_stats
    
    async def sync_repositories(self) -> Dict[str, Any]:
        """
        Synchronize data between primary and fallback repositories
        """
        if self.use_fallback:
            print("Cannot sync - primary repository not available")
            return {"error": "Primary repository not available"}
        
        sync_stats = {
            "started_at": datetime.now().isoformat(),
            "primary_to_fallback": 0,
            "fallback_to_primary": 0,
            "conflicts": 0,
            "errors": []
        }
        
        try:
            # Get symbols from both repositories
            primary_symbols = set(await self.primary_repository.get_all_symbols())
            fallback_symbols = set(await self.fallback_repository.get_all_symbols())
            
            all_symbols = primary_symbols.union(fallback_symbols)
            
            for symbol in all_symbols:
                try:
                    # Get latest from both
                    primary_latest = await self.primary_repository.get_by_symbol(symbol)
                    fallback_latest = await self.fallback_repository.get_by_symbol(symbol)
                    
                    # Determine which is newer
                    if primary_latest and fallback_latest:
                        if primary_latest.analysis_timestamp > fallback_latest.analysis_timestamp:
                            # Primary is newer, update fallback
                            await self.fallback_repository.save(primary_latest)
                            sync_stats["primary_to_fallback"] += 1
                        elif fallback_latest.analysis_timestamp > primary_latest.analysis_timestamp:
                            # Fallback is newer, update primary
                            await self.primary_repository.save(fallback_latest)
                            sync_stats["fallback_to_primary"] += 1
                        else:
                            # Same timestamp - potential conflict
                            sync_stats["conflicts"] += 1
                    
                    elif primary_latest and not fallback_latest:
                        # Only in primary, copy to fallback
                        await self.fallback_repository.save(primary_latest)
                        sync_stats["primary_to_fallback"] += 1
                    
                    elif fallback_latest and not primary_latest:
                        # Only in fallback, copy to primary
                        await self.primary_repository.save(fallback_latest)
                        sync_stats["fallback_to_primary"] += 1
                
                except Exception as e:
                    error_msg = f"Error syncing {symbol}: {e}"
                    print(error_msg)
                    sync_stats["errors"].append(error_msg)
            
            sync_stats["completed_at"] = datetime.now().isoformat()
            sync_stats["success"] = True
            
        except Exception as e:
            sync_stats["error"] = str(e)
            sync_stats["success"] = False
            print(f"Sync failed: {e}")
        
        return sync_stats
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get statistics from both repositories"""
        stats = {
            "active_repository": "fallback" if self.use_fallback else "primary",
            "primary_available": not self.use_fallback,
            "repositories": {}
        }
        
        # Primary repository stats
        try:
            if isinstance(self.primary_repository, AerospikeRepository):
                symbols = await self.primary_repository.get_all_symbols()
                stats["repositories"]["primary"] = {
                    "type": "aerospike",
                    "available": not self.use_fallback,
                    "symbols_count": len(symbols),
                    "symbols": symbols[:10]  # First 10 symbols
                }
        except Exception as e:
            stats["repositories"]["primary"] = {
                "type": "aerospike",
                "available": False,
                "error": str(e)
            }
        
        # Fallback repository stats
        try:
            if isinstance(self.fallback_repository, FinancialDataRepository):
                fallback_stats = self.fallback_repository.get_stats()
                stats["repositories"]["fallback"] = {
                    "type": "in_memory",
                    "available": True,
                    **fallback_stats
                }
        except Exception as e:
            stats["repositories"]["fallback"] = {
                "type": "in_memory",
                "available": False,
                "error": str(e)
            }
        
        return stats
    
    async def switch_to_primary(self) -> bool:
        """Switch to primary repository if available"""
        try:
            if isinstance(self.primary_repository, AerospikeRepository):
                await self.primary_repository.connect()
                # Test connection
                await self.primary_repository.get_all_symbols()
                self.use_fallback = False
                print("Switched to primary repository (Aerospike)")
                return True
        except Exception as e:
            print(f"Failed to switch to primary repository: {e}")
            return False
    
    async def switch_to_fallback(self):
        """Switch to fallback repository"""
        self.use_fallback = True
        print("Switched to fallback repository (in-memory)")