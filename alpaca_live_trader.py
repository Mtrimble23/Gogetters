#!/usr/bin/env python3
"""
Simple Live Trading with Alpaca (no complex dependencies)
"""

import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from neat_trading_model import NEATTradingModel
import requests
import json
import logging

class SimpleAlpacaTrader:
    """Live trading using simple HTTP requests to Alpaca API"""

    def __init__(self, model_path: str = "vgp_neat_AGGRESSIVE_trained.pkl"):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Load model
        print("🤖 Loading VGP-NEAT trading model...")
        self.model = NEATTradingModel("neat_config.txt")
        self.model.load_model(model_path)
        print("✅ Model loaded!")

        # Trading settings
        self.symbol = "TSLA"
        self.position_size_pct = 0.15
        self.confidence_threshold = 0.6

        # Alpaca settings (from your setup)
        self.api_key = os.getenv('APCA_API_KEY_ID', 'PK1E7AWHGHV85SI81FS7')
        self.secret_key = os.getenv('APCA_API_SECRET_KEY')
        self.base_url = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')

        if not self.secret_key:
            self.secret_key = input("Enter your Alpaca SECRET key: ").strip()

        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key,
            'Content-Type': 'application/json'
        }

        # Test connection
        self.test_connection()

    def test_connection(self):
        """Test Alpaca connection"""
        try:
            response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
            if response.status_code == 200:
                account = response.json()
                print(f"🏦 Connected to Alpaca! Portfolio: ${float(account['portfolio_value']):,.2f}")
                return True
            else:
                print(f"❌ Alpaca connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def get_account_info(self):
        """Get account information"""
        response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_position(self, symbol):
        """Get current position for symbol"""
        response = requests.get(f"{self.base_url}/v2/positions/{symbol}", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def submit_order(self, symbol, qty, side, order_type='market'):
        """Submit order to Alpaca"""
        order_data = {
            'symbol': symbol,
            'qty': str(qty),
            'side': side,
            'type': order_type,
            'time_in_force': 'day'
        }

        response = requests.post(
            f"{self.base_url}/v2/orders",
            headers=self.headers,
            json=order_data
        )

        if response.status_code in [200, 201]:  # Both 200 and 201 are success
            order_result = response.json()
            status = order_result.get('status', 'unknown')
            print(f"✅ Order {status}: {order_result.get('id', 'unknown_id')}")
            return order_result
        else:
            print(f"❌ Order failed: {response.status_code} - {response.text}")
            return None

    def get_latest_price(self, symbol):
        """Get latest price using simple request"""
        try:
            # Use Yahoo Finance for price (no dependency issues)
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except:
            pass

        # Fallback: use Alpaca bars
        try:
            response = requests.get(
                f"{self.base_url}/v2/stocks/{symbol}/bars/latest",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                return float(data['bar']['c'])  # close price
        except:
            pass

        return None

    def get_historical_data(self, symbol, days=50):
        """Get historical data and calculate features using model's pipeline"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df = ticker.history(start=start_date, end=end_date)
            df = df.reset_index()
            df['Symbol'] = symbol

            # Rename columns to match model expectations
            df = df.rename(columns={
                'Date': 'Date',
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            })

            # Save to temp CSV and use model's load_market_data method to calculate features
            temp_path = "temp_live_data.csv"
            df.to_csv(temp_path, index=False)

            # Use model's data loading method to get all calculated features
            df_processed = self.model.load_market_data(temp_path)

            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return df_processed

        except Exception as e:
            print(f"❌ Failed to get historical data: {e}")
            return None

    def make_prediction(self, df):
        """Make trading prediction"""
        if df is None or len(df) == 0:
            return {"signal": "HOLD", "confidence": 0.5}

        try:
            # Process data
            df_processed = self.model.enrich_with_sentiment(df)
            df_processed = self.model.add_vgp_signals(df_processed)
            features = self.model.prepare_features(df_processed)

            if len(features) == 0:
                return {"signal": "HOLD", "confidence": 0.5}

            # Get prediction
            latest_features = features[-1]
            prediction = self.model.predict(latest_features)

            # Get confidence
            import neat
            net = neat.nn.FeedForwardNetwork.create(self.model.best_genome, self.model.config)
            output = net.activate(latest_features)
            confidence = max(output) if len(output) == 3 else 0.5

            signal_map = {0: "SELL", 1: "HOLD", 2: "BUY"}

            return {
                "signal": signal_map[prediction],
                "confidence": confidence,
                "price": df['Close'].iloc[-1]
            }

        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return {"signal": "HOLD", "confidence": 0.5}

    def execute_trade(self, prediction):
        """Execute trade based on prediction"""
        signal = prediction["signal"]
        confidence = prediction["confidence"]
        price = prediction.get("price", 0)

        print(f"🎯 Signal: {signal} | Confidence: {confidence:.2f} | Price: ${price:.2f}")

        if confidence < self.confidence_threshold:
            print(f"⚪ Confidence too low ({confidence:.2f} < {self.confidence_threshold}), holding")
            return

        try:
            # Get account info
            account = self.get_account_info()
            if not account:
                print("❌ Could not get account info")
                return

            cash = float(account['cash'])

            # Get current position
            position = self.get_position(self.symbol)
            shares_held = int(position['qty']) if position else 0

            if signal == "BUY" and cash >= price:
                # Calculate position size
                position_value = cash * self.position_size_pct
                shares_to_buy = int(position_value / price)

                if shares_to_buy > 0:
                    print(f"🟢 BUYING {shares_to_buy} shares of {self.symbol} at ${price:.2f}")
                    order = self.submit_order(self.symbol, shares_to_buy, 'buy')
                    if order:
                        print(f"✅ Buy order submitted: {order['id']}")
                    else:
                        print("❌ Buy order failed")

            elif signal == "SELL" and shares_held > 0:
                print(f"🔴 SELLING {shares_held} shares of {self.symbol} at ${price:.2f}")
                order = self.submit_order(self.symbol, shares_held, 'sell')
                if order:
                    print(f"✅ Sell order submitted: {order['id']}")
                else:
                    print("❌ Sell order failed")

            else:
                print(f"⚪ HOLDING - {signal} signal but no action taken")

        except Exception as e:
            print(f"❌ Trade execution failed: {e}")

    def run_live_trading(self, check_interval_minutes=60):
        """Run live trading loop"""
        print("🚀 Starting LIVE VGP-NEAT trading!")
        print(f"📊 Symbol: {self.symbol}")
        print(f"💰 Position size: {self.position_size_pct*100}% per trade")
        print(f"🎯 Confidence threshold: {self.confidence_threshold}")
        print(f"⏰ Check interval: {check_interval_minutes} minutes")
        print("=" * 50)

        while True:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n⏰ {current_time} - Checking for trading opportunities...")

                # Get latest data
                df = self.get_historical_data(self.symbol)
                if df is None:
                    print("❌ Could not get market data, skipping this cycle")
                    time.sleep(300)  # Wait 5 minutes and retry
                    continue

                # Make prediction
                prediction = self.make_prediction(df)

                # Execute trade
                self.execute_trade(prediction)

                # Log
                self.logger.info(f"Signal: {prediction['signal']}, Confidence: {prediction['confidence']:.2f}")

                print(f"⏳ Waiting {check_interval_minutes} minutes until next check...")
                time.sleep(check_interval_minutes * 60)

            except KeyboardInterrupt:
                print("\n🛑 Trading stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in trading loop: {e}")
                time.sleep(60)

def main():
    """Start live trading"""
    print("🎯 VGP-NEAT LIVE TRADING SYSTEM")
    print("=" * 40)

    trader = SimpleAlpacaTrader()

    # Test single prediction
    print("\n🧪 Testing prediction...")
    df = trader.get_historical_data("TSLA")
    if df is not None:
        prediction = trader.make_prediction(df)
        print(f"Test prediction: {prediction}")
    else:
        print("❌ Could not get test data")
        return

    # Start live trading
    if input("\n🚀 Start LIVE trading? (y/n): ").lower() == 'y':
        trader.run_live_trading(check_interval_minutes=60)
    else:
        print("📊 Test completed!")

if __name__ == "__main__":
    main()