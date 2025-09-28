#!/usr/bin/env python3
"""
VGP-NEAT Live Trading with Alpaca Paper Trading
Real-time trading using the trained model
"""

import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from neat_trading_model import NEATTradingModel
import yfinance as yf
import logging

# You'll need to install alpaca-trade-api: pip install alpaca-trade-api
try:
    from alpaca_trade_api import REST, TimeFrame
    ALPACA_AVAILABLE = True
except ImportError:
    print("⚠️  alpaca-trade-api not installed. Install with: pip install alpaca-trade-api")
    ALPACA_AVAILABLE = False

class VGPAlpacaTrader:
    """Live trading with VGP-NEAT model on Alpaca paper trading"""

    def __init__(self, model_path: str = "vgp_neat_AGGRESSIVE_trained.pkl"):
        self.logger = logging.getLogger(__name__)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('alpaca_live_trading.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        # Load trained model
        print("🤖 Loading VGP-NEAT trading model...")
        self.model = NEATTradingModel("neat_config.txt")
        self.model.load_model(model_path)
        print("✅ Model loaded successfully!")

        # Portfolio settings
        self.position_size_pct = 0.15  # Use 15% of cash per trade
        self.symbol = "TSLA"

        # Initialize Alpaca (you'll need to set these environment variables)
        if ALPACA_AVAILABLE:
            self.alpaca = self.setup_alpaca()
        else:
            self.alpaca = None
            print("📊 Running in simulation mode (no Alpaca)")

    def setup_alpaca(self):
        """Setup Alpaca paper trading connection"""
        try:
            # You need to set these environment variables:
            # APCA_API_KEY_ID = your_key_id
            # APCA_API_SECRET_KEY = your_secret_key
            # APCA_API_BASE_URL = https://paper-api.alpaca.markets (for paper trading)

            api_key = os.getenv('APCA_API_KEY_ID')
            secret_key = os.getenv('APCA_API_SECRET_KEY')
            base_url = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')

            if not api_key or not secret_key:
                print("⚠️  Alpaca API credentials not found in environment variables")
                print("Set APCA_API_KEY_ID and APCA_API_SECRET_KEY")
                return None

            alpaca = REST(api_key, secret_key, base_url)

            # Test connection
            account = alpaca.get_account()
            print(f"🏦 Connected to Alpaca! Account value: ${float(account.portfolio_value):,.2f}")
            return alpaca

        except Exception as e:
            print(f"❌ Failed to connect to Alpaca: {e}")
            return None

    def get_latest_data(self, symbol: str = "TSLA", days: int = 50) -> pd.DataFrame:
        """Get latest market data for the symbol"""
        print(f"📊 Fetching latest {days} days of {symbol} data...")

        # Get data from yfinance (real-time)
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        df = ticker.history(start=start_date, end=end_date)
        df = df.reset_index()
        df['Symbol'] = symbol

        # Rename columns to match our model
        df = df.rename(columns={
            'Date': 'Date',
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        })

        print(f"✅ Got {len(df)} days of data, latest price: ${df['Close'].iloc[-1]:.2f}")
        return df

    def make_prediction(self, df: pd.DataFrame) -> dict:
        """Make trading prediction with the model"""

        # Prepare data using model's pipeline
        df_processed = self.model.enrich_with_sentiment(df)
        df_processed = self.model.add_vgp_signals(df_processed)
        features = self.model.prepare_features(df_processed)

        if len(features) == 0:
            return {"prediction": 1, "confidence": 0.5, "signal": "HOLD"}

        # Get prediction for latest data point
        latest_features = features[-1]
        prediction = self.model.predict(latest_features)

        # Get confidence from raw neural network output
        import neat
        net = neat.nn.FeedForwardNetwork.create(self.model.best_genome, self.model.config)
        output = net.activate(latest_features)
        confidence = max(output) if len(output) == 3 else 0.5

        signal_map = {0: "SELL", 1: "HOLD", 2: "BUY"}

        return {
            "prediction": prediction,
            "confidence": confidence,
            "signal": signal_map[prediction],
            "current_price": df['Close'].iloc[-1],
            "timestamp": df['Date'].iloc[-1]
        }

    def execute_trade(self, prediction_result: dict):
        """Execute trade based on prediction"""

        signal = prediction_result["signal"]
        price = prediction_result["current_price"]
        confidence = prediction_result["confidence"]

        print(f"🎯 Signal: {signal} | Confidence: {confidence:.2f} | Price: ${price:.2f}")

        if not self.alpaca:
            print("📊 Simulation mode - would execute trade here")
            return

        try:
            # Get account info
            account = self.alpaca.get_account()
            cash = float(account.cash)

            # Get current position
            try:
                position = self.alpaca.get_position(self.symbol)
                shares_held = int(position.qty)
            except:
                shares_held = 0

            if signal == "BUY" and cash >= price and confidence > 0.6:
                # Calculate position size
                position_value = cash * self.position_size_pct
                shares_to_buy = int(position_value / price)

                if shares_to_buy > 0:
                    print(f"🟢 BUYING {shares_to_buy} shares of {self.symbol} at ${price:.2f}")

                    order = self.alpaca.submit_order(
                        symbol=self.symbol,
                        qty=shares_to_buy,
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    print(f"✅ Buy order submitted: {order.id}")

            elif signal == "SELL" and shares_held > 0 and confidence > 0.6:
                print(f"🔴 SELLING {shares_held} shares of {self.symbol} at ${price:.2f}")

                order = self.alpaca.submit_order(
                    symbol=self.symbol,
                    qty=shares_held,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
                print(f"✅ Sell order submitted: {order.id}")

            else:
                print(f"⚪ HOLDING - {signal} signal with {confidence:.2f} confidence")

        except Exception as e:
            print(f"❌ Trade execution failed: {e}")

    def run_live_trading(self, check_interval_minutes: int = 60):
        """Run live trading loop"""

        print("🚀 Starting VGP-NEAT live trading...")
        print(f"📊 Symbol: {self.symbol}")
        print(f"💰 Position size: {self.position_size_pct*100}% per trade")
        print(f"⏰ Check interval: {check_interval_minutes} minutes")
        print("=" * 50)

        while True:
            try:
                # Get latest market data
                df = self.get_latest_data(self.symbol)

                # Make prediction
                prediction = self.make_prediction(df)

                # Execute trade
                self.execute_trade(prediction)

                # Log results
                self.logger.info(f"Signal: {prediction['signal']}, Confidence: {prediction['confidence']:.2f}, Price: ${prediction['current_price']:.2f}")

                print(f"⏳ Waiting {check_interval_minutes} minutes until next check...")
                time.sleep(check_interval_minutes * 60)

            except KeyboardInterrupt:
                print("\n🛑 Trading stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in trading loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Run live trading"""
    print("🎯 VGP-NEAT Live Trading System")
    print("=" * 40)

    # Initialize trader
    trader = VGPAlpacaTrader()

    # Test single prediction first
    print("\n🧪 Testing single prediction...")
    df = trader.get_latest_data("TSLA")
    prediction = trader.make_prediction(df)
    print(f"Test prediction: {prediction}")

    # Ask user if they want to start live trading
    if input("\n🚀 Start live trading? (y/n): ").lower() == 'y':
        trader.run_live_trading(check_interval_minutes=60)
    else:
        print("📊 Single prediction completed!")

if __name__ == "__main__":
    main()