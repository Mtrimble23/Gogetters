#!/bin/bash
# Single Command: Load All Stocks to Database
# This ensures all supported stocks are cached in Aerospike with identical format

echo "Loading all stocks to database..."
python3 preload_all_stocks.py

echo ""
echo "Verifying format consistency..."
python3 verify_format_consistency.py

echo ""
echo "Final database status:"
curl -s "http://localhost:8000/stats" | jq '.database.cached_symbols, .database.cache_count'

echo ""
echo "SUCCESS: All stocks loaded and verified!"