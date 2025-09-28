#!/usr/bin/env python3
"""
Debug the temp file issue in simulation
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import os

def test_temp_file_consistency():
    """Test if temp file creation is causing inconsistency"""

    print("🐛 DEBUGGING TEMP FILE ISSUE")
    print("=" * 40)

    # Get same data
    ticker = yf.Ticker('TSLA')
    df = ticker.history(start='2025-09-20', end='2025-09-26')
    df = df.reset_index()
    df['Symbol'] = 'TSLA'

    print(f"Original data shape: {df.shape}")
    print(f"First price: {df.iloc[0]['Close']:.10f}")

    # Test what happens when we save/load the same data
    for run in range(2):
        print(f"\nRun {run + 1}:")

        # Use different temp file names to avoid conflicts
        temp_path = f"temp_debug_run_{run}_{datetime.now().strftime('%H%M%S%f')}.csv"

        # Save the SAME data
        df.to_csv(temp_path, index=False)

        # Load it back
        df_loaded = pd.read_csv(temp_path)

        print(f"  Loaded data shape: {df_loaded.shape}")
        print(f"  First price: {df_loaded.iloc[0]['Close']:.10f}")

        # Check if they're identical
        if df.equals(df_loaded):
            print("  ✅ Data identical after save/load")
        else:
            print("  ❌ Data changed during save/load!")

            # Find differences
            for col in df.columns:
                if col in df_loaded.columns:
                    orig_vals = df[col].values
                    loaded_vals = df_loaded[col].values

                    if not np.array_equal(orig_vals, loaded_vals, equal_nan=True):
                        print(f"    Difference in column: {col}")
                        print(f"    Original sample: {orig_vals[0] if len(orig_vals) > 0 else 'empty'}")
                        print(f"    Loaded sample: {loaded_vals[0] if len(loaded_vals) > 0 else 'empty'}")

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_simulation_data_processing():
    """Test if the data processing in simulation is consistent"""

    print(f"\n📊 TESTING SIMULATION DATA PROCESSING")
    print("=" * 40)

    from neat_trading_model import NEATTradingModel

    # Create identical test data
    test_data = pd.DataFrame({
        'Date': pd.date_range('2025-09-20', periods=5, freq='D'),
        'Open': [440.0, 441.0, 442.0, 443.0, 444.0],
        'High': [445.0, 446.0, 447.0, 448.0, 449.0],
        'Low': [435.0, 436.0, 437.0, 438.0, 439.0],
        'Close': [440.4, 441.4, 442.4, 443.4, 444.4],
        'Volume': [25000000] * 5,
        'Symbol': ['TSLA'] * 5
    })

    for run in range(2):
        print(f"\nRun {run + 1}:")

        # Use unique temp file name
        temp_path = f"temp_sim_test_{run}_{datetime.now().strftime('%H%M%S%f')}.csv"
        test_data.to_csv(temp_path, index=False)

        try:
            model = NEATTradingModel("neat_config.txt")
            model.load_model("vgp_neat_AGGRESSIVE_trained.pkl")

            # Process data through full pipeline
            df_processed = model.load_market_data(temp_path)
            df_processed = model.enrich_with_sentiment(df_processed)
            df_processed = model.add_vgp_signals(df_processed)
            features = model.prepare_features(df_processed)

            if len(features) > 0:
                # Test with last row features
                latest_features = features[-1]
                prediction = model.predict(latest_features)

                # Get confidence
                import neat
                net = neat.nn.FeedForwardNetwork.create(model.best_genome, model.config)
                output = net.activate(latest_features)
                confidence = max(output) if len(output) == 3 else 0.5

                print(f"  Features shape: {latest_features.shape}")
                print(f"  Features sum: {np.sum(latest_features):.10f}")
                print(f"  Prediction: {prediction}")
                print(f"  Confidence: {confidence:.10f}")
                print(f"  Raw output: {[f'{x:.8f}' for x in output]}")

        except Exception as e:
            print(f"  Error: {e}")

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    test_temp_file_consistency()
    test_simulation_data_processing()