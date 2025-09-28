#!/usr/bin/env python3
"""
Validate the historical simulation results by manually checking trade logic
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from neat_trading_model import NEATTradingModel

def validate_simulation():
    """Manually validate the simulation logic"""

    print("SIMULATION VALIDATION")
    print("=" * 50)

    # Get the actual data used
    ticker = yf.Ticker('TSLA')
    df = ticker.history(start='2025-01-01', end=datetime.now())
    df = df.reset_index()
    df['Symbol'] = 'TSLA'

    print(f"Data points: {len(df)}")
    print(f"Date range: {df['Date'].iloc[0].date()} to {df['Date'].iloc[-1].date()}")
    print()

    # Load the model
    model = NEATTradingModel("neat_config.txt")
    model.load_model("vgp_neat_AGGRESSIVE_trained.pkl")

    # Simulate first few trades manually
    print("MANUAL TRADE SIMULATION (First 10 potential trades):")
    print("-" * 60)

    cash = 10000
    shares_held = 0
    position_size_pct = 0.15
    confidence_threshold = 0.6
    trades_made = 0

    for i in range(50, len(df)):  # Check ALL days after 50-day warmup
        current_date = df.iloc[i]['Date']
        current_price = df.iloc[i]['Close']

        # Get historical data up to this point
        historical_data = df.iloc[:i+1].copy()

        # Process data like the simulation does
        temp_path = "temp_validation.csv"
        historical_data.to_csv(temp_path, index=False)

        try:
            df_processed = model.load_market_data(temp_path)
            df_processed = model.enrich_with_sentiment(df_processed)
            df_processed = model.add_vgp_signals(df_processed)
            features = model.prepare_features(df_processed)

            if len(features) > 0:
                latest_features = features[-1]
                prediction = model.predict(latest_features)

                # Get confidence
                import neat
                net = neat.nn.FeedForwardNetwork.create(model.best_genome, model.config)
                output = net.activate(latest_features)
                confidence = max(output) if len(output) == 3 else 0.5

                signal_map = {0: "SELL", 1: "HOLD", 2: "BUY"}
                signal = signal_map[prediction]

                # Check if we would trade
                portfolio_value = cash + shares_held * current_price

                # Only print trades, not every day (too much output)
                if signal != "HOLD" and confidence > confidence_threshold:
                    print(f"Day {i-49}: {current_date.date()} | Price: ${current_price:.2f} | Signal: {signal} | Conf: {confidence:.2f}")
                    print(f"   Portfolio: ${portfolio_value:.2f} | Cash: ${cash:.2f} | Shares: {shares_held}")

                if signal == "BUY" and cash >= current_price and confidence > confidence_threshold:
                    position_value = cash * position_size_pct
                    shares_to_buy = int(position_value / current_price)

                    if shares_to_buy > 0:
                        cost = shares_to_buy * current_price
                        cash -= cost
                        shares_held += shares_to_buy
                        trades_made += 1

                        print(f"   *** BUY {shares_to_buy} shares for ${cost:.2f} ***")
                        print(f"   New Cash: ${cash:.2f} | New Shares: {shares_held}")

                elif signal == "SELL" and shares_held > 0 and confidence > confidence_threshold:
                    proceeds = shares_held * current_price
                    cash += proceeds
                    trades_made += 1

                    print(f"   *** SELL {shares_held} shares for ${proceeds:.2f} ***")
                    shares_held = 0
                    print(f"   New Cash: ${cash:.2f} | New Shares: {shares_held}")

                # Show progress every 20 days
                if (i - 50) % 20 == 0:
                    portfolio_value = cash + shares_held * current_price
                    print(f"Day {i-49}: {current_date.date()} | Portfolio: ${portfolio_value:.2f} | Trades so far: {trades_made}")
                    print()

        except Exception as e:
            print(f"   Error processing day {i}: {e}")
            continue

        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # Final summary
    final_portfolio = cash + shares_held * df.iloc[-1]['Close']
    print("MANUAL VALIDATION SUMMARY:")
    print(f"Trades executed: {trades_made}")
    print(f"Final cash: ${cash:.2f}")
    print(f"Final shares: {shares_held}")
    print(f"Final portfolio value: ${final_portfolio:.2f}")
    print(f"Return: {(final_portfolio - 10000) / 10000 * 100:.1f}%")

    # Compare to buy and hold
    buy_hold_value = 10000 * (df.iloc[-1]['Close'] / df.iloc[0]['Close'])
    print(f"Buy & Hold value: ${buy_hold_value:.2f}")
    print(f"Strategy vs B&H: ${final_portfolio - buy_hold_value:.2f}")

if __name__ == "__main__":
    validate_simulation()