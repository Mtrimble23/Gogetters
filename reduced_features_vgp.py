"""
Reduced Feature VGP System
==========================

This is a modified version of the VGP system that excludes the 13 statistically 
non-significant features (p > 0.05) identified in the feature analysis:

Excluded features:
1. macd_histogram (p=0.761)
2. gap (p=0.728)
3. rsi_21 (p=0.564)
4. macd (p=0.516)
5. ema_50_ratio (p=0.438)
6. macd_signal (p=0.434)
7. momentum_10 (p=0.374)
8. volume_ratio (p=0.271)
9. sma_20_ratio (p=0.145)
10. stoch_d_14 (p=0.140)
11. rsi_7 (p=0.140)
12. price_range (p=0.106)
13. sma_200_ratio (p=0.082)

This should reduce model complexity from 49 to 36 features while maintaining performance.
"""

import pandas as pd
from typing import Tuple
from python_vgp import TechnicalIndicators as BaseTechnicalIndicators

class ReducedTechnicalIndicators(BaseTechnicalIndicators):
    """Technical indicators class with non-significant features removed"""
    
    # List of features to exclude (p > 0.05)
    EXCLUDED_FEATURES = [
        'macd_histogram', 'gap', 'rsi_21', 'macd', 'ema_50_ratio', 
        'macd_signal', 'momentum_10', 'volume_ratio', 'sma_20_ratio',
        'stoch_d_14', 'rsi_7', 'price_range', 'sma_200_ratio'
    ]
    
    @staticmethod
    def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate only the 36 statistically significant technical indicators"""
        features = pd.DataFrame(index=df.index)
        
        # Basic price features (keeping significant ones only)
        features['close'] = df['close']
        features['open'] = df['open'] 
        features['high'] = df['high']
        features['low'] = df['low']
        features['volume'] = df['volume']
        
        # Price derivatives (excluding 'gap' and 'price_range')
        features['price_change'] = df['close'].pct_change()
        # Excluded: gap, price_range
        
        # Moving Averages (5 SMAs) - excluding ratios for sma_20 and sma_200
        for window in [5, 10, 20, 50, 200]:
            features[f'sma_{window}'] = ReducedTechnicalIndicators.sma(df['close'], window)
            # Include ratios except for sma_20_ratio and sma_200_ratio
            if window not in [20, 200]:
                features[f'sma_{window}_ratio'] = df['close'] / features[f'sma_{window}']
        
        # Exponential Moving Averages (5 EMAs) - excluding ema_50_ratio
        for window in [8, 12, 21, 26, 50]:
            features[f'ema_{window}'] = ReducedTechnicalIndicators.ema(df['close'], window)
            # Include ratios except for ema_50_ratio
            if window != 50:
                features[f'ema_{window}_ratio'] = df['close'] / features[f'ema_{window}']
        
        # RSI variations (excluding rsi_7 and rsi_21, keeping rsi_14)
        features['rsi_14'] = ReducedTechnicalIndicators.rsi(df['close'], 14)
        # Excluded: rsi_7, rsi_21
        
        # MACD components (EXCLUDED ALL - macd, macd_signal, macd_histogram)
        # Excluded: macd, macd_signal, macd_histogram
        
        # Bollinger Bands (2 sets) - keeping all
        for window, std_dev in [(20, 2.0), (10, 1.5)]:
            bb_upper, bb_middle, bb_lower = ReducedTechnicalIndicators.bollinger_bands(
                df['close'], window, std_dev)
            features[f'bb_upper_{window}'] = bb_upper
            features[f'bb_lower_{window}'] = bb_lower
            features[f'bb_position_{window}'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
        
        # Stochastic (excluding stoch_d_14, keeping others)
        for k_window, d_window in [(14, 3), (9, 3)]:
            stoch_k, stoch_d = ReducedTechnicalIndicators.stochastic(
                df['high'], df['low'], df['close'], k_window, d_window)
            features[f'stoch_k_{k_window}'] = stoch_k
            # Exclude stoch_d_14 but keep stoch_d_9
            if k_window != 14:  # This excludes stoch_d_14
                features[f'stoch_d_{k_window}'] = stoch_d
        
        # Volume indicators (excluding volume_ratio)
        features['volume_sma'] = ReducedTechnicalIndicators.sma(df['volume'], 20)
        # Excluded: volume_ratio
        
        # Momentum indicators (excluding momentum_10, keeping momentum_5)
        features['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        # Excluded: momentum_10
        
        # Volatility (keeping)
        features['volatility'] = df['close'].rolling(20).std()
        
        # Fill NaN values - CRITICAL: Use forward fill only (no look-ahead bias)
        features = features.fillna(method='ffill').fillna(0)
        
        # Verify we excluded the right features
        excluded_found = [col for col in features.columns if col in ReducedTechnicalIndicators.EXCLUDED_FEATURES]
        if excluded_found:
            print(f"WARNING: Found excluded features in output: {excluded_found}")
        
        print(f"Generated {len(features.columns)} technical indicators (reduced from 49)")
        print(f"Excluded {len(ReducedTechnicalIndicators.EXCLUDED_FEATURES)} non-significant features")
        
        return features

# Test the reduced feature set
if __name__ == "__main__":
    print("Testing Reduced Technical Indicators...")
    
    # Create sample data
    import numpy as np
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'close': np.random.randn(100).cumsum() + 100,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)
    
    # Test original features
    from python_vgp import TechnicalIndicators
    original_features = TechnicalIndicators.calculate_features(sample_data)
    
    # Test reduced features
    reduced_features = ReducedTechnicalIndicators.calculate_features(sample_data)
    
    print(f"\nOriginal features: {len(original_features.columns)}")
    print(f"Reduced features: {len(reduced_features.columns)}")
    print(f"Reduction: {len(original_features.columns) - len(reduced_features.columns)} features")
    
    print(f"\nExcluded features check:")
    for excluded in ReducedTechnicalIndicators.EXCLUDED_FEATURES:
        in_original = excluded in original_features.columns
        in_reduced = excluded in reduced_features.columns
        print(f"  {excluded}: Original={in_original}, Reduced={in_reduced} {'✓' if in_original and not in_reduced else '✗'}")