#!/usr/bin/env python3
"""
Proper Train/Test Evaluation for VGP-NEAT Model
Train: 2020-2024, Test: 2025 (unseen data)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from pathlib import Path
from neat_trading_model import NEATTradingModel
import matplotlib.pyplot as plt

class ProperTrainTestEvaluator:
    """Evaluate model with proper train/test split"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('proper_evaluation.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def split_data_by_year(self, data_path: str):
        """Split data into training (2020-2024) and testing (2025)"""

        print("📊 Loading and splitting TSLA data...")
        df = pd.read_csv(data_path)
        df['Date'] = pd.to_datetime(df['Date'])

        # Split by year
        train_mask = df['Date'].dt.year <= 2024
        test_mask = df['Date'].dt.year >= 2025

        train_data = df[train_mask].copy()
        test_data = df[test_mask].copy()

        print(f"📈 Training data: {train_data['Date'].min()} to {train_data['Date'].max()}")
        print(f"   - {len(train_data)} trading days")
        print(f"🧪 Testing data: {test_data['Date'].min()} to {test_data['Date'].max()}")
        print(f"   - {len(test_data)} trading days")

        # Save splits
        train_data.to_csv('data/TSLA_train_2020_2024.csv', index=False)
        test_data.to_csv('data/TSLA_test_2025.csv', index=False)

        return train_data, test_data

    def train_model_on_historical_data(self, train_data_path: str):
        """Train model on 2020-2024 data only"""

        print("\n🎓 Training VGP-NEAT model on historical data (2020-2024)...")
        print("⚠️  Model will NOT see any 2025 data during training!")

        model = NEATTradingModel("neat_config.txt")

        # Train on historical data only
        winner = model.train(train_data_path, generations=15)

        # Save trained model
        model.save_model("vgp_neat_trained_2020_2024.pkl")

        print("✅ Model training completed on historical data")
        return model

    def evaluate_on_unseen_data(self, model, test_data_path: str, initial_capital: float = 10000):
        """Evaluate trained model on completely unseen 2025 data with REAL portfolio tracking"""

        print("\n🧪 Evaluating on UNSEEN 2025 data...")
        print("🔍 This is the real test - model has never seen this data!")
        print(f"💰 Starting with ${initial_capital:,.2f} capital")

        # Use model's preprocessing pipeline to ensure same features
        test_df = model.load_market_data(test_data_path)  # This adds all calculated features
        test_df = model.enrich_with_sentiment(test_df)
        test_df = model.add_vgp_signals(test_df)

        # Prepare features
        X_test = model.prepare_features(test_df)

        # REAL Portfolio tracking
        portfolio_value = initial_capital
        cash = initial_capital
        shares_held = 0
        portfolio_history = [portfolio_value]

        # Get model predictions and execute trades
        predictions = []
        actual_returns = []
        trades_made = []
        executed_trades = []

        for i in range(len(X_test) - 5):  # Need 5 days ahead for returns
            features = X_test[i]
            prediction = model.predict(features)

            current_price = test_df.iloc[i]['Close']
            current_date = test_df.iloc[i]['Date']

            # Execute trades based on model prediction
            trade_executed = False

            if prediction == 2 and cash >= current_price:  # BUY signal and have cash
                # Use only 15% of available cash per trade (better position sizing)
                position_size = cash * 0.15  # Risk only 15% per trade
                shares_to_buy = int(position_size / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    cash -= cost
                    shares_held += shares_to_buy
                    trade_executed = True

                    executed_trades.append({
                        'date': current_date,
                        'action': 'BUY',
                        'shares': shares_to_buy,
                        'price': current_price,
                        'cost': cost,
                        'portfolio_value': cash + shares_held * current_price
                    })

            elif prediction == 0 and shares_held > 0:  # SELL signal and have shares
                # Sell all shares
                proceeds = shares_held * current_price
                cash += proceeds

                executed_trades.append({
                    'date': current_date,
                    'action': 'SELL',
                    'shares': shares_held,
                    'price': current_price,
                    'proceeds': proceeds,
                    'portfolio_value': cash
                })

                shares_held = 0
                trade_executed = True

            # Calculate portfolio value (cash + value of shares)
            portfolio_value = cash + shares_held * current_price
            portfolio_history.append(portfolio_value)

            # Calculate actual 5-day return for analysis
            future_price = test_df.iloc[i + 5]['Close']
            actual_return = (future_price - current_price) / current_price

            predictions.append(prediction)
            actual_returns.append(actual_return)

            # Record all decisions (not just executed trades)
            trades_made.append({
                'date': current_date,
                'prediction': prediction,
                'actual_return_5d': actual_return,
                'current_price': current_price,
                'future_price': future_price,
                'trade_executed': trade_executed,
                'portfolio_value': portfolio_value
            })

        # Final portfolio value (sell any remaining shares)
        if shares_held > 0:
            final_price = test_df.iloc[-1]['Close']
            final_proceeds = shares_held * final_price
            cash += final_proceeds
            portfolio_value = cash

            executed_trades.append({
                'date': test_df.iloc[-1]['Date'],
                'action': 'FINAL_SELL',
                'shares': shares_held,
                'price': final_price,
                'proceeds': final_proceeds,
                'portfolio_value': portfolio_value
            })

        return predictions, actual_returns, trades_made, portfolio_history, executed_trades, portfolio_value

    def calculate_real_performance_metrics(self, predictions, actual_returns, trades_made,
                                          portfolio_history, executed_trades, final_portfolio_value, initial_capital=10000):
        """Calculate honest performance metrics on unseen data with REAL portfolio tracking"""

        print("\n📊 REAL PORTFOLIO PERFORMANCE (Unseen 2025 Data)")
        print("=" * 60)

        # REAL Portfolio Performance
        total_return = (final_portfolio_value - initial_capital) / initial_capital
        total_profit = final_portfolio_value - initial_capital

        print(f"💰 ACTUAL PORTFOLIO RESULTS:")
        print(f"   Starting Capital: ${initial_capital:,.2f}")
        print(f"   Final Portfolio Value: ${final_portfolio_value:,.2f}")
        print(f"   Total Profit/Loss: ${total_profit:,.2f}")
        print(f"   Total Return: {total_return:.1%}")

        # Trading activity
        num_executed_trades = len(executed_trades)
        buy_trades = [t for t in executed_trades if t['action'] == 'BUY']
        sell_trades = [t for t in executed_trades if t['action'] in ['SELL', 'FINAL_SELL']]

        print(f"\n📈 TRADING ACTIVITY:")
        print(f"   Total executed trades: {num_executed_trades}")
        print(f"   Buy transactions: {len(buy_trades)}")
        print(f"   Sell transactions: {len(sell_trades)}")

        if buy_trades and sell_trades:
            avg_buy_price = np.mean([t['price'] for t in buy_trades])
            avg_sell_price = np.mean([t['price'] for t in sell_trades if t['action'] != 'FINAL_SELL'])
            print(f"   Average buy price: ${avg_buy_price:.2f}")
            print(f"   Average sell price: ${avg_sell_price:.2f}")

        # Annualized return
        days_trading = len(portfolio_history)
        years = days_trading / 252
        annualized_return = (final_portfolio_value / initial_capital) ** (1/years) - 1

        print(f"\n📅 TIME-BASED METRICS:")
        print(f"   Trading period: {days_trading} days ({years:.2f} years)")
        print(f"   Annualized return: {annualized_return:.1%}")

        # Convert to numpy arrays
        predictions = np.array(predictions)
        actual_returns = np.array(actual_returns)

        # Basic metrics
        total_trades = len(predictions)
        buy_signals = np.sum(predictions == 2)  # Buy signals are prediction=2!
        hold_signals = np.sum(predictions == 1)  # Hold signals are prediction=1!
        sell_signals = np.sum(predictions == 0)  # Sell signals are prediction=0!

        print(f"📈 Total decisions made: {total_trades}")
        print(f"📈 Buy signals: {buy_signals} ({buy_signals/total_trades:.1%})")
        print(f"📈 Hold signals: {hold_signals} ({hold_signals/total_trades:.1%})")

        # Performance on buy signals only
        buy_mask = predictions == 2  # Buy signals are prediction=2!
        buy_returns = actual_returns[buy_mask]

        # Initialize variables
        avg_return_per_trade = 0
        win_rate = 0
        annualized_return = 0

        if len(buy_returns) > 0:
            avg_return_per_trade = np.mean(buy_returns)
            successful_buys = np.sum(buy_returns > 0)
            win_rate = successful_buys / len(buy_returns)

            print(f"\n🎯 BUY SIGNAL PERFORMANCE:")
            print(f"   Average return per buy: {avg_return_per_trade:.2%}")
            print(f"   Win rate: {win_rate:.1%}")
            print(f"   Best trade: {np.max(buy_returns):.2%}")
            print(f"   Worst trade: {np.min(buy_returns):.2%}")

            # Annualized performance (if sustained)
            periods_per_year = 252 / 5  # 50.4 periods per year
            annualized_return = (1 + avg_return_per_trade) ** periods_per_year - 1
            print(f"   Annualized return (if sustained): {annualized_return:.1%}")
        else:
            print("\n❌ NO BUY SIGNALS MADE!")
            print("   Model was too conservative and made no trades")

        # Compare to buy-and-hold
        first_price = trades_made[0]['current_price']
        last_price = trades_made[-1]['future_price']
        buy_hold_return = (last_price - first_price) / first_price

        print(f"\n📊 BENCHMARK COMPARISON:")
        print(f"   Buy & Hold return (2025): {buy_hold_return:.2%}")

        if len(buy_returns) > 0:
            print(f"   Model avg return per trade: {avg_return_per_trade:.2%}")
            alpha = avg_return_per_trade - (buy_hold_return / len(actual_returns))
            print(f"   Alpha (excess return): {alpha:.2%}")
        else:
            print(f"   Model return: 0.00% (no trades made)")
            print(f"   Model underperformed by: {buy_hold_return:.2%}")

        return {
            'avg_return_per_trade': avg_return_per_trade,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'buy_signals': buy_signals,
            'buy_hold_return': buy_hold_return,
            'annualized_return': annualized_return
        }

    def plot_real_performance(self, trades_made, metrics):
        """Plot real performance on unseen data"""

        dates = [trade['date'] for trade in trades_made]
        returns = [trade['actual_return_5d'] * 100 for trade in trades_made]  # Convert to %
        predictions = [trade['prediction'] for trade in trades_made]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

        # Plot 1: Returns over time
        colors = ['red' if pred == 2 else 'gray' for pred in predictions]
        ax1.scatter(dates, returns, c=colors, alpha=0.7, s=30)
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax1.axhline(y=np.mean(returns), color='blue', linestyle='-',
                   label=f'Mean: {np.mean(returns):.2f}%')
        ax1.set_title('Real Performance on Unseen 2025 Data\n(Red=Buy Signal, Gray=Hold)',
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('5-Day Return (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Buy signal returns distribution
        buy_returns = [r for r, p in zip(returns, predictions) if p == 2]
        if buy_returns:
            ax2.hist(buy_returns, bins=20, alpha=0.7, color='red', edgecolor='black')
            ax2.axvline(x=np.mean(buy_returns), color='blue', linestyle='--',
                       label=f'Mean Buy Return: {np.mean(buy_returns):.2f}%')
            ax2.set_title('Distribution of Returns on Buy Signals', fontweight='bold')
            ax2.set_xlabel('5-Day Return (%)')
            ax2.set_ylabel('Frequency')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No Buy Signals Made', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=16)
            ax2.set_title('No Buy Signals to Analyze')

        plt.tight_layout()
        plt.savefig('real_performance_2025.png', dpi=300, bbox_inches='tight')
        print("📊 Real performance chart saved: real_performance_2025.png")

def main():
    """Run proper train/test evaluation"""

    print("🎯 PROPER VGP-NEAT EVALUATION")
    print("=" * 50)
    print("📚 Training: 2020-2024 (Historical)")
    print("🧪 Testing: 2025 (Completely Unseen)")
    print("=" * 50)

    evaluator = ProperTrainTestEvaluator()

    # Step 1: Split data
    train_data, test_data = evaluator.split_data_by_year('data/TSLA_enhanced_data.csv')

    # Step 2: Load the aggressive model (or train if it doesn't exist)
    model = NEATTradingModel("neat_config.txt")
    try:
        model.load_model("vgp_neat_AGGRESSIVE_trained.pkl")
        print("✅ Loaded aggressive model with real VGP signals!")
    except FileNotFoundError:
        print("⚠️  Aggressive model not found, training new one with real VGP signals...")
        winner = model.train('data/TSLA_train_2020_2024.csv', generations=15)
        model.save_model("vgp_neat_AGGRESSIVE_trained.pkl")
        print("✅ New aggressive model trained and saved!")

    # Step 3: Test on completely unseen 2025 data with REAL portfolio tracking
    predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value = evaluator.evaluate_on_unseen_data(
        model, 'data/TSLA_test_2025.csv')

    # Step 4: Calculate real metrics with actual portfolio performance
    metrics = evaluator.calculate_real_performance_metrics(
        predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value)

    # Step 5: Plot results
    evaluator.plot_real_performance(trades_made, metrics)

    print("\n🏆 EVALUATION COMPLETE!")
    print("✅ These are REAL performance metrics on unseen data")
    print("📊 Check real_performance_2025.png for visualization")

if __name__ == "__main__":
    main()