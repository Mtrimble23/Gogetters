#!/usr/bin/env python3
"""
Advanced Risk Calculator
Implements sophisticated risk metrics including VaR, CVaR, drawdown analysis,
higher-order moments, extreme value theory, and tail risk measures.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize_scalar
from typing import Dict, Any, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class AdvancedRiskCalculator:
    """
    Advanced risk calculation engine implementing sophisticated financial risk metrics
    """
    
    def __init__(self):
        self.confidence_levels = [0.95, 0.99, 0.999]  # Standard VaR confidence levels
        
    def calculate_returns(self, prices: np.ndarray) -> np.ndarray:
        """Calculate returns from price series"""
        if len(prices) < 2:
            return np.array([])
        return np.diff(np.log(prices))
    
    def calculate_all_risk_metrics(self, prices: np.ndarray, 
                                 market_prices: Optional[np.ndarray] = None,
                                 risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """
        Calculate all advanced risk metrics for a price series
        
        Args:
            prices: Array of historical prices
            market_prices: Optional market index prices for beta calculation
            risk_free_rate: Risk-free rate for Sharpe/Sortino calculations
        
        Returns:
            Dictionary containing all calculated risk metrics
        """
        if len(prices) < 30:  # Need sufficient data
            return self._get_default_risk_metrics()
            
        returns = self.calculate_returns(prices)
        if len(returns) == 0:
            return self._get_default_risk_metrics()
        
        results = {}
        
        # 1. Volatility & Higher-Order Moments
        volatility_metrics = self.calculate_volatility_moments(returns)
        results.update(volatility_metrics)
        
        # 2. Value at Risk (VaR) & Conditional VaR
        var_metrics = self.calculate_var_cvar(returns)
        results.update(var_metrics)
        
        # 3. Drawdown Risk
        drawdown_metrics = self.calculate_drawdown_metrics(prices, returns)
        results.update(drawdown_metrics)
        
        # 4. Tail Risk Measures
        tail_risk_metrics = self.calculate_tail_risk_measures(returns, risk_free_rate)
        results.update(tail_risk_metrics)
        
        # 5. Correlation & Systemic Risk
        if market_prices is not None and len(market_prices) == len(prices):
            market_returns = self.calculate_returns(market_prices)
            if len(market_returns) == len(returns):
                systemic_metrics = self.calculate_systemic_risk(returns, market_returns)
                results.update(systemic_metrics)
        
        # 6. Extreme Value Theory (EVT)
        evt_metrics = self.calculate_evt_metrics(returns)
        results.update(evt_metrics)
        
        return results
    
    def calculate_volatility_moments(self, returns: np.ndarray) -> Dict[str, float]:
        """
        Calculate volatility and higher-order moments
        
        Returns:
            Dictionary with volatility, skewness, and kurtosis metrics
        """
        if len(returns) == 0:
            return {'volatility': 0, 'annualized_volatility': 0, 'skewness': 0, 'kurtosis': 0, 'excess_kurtosis': 0}
        
        # Standard deviation (volatility)
        volatility = np.std(returns, ddof=1)
        annualized_volatility = volatility * np.sqrt(252)  # Assuming daily returns
        
        # Skewness - measure of asymmetry
        mean_return = np.mean(returns)
        skewness = np.mean(((returns - mean_return) / volatility) ** 3)
        
        # Kurtosis - measure of tail risk
        kurtosis = np.mean(((returns - mean_return) / volatility) ** 4)
        excess_kurtosis = kurtosis - 3  # Excess over normal distribution
        
        return {
            'volatility': float(volatility),
            'annualized_volatility': float(annualized_volatility),
            'skewness': float(skewness),
            'kurtosis': float(kurtosis),
            'excess_kurtosis': float(excess_kurtosis)
        }
    
    def calculate_var_cvar(self, returns: np.ndarray) -> Dict[str, Any]:
        """
        Calculate Value at Risk (VaR) and Conditional VaR using multiple methods
        
        Returns:
            Dictionary with VaR and CVaR at different confidence levels
        """
        if len(returns) == 0:
            return {'var': {}, 'cvar': {}}
        
        results = {'var': {}, 'cvar': {}}
        
        mean_return = np.mean(returns)
        std_return = np.std(returns, ddof=1)
        
        for confidence in self.confidence_levels:
            alpha = 1 - confidence
            
            # Parametric VaR (assumes normal distribution)
            z_score = stats.norm.ppf(alpha)
            parametric_var = mean_return + z_score * std_return
            
            # Historical Simulation VaR
            historical_var = np.percentile(returns, alpha * 100)
            
            # Conditional VaR (Expected Shortfall)
            # Average of returns worse than VaR
            worse_returns = returns[returns <= historical_var]
            if len(worse_returns) > 0:
                cvar = np.mean(worse_returns)
            else:
                cvar = historical_var
            
            results['var'][f'{int(confidence*100)}%'] = {
                'parametric': float(parametric_var),
                'historical': float(historical_var)
            }
            results['cvar'][f'{int(confidence*100)}%'] = float(cvar)
        
        return results
    
    def calculate_drawdown_metrics(self, prices: np.ndarray, returns: np.ndarray) -> Dict[str, float]:
        """
        Calculate drawdown-related risk metrics
        
        Returns:
            Dictionary with maximum drawdown, Calmar ratio, and recovery time metrics
        """
        if len(prices) < 2:
            return {'max_drawdown': 0, 'calmar_ratio': 0, 'avg_drawdown': 0, 'drawdown_duration': 0}
        
        # Calculate running maximum (peak values)
        cumulative_returns = np.cumprod(1 + returns) if len(returns) > 0 else np.ones_like(prices)
        running_max = np.maximum.accumulate(cumulative_returns)
        
        # Calculate drawdowns
        drawdowns = (cumulative_returns - running_max) / running_max
        
        # Maximum drawdown
        max_drawdown = abs(np.min(drawdowns))
        
        # Average drawdown
        negative_drawdowns = drawdowns[drawdowns < 0]
        avg_drawdown = abs(np.mean(negative_drawdowns)) if len(negative_drawdowns) > 0 else 0
        
        # Calmar ratio (annualized return / max drawdown)
        if len(returns) > 0 and max_drawdown > 0:
            annualized_return = (np.prod(1 + returns) ** (252 / len(returns))) - 1
            calmar_ratio = annualized_return / max_drawdown
        else:
            calmar_ratio = 0
        
        # Average drawdown duration (simplified)
        in_drawdown = drawdowns < -0.01  # 1% threshold
        if np.any(in_drawdown):
            drawdown_periods = np.diff(np.concatenate(([False], in_drawdown, [False])))
            starts = np.where(drawdown_periods)[0][::2]
            ends = np.where(drawdown_periods)[0][1::2]
            if len(starts) == len(ends):
                durations = ends - starts
                avg_duration = np.mean(durations) if len(durations) > 0 else 0
            else:
                avg_duration = 0
        else:
            avg_duration = 0
        
        return {
            'max_drawdown': float(max_drawdown),
            'calmar_ratio': float(calmar_ratio),
            'avg_drawdown': float(avg_drawdown),
            'drawdown_duration': float(avg_duration)
        }
    
    def calculate_tail_risk_measures(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> Dict[str, float]:
        """
        Calculate tail risk measures including Omega ratio and Sortino ratio
        
        Returns:
            Dictionary with Omega ratio, Sortino ratio, and other tail risk metrics
        """
        if len(returns) == 0:
            return {'omega_ratio': 0, 'sortino_ratio': 0, 'downside_deviation': 0}
        
        daily_rf_rate = risk_free_rate / 252
        excess_returns = returns - daily_rf_rate
        
        # Sortino Ratio - using downside deviation
        downside_returns = returns[returns < daily_rf_rate]
        if len(downside_returns) > 0:
            downside_deviation = np.std(downside_returns, ddof=1)
            sortino_ratio = np.mean(excess_returns) / downside_deviation if downside_deviation > 0 else 0
        else:
            downside_deviation = 0
            sortino_ratio = float('inf') if np.mean(excess_returns) > 0 else 0
        
        # Omega Ratio - ratio of gains to losses relative to threshold
        threshold = 0  # Using 0 as threshold
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns < threshold]
        
        if len(losses) > 0 and np.sum(losses) > 0:
            omega_ratio = np.sum(gains) / np.sum(losses) if len(gains) > 0 else 0
        else:
            omega_ratio = float('inf') if len(gains) > 0 else 1
        
        # Additional tail risk measures
        # Tail ratio (95th percentile / 5th percentile)
        p95 = np.percentile(returns, 95)
        p5 = np.percentile(returns, 5)
        tail_ratio = abs(p95 / p5) if p5 != 0 else 0
        
        return {
            'omega_ratio': float(omega_ratio if not np.isinf(omega_ratio) else 999),
            'sortino_ratio': float(sortino_ratio if not np.isinf(sortino_ratio) else 999),
            'downside_deviation': float(downside_deviation),
            'tail_ratio': float(tail_ratio)
        }
    
    def calculate_systemic_risk(self, returns: np.ndarray, market_returns: np.ndarray) -> Dict[str, float]:
        """
        Calculate systemic risk measures including Beta and correlation
        
        Returns:
            Dictionary with Beta, correlation, and systematic risk metrics
        """
        if len(returns) == 0 or len(market_returns) == 0 or len(returns) != len(market_returns):
            return {'beta': 0, 'correlation': 0, 'systematic_risk': 0, 'idiosyncratic_risk': 0}
        
        # Calculate beta
        covariance = np.cov(returns, market_returns)[0, 1]
        market_variance = np.var(market_returns, ddof=1)
        beta = covariance / market_variance if market_variance > 0 else 0
        
        # Calculate correlation
        correlation = np.corrcoef(returns, market_returns)[0, 1] if len(returns) > 1 else 0
        
        # Systematic risk (explained by market)
        total_variance = np.var(returns, ddof=1)
        systematic_variance = (correlation ** 2) * total_variance
        idiosyncratic_variance = total_variance - systematic_variance
        
        return {
            'beta': float(beta),
            'correlation': float(correlation),
            'systematic_risk': float(np.sqrt(systematic_variance)),
            'idiosyncratic_risk': float(np.sqrt(idiosyncratic_variance))
        }
    
    def calculate_evt_metrics(self, returns: np.ndarray, threshold_percentile: float = 10) -> Dict[str, Any]:
        """
        Calculate Extreme Value Theory metrics using Generalized Pareto Distribution
        
        Returns:
            Dictionary with EVT parameters and extreme risk estimates
        """
        if len(returns) < 50:  # Need sufficient data for EVT
            return {'evt_available': False, 'tail_index': 0, 'extreme_risk_1pct': 0, 'extreme_risk_0_1pct': 0}
        
        try:
            # Use negative returns for tail analysis (focus on losses)
            negative_returns = -returns[returns < 0]
            
            if len(negative_returns) < 20:
                return {'evt_available': False, 'tail_index': 0, 'extreme_risk_1pct': 0, 'extreme_risk_0_1pct': 0}
            
            # Set threshold as percentile of negative returns
            threshold = np.percentile(negative_returns, 100 - threshold_percentile)
            exceedances = negative_returns[negative_returns > threshold] - threshold
            
            if len(exceedances) < 10:
                return {'evt_available': False, 'tail_index': 0, 'extreme_risk_1pct': 0, 'extreme_risk_0_1pct': 0}
            
            # Fit Generalized Pareto Distribution
            # Using method of moments for simplicity
            mean_excess = np.mean(exceedances)
            var_excess = np.var(exceedances, ddof=1)
            
            # Estimate tail index (xi) and scale parameter (beta)
            if var_excess > 0:
                tail_index = 0.5 * ((mean_excess ** 2) / var_excess - 1)
                scale = 0.5 * mean_excess * ((mean_excess ** 2) / var_excess + 1)
            else:
                tail_index = 0
                scale = mean_excess
            
            # Calculate extreme risk probabilities
            n_exceedances = len(exceedances)
            n_total = len(negative_returns)
            
            def extreme_quantile(p):
                if tail_index != 0 and scale > 0:
                    return threshold + (scale / tail_index) * (((n_total / n_exceedances) * p) ** (-tail_index) - 1)
                else:
                    return threshold
            
            extreme_risk_1pct = extreme_quantile(0.01)
            extreme_risk_0_1pct = extreme_quantile(0.001)
            
            return {
                'evt_available': True,
                'tail_index': float(tail_index),
                'scale_parameter': float(scale),
                'threshold': float(threshold),
                'extreme_risk_1pct': float(extreme_risk_1pct),
                'extreme_risk_0_1pct': float(extreme_risk_0_1pct)
            }
            
        except Exception as e:
            return {'evt_available': False, 'error': str(e), 'tail_index': 0, 'extreme_risk_1pct': 0, 'extreme_risk_0_1pct': 0}
    
    def _get_default_risk_metrics(self) -> Dict[str, Any]:
        """Return default risk metrics when insufficient data"""
        return {
            'volatility': 0,
            'annualized_volatility': 0,
            'skewness': 0,
            'kurtosis': 0,
            'excess_kurtosis': 0,
            'var': {'95%': {'parametric': 0, 'historical': 0}, 
                   '99%': {'parametric': 0, 'historical': 0},
                   '99.9%': {'parametric': 0, 'historical': 0}},
            'cvar': {'95%': 0, '99%': 0, '99.9%': 0},
            'max_drawdown': 0,
            'calmar_ratio': 0,
            'avg_drawdown': 0,
            'drawdown_duration': 0,
            'omega_ratio': 0,
            'sortino_ratio': 0,
            'downside_deviation': 0,
            'tail_ratio': 0,
            'evt_available': False,
            'tail_index': 0,
            'extreme_risk_1pct': 0,
            'extreme_risk_0_1pct': 0
        }


def test_risk_calculator():
    """Test the advanced risk calculator with sample data"""
    print("🧪 Testing Advanced Risk Calculator")
    print("=" * 50)
    
    # Generate sample price data (geometric brownian motion)
    np.random.seed(42)
    n_days = 252
    initial_price = 100
    drift = 0.1 / 252  # 10% annual drift
    volatility = 0.2 / np.sqrt(252)  # 20% annual volatility
    
    returns = np.random.normal(drift, volatility, n_days)
    prices = initial_price * np.exp(np.cumsum(returns))
    
    # Create market data (correlated)
    market_returns = 0.7 * returns + 0.3 * np.random.normal(0, volatility, n_days)
    market_prices = initial_price * np.exp(np.cumsum(market_returns))
    
    # Calculate risk metrics
    calculator = AdvancedRiskCalculator()
    risk_metrics = calculator.calculate_all_risk_metrics(prices, market_prices)
    
    # Display results
    print(f"Volatility Metrics:")
    print(f"  Annual Volatility: {risk_metrics['annualized_volatility']:.4f}")
    print(f"  Skewness: {risk_metrics['skewness']:.4f}")
    print(f"  Excess Kurtosis: {risk_metrics['excess_kurtosis']:.4f}")
    
    print(f"\nVaR Metrics (99% confidence):")
    print(f"  Historical VaR: {risk_metrics['var']['99%']['historical']:.4f}")
    print(f"  CVaR: {risk_metrics['cvar']['99%']:.4f}")
    
    print(f"\nDrawdown Metrics:")
    print(f"  Max Drawdown: {risk_metrics['max_drawdown']:.4f}")
    print(f"  Calmar Ratio: {risk_metrics['calmar_ratio']:.4f}")
    
    print(f"\nTail Risk Metrics:")
    print(f"  Omega Ratio: {risk_metrics['omega_ratio']:.4f}")
    print(f"  Sortino Ratio: {risk_metrics['sortino_ratio']:.4f}")
    
    print(f"\nSystemic Risk Metrics:")
    print(f"  Beta: {risk_metrics['beta']:.4f}")
    print(f"  Correlation: {risk_metrics['correlation']:.4f}")
    
    if risk_metrics['evt_available']:
        print(f"\nExtreme Value Theory:")
        print(f"  Tail Index: {risk_metrics['tail_index']:.4f}")
        print(f"  1% Extreme Risk: {risk_metrics['extreme_risk_1pct']:.4f}")


if __name__ == "__main__":
    test_risk_calculator()