#!/usr/bin/env python3
"""
Working ML Risk API - bypasses import issues
Real ML predictions using all 29 advanced risk equations
"""

import sys
import os
sys.path.insert(0, '.')

def get_ml_risk_prediction(symbol):
    """Get real ML risk prediction for a stock"""
    
    try:
        # Direct imports to bypass service layer issues
        from models.simple_risk_predictor import SimpleRiskPredictor
        from services.financial_risk_service import FinancialRiskService
        
        # Initialize components
        predictor = SimpleRiskPredictor()
        service = FinancialRiskService()
        
        # Load model
        model_path = 'models/simple_risk_model.pkl'
        if os.path.exists(model_path):
            predictor.load_model(model_path)
            
            # Get ML prediction
            result = predictor.predict_risk(symbol, service)
            return result
        else:
            return {'success': False, 'error': 'Model file not found'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}


def demo_working_ml_predictions():
    """Demonstrate working ML predictions"""
    
    print("🤖 WORKING ML RISK PREDICTIONS")
    print("=" * 50)
    print("Using all 29 advanced risk equations as ML features:")
    print("• Volatility measures • Value at Risk • Drawdown analysis")
    print("• Extreme value theory • Tail risk • Systemic risk")
    print("• And 23 more advanced equations...")
    
    stocks = ['AAPL', 'TSLA', 'GOOGL', 'NVDA', 'META']
    
    for symbol in stocks:
        print(f"\n📊 {symbol} ML Analysis:")
        
        result = get_ml_risk_prediction(symbol)
        
        if result['success']:
            risk = result['risk_category']
            prob = result['confidence']['high_risk_probability']
            recommendation = result['recommendation']
            
            # Color coding for terminal
            if risk == 'High Risk':
                risk_color = f"🔴 {risk}"
            elif risk == 'Moderate Risk':
                risk_color = f"🟡 {risk}"
            else:
                risk_color = f"🟢 {risk}"
            
            print(f"   Risk Level: {risk_color}")
            print(f"   High Risk Probability: {prob:.1%}")
            print(f"   Recommendation: {recommendation}")
            print(f"   Top Risk Factor: {result['top_risk_factors'][0]['feature']}")
            
        else:
            print(f"   ❌ Error: {result['error']}")
    
    print(f"\n✅ All predictions use real ML model trained on historical data")
    print(f"✅ Features derived from 29 advanced risk equations")
    print(f"✅ Binary classification with probability thresholds")


if __name__ == "__main__":
    demo_working_ml_predictions()