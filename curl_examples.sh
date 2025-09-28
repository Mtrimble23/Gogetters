#!/bin/bash
# Risk Level HTTP API Examples
# Copy and paste these curl commands to test your API

echo "RISK LEVEL HTTP API EXAMPLES"
echo "================================"

# Example 1: Get risk level for a single stock
echo -e "\n1. Get AAPL risk level:"
echo "curl http://localhost:8000/risk-level/AAPL"
curl -s http://localhost:8000/risk-level/AAPL | jq '.'

# Example 2: Get risk level for a new stock (triggers calculation)
echo -e "\n2. Get UBER risk level (new calculation):"
echo "curl http://localhost:8000/risk-level/UBER"
curl -s http://localhost:8000/risk-level/UBER | jq '.'

# Example 3: Batch analysis for multiple stocks
echo -e "\n3. Batch analysis for multiple stocks:"
echo 'curl -X POST http://localhost:8000/risk-level -H "Content-Type: application/json" -d {"symbols":["AMZN","MSFT","GOOG"]}'
curl -s -X POST http://localhost:8000/risk-level \
  -H "Content-Type: application/json" \
  -d '{"symbols":["AMZN","MSFT","GOOG"]}' | jq '.'

# Example 4: Custom risk factors
echo -e "\n4. Analysis with custom risk factors:"
echo 'curl -X POST http://localhost:8000/risk-level -H "Content-Type: application/json" -d {"symbols":["HIGH_RISK_TEST"],"risk_factors":{"volatility":0.9,"market_cap":"small","sector_risk":0.8,"liquidity":0.1}}'
curl -s -X POST http://localhost:8000/risk-level \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["HIGH_RISK_TEST"],
    "risk_factors": {
      "volatility": 0.9,
      "market_cap": "small", 
      "sector_risk": 0.8,
      "liquidity": 0.1
    }
  }' | jq '.'

echo -e "\nAll examples completed!"
echo -e "\n📚 More endpoints:"
echo "   Health Check:      curl http://localhost:8000/health"
echo "   Test Aerospike:    curl http://localhost:8000/test-aerospike"  
echo "   API Documentation: http://localhost:8000/docs"