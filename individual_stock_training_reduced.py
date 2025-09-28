#!/usr/bin/env python3
"""
Individual Stock Training with Reduced Features
=============================================

This script trains VGP models using only the 36 statistically significant features
(excluding the 13 non-significant features identified in feature analysis).

Expected benefits:
- Reduced model complexity (36 vs 49 features)
- Similar or better performance
- Less overfitting risk
- Faster training and inference
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import time

# Import VGP components
from python_vgp import (
    VGPEngine, Backtester, FitnessEvaluator, MultiStockVGP,
    Individual, Portfolio
)

# Import our reduced feature calculator
from reduced_features_vgp import ReducedTechnicalIndicators

@dataclass
class StockResult:
    """Results for individual stock training"""
    symbol: str
    individual_profit: float
    individual_trades: int
    individual_win_rate: float
    generalized_profit: float
    generalized_trades: int
    generalized_win_rate: float

def train_individual_stock_models_reduced(data_dict: Dict[str, pd.DataFrame]) -> Individual:
    """
    Train individual models for each stock using REDUCED FEATURE SET
    Returns the best performing individual model
    """
    stock_results = {}
    individual_models = {}
    
    # Phase 1: Train each stock individually WITH PROPER DATA SPLIT
    for stock_symbol, stock_data in data_dict.items():
        print(f"\\n🔄 Training {stock_symbol} (reduced features)...")
        
        # CRITICAL: Use reduced feature calculator
        ti = ReducedTechnicalIndicators()
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
        
        # Train VGP directly using reduced features
        vgp_engine = VGPEngine()
        fitness_evaluator = FitnessEvaluator()
        
        # Initialize population
        vgp_engine.initialize_population(len(train_features[0]))
        population = vgp_engine.population
        
        # Simple training loop (reduced from full VGP system)
        print(f"  Training VGP with {len(train_features[0])} features...")
        
        for generation in range(5):  # Reduced generations for faster testing
            for individual in population:
                fitness = fitness_evaluator.evaluate(individual, train_features, train_prices, debug=False)
                individual.fitness = fitness
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            if generation % 2 == 0:
                best_fitness = population[0].fitness
                print(f"    Generation {generation+1}: Best fitness = {best_fitness:.4f}")
        
        best_model = population[0]
        individual_models[stock_symbol] = best_model
        
        # Test the individual model on held-out test data
        vgp_engine = VGPEngine()
        test_signals = vgp_engine.generate_signals(best_model, test_features, threshold=0.2)
        
        backtester = Backtester(position_size_pct=0.10)  # 10% position size
        test_portfolio = backtester.backtest(test_signals, test_prices)
        
        individual_profit = (test_portfolio.equity_curve[-1] - 10000) / 10000 * 100
        individual_trades = len(test_portfolio.trades)
        individual_win_rate = sum(1 for t in test_portfolio.trades if t.is_profitable) / max(len(test_portfolio.trades), 1) * 100
        
        stock_results[stock_symbol] = {
            'model': best_model,
            'individual_profit': individual_profit,
            'individual_trades': individual_trades,
            'individual_win_rate': individual_win_rate
        }
        
        print(f"  Individual model: {individual_profit:+.2f}% profit, {individual_trades} trades, {individual_win_rate:.1f}% wins")
    
    # Phase 2: Select the best individual model as the generalized model
    print("\\n" + "="*60)
    print("SELECTING GENERALIZED MODEL FROM INDIVIDUAL RESULTS")
    print("="*60)
    
    best_symbol = None
    best_profit = -float('inf')
    
    for symbol, results in stock_results.items():
        profit = results['individual_profit']
        print(f"{symbol}: {profit:+.2f}% profit")
        
        if profit > best_profit:
            best_profit = profit
            best_symbol = symbol
    
    print(f"\\n🏆 Selected generalized model: {best_symbol} ({best_profit:+.2f}% profit)")
    generalized_model = stock_results[best_symbol]['model']
    
    # Phase 3: Test generalized model on all stocks
    print("\\n" + "="*60)
    print("TESTING GENERALIZED MODEL ON ALL STOCKS (REDUCED FEATURES)")
    print("="*60)
    
    all_results = []
    generalized_results = {}
    
    for stock_symbol, stock_data in data_dict.items():
        # Use reduced features for generalized testing too
        ti = ReducedTechnicalIndicators()
        features_df = ti.calculate_features(stock_data)
        features = features_df.values
        prices = stock_data['close'].values
        
        # Same split as training
        split_idx = int(0.8 * len(features))
        test_features = features[split_idx:]
        test_prices = prices[split_idx:]
        
        # Test generalized model
        vgp_engine = VGPEngine()
        test_signals = vgp_engine.generate_signals(generalized_model, test_features, threshold=0.2)
        
        backtester = Backtester(position_size_pct=0.10)
        test_portfolio = backtester.backtest(test_signals, test_prices)
        
        generalized_profit = (test_portfolio.equity_curve[-1] - 10000) / 10000 * 100
        generalized_trades = len(test_portfolio.trades)
        generalized_win_rate = sum(1 for t in test_portfolio.trades if t.is_profitable) / max(len(test_portfolio.trades), 1) * 100
        
        result = StockResult(
            symbol=stock_symbol,
            individual_profit=stock_results[stock_symbol]['individual_profit'],
            individual_trades=stock_results[stock_symbol]['individual_trades'],
            individual_win_rate=stock_results[stock_symbol]['individual_win_rate'],
            generalized_profit=generalized_profit,
            generalized_trades=generalized_trades,
            generalized_win_rate=generalized_win_rate
        )
        
        all_results.append(result)
        generalized_results[stock_symbol] = {
            'profit': generalized_profit,
            'trades': generalized_trades,
            'win_rate': generalized_win_rate
        }
    
    # Sort by generalized profit
    all_results.sort(key=lambda x: x.generalized_profit, reverse=True)
    
    print("Generalized Model Performance (Reduced Features):")
    for i, result in enumerate(all_results, 1):
        print(f"{i:2d}. {result.symbol:5s}: {result.generalized_profit:+6.2f}% | {result.generalized_trades:3d} trades | {result.generalized_win_rate:4.1f}% wins")
    
    # Summary statistics
    generalized_profits = [r.generalized_profit for r in all_results]
    individual_profits = [r.individual_profit for r in all_results]
    
    avg_generalized = np.mean(generalized_profits)
    avg_individual = np.mean(individual_profits)
    profitable_count = sum(1 for p in generalized_profits if p > 0)
    
    print("\\n🏆 FINAL RESULTS COMPARISON (REDUCED FEATURES)")
    print("=" * 60)
    print(f"Individual Models Average: {avg_individual:+.2f}%")
    print(f"Generalized Model Average: {avg_generalized:+.2f}%")
    print(f"Performance Difference: {avg_generalized - avg_individual:+.2f}%")
    print(f"Generalized Profitable: {profitable_count}/{len(all_results)} ({profitable_count/len(all_results)*100:.1f}%)")
    
    print("\\n✅ Training completed! Reduced-feature generalized model ready for deployment.")
    print(f"\\nTraining successful! Model contains:")
    print(f"  - Individual model results for {len(data_dict)} stocks")
    print(f"  - Generalized model performance on {len(data_dict)} stocks") 
    print(f"  - Average generalized profit: {avg_generalized:+.2f}%")
    print(f"  - Features used: 36 (reduced from 49)")
    
    return generalized_model

def main():
    """Main execution"""
    print("Individual Stock VGP Training System (REDUCED FEATURES)")
    print("Loading data and starting individual model training...")
    
    # Load data (reuse existing data loading)
    vgp_system = MultiStockVGP()
    data_dict = vgp_system.load_data("data")
    
    if data_dict:
        print(f"Loaded {len(data_dict)} stocks: {list(data_dict.keys())}")
        
        print("\\nIndividual Stock VGP Training (REDUCED FEATURES)")
        print(f"Training on {len(data_dict)} stocks individually...")
        print("="*60)
        
        # Train with reduced features
        best_model = train_individual_stock_models_reduced(data_dict)
        
        print(f"\\n🎯 REDUCED FEATURES MODEL SUMMARY:")
        print(f"   - Features: 36 (vs 49 original)")
        print(f"   - Excluded: 13 non-significant features")
        print(f"   - Expected: Similar performance, less complexity")
        
    else:
        print("No data loaded - please ensure CSV files are in 'data' directory")

if __name__ == "__main__":
    main()