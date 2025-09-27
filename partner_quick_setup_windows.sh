#!/bin/bash
# Quick Setup Script for Partner - Windows Compatible Version
# Runs all setup steps in sequence

echo "VTHacks26 Financial Risk API - Quick Setup"
echo "==========================================="

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.7+ first."
    exit 1
fi

echo "SUCCESS: Prerequisites check passed"

# Step 2: Install dependencies
echo ""
echo "Step 2: Installing Python dependencies..."
pip3 install --break-system-packages -r requirements.txt || pip3 install --user -r requirements.txt

# Step 3: Start database
echo ""
echo "Step 3: Starting Aerospike database..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 10

# Check if database is running
if ! docker ps | grep aerospike | grep -q "healthy\|Up"; then
    echo "ERROR: Database failed to start properly"
    exit 1
fi

echo "SUCCESS: Database is running"

# Step 4: Start backend
echo ""
echo "Step 4: Starting backend server..."
nohup python3 financial_api_backend.py > backend.log 2>&1 &

echo "Waiting for backend to start..."
sleep 5

# Check if backend is responding
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "ERROR: Backend failed to start. Check backend.log for errors."
    exit 1
fi

echo "SUCCESS: Backend is running"

# Step 5: Load all stocks
echo ""
echo "Step 5: Loading all stock data..."
if [ -f "./load_all_stocks.sh" ]; then
    ./load_all_stocks.sh
else
    python3 preload_all_stocks.py
fi

# Step 6: Final verification
echo ""
echo "Step 6: Final verification..."

# Check health
health_status=$(curl -s http://localhost:8000/health | jq -r '.database_connected // false')
if [ "$health_status" != "true" ]; then
    echo "WARNING: Database connection issue detected"
else
    echo "SUCCESS: Database connection verified"
fi

# Check cache
cache_count=$(curl -s http://localhost:8000/stats | jq -r '.database.cache_count // 0')
if [ "$cache_count" -eq 6 ]; then
    echo "SUCCESS: All 6 stocks loaded and cached"
else
    echo "WARNING: Only $cache_count/6 stocks cached"
fi

echo ""
echo "SETUP COMPLETE!"
echo "==============="
echo "API Server: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo "Test API: curl http://localhost:8000/risk-level/AAPL"
echo ""
echo "See FINAL_PARTNER_GUIDE.md for full documentation"
echo "Ready to build your application!"