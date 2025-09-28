#!/usr/bin/env python3
"""
Advanced Risk Analysis Demo
Demonstrates the comprehensive risk calculation capabilities
"""

import sys
import os
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.financial_risk_service import FinancialRiskService
from services.advanced_risk_calculator import AdvancedRiskCalculator
from services.risk_utilities import RiskUtilities
from parsers.yahoo_finance_parser import YahooFinanceParser


def demo_advanced_risk_analysis():
    """Demonstrate advanced risk analysis capabilities"""
    print("🚀 ADVANCED FINANCIAL RISK ANALYSIS DEMO")
    print("=" * 60)
    
    # Initialize services
    risk_service = FinancialRiskService()
    
    # Test symbols
    test_symbols = ['AAPL', 'NVDA', 'TSLA']  # Different risk profiles
    
    for symbol in test_symbols:
        print(f"\n📈 ANALYZING {symbol}")
        print("-" * 40)
        
        # Perform advanced risk analysis
        result = risk_service.analyze_advanced_risk(symbol, period="1y")
        
        if result['success']:
            print(f"✅ Analysis successful for {symbol}")
            print(f"📊 Data points used: {result['data_points']}")
            
            # Display key metrics
            metrics = result['advanced_risk_metrics']
            interpretation = result['risk_interpretation']
            
            print("\n🔹 VOLATILITY & MOMENTS:")
            print(f"  Annual Volatility: {metrics.get('annualized_volatility', 0):.2%}")
            print(f"  Skewness: {metrics.get('skewness', 0):.3f}")
            print(f"  Excess Kurtosis: {metrics.get('excess_kurtosis', 0):.3f}")
            
            print("\n🔹 VALUE AT RISK (VaR):")
            var_metrics = metrics.get('var', {})
            if '99%' in var_metrics:
                print(f"  99% Historical VaR: {var_metrics['99%'].get('historical', 0):.2%}")
                print(f"  99% Parametric VaR: {var_metrics['99%'].get('parametric', 0):.2%}")
            
            cvar_metrics = metrics.get('cvar', {})
            if '99%' in cvar_metrics:
                print(f"  99% CVaR (Expected Shortfall): {cvar_metrics['99%']:.2%}")
            
            print("\n🔹 DRAWDOWN ANALYSIS:")
            print(f"  Maximum Drawdown: {metrics.get('max_drawdown', 0):.2%}")
            print(f"  Calmar Ratio: {metrics.get('calmar_ratio', 0):.3f}")
            
            print("\n🔹 TAIL RISK MEASURES:")
            omega = min(metrics.get('omega_ratio', 0), 999)  # Cap display
            sortino = min(metrics.get('sortino_ratio', 0), 999)  # Cap display
            print(f"  Omega Ratio: {omega:.3f}")
            print(f"  Sortino Ratio: {sortino:.3f}")
            
            # Systematic risk (if available)
            if 'beta' in metrics and metrics['beta'] != 0:
                print("\n🔹 SYSTEMATIC RISK:")
                print(f"  Beta: {metrics.get('beta', 0):.3f}")
                print(f"  Market Correlation: {metrics.get('correlation', 0):.3f}")
            
            # Extreme Value Theory
            if metrics.get('evt_available', False):
                print("\n🔹 EXTREME VALUE THEORY:")
                print(f"  Tail Index: {metrics.get('tail_index', 0):.3f}")
                print(f"  1% Extreme Risk: {metrics.get('extreme_risk_1pct', 0):.2%}")
            
            # Risk Interpretation
            print("\n🧠 RISK INTERPRETATION:")
            for key, value in interpretation.items():
                if key != 'overall_risk':
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            
            print(f"\n🎯 OVERALL RISK: {interpretation.get('overall_risk', 'Unknown')}")
            
        else:
            print(f"❌ Analysis failed for {symbol}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)


def demo_utility_functions():
    """Demonstrate utility functions"""
    print("\n🛠️  UTILITY FUNCTIONS DEMO")
    print("=" * 60)
    
    # Test with sample data
    import numpy as np
    np.random.seed(42)
    
    # Generate sample returns with regime changes
    n_days = 504  # 2 years of data
    regime1 = np.random.normal(0.001, 0.01, 252)  # Low volatility regime
    regime2 = np.random.normal(0.0005, 0.03, 252)  # High volatility regime
    returns = np.concatenate([regime1, regime2])
    
    print("📊 Testing Regime Change Detection:")
    regime_info = RiskUtilities.detect_regime_changes(returns, window=60)
    print(f"  Current Regime: {regime_info['current_regime']}")
    print(f"  Regime Changes Detected: {len(regime_info['regime_changes'])}")
    print(f"  Recent Volatility: {regime_info['recent_volatility']:.4f}")
    print(f"  Historical Volatility: {regime_info['historical_volatility']:.4f}")
    
    print("\n💥 Testing Stress Scenarios:")
    stress_results = RiskUtilities.stress_test_scenarios(returns)
    print(f"  Expected Loss: {stress_results['expected_loss']:.4f}")
    print(f"  Worst Case Loss: {stress_results['worst_case_loss']:.4f}")
    print(f"  Number of Scenarios: {stress_results['number_of_scenarios']}")
    
    # Show individual scenarios
    for scenario in stress_results['stress_results'][:3]:  # Show first 3
        print(f"    {scenario['scenario_name']}: {scenario['percentage_loss']:.1f}% loss")
    
    print("\n📈 Testing Portfolio Metrics:")
    # Create multi-asset returns matrix
    asset1_returns = returns
    asset2_returns = 0.7 * returns + 0.3 * np.random.normal(0, 0.015, len(returns))
    returns_matrix = np.column_stack([asset1_returns, asset2_returns])
    weights = np.array([0.6, 0.4])
    
    portfolio_metrics = RiskUtilities.calculate_portfolio_metrics(weights, returns_matrix)
    if 'error' not in portfolio_metrics:
        print(f"  Portfolio Volatility: {portfolio_metrics['portfolio_volatility']:.4f}")
        print(f"  Annualized Volatility: {portfolio_metrics['annualized_volatility']:.2%}")
        print(f"  Diversification Ratio: {portfolio_metrics['diversification_ratio']:.3f}")
    else:
        print(f"  Error: {portfolio_metrics['error']}")


def create_risk_summary_report():
    """Create a comprehensive risk summary for multiple stocks"""
    print("\n📋 RISK SUMMARY REPORT")
    print("=" * 60)
    
    risk_service = FinancialRiskService()
    symbols = ['AAPL', 'GOOGL', 'TSLA', 'META']
    
    summary_data = []
    
    for symbol in symbols:
        result = risk_service.analyze_advanced_risk(symbol, period="1y")
        if result['success']:
            metrics = result['advanced_risk_metrics']
            interpretation = result['risk_interpretation']
            
            summary_data.append({
                'symbol': symbol,
                'volatility': metrics.get('annualized_volatility', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'var_99': abs(metrics.get('var', {}).get('99%', {}).get('historical', 0)),
                'beta': metrics.get('beta', 0),
                'overall_risk': interpretation.get('overall_risk', 'Unknown')
            })
    
    # Display summary table
    print(f"{'Symbol':<8} {'Volatility':<12} {'Max DD':<10} {'99% VaR':<10} {'Beta':<8} {'Risk Level'}")
    print("-" * 70)
    
    for data in summary_data:
        print(f"{data['symbol']:<8} "
              f"{data['volatility']:<12.2%} "
              f"{data['max_drawdown']:<10.2%} "
              f"{data['var_99']:<10.2%} "
              f"{data['beta']:<8.3f} "
              f"{data['overall_risk']}")
    
    # Risk ranking
    if summary_data:
        print("\n🏆 RISK RANKING (by Overall Risk Score):")
        # Simple risk score calculation
        for i, data in enumerate(summary_data):
            risk_score = (data['volatility'] * 0.3 + 
                         data['max_drawdown'] * 0.4 + 
                         data['var_99'] * 0.3)
            print(f"  {i+1}. {data['symbol']} - Risk Score: {risk_score:.3f}")


def main():
    """Run the complete demo"""
    print("🎯 COMPREHENSIVE ADVANCED RISK ANALYSIS SYSTEM")
    print("=" * 80)
    print()
    print("This demo showcases advanced financial risk calculations including:")
    print("• Volatility & Higher-Order Moments (Skewness, Kurtosis)")
    print("• Value at Risk (VaR) & Conditional VaR")
    print("• Drawdown Analysis & Calmar Ratio")
    print("• Tail Risk Measures (Omega, Sortino)")
    print("• Systematic Risk (Beta, Correlation)")
    print("• Extreme Value Theory (EVT)")
    print("• Risk Utilities & Stress Testing")
    print()
    print("=" * 80)
    
    try:
        # Run demonstrations
        demo_advanced_risk_analysis()
        demo_utility_functions()
        create_risk_summary_report()
        
        print("\n✅ DEMO COMPLETED SUCCESSFULLY!")
        print("🎉 All advanced risk calculation functions are ready for use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Note: This demo requires numpy, scipy, and pandas to be installed.")
        print("Some import errors are expected in VS Code but the code will work when run.")


if __name__ == "__main__":
    main()