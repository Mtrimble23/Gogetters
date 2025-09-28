#!/usr/bin/env python3
"""
Test if rolling windows cause non-determinism
"""

import pandas as pd
import numpy as np

def test_rolling_determinism():
    """Test if rolling windows give different results with different data lengths"""

    print("🎯 TESTING ROLLING WINDOW DETERMINISM")
    print("=" * 50)

    # Create test data
    prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
    volumes = [1000000] * 11

    # Test 1: Same data, same length
    print("Test 1: Same data length")
    for run in range(2):
        df = pd.DataFrame({'Close': prices, 'Volume': volumes})
        volume_ma = df['Volume'].rolling(5, min_periods=1).mean()
        print(f"  Run {run+1}: Last rolling mean = {volume_ma.iloc[-1]:.6f}")

    # Test 2: Different data lengths (simulating day-by-day processing)
    print("\nTest 2: Different data lengths (the problem!)")

    # Simulate day 8 vs day 9 processing
    for day, length in [(8, 9), (9, 10)]:
        df = pd.DataFrame({'Close': prices[:length], 'Volume': volumes[:length]})
        volume_ma = df['Volume'].rolling(5, min_periods=1).mean()
        print(f"  Day {day}: Rolling mean at day 8 = {volume_ma.iloc[7]:.6f}")

    # Test 3: What happens with different rolling window positions
    print("\nTest 3: Same value at different positions")

    # Value at position 8 when we have 9 vs 10 total points
    df1 = pd.DataFrame({'Close': prices[:9], 'Volume': volumes[:9]})
    df2 = pd.DataFrame({'Close': prices[:10], 'Volume': volumes[:10]})

    volume_ma1 = df1['Volume'].rolling(5, min_periods=1).mean()
    volume_ma2 = df2['Volume'].rolling(5, min_periods=1).mean()

    print(f"  Position 8 with 9 total points: {volume_ma1.iloc[8]:.6f}")
    print(f"  Position 8 with 10 total points: {volume_ma2.iloc[8]:.6f}")

    if abs(volume_ma1.iloc[8] - volume_ma2.iloc[8]) > 1e-10:
        print("  ❌ DIFFERENT! This is the source of non-determinism!")
    else:
        print("  ✅ Same value")

if __name__ == "__main__":
    test_rolling_determinism()