"""
Application settings
"""

import os
from typing import List, Dict, Any
from functools import lru_cache


class Settings:
    """Application settings"""
    
    def __init__(self):
        # API Settings
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
        
        # Aerospike Settings
        self.AEROSPIKE_HOSTS = self._parse_aerospike_hosts()
        self.AEROSPIKE_NAMESPACE = os.getenv("AEROSPIKE_NAMESPACE", "test")
        self.AEROSPIKE_SET = os.getenv("AEROSPIKE_SET", "finance")
        self.AEROSPIKE_TIMEOUT = int(os.getenv("AEROSPIKE_TIMEOUT", "5000"))
        
        # Analysis Settings
        self.SENTIMENT_MODEL = os.getenv(
            "SENTIMENT_MODEL", 
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )
        self.SENTIMENT_BATCH_SIZE = int(os.getenv("SENTIMENT_BATCH_SIZE", "32"))
        self.RISK_ANALYSIS_TIMEOUT = int(os.getenv("RISK_ANALYSIS_TIMEOUT", "30"))
        
        # Cache Settings
        self.CACHE_DIR = os.getenv("CACHE_DIR", "./cache")
        self.SENTIMENT_CACHE_DIR = os.path.join(self.CACHE_DIR, "sentiment")
        
        # Rate Limiting
        self.MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "20"))
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        # CORS Settings
        self.CORS_ORIGINS = self._parse_cors_origins()
        
    def _parse_aerospike_hosts(self) -> List[Dict[str, Any]]:
        """Parse Aerospike hosts from environment"""
        hosts_str = os.getenv("AEROSPIKE_HOSTS", "127.0.0.1:3000")
        hosts = []
        
        for host_str in hosts_str.split(","):
            host_str = host_str.strip()
            if ":" in host_str:
                addr, port = host_str.split(":")
                hosts.append({"addr": addr, "port": int(port)})
            else:
                hosts.append({"addr": host_str, "port": 3000})
        
        return hosts
    
    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment"""
        origins_str = os.getenv("CORS_ORIGINS", "*")
        
        if origins_str == "*":
            return ["*"]
        
        return [origin.strip() for origin in origins_str.split(",")]
    
    def get_aerospike_config(self) -> Dict[str, Any]:
        """Get Aerospike configuration"""
        return {
            "hosts": self.AEROSPIKE_HOSTS,
            "namespace": self.AEROSPIKE_NAMESPACE,
            "set_name": self.AEROSPIKE_SET,
            "timeout": self.AEROSPIKE_TIMEOUT
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return {
            "host": self.API_HOST,
            "port": self.API_PORT,
            "debug": self.DEBUG,
            "log_level": self.LOG_LEVEL,
            "cors_origins": self.CORS_ORIGINS
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()