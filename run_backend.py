#!/usr/bin/env python3
"""
Main entry point for the Financial Risk Analyzer Backend
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.api.main import app
from backend.config import get_settings


def main():
    """Main entry point"""
    import uvicorn
    
    settings = get_settings()
    config = settings.get_api_config()
    
    print("🚀 Starting Financial Risk Analyzer Backend...")
    print(f"📊 API will be available at: http://{config['host']}:{config['port']}")
    print(f"📚 API Documentation: http://{config['host']}:{config['port']}/docs")
    print(f"🏥 Health Check: http://{config['host']}:{config['port']}/api/v1/health")
    
    uvicorn.run(
        app,
        host=config["host"],
        port=config["port"],
        log_level=config["log_level"],
        reload=config["debug"]
    )


if __name__ == "__main__":
    main()