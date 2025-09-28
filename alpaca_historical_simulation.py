#!/usr/bin/env python3
"""
Historical Simulation: 2025 to Now with Alpaca-style Trading
Simulate what would have happened if we were live trading from Jan 2025 to now
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from neat_trading_model import NEATTradingModel
import yfinance as yf
import logging
import random

# Set deterministic seeds for reproducible results
np.random.seed(42)
random.seed(42)

# Alpaca API for live trading
try:
    from alpaca_trade_api import REST, TimeFrame
    ALPACA_AVAILABLE = True
    print("OK Alpaca API available for live trading!")
except ImportError as e:
    print(f"ERROR Alpaca API error: {e}")
    ALPACA_AVAILABLE = False

class AlpacaHistoricalSimulation:
    """Simulate live trading from 2025 to now using Alpaca-style execution"""

    def __init__(self, model_path: str = "vgp_neat_AGGRESSIVE_trained.pkl"):
        self.logger = logging.getLogger(__name__)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('alpaca_simulation.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        # Load trained model
        print("🤖 Loading VGP-NEAT trading model...")
        self.model = NEATTradingModel("neat_config.txt")
        self.model.load_model(model_path)
        print("✅ Model loaded successfully!")

        # Portfolio settings (matching our improved evaluation)
        self.initial_capital = 10000
        self.position_size_pct = 0.15  # Use 15% of cash per trade
        self.symbol = "TSLA"
        self.confidence_threshold = 0.6  # Only trade with >60% confidence

        # Initialize Alpaca connection (optional for this simulation)
        if ALPACA_AVAILABLE:
            self.alpaca = self.setup_alpaca()
        else:
            self.alpaca = None

    def setup_alpaca(self):
        """Setup Alpaca connection (optional for historical simulation)"""
        try:
            api_key = os.getenv('APCA_API_KEY_ID')
            secret_key = os.getenv('APCA_API_SECRET_KEY')
            base_url = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')

            if not api_key or not secret_key:
                print("⚠️  Alpaca API credentials not set (OK for simulation)")
                return None

            alpaca = REST(api_key, secret_key, base_url)
            account = alpaca.get_account()
            print(f"🏦 Connected to Alpaca! Account value: ${float(account.portfolio_value):,.2f}")
            return alpaca

        except Exception as e:
            print(f"⚠️  Alpaca connection failed (OK for simulation): {e}")
            return None

    def get_historical_data(self, symbol: str = "TSLA", start_date: str = "2025-01-01") -> pd.DataFrame:
        """Get historical data from start_date to now"""
        print(f"📊 Fetching {symbol} data from {start_date} to now...")

        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start = datetime.strptime(start_date, "%Y-%m-%d")

        df = ticker.history(start=start, end=end_date)
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

        print(f"✅ Got {len(df)} days of data ({start_date} to {end_date.strftime('%Y-%m-%d')})")
        print(f"   Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
        return df

    def simulate_daily_trading(self, df: pd.DataFrame) -> dict:
        """Simulate daily trading decisions like live trading would work"""

        # Investigation: Let's see what's causing non-determinism

        print("🚀 Starting historical trading simulation...")
        print(f"💰 Starting capital: ${self.initial_capital:,.2f}")
        print(f"📊 Position size: {self.position_size_pct*100}% per trade")
        print(f"🎯 Confidence threshold: {self.confidence_threshold}")
        print("🔒 Deterministic mode: Same results every run")
        print("=" * 60)

        # Portfolio tracking
        cash = self.initial_capital
        shares_held = 0
        portfolio_history = []
        trades_executed = []
        daily_decisions = []

        # Process each day (simulating daily checks)
        for i in range(50, len(df)):  # Start after 50 days for technical indicators
            current_date = df.iloc[i]['Date']
            current_price = df.iloc[i]['Close']

            # Get historical data up to this point (what model would see)
            historical_data = df.iloc[:i+1].copy()

            # Make prediction using only data available up to this date
            prediction_result = self.make_daily_prediction(historical_data, day_index=i)

            signal = prediction_result["signal"]
            confidence = prediction_result["confidence"]

            # Calculate portfolio value
            portfolio_value = cash + shares_held * current_price
            portfolio_history.append({
                'date': current_date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'shares_held': shares_held,
                'price': current_price
            })

            # Execute trades based on signal and confidence
            trade_executed = False

            if signal == "BUY" and cash >= current_price and confidence > self.confidence_threshold:
                # Calculate position size
                position_value = cash * self.position_size_pct
                shares_to_buy = int(position_value / current_price)

                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    cash -= cost
                    shares_held += shares_to_buy
                    trade_executed = True

                    trades_executed.append({
                        'date': current_date,
                        'action': 'BUY',
                        'shares': shares_to_buy,
                        'price': current_price,
                        'cost': cost,
                        'confidence': confidence,
                        'portfolio_value': cash + shares_held * current_price
                    })

                    print(f"🟢 {current_date.strftime('%Y-%m-%d')}: BUY {shares_to_buy} shares at ${current_price:.2f} (conf: {confidence:.2f})")

            elif signal == "SELL" and shares_held > 0 and confidence > self.confidence_threshold:
                # Sell all shares
                proceeds = shares_held * current_price
                cash += proceeds
                trade_executed = True

                trades_executed.append({
                    'date': current_date,
                    'action': 'SELL',
                    'shares': shares_held,
                    'price': current_price,
                    'proceeds': proceeds,
                    'confidence': confidence,
                    'portfolio_value': cash
                })

                print(f"🔴 {current_date.strftime('%Y-%m-%d')}: SELL {shares_held} shares at ${current_price:.2f} (conf: {confidence:.2f})")
                shares_held = 0

            # Record daily decision with correct portfolio calculation
            current_portfolio_value = cash + shares_held * current_price
            daily_decisions.append({
                'date': current_date,
                'signal': signal,
                'confidence': confidence,
                'price': current_price,
                'trade_executed': trade_executed,
                'portfolio_value': current_portfolio_value
            })

        # Final portfolio value (sell remaining shares)
        if shares_held > 0:
            final_price = df.iloc[-1]['Close']
            final_proceeds = shares_held * final_price
            cash += final_proceeds

            trades_executed.append({
                'date': df.iloc[-1]['Date'],
                'action': 'FINAL_SELL',
                'shares': shares_held,
                'price': final_price,
                'proceeds': final_proceeds,
                'confidence': 1.0,
                'portfolio_value': cash
            })

        final_portfolio_value = cash

        # Add final portfolio value to daily decisions
        if daily_decisions:
            daily_decisions[-1]['portfolio_value'] = final_portfolio_value

        # Save all decisions to CSV for analysis
        self.save_decisions_to_csv(daily_decisions, trades_executed)

        return {
            'final_portfolio_value': final_portfolio_value,
            'total_return': (final_portfolio_value - self.initial_capital) / self.initial_capital,
            'trades_executed': trades_executed,
            'portfolio_history': portfolio_history,
            'daily_decisions': daily_decisions
        }

    def make_daily_prediction(self, historical_data: pd.DataFrame, day_index: int = 0) -> dict:
        """Make prediction using only historical data up to current date"""

        # Use deterministic temp file name based on day index to ensure consistency
        temp_path = f"temp_historical_data_day_{day_index}.csv"
        # Write CSV with fixed precision to ensure deterministic results
        historical_data.to_csv(temp_path, index=False, float_format='%.10f')

        # Use model's data loading method to get all calculated features
        df_processed = self.model.load_market_data(temp_path)
        df_processed = self.model.enrich_with_sentiment(df_processed)
        df_processed = self.model.add_vgp_signals(df_processed)
        features = self.model.prepare_features(df_processed)

        # Clean up temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if len(features) == 0:
            return {"prediction": 1, "confidence": 0.5, "signal": "HOLD"}

        # Get prediction for most recent data point
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
            "signal": signal_map[prediction]
        }

    def save_decisions_to_csv(self, daily_decisions, trades_executed):
        """Save all trading decisions and trades to CSV files for analysis"""

        import pandas as pd
        from datetime import datetime

        # Save daily decisions
        if daily_decisions:
            decisions_df = pd.DataFrame(daily_decisions)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            decisions_file = f"trading_decisions_{timestamp}.csv"
            decisions_df.to_csv(decisions_file, index=False)
            print(f"💾 Trading decisions saved to: {decisions_file}")

        # Save executed trades
        if trades_executed:
            trades_df = pd.DataFrame(trades_executed)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trades_file = f"executed_trades_{timestamp}.csv"
            trades_df.to_csv(trades_file, index=False)
            print(f"💾 Executed trades saved to: {trades_file}")

        # Save portfolio performance summary
        summary = {
            'total_decisions': len(daily_decisions),
            'total_trades': len(trades_executed),
            'buy_trades': len([t for t in trades_executed if t['action'] == 'BUY']),
            'sell_trades': len([t for t in trades_executed if t['action'] in ['SELL', 'FINAL_SELL']]),
            'avg_confidence': np.mean([d['confidence'] for d in daily_decisions]) if daily_decisions else 0,
            'signals_count': {
                'BUY': len([d for d in daily_decisions if d['signal'] == 'BUY']),
                'SELL': len([d for d in daily_decisions if d['signal'] == 'SELL']),
                'HOLD': len([d for d in daily_decisions if d['signal'] == 'HOLD'])
            }
        }

        summary_file = f"trading_summary_{timestamp}.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"📊 Trading summary saved to: {summary_file}")

    def analyze_results(self, results: dict):
        """Analyze and display simulation results"""

        print("\n" + "="*60)
        print("🏆 ALPACA-STYLE HISTORICAL SIMULATION RESULTS")
        print("="*60)

        # Portfolio performance
        initial = self.initial_capital
        final = results['final_portfolio_value']
        total_return = results['total_return']
        profit = final - initial

        print(f"💰 PORTFOLIO PERFORMANCE:")
        print(f"   Starting Capital: ${initial:,.2f}")
        print(f"   Final Portfolio: ${final:,.2f}")
        print(f"   Total Profit: ${profit:,.2f}")
        print(f"   Total Return: {total_return:.1%}")

        # Trading activity
        trades = results['trades_executed']
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] in ['SELL', 'FINAL_SELL']]

        print(f"\n📈 TRADING ACTIVITY:")
        print(f"   Total executed trades: {len(trades)}")
        print(f"   Buy transactions: {len(buy_trades)}")
        print(f"   Sell transactions: {len(sell_trades)}")

        if buy_trades:
            avg_buy_price = np.mean([t['price'] for t in buy_trades])
            avg_buy_confidence = np.mean([t['confidence'] for t in buy_trades])
            print(f"   Average buy price: ${avg_buy_price:.2f}")
            print(f"   Average buy confidence: {avg_buy_confidence:.2f}")

        if sell_trades:
            avg_sell_price = np.mean([t['price'] for t in sell_trades if t['action'] != 'FINAL_SELL'])
            if len([t for t in sell_trades if t['action'] != 'FINAL_SELL']) > 0:
                avg_sell_confidence = np.mean([t['confidence'] for t in sell_trades if t['action'] != 'FINAL_SELL'])
                print(f"   Average sell price: ${avg_sell_price:.2f}")
                print(f"   Average sell confidence: {avg_sell_confidence:.2f}")

        # Time-based metrics
        days = len(results['portfolio_history'])
        years = days / 365.25
        annualized_return = (final / initial) ** (1/years) - 1

        print(f"\n📅 TIME METRICS:")
        print(f"   Trading period: {days} days ({years:.2f} years)")
        print(f"   Annualized return: {annualized_return:.1%}")

        # Compare to buy and hold
        first_price = results['portfolio_history'][0]['price']
        last_price = results['portfolio_history'][-1]['price']
        buy_hold_return = (last_price - first_price) / first_price
        buy_hold_value = initial * (1 + buy_hold_return)

        print(f"\n📊 BENCHMARK COMPARISON:")
        print(f"   Buy & Hold return: {buy_hold_return:.1%}")
        print(f"   Buy & Hold value: ${buy_hold_value:,.2f}")
        print(f"   Strategy outperformance: ${final - buy_hold_value:,.2f}")

        return results

def main():
    """Run historical simulation"""
    print("🎯 VGP-NEAT Alpaca Historical Simulation")
    print("📅 Simulating live trading from 2025-01-01 to now")
    print("="*60)

    # Initialize simulator
    simulator = AlpacaHistoricalSimulation()

    # Get historical data
    df = simulator.get_historical_data("TSLA", "2025-01-01")

    # Run simulation
    results = simulator.simulate_daily_trading(df)

    # Analyze results
    simulator.analyze_results(results)

    print(f"\n✅ Simulation complete! Check alpaca_simulation.log for details")

if __name__ == "__main__":
    main()