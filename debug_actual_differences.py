#!/usr/bin/env python3
"""
Debug actual differences between simulation runs
"""

import yfinance as yf
import pandas as pd
import numpy as np
from neat_trading_model import NEATTradingModel
import uuid

def compare_two_runs():
    """Compare what's actually different between two simulation runs"""

    print("🔍 COMPARING TWO ACTUAL SIMULATION RUNS")
    print("=" * 50)

    # Get the same base data
    ticker = yf.Ticker('TSLA')
    df = ticker.history(start='2025-09-25', end='2025-09-26')
    df = df.reset_index()
    df['Symbol'] = 'TSLA'

    print(f"Base data: {len(df)} rows")
    print(f"First price: {df.iloc[0]['Close']:.10f}")

    results = []

    for run in range(2):
        print(f"\n--- RUN {run + 1} ---")

        # Use unique temp file
        temp_path = f"debug_comparison_{uuid.uuid4().hex[:8]}.csv"
        df.to_csv(temp_path, index=False, float_format='%.10f')

        try:
            model = NEATTradingModel("neat_config.txt")
            model.load_model("vgp_neat_AGGRESSIVE_trained.pkl")

            # Process through full pipeline
            df_processed = model.load_market_data(temp_path)
            df_processed = model.enrich_with_sentiment(df_processed)
            df_processed = model.add_vgp_signals(df_processed)
            features = model.prepare_features(df_processed)

            if len(features) > 0:
                latest_features = features[-1]
                prediction = model.predict(latest_features)

                # Get raw neural network output
                import neat
                net = neat.nn.FeedForwardNetwork.create(model.best_genome, model.config)
                output = net.activate(latest_features)
                confidence = max(output) if len(output) == 3 else 0.5

                # Store results for comparison
                result = {
                    'processed_rows': len(df_processed),
                    'features_shape': latest_features.shape,
                    'features_sum': np.sum(latest_features),
                    'features_first_5': latest_features[:5].tolist(),
                    'vgp_signals': [
                        getattr(df_processed.iloc[-1], 'VGP_Signal_1', 0),
                        getattr(df_processed.iloc[-1], 'VGP_Signal_2', 0),
                        getattr(df_processed.iloc[-1], 'VGP_Signal_3', 0)
                    ],
                    'sentiment': getattr(df_processed.iloc[-1], 'Sentiment_Current', 0),
                    'prediction': prediction,
                    'confidence': confidence,
                    'raw_output': list(output)
                }

                results.append(result)

                print(f"Processed rows: {result['processed_rows']}")
                print(f"Features sum: {result['features_sum']:.10f}")
                print(f"First 5 features: {[f'{x:.6f}' for x in result['features_first_5']]}")
                print(f"VGP signals: {[f'{x:.6f}' for x in result['vgp_signals']]}")
                print(f"Sentiment: {result['sentiment']:.6f}")
                print(f"Prediction: {result['prediction']}")
                print(f"Confidence: {result['confidence']:.10f}")
                print(f"Raw output: {[f'{x:.8f}' for x in result['raw_output']]}")

        except Exception as e:
            print(f"Error in run {run + 1}: {e}")
            results.append(None)

        # Clean up
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Compare results
    if len(results) == 2 and all(r is not None for r in results):
        print(f"\n🔍 COMPARISON:")
        print("=" * 30)

        r1, r2 = results

        # Check each field
        fields_to_check = [
            ('processed_rows', lambda x: x),
            ('features_sum', lambda x: f'{x:.10f}'),
            ('prediction', lambda x: x),
            ('confidence', lambda x: f'{x:.10f}'),
        ]

        differences_found = False

        for field, formatter in fields_to_check:
            val1 = r1[field]
            val2 = r2[field]

            if val1 != val2:
                print(f"❌ {field}: {formatter(val1)} vs {formatter(val2)}")
                differences_found = True
            else:
                print(f"✅ {field}: {formatter(val1)}")

        # Check arrays
        if not np.allclose(r1['features_first_5'], r2['features_first_5'], rtol=1e-10):
            print(f"❌ features_first_5: Different")
            print(f"   Run 1: {[f'{x:.8f}' for x in r1['features_first_5']]}")
            print(f"   Run 2: {[f'{x:.8f}' for x in r2['features_first_5']]}")
            differences_found = True
        else:
            print(f"✅ features_first_5: Identical")

        if not np.allclose(r1['vgp_signals'], r2['vgp_signals'], rtol=1e-10):
            print(f"❌ vgp_signals: Different")
            print(f"   Run 1: {[f'{x:.8f}' for x in r1['vgp_signals']]}")
            print(f"   Run 2: {[f'{x:.8f}' for x in r2['vgp_signals']]}")
            differences_found = True
        else:
            print(f"✅ vgp_signals: Identical")

        if abs(r1['sentiment'] - r2['sentiment']) > 1e-10:
            print(f"❌ sentiment: {r1['sentiment']:.10f} vs {r2['sentiment']:.10f}")
            differences_found = True
        else:
            print(f"✅ sentiment: Identical")

        if not differences_found:
            print(f"\n🎉 ALL IDENTICAL! The model IS deterministic!")
        else:
            print(f"\n🐛 DIFFERENCES FOUND! This explains the non-determinism.")

if __name__ == "__main__":
    compare_two_runs()