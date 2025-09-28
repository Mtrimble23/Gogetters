#!/usr/bin/env python3
"""
Complete Risk Analysis Demo with ML Integration
Shows how ALL advanced risk equations feed into ML model predictions
"""

import sys
import os
from typing import Dict, Any
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.financial_risk_service import FinancialRiskService


def print_separator(title: str, length: int = 80):
    """Print a formatted separator with title"""
    print("\n" + "=" * length)
    print(f" {title} ".center(length))
    print("=" * length)


def display_advanced_equations():
    """Display all the mathematical equations being used"""
    print_separator("ADVANCED RISK EQUATIONS IMPLEMENTED", 80)
    
    equations = [
        ("🔹 Volatility & Higher-Order Moments", [
            "σ = √(1/(N-1) * Σ(ri - r̄)²) * √252  (Annualized Volatility)",
            "Skewness = (1/N) * Σ((ri - r̄)/σ)³   (Asymmetry Risk)",
            "Excess Kurtosis = (1/N) * Σ((ri - r̄)/σ)⁴ - 3  (Tail Risk)"
        ]),
        ("🔹 Value at Risk (VaR) & Conditional VaR", [
            "VaRα = μ + zα * σ  (Parametric VaR)",
            "VaRα = Quantile(returns, α)  (Historical VaR)",
            "CVaRα = E[R | R ≤ VaRα]  (Expected Shortfall)"
        ]),
        ("🔹 Drawdown Risk", [
            "MDD = max((Peak - Trough) / Peak)  (Maximum Drawdown)",
            "Calmar = Annual Return / Max Drawdown  (Risk-Adjusted Return)"
        ]),
        ("🔹 Tail Risk Measures", [
            "Ω(τ) = Σ(gains > τ) / Σ(losses < τ)  (Omega Ratio)",
            "Sortino = (Rp - Rf) / σd  (Downside-Adjusted Sharpe)"
        ]),
        ("🔹 Systemic Risk", [
            "β = Cov(Ri, Rm) / σm²  (Market Sensitivity)",
            "ρ = Cov(Ri, Rm) / (σi * σm)  (Market Correlation)"
        ]),
        ("🔹 Extreme Value Theory", [
            "GPD fitting for tail analysis",
            "P(R < r) ≈ (1 + ξ(r-u)/β)^(-1/ξ)  (Extreme Risk Estimation)"
        ])
    ]
    
    for category, formulas in equations:
        print(f"\n{category}")
        for formula in formulas:
            print(f"  • {formula}")


def analyze_stock_comprehensively(service: FinancialRiskService, symbol: str):
    """Perform comprehensive analysis showing all equation usage"""
    print_separator(f"COMPREHENSIVE RISK ANALYSIS: {symbol}", 80)
    
    # Get comprehensive analysis (uses ALL equations)
    print(f"📊 Analyzing {symbol} using ALL advanced risk equations...")
    
    start_time = time.time()
    result = service.get_comprehensive_risk_analysis(symbol)
    analysis_time = time.time() - start_time
    
    print(f"⏱️  Analysis completed in {analysis_time:.2f} seconds")
    
    # Display basic metrics
    if result['comprehensive_analysis']['basic_risk_analysis']['success']:
        basic_data = result['comprehensive_analysis']['basic_risk_analysis']['financial_data']
        
        print(f"\n📈 Basic Financial Metrics:")
        print(f"   Current Price: ${basic_data.get('current_price', 0):.2f}")
        print(f"   Price Change: {basic_data.get('price_change_percent', 0):.2f}%")
        print(f"   Market Cap: ${basic_data.get('market_cap', 0):,.0f}")
        print(f"   P/E Ratio: {basic_data.get('pe_ratio', 0):.2f}")
        print(f"   Beta: {basic_data.get('beta', 0):.3f}")
        print(f"   Debt/Equity: {basic_data.get('debt_to_equity', 0):.2f}")
    
    # Display advanced risk metrics (ALL equations)
    if result['comprehensive_analysis']['advanced_risk_analysis']['success']:
        advanced_metrics = result['comprehensive_analysis']['advanced_risk_analysis']['advanced_risk_metrics']
        
        print(f"\n🧮 Advanced Risk Metrics (Using ALL Equations):")
        
        # Volatility & Moments
        print(f"   🔸 Volatility & Moments:")
        print(f"      Annual Volatility (σ): {advanced_metrics.get('annualized_volatility', 0):.3f}")
        print(f"      Skewness: {advanced_metrics.get('skewness', 0):.3f}")
        print(f"      Excess Kurtosis: {advanced_metrics.get('excess_kurtosis', 0):.3f}")
        
        # VaR & CVaR
        print(f"   🔸 Value at Risk:")
        var_data = advanced_metrics.get('var', {})
        cvar_data = advanced_metrics.get('cvar', {})
        if '95%' in var_data:
            print(f"      95% Historical VaR: {var_data['95%'].get('historical', 0):.3f}")
            print(f"      95% Parametric VaR: {var_data['95%'].get('parametric', 0):.3f}")
        if '95%' in cvar_data:
            print(f"      95% CVaR (Expected Shortfall): {cvar_data['95%']:.3f}")
        
        # Drawdown
        print(f"   🔸 Drawdown Analysis:")
        print(f"      Maximum Drawdown: {advanced_metrics.get('max_drawdown', 0):.3f}")
        print(f"      Calmar Ratio: {advanced_metrics.get('calmar_ratio', 0):.3f}")
        
        # Tail Risk
        print(f"   🔸 Tail Risk Measures:")
        print(f"      Omega Ratio: {min(advanced_metrics.get('omega_ratio', 0), 99):.3f}")
        print(f"      Sortino Ratio: {min(advanced_metrics.get('sortino_ratio', 0), 99):.3f}")
        
        # Systemic Risk
        if advanced_metrics.get('beta', 0) != 0:
            print(f"   🔸 Systemic Risk:")
            print(f"      Beta (Market Sensitivity): {advanced_metrics.get('beta', 0):.3f}")
            print(f"      Market Correlation: {advanced_metrics.get('correlation', 0):.3f}")
        
        # EVT
        if advanced_metrics.get('evt_available', False):
            print(f"   🔸 Extreme Value Theory:")
            print(f"      Tail Index: {advanced_metrics.get('tail_index', 0):.3f}")
            print(f"      1% Extreme Risk: {advanced_metrics.get('extreme_risk_1pct', 0):.3f}")
    
    # Display ML prediction (uses ALL equations as features)
    ml_result = result['comprehensive_analysis']['ml_risk_prediction']
    if ml_result and ml_result['success']:
        print(f"\n🤖 ML Risk Prediction (Using ALL {ml_result.get('equations_used', 0)} Equations):")
        print(f"   Risk Category: {ml_result['risk_category']}")
        print(f"   High Risk Probability: {ml_result['confidence']['high_risk_probability']:.1%}")
        print(f"   Recommendation: {ml_result['recommendation']}")
        print(f"   Confidence Level: {ml_result['confidence']['confidence_level']}")
        
        print(f"\n   🔧 Top Risk Factors (From ML Model):")
        for i, factor in enumerate(ml_result['top_risk_factors'][:5]):
            direction_icon = "🔴" if factor['direction'] == 'increases risk' else "🟢"
            print(f"      {i+1}. {direction_icon} {factor['feature']}")
            print(f"         ({factor['equation_type']}) - {factor['direction']}")
        
        print(f"\n   📊 Advanced Metrics Used by ML Model:")
        for metric in ml_result['advanced_metrics_used'][:8]:  # Show first 8
            print(f"      ✓ {metric}")
        if len(ml_result['advanced_metrics_used']) > 8:
            print(f"      ✓ ... and {len(ml_result['advanced_metrics_used'])-8} more")
    
    else:
        print(f"\n🤖 ML Risk Prediction: Not Available")
        print(f"   💡 Train the model first by running:")
        print(f"      python src/models/simple_risk_predictor.py")
    
    # Display risk interpretation
    if result['comprehensive_analysis']['advanced_risk_analysis']['success']:
        interpretation = result['comprehensive_analysis']['advanced_risk_analysis']['risk_interpretation']
        
        print(f"\n🧠 Risk Interpretation:")
        for key, value in interpretation.items():
            if key != 'overall_risk':
                clean_key = key.replace('_', ' ').title()
                print(f"   • {clean_key}: {value}")
        
        print(f"\n🎯 Overall Risk Assessment: {interpretation.get('overall_risk', 'Unknown')}")


def compare_risk_across_stocks(service: FinancialRiskService, symbols: list):
    """Compare risk metrics across multiple stocks"""
    print_separator("RISK COMPARISON ACROSS STOCKS", 80)
    
    comparison_data = []
    
    for symbol in symbols:
        print(f"\n📊 Analyzing {symbol}...")
        result = service.get_comprehensive_risk_analysis(symbol)
        
        if (result['comprehensive_analysis']['advanced_risk_analysis']['success'] and
            result['comprehensive_analysis']['ml_risk_prediction'] and
            result['comprehensive_analysis']['ml_risk_prediction']['success']):
            
            advanced_metrics = result['comprehensive_analysis']['advanced_risk_analysis']['advanced_risk_metrics']
            ml_result = result['comprehensive_analysis']['ml_risk_prediction']
            
            comparison_data.append({
                'symbol': symbol,
                'volatility': advanced_metrics.get('annualized_volatility', 0),
                'max_drawdown': advanced_metrics.get('max_drawdown', 0),
                'var_95': abs(advanced_metrics.get('var', {}).get('95%', {}).get('historical', 0)),
                'skewness': advanced_metrics.get('skewness', 0),
                'ml_risk_prob': ml_result['confidence']['high_risk_probability'],
                'ml_category': ml_result['risk_category'],
                'recommendation': ml_result['recommendation']
            })
    
    if comparison_data:
        print(f"\n📋 Risk Comparison Summary:")
        print(f"{'Symbol':<8} {'Volatility':<12} {'Max DD':<10} {'95% VaR':<10} {'Skewness':<10} {'ML Risk':<12} {'Category'}")
        print("-" * 90)
        
        for data in comparison_data:
            print(f"{data['symbol']:<8} "
                  f"{data['volatility']:<12.3f} "
                  f"{data['max_drawdown']:<10.3f} "
                  f"{data['var_95']:<10.3f} "
                  f"{data['skewness']:<10.3f} "
                  f"{data['ml_risk_prob']:<12.1%} "
                  f"{data['ml_category']}")
        
        # Risk ranking
        print(f"\n🏆 Risk Rankings (by ML High Risk Probability):")
        sorted_data = sorted(comparison_data, key=lambda x: x['ml_risk_prob'], reverse=True)
        for i, data in enumerate(sorted_data):
            risk_emoji = "🔴" if data['ml_risk_prob'] > 0.7 else "🟡" if data['ml_risk_prob'] > 0.3 else "🟢"
            print(f"   {i+1}. {risk_emoji} {data['symbol']} - {data['ml_risk_prob']:.1%} risk ({data['recommendation']})")


def main():
    """Run the complete comprehensive demo"""
    print("🚀 COMPREHENSIVE RISK ANALYSIS WITH ML INTEGRATION")
    print("   Demonstrating ALL Advanced Risk Equations → ML Model")
    print("   Using Mathematical Risk Theory + Machine Learning")
    
    # Display all equations first
    display_advanced_equations()
    
    # Initialize service
    try:
        print_separator("INITIALIZING RISK ANALYSIS SYSTEM", 80)
        service = FinancialRiskService()
        print("✅ Financial Risk Service initialized")
        print("✅ Advanced Risk Calculator loaded (with ALL equations)")
        print("✅ Yahoo Finance Parser ready")
        print("✅ CBOE Volatility Calculator ready")
        
        if hasattr(service, 'ml_predictor') and service.ml_predictor:
            print("✅ ML Risk Predictor loaded")
        else:
            print("⚠️  ML Risk Predictor not trained yet")
        
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return
    
    # Analyze individual stocks comprehensively
    test_symbols = ['AAPL', 'TSLA', 'NVDA']  # Different risk profiles
    
    for symbol in test_symbols:
        try:
            analyze_stock_comprehensively(service, symbol)
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
    
    # Compare across stocks
    try:
        compare_risk_across_stocks(service, test_symbols)
    except Exception as e:
        print(f"❌ Error in comparison: {e}")
    
    # Final summary
    print_separator("IMPLEMENTATION SUMMARY", 80)
    print("🎯 What We've Built:")
    print("   ✓ 25+ Advanced Risk Equations (VaR, Skewness, Kurtosis, etc.)")
    print("   ✓ Logistic Regression ML Model using ALL equations as features")
    print("   ✓ Three-tier risk classification (Low/Moderate/High)")
    print("   ✓ Comprehensive risk interpretation")
    print("   ✓ Feature importance analysis")
    print("   ✓ Integration with existing financial service")
    
    print(f"\n💡 Next Steps:")
    print("   1. Train ML model: python src/models/simple_risk_predictor.py")
    print("   2. Integrate with your dashboard")
    print("   3. Add real-time risk monitoring")
    print("   4. Implement portfolio-level risk analysis")
    
    print(f"\n🎉 Advanced Risk Analysis System Complete!")
    print("   All mathematical risk equations are now feeding into ML predictions!")


if __name__ == "__main__":
    main()