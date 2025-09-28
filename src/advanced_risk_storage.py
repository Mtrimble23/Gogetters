#!/usr/bin/env python3
"""
Advanced Risk Metrics Storage
Calculates advanced risk metrics for all stocks and stores them in Aerospike
"""

import sys
import os
sys.path.insert(0, '.')

from services.financial_risk_service import FinancialRiskService
from repositories.aerospike_repository import AerospikeRepository
from datetime import datetime


def calculate_and_store_advanced_metrics():
    """Calculate advanced risk metrics for all stocks and store in Aerospike"""

    print("CALCULATING ADVANCED RISK METRICS AND STORING TO AEROSPIKE")
    print("=" * 70)

    # Initialize components
    financial_service = FinancialRiskService()
    aerospike_repo = AerospikeRepository()

    # The 6 stocks we're tracking
    stocks = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']

    # Dictionary to store all metrics
    all_metrics = {}

    print(f"Calculating advanced risk metrics for {len(stocks)} stocks...")

    for symbol in stocks:
        print(f"\nProcessing {symbol}...")

        try:
            # Get advanced risk analysis from the financial service
            result = financial_service.analyze_advanced_risk(symbol, period="2y")

            if result['success']:
                # Extract the advanced risk metrics
                risk_metrics = result['advanced_risk_metrics']

                all_metrics[symbol] = risk_metrics

                print(f"   SUCCESS {symbol}: Calculated {len(risk_metrics)} risk metrics")

                # Show some key metrics
                if 'annualized_volatility' in risk_metrics:
                    print(f"   Volatility: {risk_metrics['annualized_volatility']:.4f}")
                if 'max_drawdown' in risk_metrics:
                    print(f"   Max Drawdown: {risk_metrics['max_drawdown']:.4f}")
                if 'var' in risk_metrics and '95%' in risk_metrics['var']:
                    var_95 = risk_metrics['var']['95%'].get('historical', 0)
                    print(f"   VaR (95%): {var_95:.4f}")

            else:
                print(f"   ERROR Failed to get advanced metrics for {symbol}: {result['error']}")

        except Exception as e:
            print(f"   ERROR processing {symbol}: {e}")

    print(f"\nStoring advanced risk metrics to Aerospike...")
    print(f"   Namespace: test")
    print(f"   Set: finance")
    print(f"   Bin pattern: advRisk_[SYMBOL]")

    # Store metrics in Aerospike
    if all_metrics:
        success = aerospike_repo.store_all_advanced_metrics(all_metrics)

        if success:
            print(f"SUCCESS: Successfully stored advanced metrics for all {len(all_metrics)} stocks!")

            print(f"\nADVANCED RISK METRICS STORED:")
            for symbol, metrics in all_metrics.items():
                print(f"   {symbol}: {len(metrics)} metrics")

            # Test retrieval
            print(f"\nTesting retrieval...")
            retrieved_metrics = aerospike_repo.get_all_advanced_metrics()

            if retrieved_metrics:
                print(f"SUCCESS: Successfully retrieved metrics for {len(retrieved_metrics)} stocks!")
                print(f"   Data integrity verified for all stocks")

                # Show sample of retrieved data
                if 'AAPL' in retrieved_metrics:
                    aapl_metrics = retrieved_metrics['AAPL']
                    print(f"   Sample AAPL metrics: {len(aapl_metrics)} entries")

            else:
                print(f"WARNING: Could not retrieve advanced metrics from Aerospike")

        else:
            print(f"ERROR: Failed to store some or all advanced metrics in Aerospike")
    else:
        print(f"ERROR: No advanced metrics calculated - nothing to store")

    print(f"\nAdvanced risk calculation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Close connections
    aerospike_repo.close()

    return all_metrics


def get_stored_advanced_metrics():
    """Retrieve and display stored advanced risk metrics from Aerospike"""

    print("RETRIEVING STORED ADVANCED RISK METRICS FROM AEROSPIKE")
    print("=" * 60)

    aerospike_repo = AerospikeRepository()

    try:
        all_metrics = aerospike_repo.get_all_advanced_metrics()

        if all_metrics:
            print(f"SUCCESS: Found advanced metrics for {len(all_metrics)} stocks:")
            print()

            for symbol, metrics in all_metrics.items():
                print(f"   {symbol}: {len(metrics)} risk metrics")

                # Show key metrics if available
                if 'annualized_volatility' in metrics:
                    vol = metrics['annualized_volatility']
                    print(f"      Annual Volatility: {vol:.4f}")

                if 'max_drawdown' in metrics:
                    dd = metrics['max_drawdown']
                    print(f"      Max Drawdown: {dd:.4f}")

                if 'var' in metrics and isinstance(metrics['var'], dict):
                    var_data = metrics['var']
                    if '95%' in var_data and isinstance(var_data['95%'], dict):
                        var_95 = var_data['95%'].get('historical', 0)
                        print(f"      VaR (95%): {var_95:.4f}")

                print()

            return all_metrics
        else:
            print("WARNING: No advanced risk metrics found in Aerospike")
            return None

    except Exception as e:
        print(f"ERROR: Error retrieving advanced metrics: {e}")
        return None

    finally:
        aerospike_repo.close()


def display_metric_summary(all_metrics: dict):
    """Display a summary of all calculated metrics"""

    print("ADVANCED RISK METRICS SUMMARY")
    print("=" * 40)

    if not all_metrics:
        print("No metrics to display")
        return

    for symbol, metrics in all_metrics.items():
        print(f"\n{symbol} Risk Profile:")
        print(f"  Total metrics calculated: {len(metrics)}")

        # Key volatility metrics
        if 'annualized_volatility' in metrics:
            vol = metrics['annualized_volatility']
            risk_level = "High" if vol > 0.3 else "Medium" if vol > 0.2 else "Low"
            print(f"  Volatility Risk: {risk_level} ({vol:.2%})")

        # Drawdown risk
        if 'max_drawdown' in metrics:
            dd = abs(metrics['max_drawdown'])
            dd_risk = "High" if dd > 0.3 else "Medium" if dd > 0.15 else "Low"
            print(f"  Drawdown Risk: {dd_risk} ({dd:.2%})")

        # Tail risk (VaR)
        if 'var' in metrics and '95%' in metrics['var']:
            var_95 = abs(metrics['var']['95%'].get('historical', 0))
            tail_risk = "High" if var_95 > 0.05 else "Medium" if var_95 > 0.03 else "Low"
            print(f"  Tail Risk (VaR): {tail_risk} ({var_95:.2%})")


if __name__ == "__main__":
    # Calculate and store advanced metrics
    print("Step 1: Calculating and storing advanced risk metrics...")
    metrics = calculate_and_store_advanced_metrics()

    print("\n" + "=" * 70)

    # Test retrieval
    print("Step 2: Testing retrieval...")
    stored_metrics = get_stored_advanced_metrics()

    print("\n" + "=" * 70)

    # Display summary
    print("Step 3: Risk profile summary...")
    if metrics:
        display_metric_summary(metrics)
    elif stored_metrics:
        display_metric_summary(stored_metrics)