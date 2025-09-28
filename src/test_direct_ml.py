#!/usr/bin/env python3
"""
Direct ML Risk Predictor Test
Bypass import issues and test ML predictions directly
"""

import sys
import os
sys.path.insert(0, '.')

def test_direct_ml_prediction():
    """Test ML predictions directly without service layer"""
    
    print("🤖 DIRECT ML RISK PREDICTION TEST")
    print("=" * 50)
    
    try:
        # Direct imports
        from models.simple_risk_predictor import SimpleRiskPredictor
        from services.financial_risk_service import FinancialRiskService
        
        print("✅ Imports successful")
        
        # Initialize
        predictor = SimpleRiskPredictor()
        service = FinancialRiskService()
        
        # Load model directly
        model_path = 'models/simple_risk_model.pkl'
        if os.path.exists(model_path):
            predictor.load_model(model_path)
            print(f"✅ Model loaded from {model_path}")
            
            # Test prediction
            symbols = ['AAPL', 'TSLA', 'GOOGL']
            
            print(f"\n🧪 Testing ML Predictions:")
            
            for symbol in symbols:
                print(f"\n📊 {symbol} ML Risk Prediction:")
                
                try:
                    result = predictor.predict_risk(symbol, service)
                    
                    if result['success']:
                        print(f"   ✅ Prediction successful!")
                        print(f"   Risk Category: {result['risk_category']}")
                        print(f"   High Risk Probability: {result['confidence']['high_risk_probability']:.1%}")
                        print(f"   Low Risk Probability: {result['confidence']['low_risk_probability']:.1%}")
                        print(f"   Recommendation: {result['recommendation']}")
                        print(f"   Confidence Level: {result['confidence']['confidence_level']}")
                        
                        print(f"   🔧 Top 3 Risk Factors:")
                        for i, factor in enumerate(result['top_risk_factors'][:3]):
                            print(f"      {i+1}. {factor['feature']} ({factor['equation_type']})")
                            print(f"         → {factor['direction']}")
                        
                        print(f"   📊 Using {result['equations_used']} advanced equations as features")
                        
                    else:
                        print(f"   ❌ Prediction failed: {result['error']}")
                        
                except Exception as e:
                    print(f"   ❌ Error during prediction: {e}")
                    import traceback
                    traceback.print_exc()
            
        else:
            print(f"❌ Model file not found: {model_path}")
            print("   Available files:")
            if os.path.exists('models'):
                for f in os.listdir('models'):
                    print(f"     {f}")
            
    except Exception as e:
        print(f"❌ Import or setup error: {e}")
        import traceback
        traceback.print_exc()


def fix_service_import():
    """Fix the service import issue"""
    
    print(f"\n🔧 FIXING SERVICE IMPORT ISSUE")
    print("=" * 50)
    
    try:
        # Test service creation without ML model
        from services.financial_risk_service import FinancialRiskService
        
        print("Testing service initialization...")
        service = FinancialRiskService()
        
        # Check if ML predictor was initialized
        if hasattr(service, 'ml_predictor') and service.ml_predictor:
            print("✅ ML predictor is available in service")
            
            # Test ML prediction through service
            result = service.predict_stock_risk_ml('AAPL')
            if result and result.get('success'):
                print("✅ Service ML prediction working!")
                print(f"   Risk Category: {result['risk_category']}")
                print(f"   Probability: {result['confidence']['high_risk_probability']:.1%}")
            else:
                print(f"❌ Service ML prediction failed: {result}")
        else:
            print("❌ ML predictor not available in service")
            
    except Exception as e:
        print(f"❌ Service test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_direct_ml_prediction()
    fix_service_import()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. If predictions work above, the ML model is functional")
    print(f"   2. The issue is just in the service import logic")
    print(f"   3. We can bypass this and use direct ML predictions")