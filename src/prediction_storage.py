#!/usr/bin/env python3
"""
Prediction Storage Integration
Runs market predictions and stores them in Aerospike
"""

import sys
import os
sys.path.insert(0, '.')

from market_realistic_predictor import MarketRealisticPredictor
from services.financial_risk_service import FinancialRiskService
from repositories.aerospike_repository import AerospikeRepository
from datetime import datetime


def run_and_store_predictions():
    """Run predictions for all stocks and store in Aerospike"""

    print("RUNNING MARKET PREDICTIONS AND STORING TO AEROSPIKE")
    print("=" * 60)

    # Initialize components
    predictor = MarketRealisticPredictor()
    financial_service = FinancialRiskService()
    aerospike_repo = AerospikeRepository()

    # The 6 stocks we're tracking
    stocks = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']

    # Dictionary to store all predictions
    predictions = {}

    print(f"Generating predictions for {len(stocks)} stocks...")

    for symbol in stocks:
        print(f"\nProcessing {symbol}...")

        try:
            # Get prediction from the model
            result = predictor.predict_realistic_risk(symbol, financial_service)

            if result['success']:
                # Extract the high risk probability as a percentage
                high_risk_prob = result['confidence']['high_risk_probability']
                percentage_prediction = round(high_risk_prob * 100, 2)

                predictions[symbol] = percentage_prediction

                print(f"   SUCCESS {symbol}: {percentage_prediction}% risk probability")
                print(f"   Risk Category: {result['risk_category']}")
                print(f"   Recommendation: {result['recommendation']}")

            else:
                print(f"   ERROR Failed to get prediction for {symbol}: {result['error']}")

        except Exception as e:
            print(f"   ERROR processing {symbol}: {e}")

    print(f"\nStoring predictions to Aerospike...")
    print(f"   Namespace: test")
    print(f"   Set: finance")
    print(f"   Bin: tkrPreds")

    # Store predictions in Aerospike
    if predictions:
        success = aerospike_repo.store_predictions(predictions)

        if success:
            print(f"SUCCESS: Successfully stored {len(predictions)} predictions!")
            print(f"\nFINAL PREDICTIONS STORED:")
            for symbol, percentage in predictions.items():
                print(f"   {symbol}: {percentage}%")

            # Test retrieval
            print(f"\nTesting retrieval...")
            retrieved_predictions = aerospike_repo.get_predictions()

            if retrieved_predictions:
                print(f"SUCCESS: Successfully retrieved predictions from Aerospike!")
                print(f"   Retrieved data matches: {retrieved_predictions == predictions}")
            else:
                print(f"WARNING: Could not retrieve predictions from Aerospike")

        else:
            print(f"ERROR: Failed to store predictions in Aerospike")
    else:
        print(f"ERROR: No predictions generated - nothing to store")

    print(f"\nPrediction run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Close connections
    aerospike_repo.close()

    return predictions


def get_stored_predictions():
    """Retrieve and display stored predictions from Aerospike"""

    print("RETRIEVING STORED PREDICTIONS FROM AEROSPIKE")
    print("=" * 50)

    aerospike_repo = AerospikeRepository()

    try:
        predictions = aerospike_repo.get_predictions()

        if predictions:
            print(f"SUCCESS: Found {len(predictions)} stored predictions:")
            print()

            for symbol, percentage in predictions.items():
                print(f"   {symbol}: {percentage}% risk probability")

            return predictions
        else:
            print("WARNING: No predictions found in Aerospike")
            return None

    except Exception as e:
        print(f"ERROR: Error retrieving predictions: {e}")
        return None

    finally:
        aerospike_repo.close()


if __name__ == "__main__":
    # Run predictions and store them
    predictions = run_and_store_predictions()

    print("\n" + "=" * 60)

    # Test retrieval
    stored_predictions = get_stored_predictions()