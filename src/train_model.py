#!/usr/bin/env python3
"""
Model Training Script
Simple script to train the ML risk prediction model using all advanced equations
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.financial_risk_service import FinancialRiskService
from models.simple_risk_predictor import SimpleRiskPredictor


def main():
    """Train the ML model with comprehensive logging"""
    print("🎯 TRAINING ML RISK PREDICTION MODEL")
    print("   Using ALL Advanced Risk Equations as Features")
    print("=" * 60)
    
    try:
        # Initialize services
        print("📊 Initializing services...")
        financial_service = FinancialRiskService()
        risk_predictor = SimpleRiskPredictor()
        
        # Get training symbols
        symbols = financial_service.get_supported_symbols()
        print(f"✅ Loaded {len(symbols)} supported symbols: {symbols}")
        print(f"✅ Loaded {len(risk_predictor.feature_columns)} advanced risk features")
        
        # Start training
        print(f"\n🚀 Starting model training...")
        start_time = time.time()
        
        training_results = risk_predictor.train_model(symbols, financial_service)
        
        training_time = time.time() - start_time
        print(f"\n⏱️  Training completed in {training_time:.1f} seconds")
        
        # Save model
        model_path = os.path.join('models', 'simple_risk_model.pkl')
        risk_predictor.save_model(model_path)
        
        # Test predictions
        print(f"\n🧪 Testing model predictions...")
        for symbol in ['AAPL', 'TSLA']:
            result = risk_predictor.predict_risk(symbol, financial_service)
            if result['success']:
                print(f"   {symbol}: {result['risk_category']} "
                      f"({result['confidence']['high_risk_probability']:.1%} risk)")
            else:
                print(f"   {symbol}: Error - {result['error']}")
        
        print(f"\n✅ Model training completed successfully!")
        print(f"   You can now use the comprehensive risk analysis.")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()