#!/usr/bin/env python3
"""
Check Data Completeness for All Stocks
Verifies that all required fields are loaded and no critical data is missing
"""

import requests
import json

API_BASE = "http://localhost:8000"
SUPPORTED_STOCKS = ["AAPL", "AMZN", "GOOGL", "NVDA", "META", "TSLA"]

# Define required fields for completeness check
REQUIRED_FINANCIAL_FIELDS = [
    "symbol",
    "current_price", 
    "price_change_percent",
    "dividend_yield",
    "beta",
    "pe_ratio", 
    "debt_to_equity",
    "market_cap",
    "cboe_volatility",
    "fifty_two_week_high",
    "fifty_two_week_low",
    "volume",
    "avg_volume",
    "price_history"
]

REQUIRED_RISK_FIELDS = [
    "risk_level",
    "risk_score", 
    "recommendation",
    "risk_factors",
    "metrics_used"
]

def check_data_completeness():
    """Check that all stocks have complete data"""
    print("Checking data completeness for all stocks...")
    print("=" * 60)
    
    results = {}
    
    for symbol in SUPPORTED_STOCKS:
        try:
            response = requests.get(f"{API_BASE}/risk-level/{symbol}")
            
            if response.status_code != 200:
                results[symbol] = {"error": f"HTTP {response.status_code}"}
                continue
                
            data = response.json()
            
            if not data.get("success"):
                results[symbol] = {"error": "API returned success=false"}
                continue
                
            # Check financial data
            financial_data = data.get("data", {}).get("financial_data", {})
            risk_analysis = data.get("data", {}).get("risk_analysis", {})
            
            missing_financial = []
            missing_risk = []
            null_financial = []
            null_risk = []
            
            # Check financial fields
            for field in REQUIRED_FINANCIAL_FIELDS:
                if field not in financial_data:
                    missing_financial.append(field)
                elif financial_data[field] is None:
                    null_financial.append(field)
            
            # Check risk analysis fields
            for field in REQUIRED_RISK_FIELDS:
                if field not in risk_analysis:
                    missing_risk.append(field)
                elif risk_analysis[field] is None:
                    null_risk.append(field)
            
            # Check price history completeness
            price_history = financial_data.get("price_history", {})
            if isinstance(price_history, dict):
                prices = price_history.get("prices", [])
                dates = price_history.get("dates", [])
                price_history_complete = len(prices) > 0 and len(dates) > 0 and len(prices) == len(dates)
            else:
                price_history_complete = False
            
            results[symbol] = {
                "success": True,
                "missing_financial": missing_financial,
                "missing_risk": missing_risk,
                "null_financial": null_financial,
                "null_risk": null_risk,
                "price_history_complete": price_history_complete,
                "price_history_length": len(prices) if 'prices' in locals() else 0,
                "current_price": financial_data.get("current_price"),
                "risk_level": risk_analysis.get("risk_level"),
                "cboe_volatility": financial_data.get("cboe_volatility")
            }
            
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    # Analyze results
    print("COMPLETENESS RESULTS")
    print("=" * 60)
    
    all_complete = True
    
    for symbol, result in results.items():
        if "error" in result:
            print(f"ERROR {symbol}: ERROR - {result['error']}")
            all_complete = False
            continue
            
        # Check for issues
        issues = []
        if result["missing_financial"]:
            issues.append(f"Missing financial: {', '.join(result['missing_financial'])}")
        if result["missing_risk"]:
            issues.append(f"Missing risk: {', '.join(result['missing_risk'])}")
        if result["null_financial"]:
            issues.append(f"Null financial: {', '.join(result['null_financial'])}")
        if result["null_risk"]:
            issues.append(f"Null risk: {', '.join(result['null_risk'])}")
        if not result["price_history_complete"]:
            issues.append("Incomplete price history")
        
        if issues:
            print(f"WARNING {symbol}: {'; '.join(issues)}")
            all_complete = False
        else:
            print(f"SUCCESS {symbol}: Complete - ${result['current_price']}, {result['risk_level']} risk, {result['price_history_length']} price points, {result['cboe_volatility']}% volatility")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    successful = len([r for r in results.values() if "error" not in r])
    
    if all_complete and successful == len(SUPPORTED_STOCKS):
        print("ALL STOCKS HAVE COMPLETE DATA!")
        print(f"SUCCESS: {successful}/{len(SUPPORTED_STOCKS)} stocks verified")
        print("All required fields present and populated")
        print("Price history data complete")
        print("Risk analysis complete")
        print("Yahoo Finance data complete")
        print("CBOE volatility data complete")
    else:
        print("SOME DATA IS INCOMPLETE!")
        print(f"WARNING: Issues found in {len(SUPPORTED_STOCKS) - successful} stocks")
    
    return all_complete

if __name__ == "__main__":
    success = check_data_completeness()
    exit(0 if success else 1)