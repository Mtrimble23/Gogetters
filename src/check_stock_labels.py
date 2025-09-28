#!/usr/bin/env python3
"""
Check actual risk metrics for Apple and other stocks
to see why ML model is misclassifying them
"""

import sys
import os
sys.path.insert(0, '.')

def check_stock_metrics():
    """Check actual risk metrics for major stocks"""
    
    print("🔍 ACTUAL STOCK RISK METRICS ANALYSIS")
    print("=" * 60)
    
    try:
        from services.financial_risk_service import FinancialRiskService
        
        service = FinancialRiskService()
        
        # Known classifications
        known_risk_levels = {
            'AAPL': 'Low Risk (Blue Chip)',
            'GOOGL': 'Low Risk (Blue Chip)', 
            'TSLA': 'High Risk (Volatile)',
            'NVDA': 'Moderate Risk (Growth)',
            'META': 'Moderate Risk (Tech)'
        }
        
        for symbol, expected in known_risk_levels.items():
            print(f"\n📊 {symbol} - Expected: {expected}")
            
            try:
                # Get basic analysis
                basic = service.analyze_single_stock(symbol)
                if basic['success']:
                    risk_score = basic['risk_analysis']['risk_score']
                    print(f"   Traditional Risk Score: {risk_score:.3f}")
                
                # Get advanced analysis
                advanced = service.analyze_advanced_risk(symbol, period="1y")
                if advanced['success']:
                    metrics = advanced['advanced_risk_metrics']
                    
                    print(f"   📈 Key Metrics:")
                    print(f"      Volatility: {metrics.get('annualized_volatility', 0):.3f}")
                    print(f"      Max Drawdown: {metrics.get('max_drawdown', 0):.3f}")
                    print(f"      VaR 95%: {abs(metrics.get('var', {}).get('95%', {}).get('historical', 0)):.4f}")
                    print(f"      Skewness: {metrics.get('skewness', 0):.3f}")
                    print(f"      Excess Kurtosis: {metrics.get('excess_kurtosis', 0):.3f}")
                    
                    # Check current labeling logic
                    high_risk_conditions = [
                        risk_score > 0.65,
                        metrics.get('annualized_volatility', 0) > 0.4,
                        metrics.get('max_drawdown', 0) > 0.25,
                        abs(metrics.get('var', {}).get('95%', {}).get('historical', 0)) > 0.04,
                        abs(metrics.get('cvar', {}).get('95%', 0)) > 0.05,
                        metrics.get('excess_kurtosis', 0) > 5,
                        abs(metrics.get('skewness', 0)) > 1
                    ]
                    
                    triggered = sum(high_risk_conditions)
                    current_label = 1 if triggered >= 3 else 0
                    
                    print(f"   🎯 Current ML Label: {'High Risk' if current_label else 'Low Risk'}")
                    print(f"   ⚡ Risk Conditions Triggered: {triggered}/7")
                    
                    if (expected.startswith('Low') and current_label == 1) or \
                       (expected.startswith('High') and current_label == 0):
                        print(f"   ❌ MISLABELED! Expected {expected}, got {'High' if current_label else 'Low'} Risk")
                    else:
                        print(f"   ✅ Correctly labeled")
                        
            except Exception as e:
                print(f"   ❌ Error analyzing {symbol}: {e}")
    
    except Exception as e:
        print(f"❌ Setup error: {e}")


if __name__ == "__main__":
    check_stock_metrics()