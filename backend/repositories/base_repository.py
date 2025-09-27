"""
Base repository interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository class"""
    
    @abstractmethod
    async def save(self, entity: T, key: str = None) -> str:
        """Save an entity and return its key"""
        pass
    
    @abstractmethod
    async def get_by_key(self, key: str) -> Optional[T]:
        """Get an entity by key"""
        pass
    
    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> Optional[T]:
        """Get an entity by symbol"""
        pass
    
    @abstractmethod
    async def get_latest_by_symbol(self, symbol: str, limit: int = 10) -> List[T]:
        """Get latest entities for a symbol"""
        pass
    
    @abstractmethod
    async def search(self, filters: Dict[str, Any]) -> List[T]:
        """Search entities by filters"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete an entity by key"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if entity exists"""
        pass
    
    @abstractmethod
    async def get_all_symbols(self) -> List[str]:
        """Get all unique symbols"""
        pass