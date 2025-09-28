#!/usr/bin/env python3
"""
Financial Risk Utilities
Helper functions for statistical calculations, data preprocessing, and risk analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, timedelta


class RiskUtilities:
    """Utility functions for risk calculations and data processing"""
    
    @staticmethod
    def clean_price_data(prices: np.ndarray, remove_outliers: bool = True) -> np.ndarray:
        """
        Clean price data by removing NaN values and optionally outliers
        
        Args:
            prices: Array of price data
            remove_outliers: Whether to remove statistical outliers
            
        Returns:
            Cleaned price array
        """
        if len(prices) == 0:
            return prices
        
        # Remove NaN values
        clean_prices = prices[~np.isnan(prices)]
        
        if not remove_outliers or len(clean_prices) < 10:
            return clean_prices
        
        # Remove outliers using IQR method
        returns = np.diff(np.log(clean_prices))
        if len(returns) == 0:
            return clean_prices
        
        q1 = np.percentile(returns, 25)
        q3 = np.percentile(returns, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Find outlier positions in returns and map back to prices
        outlier_mask = (returns < lower_bound) | (returns > upper_bound)
        # Keep the first price and remove subsequent prices corresponding to outlier returns
        keep_mask = np.concatenate(([True], ~outlier_mask))
        
        return clean_prices[keep_mask]
    
    @staticmethod
    def annualize_metric(metric_value: float, frequency: str = 'daily') -> float:
        """
        Annualize a metric based on data frequency
        
        Args:
            metric_value: The metric value to annualize
            frequency: Data frequency ('daily', 'weekly', 'monthly')
            
        Returns:
            Annualized metric value
        """
        frequency_multipliers = {
            'daily': 252,
            'weekly': 52,
            'monthly': 12
        }
        
        multiplier = frequency_multipliers.get(frequency, 252)
        return metric_value * np.sqrt(multiplier)
    
    @staticmethod
    def calculate_rolling_metric(returns: np.ndarray, window: int, metric_func) -> np.ndarray:
        """
        Calculate rolling metric over a specified window
        
        Args:
            returns: Array of returns
            window: Rolling window size
            metric_func: Function to calculate metric (e.g., np.std, np.mean)
            
        Returns:
            Array of rolling metric values
        """
        if len(returns) < window:
            return np.array([])
        
        rolling_values = []
        for i in range(window - 1, len(returns)):
            window_data = returns[i - window + 1:i + 1]
            rolling_values.append(metric_func(window_data))
        
        return np.array(rolling_values)
    
    @staticmethod
    def detect_regime_changes(returns: np.ndarray, window: int = 60) -> Dict[str, Any]:
        """
        Detect regime changes in volatility using rolling standard deviation
        
        Args:
            returns: Array of returns
            window: Window size for regime detection
            
        Returns:
            Dictionary with regime change information
        """
        if len(returns) < window * 2:
            return {'regime_changes': [], 'current_regime': 'insufficient_data'}
        
        rolling_vol = RiskUtilities.calculate_rolling_metric(returns, window, lambda x: np.std(x, ddof=1))
        
        if len(rolling_vol) == 0:
            return {'regime_changes': [], 'current_regime': 'insufficient_data'}
        
        # Identify regime changes using standard deviation of rolling volatility
        vol_changes = np.abs(np.diff(rolling_vol))
        threshold = np.percentile(vol_changes, 90)  # Top 10% of changes
        
        regime_changes = []
        change_indices = np.where(vol_changes > threshold)[0]
        
        for idx in change_indices:
            regime_changes.append({
                'index': int(idx + window),
                'volatility_change': float(vol_changes[idx]),
                'pre_regime_vol': float(rolling_vol[idx]),
                'post_regime_vol': float(rolling_vol[idx + 1])
            })
        
        # Determine current regime
        recent_vol = np.mean(rolling_vol[-10:]) if len(rolling_vol) >= 10 else rolling_vol[-1]
        historical_vol = np.mean(rolling_vol)
        
        if recent_vol > historical_vol * 1.3:
            current_regime = 'high_volatility'
        elif recent_vol < historical_vol * 0.7:
            current_regime = 'low_volatility'
        else:
            current_regime = 'normal_volatility'
        
        return {
            'regime_changes': regime_changes,
            'current_regime': current_regime,
            'recent_volatility': float(recent_vol),
            'historical_volatility': float(historical_vol)
        }
    
    @staticmethod
    def calculate_correlation_matrix(returns_matrix: np.ndarray, method: str = 'pearson') -> np.ndarray:
        """
        Calculate correlation matrix for multiple return series
        
        Args:
            returns_matrix: 2D array where each column is a return series
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Correlation matrix
        """
        if returns_matrix.ndim != 2 or returns_matrix.shape[1] < 2:
            return np.array([[]])
        
        if method == 'pearson':
            return np.corrcoef(returns_matrix, rowvar=False)
        elif method == 'spearman':
            # Simple rank-based correlation
            ranks = np.apply_along_axis(lambda x: np.argsort(np.argsort(x)), 0, returns_matrix)
            return np.corrcoef(ranks, rowvar=False)
        else:
            # Default to Pearson
            return np.corrcoef(returns_matrix, rowvar=False)
    
    @staticmethod
    def calculate_portfolio_metrics(weights: np.ndarray, returns_matrix: np.ndarray) -> Dict[str, float]:
        """
        Calculate portfolio-level risk metrics
        
        Args:
            weights: Portfolio weights (must sum to 1)
            returns_matrix: 2D array of individual asset returns
            
        Returns:
            Dictionary with portfolio risk metrics
        """
        if len(weights) != returns_matrix.shape[1] or abs(np.sum(weights) - 1.0) > 1e-6:
            return {'error': 'Invalid weights - must sum to 1 and match number of assets'}
        
        # Portfolio returns
        portfolio_returns = np.dot(returns_matrix, weights)
        
        # Portfolio metrics
        portfolio_vol = np.std(portfolio_returns, ddof=1)
        portfolio_mean = np.mean(portfolio_returns)
        
        # Diversification ratio
        individual_vols = np.array([np.std(returns_matrix[:, i], ddof=1) for i in range(returns_matrix.shape[1])])
        weighted_avg_vol = np.dot(weights, individual_vols)
        diversification_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 0
        
        return {
            'portfolio_volatility': float(portfolio_vol),
            'portfolio_return': float(portfolio_mean),
            'diversification_ratio': float(diversification_ratio),
            'annualized_volatility': float(portfolio_vol * np.sqrt(252)),
            'annualized_return': float(portfolio_mean * 252)
        }
    
    @staticmethod
    def stress_test_scenarios(returns: np.ndarray, scenarios: Optional[List[Dict[str, float]]] = None) -> Dict[str, Any]:
        """
        Apply stress test scenarios to return data
        
        Args:
            returns: Historical return data
            scenarios: List of stress scenarios with 'shock' and 'probability' keys
            
        Returns:
            Dictionary with stress test results
        """
        if scenarios is None:
            # Default stress scenarios
            scenarios = [
                {'name': '2008 Financial Crisis', 'shock': -0.15, 'probability': 0.01},
                {'name': 'COVID-19 Crash', 'shock': -0.12, 'probability': 0.02},
                {'name': 'Black Monday 1987', 'shock': -0.20, 'probability': 0.005},
                {'name': 'Moderate Correction', 'shock': -0.05, 'probability': 0.05}
            ]
        
        if len(returns) == 0:
            return {'stress_results': [], 'expected_loss': 0}
        
        current_value = 1.0  # Normalized starting value
        stress_results = []
        
        for scenario in scenarios:
            shocked_return = scenario.get('shock', 0)
            probability = scenario.get('probability', 0.01)
            name = scenario.get('name', 'Unnamed Scenario')
            
            # Apply shock to current value
            shocked_value = current_value * (1 + shocked_return)
            loss = current_value - shocked_value
            
            stress_results.append({
                'scenario_name': name,
                'shock_magnitude': float(shocked_return),
                'probability': float(probability),
                'resulting_value': float(shocked_value),
                'absolute_loss': float(loss),
                'percentage_loss': float(abs(shocked_return) * 100)
            })
        
        # Calculate expected loss
        expected_loss = sum(result['absolute_loss'] * result['probability'] for result in stress_results)
        
        return {
            'stress_results': stress_results,
            'expected_loss': float(expected_loss),
            'worst_case_loss': float(max(result['absolute_loss'] for result in stress_results)),
            'number_of_scenarios': len(scenarios)
        }
    
    @staticmethod
    def format_risk_report(risk_metrics: Dict[str, Any], symbol: str) -> str:
        """
        Format risk metrics into a readable report
        
        Args:
            risk_metrics: Dictionary of calculated risk metrics
            symbol: Stock symbol
            
        Returns:
            Formatted risk report as string
        """
        report_lines = [
            f"📊 ADVANCED RISK ANALYSIS REPORT: {symbol}",
            "=" * 50,
            "",
            "🔹 VOLATILITY & MOMENTS:",
            f"  Annual Volatility: {risk_metrics.get('annualized_volatility', 0):.2%}",
            f"  Skewness: {risk_metrics.get('skewness', 0):.3f}",
            f"  Excess Kurtosis: {risk_metrics.get('excess_kurtosis', 0):.3f}",
            "",
            "🔹 VALUE AT RISK (99% Confidence):",
            f"  Historical VaR: {risk_metrics.get('var', {}).get('99%', {}).get('historical', 0):.2%}",
            f"  Conditional VaR: {risk_metrics.get('cvar', {}).get('99%', 0):.2%}",
            "",
            "🔹 DRAWDOWN ANALYSIS:",
            f"  Maximum Drawdown: {risk_metrics.get('max_drawdown', 0):.2%}",
            f"  Calmar Ratio: {risk_metrics.get('calmar_ratio', 0):.3f}",
            "",
            "🔹 TAIL RISK MEASURES:",
            f"  Omega Ratio: {min(risk_metrics.get('omega_ratio', 0), 999):.3f}",
            f"  Sortino Ratio: {min(risk_metrics.get('sortino_ratio', 0), 999):.3f}",
            ""
        ]
        
        # Add systematic risk if available
        if 'beta' in risk_metrics and risk_metrics['beta'] != 0:
            report_lines.extend([
                "🔹 SYSTEMATIC RISK:",
                f"  Beta: {risk_metrics.get('beta', 0):.3f}",
                f"  Correlation with Market: {risk_metrics.get('correlation', 0):.3f}",
                ""
            ])
        
        # Add EVT if available
        if risk_metrics.get('evt_available', False):
            report_lines.extend([
                "🔹 EXTREME VALUE THEORY:",
                f"  Tail Index: {risk_metrics.get('tail_index', 0):.3f}",
                f"  1% Extreme Risk: {risk_metrics.get('extreme_risk_1pct', 0):.2%}",
                ""
            ])
        
        report_lines.extend([
            "=" * 50,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\n".join(report_lines)


def test_utilities():
    """Test the utility functions"""
    print("🧪 Testing Risk Utilities")
    print("=" * 40)
    
    # Generate sample data
    np.random.seed(42)
    prices = 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 252)))
    returns = np.diff(np.log(prices))
    
    # Test data cleaning
    print("Testing data cleaning...")
    clean_prices = RiskUtilities.clean_price_data(prices)
    print(f"Original prices: {len(prices)}, Clean prices: {len(clean_prices)}")
    
    # Test regime detection
    print("\nTesting regime detection...")
    regime_info = RiskUtilities.detect_regime_changes(returns)
    print(f"Current regime: {regime_info['current_regime']}")
    print(f"Regime changes detected: {len(regime_info['regime_changes'])}")
    
    # Test stress testing
    print("\nTesting stress scenarios...")
    stress_results = RiskUtilities.stress_test_scenarios(returns)
    print(f"Expected loss from stress tests: {stress_results['expected_loss']:.4f}")
    
    # Test portfolio metrics
    print("\nTesting portfolio metrics...")
    returns_matrix = np.column_stack([returns, returns * 0.8 + np.random.normal(0, 0.01, len(returns))])
    weights = np.array([0.6, 0.4])
    portfolio_metrics = RiskUtilities.calculate_portfolio_metrics(weights, returns_matrix)
    print(f"Portfolio volatility: {portfolio_metrics.get('portfolio_volatility', 0):.4f}")
    print(f"Diversification ratio: {portfolio_metrics.get('diversification_ratio', 0):.4f}")


if __name__ == "__main__":
    test_utilities()