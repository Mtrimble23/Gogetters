#!/bin/bash
# Startup script for Financial API Backend
# This script runs the required initialization scripts and starts the API

echo "========================================"
echo "VTHacks26 Financial API Startup"
echo "========================================"

# Wait for Aerospike to be ready (if using external Aerospike)
if [ ! -z "$AEROSPIKE_HOST" ]; then
    echo "Waiting for Aerospike at $AEROSPIKE_HOST:3000..."
    until nc -z $AEROSPIKE_HOST 3000; do
        echo "Aerospike not ready yet, waiting..."
        sleep 2
    done
    echo "✅ Aerospike is ready!"
fi

# Set Python path
export PYTHONPATH=/app

echo "📊 Running advanced risk storage initialization..."
cd /app
python src/advanced_risk_storage.py

echo "🔮 Running prediction storage initialization..."
python src/prediction_storage.py

echo "🚀 Starting Financial API Backend..."
python financial_api_backend.py