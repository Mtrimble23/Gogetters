"""
Aerospike configuration and connection management
"""

from typing import List, Dict, Any, Optional
import logging
from ..config.settings import get_settings


class AerospikeConfig:
    """Aerospike configuration and utilities"""
    
    def __init__(self, settings=None):
        """Initialize Aerospike configuration"""
        self.settings = settings or get_settings()
        self.config = self.settings.get_aerospike_config()
        self.logger = logging.getLogger(__name__)
    
    def get_client_config(self) -> Dict[str, Any]:
        """Get client configuration for Aerospike connection"""
        return {
            "hosts": self.config["hosts"],
            "policies": {
                "timeout": self.config["timeout"]
            }
        }
    
    def get_namespace(self) -> str:
        """Get Aerospike namespace"""
        return self.config["namespace"]
    
    def get_set_name(self) -> str:
        """Get Aerospike set name"""
        return self.config["set_name"]
    
    def create_indexes(self, client) -> bool:
        """
        Create secondary indexes for efficient queries
        
        This should be called when Aerospike is first set up
        """
        try:
            namespace = self.get_namespace()
            set_name = self.get_set_name()
            
            # Index for symbol queries
            try:
                client.index_string_create(
                    namespace, 
                    set_name, 
                    "symbol", 
                    "symbol_idx"
                )
                self.logger.info("Created symbol index")
            except Exception as e:
                if "Index already exists" not in str(e):
                    self.logger.warning(f"Failed to create symbol index: {e}")
            
            # Index for timestamp queries
            try:
                client.index_integer_create(
                    namespace, 
                    set_name, 
                    "timestamp", 
                    "timestamp_idx"
                )
                self.logger.info("Created timestamp index")
            except Exception as e:
                if "Index already exists" not in str(e):
                    self.logger.warning(f"Failed to create timestamp index: {e}")
            
            # Index for risk level queries
            try:
                client.index_string_create(
                    namespace, 
                    set_name, 
                    "risk_level", 
                    "risk_level_idx"
                )
                self.logger.info("Created risk_level index")
            except Exception as e:
                if "Index already exists" not in str(e):
                    self.logger.warning(f"Failed to create risk_level index: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create indexes: {e}")
            return False
    
    def validate_connection(self, client) -> bool:
        """Validate Aerospike connection"""
        try:
            # Simple validation - try to get cluster info
            cluster_info = client.info("version")
            self.logger.info(f"Connected to Aerospike cluster: {cluster_info}")
            return True
            
        except Exception as e:
            self.logger.error(f"Aerospike connection validation failed: {e}")
            return False
    
    def get_query_policy(self) -> Dict[str, Any]:
        """Get query policy for Aerospike operations"""
        return {
            "timeout": self.config["timeout"]
        }
    
    def get_write_policy(self) -> Dict[str, Any]:
        """Get write policy for Aerospike operations"""
        return {
            "timeout": self.config["timeout"],
            "retry": True,
            "max_retries": 3
        }