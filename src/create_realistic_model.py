#!/usr/bin/env python3
"""
Create Realistic Risk Model
Simple approach using known market classifications
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

sys.path.insert(0, '.')

def create_realistic_model():
    """Create a model with realistic risk classifications"""
    
    print("🎯 CREATING REALISTIC RISK MODEL")
    print("=" * 50)
    
    try:
        from services.financial_risk_service import FinancialRiskService
        
        service = FinancialRiskService()
        
        # Market-consensus risk classifications
        stock_classifications = {
            'AAPL': {'risk': 0, 'name': 'Low Risk (Blue Chip)'},
            'GOOGL': {'risk': 0, 'name': 'Low Risk (Strong Tech)'},
            'AMZN': {'risk': 0, 'name': 'Low Risk (Diversified)'},
            'META': {'risk': 1, 'name': 'High Risk (Regulatory/Volatile)'},
            'TSLA': {'risk': 1, 'name': 'High Risk (Volatile/Speculative)'},
            'NVDA': {'risk': 1, 'name': 'High Risk (Semiconductor Cycle)'},
        }
        
        print("📊 Market-Based Risk Classifications:")
        for symbol, info in stock_classifications.items():
            print(f"   {symbol}: {info['name']}")
        
        # Collect training data
        training_data = []
        
        for symbol, classification in stock_classifications.items():
            print(f"\n📈 Analyzing {symbol}...")
            
            try:
                basic = service.analyze_single_stock(symbol)
                advanced = service.analyze_advanced_risk(symbol, period="1y")
                
                if basic['success'] and advanced['success']:
                    
                    # Create feature vector from all our advanced equations
                    basic_metrics = basic['risk_analysis']
                    advanced_metrics = advanced['advanced_risk_metrics']
                    
                    features = {
                        # Basic metrics
                        'beta': basic_metrics.get('beta', 1.0),
                        'pe_ratio': basic_metrics.get('pe_ratio', 15.0),
                        'debt_to_equity': basic_metrics.get('debt_to_equity', 0.5),
                        'cboe_volatility': basic_metrics.get('cboe_volatility', 0.2),
                        'price_change_percent': basic_metrics.get('price_change_percent', 0.0),
                        'market_cap_log': np.log(basic_metrics.get('market_cap', 1e9)),
                        
                        # Our 29 advanced risk equations
                        'annualized_volatility': advanced_metrics.get('annualized_volatility', 0.2),
                        'skewness': advanced_metrics.get('skewness', 0.0),
                        'excess_kurtosis': advanced_metrics.get('excess_kurtosis', 0.0),
                        'var_95_historical': abs(advanced_metrics.get('var', {}).get('95%', {}).get('historical', 0.02)),
                        'var_99_historical': abs(advanced_metrics.get('var', {}).get('99%', {}).get('historical', 0.03)),
                        'var_95_parametric': abs(advanced_metrics.get('var', {}).get('95%', {}).get('parametric', 0.02)),
                        'var_99_parametric': abs(advanced_metrics.get('var', {}).get('99%', {}).get('parametric', 0.03)),
                        'cvar_95': abs(advanced_metrics.get('cvar', {}).get('95%', 0.025)),
                        'cvar_99': abs(advanced_metrics.get('cvar', {}).get('99%', 0.035)),
                        'max_drawdown': advanced_metrics.get('max_drawdown', 0.1),
                        'avg_drawdown': advanced_metrics.get('avg_drawdown', 0.05),
                        'recovery_time': advanced_metrics.get('recovery_time', 10),
                        'calmar_ratio': advanced_metrics.get('calmar_ratio', 1.0),
                        'burke_ratio': advanced_metrics.get('burke_ratio', 1.0),
                        'pain_index': advanced_metrics.get('pain_index', 0.05),
                        'ulcer_performance_index': advanced_metrics.get('ulcer_performance_index', 1.0),
                        'sortino_ratio': advanced_metrics.get('sortino_ratio', 1.0),
                        'omega_ratio': advanced_metrics.get('omega_ratio', 1.0),
                        'downside_deviation': advanced_metrics.get('downside_deviation', 0.15),
                        'shape_ratio_95': advanced_metrics.get('shape_ratio', {}).get('95%', 1.0),
                        'shape_ratio_99': advanced_metrics.get('shape_ratio', {}).get('99%', 1.0),
                        'gumbel_beta': advanced_metrics.get('extreme_value_theory', {}).get('gumbel_beta', 0.02),
                        'generalized_pareto_sigma': advanced_metrics.get('extreme_value_theory', {}).get('generalized_pareto_sigma', 0.02),
                        'tail_index': advanced_metrics.get('extreme_value_theory', {}).get('tail_index', 2.0),
                        'correlation': advanced_metrics.get('correlation', 0.5),
                        'systematic_risk': advanced_metrics.get('systematic_risk', 0.3),
                        'idiosyncratic_risk': advanced_metrics.get('idiosyncratic_risk', 0.2),
                        'tracking_error': advanced_metrics.get('tracking_error', 0.05),
                        'information_ratio': advanced_metrics.get('information_ratio', 0.5),
                        
                        # Target label - realistic classification
                        'risk_label': classification['risk']
                    }
                    
                    training_data.append(features)
                    print(f"   ✅ Features collected for {symbol}")
                    
            except Exception as e:
                print(f"   ❌ Error processing {symbol}: {e}")
        
        if len(training_data) >= 4:
            print(f"\n🤖 Training model with {len(training_data)} samples...")
            
            df = pd.DataFrame(training_data)
            
            # Prepare features and labels
            feature_columns = [col for col in df.columns if col != 'risk_label']
            X = df[feature_columns]
            y = df['risk_label']
            
            print(f"   Features: {len(feature_columns)} risk metrics")
            print(f"   Samples: {len(X)} stocks")
            print(f"   Labels: {sum(y)} high risk, {len(y)-sum(y)} low risk")
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model = LogisticRegression(random_state=42, max_iter=1000)
            model.fit(X_scaled, y)
            
            # Save model and scaler
            os.makedirs('models', exist_ok=True)
            
            model_data = {
                'model': model,
                'scaler': scaler,
                'feature_columns': feature_columns,
                'training_info': {
                    'samples': len(X),
                    'features': len(feature_columns),
                    'classifications': stock_classifications
                }
            }
            
            joblib.dump(model_data, 'models/realistic_risk_model.pkl')
            print(f"✅ Model saved to models/realistic_risk_model.pkl")
            
            # Test predictions
            print(f"\n🧪 Testing Realistic Model Predictions:")
            
            for symbol in ['AAPL', 'GOOGL', 'TSLA']:
                if symbol in stock_classifications:
                    expected = stock_classifications[symbol]['name']
                    
                    # Find the sample for this stock
                    stock_data = next((item for item in training_data if item.get('symbol') == symbol), None)
                    if not stock_data:
                        # Get current data for prediction
                        try:
                            basic = service.analyze_single_stock(symbol)
                            advanced = service.analyze_advanced_risk(symbol, period="1y")
                            
                            if basic['success'] and advanced['success']:
                                # Create prediction features (same as training)
                                basic_metrics = basic['risk_analysis']
                                advanced_metrics = advanced['advanced_risk_metrics']
                                
                                pred_features = []
                                for col in feature_columns:
                                    if col == 'beta':
                                        pred_features.append(basic_metrics.get('beta', 1.0))
                                    elif col == 'annualized_volatility':
                                        pred_features.append(advanced_metrics.get('annualized_volatility', 0.2))
                                    elif col == 'max_drawdown':
                                        pred_features.append(advanced_metrics.get('max_drawdown', 0.1))
                                    # Add more mappings as needed
                                    else:
                                        pred_features.append(0.1)  # Default value
                                
                                pred_scaled = scaler.transform([pred_features])
                                prediction = model.predict(pred_scaled)[0]
                                probability = model.predict_proba(pred_scaled)[0]
                                
                                risk_category = "High Risk" if prediction == 1 else "Low Risk"
                                high_prob = probability[1] * 100
                                
                                print(f"   {symbol}: {risk_category} ({high_prob:.1f}% high risk)")
                                print(f"      Expected: {expected}")
                                
                                if (expected.startswith('Low') and prediction == 0) or \
                                   (expected.startswith('High') and prediction == 1):
                                    print(f"      ✅ Correct prediction!")
                                else:
                                    print(f"      ❌ Mismatch with expected")
                        except:
                            print(f"   {symbol}: Unable to predict")
            
            print(f"\n🎉 Realistic risk model created successfully!")
            return True
            
        else:
            print(f"❌ Insufficient training data: {len(training_data)} samples")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    create_realistic_model()