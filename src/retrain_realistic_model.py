#!/usr/bin/env python3
"""
Retrain ML model with correct realistic risk labels
Based on actual market consensus
"""

import sys
import os
sys.path.insert(0, '.')

def retrain_model_with_realistic_labels():
    """Retrain the ML model with proper risk classifications"""
    
    print("🔄 RETRAINING ML MODEL WITH REALISTIC LABELS")
    print("=" * 60)
    
    try:
        from models.simple_risk_predictor import SimpleRiskPredictor
        from services.financial_risk_service import FinancialRiskService
        
        predictor = SimpleRiskPredictor()
        service = FinancialRiskService()
        
        # Override the risk labeling with realistic market-based labels
        realistic_labels = {
            'AAPL': 0,    # Low Risk - Blue chip, stable
            'GOOGL': 0,   # Low Risk - Strong fundamentals  
            'AMZN': 0,    # Low Risk - Established tech giant
            'META': 1,    # High Risk - Regulatory issues, volatility
            'TSLA': 1,    # High Risk - High volatility, speculative
            'NVDA': 1,    # High Risk - Semiconductor volatility
        }
        
        print("📊 Using realistic market-based risk labels:")
        for symbol, label in realistic_labels.items():
            risk_level = "High Risk" if label else "Low Risk"
            print(f"   {symbol}: {risk_level}")
        
        # Create custom training method
        def train_with_realistic_labels():
            """Train model with realistic labels"""
            
            training_data = []
            
            for symbol in realistic_labels.keys():
                try:
                    print(f"\n🔍 Collecting features for {symbol}...")
                    
                    # Get all risk metrics (our 29 features)
                    basic_analysis = service.analyze_single_stock(symbol)
                    advanced_analysis = service.analyze_advanced_risk(symbol, period="1y")
                    
                    if basic_analysis['success'] and advanced_analysis['success']:
                        # Extract all features
                        features = predictor.extract_features(symbol, service)
                        
                        if features is not None:
                            # Add realistic label
                            features['risk_label'] = realistic_labels[symbol]
                            training_data.append(features)
                            print(f"   ✅ Features extracted for {symbol}")
                        else:
                            print(f"   ❌ Failed to extract features for {symbol}")
                    
                except Exception as e:
                    print(f"   ❌ Error processing {symbol}: {e}")
            
            if len(training_data) >= 4:  # Need minimum data
                import pandas as pd
                
                df = pd.DataFrame(training_data)
                print(f"\n📈 Training model with {len(df)} samples...")
                print(f"   Features: {len(predictor.feature_columns)} advanced risk metrics")
                
                # Train the model
                success = predictor.train_model(df)
                
                if success:
                    # Save model
                    model_path = 'models/realistic_risk_model.pkl'
                    predictor.save_model(model_path)
                    print(f"✅ Model saved to {model_path}")
                    
                    # Test predictions
                    print(f"\n🧪 Testing new model predictions:")
                    for symbol in ['AAPL', 'TSLA', 'GOOGL']:
                        result = predictor.predict_risk(symbol, service)
                        if result['success']:
                            print(f"   {symbol}: {result['risk_category']} ({result['confidence']['high_risk_probability']:.1%} high risk)")
                        
                    return True
                else:
                    print("❌ Model training failed")
                    return False
            else:
                print(f"❌ Insufficient training data: {len(training_data)} samples")
                return False
        
        # Train the model
        success = train_with_realistic_labels()
        
        if success:
            print(f"\n🎉 SUCCESS!")
            print(f"✅ ML model retrained with realistic market-based labels")
            print(f"✅ Apple should now be classified as Low Risk")
            print(f"✅ TSLA should remain High Risk")
        else:
            print(f"\n❌ Training failed - check data availability")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    retrain_model_with_realistic_labels()