#!/usr/bin/env python3
"""
Python VGP Trading System - Individual Stock Training Approach
Multi-stock training: individual models per stock, then generalization
"""

import numpy as np
import pandas as pd
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path

# Import from existing python_vgp.py for core classes
# This is a focused training script for individual stock approach

def train_individual_stock_models(data_dict: Dict[str, pd.DataFrame]):
    """
    New training approach:
    1. Train individual model for each stock
    2. Find best performing approaches 
    3. Create generalized model
    4. Test on all stocks with profit reporting
    """
    print(f"Individual Stock VGP Training")
    print(f"Training on {len(data_dict)} stocks individually...")
    print("=" * 60)
    
    # We'll use the existing classes but train differently
    from python_vgp import (MultiStockVGP, TechnicalIndicators, 
                           Backtester, FitnessEvaluator, VGPEngine)
    
    stock_results = {}
    individual_models = {}
    
    # Phase 1: Train each stock individually WITH PROPER DATA SPLIT
    for stock_symbol, stock_data in data_dict.items():
        print(f"\\n🔄 Training {stock_symbol}...")
        
        # CRITICAL: Split data BEFORE training to prevent data leakage
        ti = TechnicalIndicators()
        features_df = ti.calculate_features(stock_data)
        features = features_df.values
        prices = stock_data['close'].values
        
        # Split into train/test (80/20) BEFORE any training
        split_idx = int(0.8 * len(features))
        train_features = features[:split_idx]
        train_prices = prices[:split_idx]
        test_features = features[split_idx:]
        test_prices = prices[split_idx:]
        
        print(f"  Training samples: {len(train_features)}")
        print(f"  Test samples: {len(test_features)} (unseen during training)")
        
        # Create training data dict with ONLY training portion
        train_data = stock_data.iloc[:split_idx].copy()
        single_stock_train_dict = {stock_symbol: train_data}
        
        # Create individual training system for this stock
        vgp_system = MultiStockVGP(population_size=50, generations=10)
        
        # Train on ONLY training data (80%)
        best_model = vgp_system.train(single_stock_train_dict)
        
        if best_model:
            individual_models[stock_symbol] = best_model
            
            # Test on the PROPERLY held-out test data (never seen during training)
            fitness_evaluator = FitnessEvaluator()  # Create fresh evaluator
            test_fitness = fitness_evaluator.evaluate(best_model, test_features, test_prices, debug=True)
            
            # Calculate actual returns on unseen test data
            backtester = Backtester(initial_capital=10000)
            vgp_engine = VGPEngine()
            # Use generate_signals to convert continuous output to discrete buy/sell/hold signals
            # Use a more sensitive threshold to generate more trades
            signals = vgp_engine.generate_signals(best_model, test_features, threshold=0.1)
            portfolio = backtester.backtest(signals, test_prices)
            
            profit_pct = ((portfolio.equity_curve[-1] - portfolio.initial_capital) / portfolio.initial_capital) * 100
            
            stock_results[stock_symbol] = {
                'model': best_model,
                'test_fitness': test_fitness,
                'profit_pct': profit_pct,
                'trades': portfolio.num_trades,
                'win_rate': portfolio.win_rate * 100,
                'final_equity': portfolio.equity_curve[-1],
                'initial_capital': portfolio.initial_capital
            }
            
            print(f"  ✅ {stock_symbol}: {profit_pct:+.2f}% profit, {portfolio.num_trades} trades, {portfolio.win_rate*100:.1f}% wins")
        else:
            print(f"  ❌ {stock_symbol}: Training failed")
    
    # Phase 2: Analysis and Generalization  
    if not stock_results:
        print("\\n❌ No individual models trained successfully!")
        return None
    
    print(f"\\n📊 INDIVIDUAL MODEL RESULTS")
    print("=" * 60)
    
    # Sort by profit
    sorted_results = sorted(stock_results.items(), key=lambda x: x[1]['profit_pct'], reverse=True)
    
    total_profit = 0
    profitable_count = 0
    
    for i, (symbol, results) in enumerate(sorted_results):
        profit = results['profit_pct']
        total_profit += profit
        if profit > 0:
            profitable_count += 1
            
        print(f"{i+1:2d}. {symbol}: {profit:+7.2f}% | {results['trades']:3d} trades | {results['win_rate']:5.1f}% wins | ${results['final_equity']:,.0f}")
    
    avg_profit = total_profit / len(stock_results)
    
    print("\\n📈 SUMMARY STATISTICS")
    print("-" * 40)
    print(f"Average profit per stock: {avg_profit:+.2f}%")
    print(f"Best performer: {sorted_results[0][0]} ({sorted_results[0][1]['profit_pct']:+.2f}%)")
    print(f"Worst performer: {sorted_results[-1][0]} ({sorted_results[-1][1]['profit_pct']:+.2f}%)")
    print(f"Profitable stocks: {profitable_count}/{len(stock_results)} ({profitable_count/len(stock_results)*100:.1f}%)")
    
    # Phase 3: Select best model as generalized model
    best_stock, best_results = sorted_results[0]
    generalized_model = best_results['model']
    
    print(f"\\n🎯 GENERALIZED MODEL SELECTION")
    print("-" * 40)
    print(f"Selected model from: {best_stock}")
    print(f"Selection criteria: Highest profit ({best_results['profit_pct']:+.2f}%)")
    
    # Phase 4: Test generalized model on all stocks
    print(f"\\n🧪 GENERALIZED MODEL TESTING")
    print("=" * 60)
    print("Testing best model on all stocks...")
    
    generalized_results = {}
    gen_total_profit = 0
    gen_profitable_count = 0
    
    for stock_symbol, stock_data in data_dict.items():
        # Test generalized model on this stock with correct method
        ti = TechnicalIndicators()
        features_df = ti.calculate_features(stock_data)
        features = features_df.values  # Convert to numpy array
        prices = stock_data['close'].values
        
        if features is None:
            continue
            
        # Test on held-out 20%
        split_idx = int(0.8 * len(features))
        test_features = features[split_idx:]
        test_prices = prices[split_idx:]
        
        backtester = Backtester(initial_capital=10000)
        vgp_engine = VGPEngine()
        # Use generate_signals to convert continuous output to discrete buy/sell/hold signals
        # Use a more sensitive threshold to generate more trades
        signals = vgp_engine.generate_signals(generalized_model, test_features, threshold=0.1)
        portfolio = backtester.backtest(signals, test_prices)
        
        profit_pct = ((portfolio.equity_curve[-1] - portfolio.initial_capital) / portfolio.initial_capital) * 100
        
        generalized_results[stock_symbol] = {
            'profit_pct': profit_pct,
            'trades': portfolio.num_trades,
            'win_rate': portfolio.win_rate * 100,
            'final_equity': portfolio.equity_curve[-1]
        }
        
        gen_total_profit += profit_pct
        if profit_pct > 0:
            gen_profitable_count += 1
    
    # Sort generalized results
    gen_sorted = sorted(generalized_results.items(), key=lambda x: x[1]['profit_pct'], reverse=True)
    
    print("Generalized Model Performance:")
    for i, (symbol, results) in enumerate(gen_sorted):
        profit = results['profit_pct']
        print(f"{i+1:2d}. {symbol}: {profit:+7.2f}% | {results['trades']:3d} trades | {results['win_rate']:5.1f}% wins")
    
    gen_avg_profit = gen_total_profit / len(generalized_results) if generalized_results else 0
    
    print(f"\\n🏆 FINAL RESULTS COMPARISON")
    print("=" * 60)
    print(f"Individual Models Average: {avg_profit:+.2f}%")
    print(f"Generalized Model Average: {gen_avg_profit:+.2f}%")
    print(f"Performance Difference: {gen_avg_profit - avg_profit:+.2f}%")
    print(f"Generalized Profitable: {gen_profitable_count}/{len(generalized_results)} ({gen_profitable_count/len(generalized_results)*100:.1f}%)")
    
    # Store all results in the generalized model
    generalized_model.individual_results = stock_results
    generalized_model.generalized_results = generalized_results
    generalized_model.avg_individual_profit = avg_profit
    generalized_model.avg_generalized_profit = gen_avg_profit
    
    print(f"\\n✅ Training completed! Generalized model ready for deployment.")
    
    return generalized_model

if __name__ == "__main__":
    print("Individual Stock VGP Training System")
    print("Loading data and starting individual model training...")
    
    # Load data (reuse existing data loading)
    from python_vgp import MultiStockVGP
    
    vgp_system = MultiStockVGP()
    data_dict = vgp_system.load_data("data")
    
    if data_dict:
        print(f"Loaded {len(data_dict)} stocks: {list(data_dict.keys())}")
        
        # Train individual models and create generalized model
        best_model = train_individual_stock_models(data_dict)
        
        if best_model:
            print("\\nTraining successful! Model contains:")
            print(f"  - Individual model results for {len(best_model.individual_results)} stocks")
            print(f"  - Generalized model performance on {len(best_model.generalized_results)} stocks")
            print(f"  - Average generalized profit: {best_model.avg_generalized_profit:+.2f}%")
        else:
            print("\\nTraining failed!")
    else:
        print("No data loaded - please ensure CSV files are in 'data' directory")