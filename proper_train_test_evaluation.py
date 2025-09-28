#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

Proper Train/Test Evaluation for VGP-NEAT Model""""""

Train: 2020-2024, Test: 2025 (unseen data)

"""Proper Train/Test Evaluation for VGP-NEAT Modelclass ProperTrainTestEvaluator:



import pandas as pdTrain: 2020-2024, Test: 2025 (unseen data)    """Evaluate model with proper train/test split"""oper Train/Test Evaluation for VGP-NEAT Model

import numpy as np

from datetime import datetime"""Train: 2020-2024        pred        executed_trades = []

import logging

from pathlib import Path

from neat_trading_model import NEATTradingModel

import matplotlib.pyplot as pltimport pandas as pd        print(f"🎯 Model will make predictions on {len(X_test) - 5} trading days...")



class ProperTrainTestEvaluator:import numpy as np        print(f"💰 Portfolio tracking: Starting with ${cash:,.2f} cash, {shares_held} shares")

    """Evaluate model with proper train/test split"""

from datetime import datetime        print("📊 Model now considers CASH AVAILABILITY and prioritizes VGP signals!")

    def __init__(self):

        self.logger = logging.getLogger(__name__)import logging



        # Setup loggingfrom pathlib import Path        for i in range(len(X_test) - 5):  # Need 5 days ahead for returnsions = []

        logging.basicConfig(

            level=logging.INFO,from neat_trading_model import NEATTradingModel        actual_returns = []

            format='%(asctime)s - %(levelname)s - %(message)s',

            handlers=[import matplotlib.pyplot as plt        trades_made = []

                logging.FileHandler('proper_evaluation.log', encoding='utf-8'),

                logging.StreamHandler()        executed_trades = []

            ]

        )class ProperTrainTestEvaluator:



    def split_data_by_year(self, data_path: str):    """Evaluate model with proper train/test split"""        print(f"🎯 Model will make predictions on {len(X_test) - 5} trading days...")

        """Split data into training (2020-2024) and testing (2025)"""

        print(f"💰 Portfolio tracking: Starting with ${cash:,.2f} cash, {shares_held} shares")

        print("📊 Loading and splitting TSLA data...")

        df = pd.read_csv(data_path)    def __init__(self):        print("📊 Model now considers CASH AVAILABILITY and prioritizes VGP signals!")

        df['Date'] = pd.to_datetime(df['Date'])

        self.logger = logging.getLogger(__name__)

        # Split by year

        train_mask = df['Date'].dt.year <= 2024        for i in range(len(X_test) - 5):  # Need 5 days ahead for returns: 2025 (unseen data)

        test_mask = df['Date'].dt.year >= 2025

        # Setup logging"""

        train_data = df[train_mask].copy()

        test_data = df[test_mask].copy()        logging.basicConfig(



        print(f"📈 Training data: {train_data['Date'].min()} to {train_data['Date'].max()}")            level=logging.INFO,import pandas as pd

        print(f"   - {len(train_data)} trading days")

        print(f"🧪 Testing data: {test_data['Date'].min()} to {test_data['Date'].max()}")            format='%(asctime)s - %(levelname)s - %(message)s',import numpy as np

        print(f"   - {len(test_data)} trading days")

            handlers=[from datetime import datetime

        # Save splits

        train_data.to_csv('data/TSLA_train_2020_2024.csv', index=False)                logging.FileHandler('proper_evaluation.log', encoding='utf-8'),import logging

        test_data.to_csv('data/TSLA_test_2025.csv', index=False)

                logging.StreamHandler()from pathlib import Path

        return train_data, test_data

            ]from neat_trading_model import NEATTradingModel

    def train_model_on_historical_data(self, train_data_path: str):

        """Train model on 2020-2024 data only"""        )import matplotlib.pyplot as plt



        print("\\n🎓 Training VGP-NEAT model on historical data (2020-2024)...")

        print("⚠️  Model will NOT see any 2025 data during training!")

    def split_data_by_year(self, data_path: str):class ProperTrainTestEvaluator:

        model = NEATTradingModel("neat_config.txt")

        """Split data into training (2020-2024) and testing (2025)"""    """Evalu    print(\"✅ These are REAL performance metrics on unseen data\")\n    print(\"💰 Model now considers CASH AVAILABILITY during training\")\n    print(\"🎯 VGP signals are PRIORITIZED with 2x weight in feature vector\")te model with proper train/test split"""

        # Train on historical data only

        winner = model.train(train_data_path, generations=15)



        # Save trained model        print("📊 Loading and splitting TSLA data...")    def __init__(self):

        model.save_model("vgp_neat_trained_2020_2024.pkl")

        df = pd.read_csv(data_path)        self.logger = logging.getLogger(__name__)

        print("✅ Model training completed on historical data")

        return model        df['Date'] = pd.to_datetime(df['Date'])



    def evaluate_on_unseen_data(self, model, test_data_path: str, initial_capital: float = 10000):        # Setup logging

        """Evaluate trained model on completely unseen 2025 data with REAL portfolio tracking"""

        # Split by year        logging.basicConfig(

        print("\\n🧪 Evaluating on UNSEEN 2025 data...")

        print("🔍 This is the real test - model has never seen this data!")        train_mask = df['Date'].dt.year <= 2024            level=logging.INFO,

        print(f"💰 Starting with ${initial_capital:,.2f} capital")

        test_mask = df['Date'].dt.year >= 2025            format='%(asctime)s - %(levelname)s - %(message)s',

        # Use model's preprocessing pipeline to ensure same features

        test_df = model.load_market_data(test_data_path)  # This adds all calculated features            handlers=[

        test_df = model.enrich_with_sentiment(test_df)

        test_df = model.add_vgp_signals(test_df)        train_data = df[train_mask].copy()                logging.FileHandler('proper_evaluation.log', encoding='utf-8'),



        # Prepare features        test_data = df[test_mask].copy()                logging.StreamHandler()

        X_test = model.prepare_features(test_df)

            ]

        # REAL Portfolio tracking

        portfolio_value = initial_capital        print(f"📈 Training data: {train_data['Date'].min()} to {train_data['Date'].max()}")        )

        cash = initial_capital

        shares_held = 0        print(f"   - {len(train_data)} trading days")

        portfolio_history = [portfolio_value]

        print(f"🧪 Testing data: {test_data['Date'].min()} to {test_data['Date'].max()}")    def split_data_by_year(self, data_path: str):

        # Get model predictions and execute trades with enhanced portfolio awareness

        predictions = []        print(f"   - {len(test_data)} trading days")        """Split data into training (2020-2024) and testing (2025)"""

        actual_returns = []

        trades_made = []

        executed_trades = []

        # Save splits        print("📊 Loading and splitting TSLA data...")

        print(f"🎯 Model will make predictions on {len(X_test) - 5} trading days...")

        print(f"💰 Portfolio tracking: Starting with ${cash:,.2f} cash, {shares_held} shares")        train_data.to_csv('data/TSLA_train_2020_2024.csv', index=False)        df = pd.read_csv(data_path)

        print("📊 Model now considers CASH AVAILABILITY and prioritizes VGP signals!")

        test_data.to_csv('data/TSLA_test_2025.csv', index=False)        df['Date'] = pd.to_datetime(df['Date'])

        for i in range(len(X_test) - 5):  # Need 5 days ahead for returns

            features = X_test[i]

            prediction = model.predict(features)

        return train_data, test_data        # Split by year

            current_price = test_df.iloc[i]['Close']

            current_date = test_df.iloc[i]['Date']        train_mask = df['Date'].dt.year <= 2024



            # Execute trades based on model prediction    def train_model_on_historical_data(self, train_data_path: str):        test_mask = df['Date'].dt.year >= 2025

            trade_executed = False

        """Train model on 2020-2024 data only"""

            if prediction == 2 and cash >= current_price:  # BUY signal and have cash

                # Use only 15% of available cash per trade (better position sizing)        train_data = df[train_mask].copy()

                position_size = cash * 0.15  # Risk only 15% per trade

                shares_to_buy = int(position_size / current_price)        print("\n🎓 Training VGP-NEAT model on historical data (2020-2024)...")        test_data = df[test_mask].copy()

                if shares_to_buy > 0:

                    cost = shares_to_buy * current_price        print("⚠️  Model will NOT see any 2025 data during training!")

                    cash -= cost

                    shares_held += shares_to_buy        print(f"📈 Training data: {train_data['Date'].min()} to {train_data['Date'].max()}")

                    trade_executed = True

        model = NEATTradingModel("neat_config.txt")        print(f"   - {len(train_data)} trading days")

                    executed_trades.append({

                        'date': current_date,        print(f"🧪 Testing data: {test_data['Date'].min()} to {test_data['Date'].max()}")

                        'action': 'BUY',

                        'shares': shares_to_buy,        # Train on historical data only        print(f"   - {len(test_data)} trading days")

                        'price': current_price,

                        'cost': cost,        winner = model.train(train_data_path, generations=15)

                        'portfolio_value': cash + shares_held * current_price

                    })        # Save splits



            elif prediction == 0 and shares_held > 0:  # SELL signal and have shares        # Save trained model        train_data.to_csv('data/TSLA_train_2020_2024.csv', index=False)

                # Sell all shares

                proceeds = shares_held * current_price        model.save_model("vgp_neat_trained_2020_2024.pkl")        test_data.to_csv('data/TSLA_test_2025.csv', index=False)

                cash += proceeds



                executed_trades.append({

                    'date': current_date,        print("✅ Model training completed on historical data")        return train_data, test_data

                    'action': 'SELL',

                    'shares': shares_held,        return model

                    'price': current_price,

                    'proceeds': proceeds,    def train_model_on_historical_data(self, train_data_path: str):

                    'portfolio_value': cash

                })    def evaluate_on_unseen_data(self, model, test_data_path: str, initial_capital: float = 10000):        """Train model on 2020-2024 data only"""



                shares_held = 0        """Evaluate trained model on completely unseen 2025 data with REAL portfolio tracking"""

                trade_executed = True

        print("\n🎓 Training VGP-NEAT model on historical data (2020-2024)...")

            # Calculate portfolio value (cash + value of shares)

            portfolio_value = cash + shares_held * current_price        print("\n🧪 Evaluating on UNSEEN 2025 data...")        print("⚠️  Model will NOT see any 2025 data during training!")

            portfolio_history.append(portfolio_value)

        print("🔍 This is the real test - model has never seen this data!")

            # Calculate actual 5-day return for analysis

            future_price = test_df.iloc[i + 5]['Close']        print(f"💰 Starting with ${initial_capital:,.2f} capital")        model = NEATTradingModel("neat_config.txt")

            actual_return = (future_price - current_price) / current_price



            predictions.append(prediction)

            actual_returns.append(actual_return)        # Use model's preprocessing pipeline to ensure same features        # Train on historical data only



            # Record all decisions (not just executed trades)        test_df = model.load_market_data(test_data_path)  # This adds all calculated features        winner = model.train(train_data_path, generations=15)

            trades_made.append({

                'date': current_date,        test_df = model.enrich_with_sentiment(test_df)

                'prediction': prediction,

                'actual_return_5d': actual_return,        test_df = model.add_vgp_signals(test_df)        # Save trained model

                'current_price': current_price,

                'future_price': future_price,        model.save_model("vgp_neat_trained_2020_2024.pkl")

                'trade_executed': trade_executed,

                'portfolio_value': portfolio_value        # Prepare features

            })

        X_test = model.prepare_features(test_df)        print("✅ Model training completed on historical data")

        # Final portfolio value (sell any remaining shares)

        if shares_held > 0:        return model

            final_price = test_df.iloc[-1]['Close']

            final_proceeds = shares_held * final_price        # REAL Portfolio tracking

            cash += final_proceeds

            portfolio_value = cash        portfolio_value = initial_capital    def evaluate_on_unseen_data(self, model, test_data_path: str, initial_capital: float = 10000):



            executed_trades.append({        cash = initial_capital        """Evaluate trained model on completely unseen 2025 data with REAL portfolio tracking"""

                'date': test_df.iloc[-1]['Date'],

                'action': 'FINAL_SELL',        shares_held = 0

                'shares': shares_held,

                'price': final_price,        portfolio_history = [portfolio_value]        print("\n🧪 Evaluating on UNSEEN 2025 data...")

                'proceeds': final_proceeds,

                'portfolio_value': portfolio_value        print("🔍 This is the real test - model has never seen this data!")

            })

        # Get model predictions and execute trades with enhanced portfolio awareness        print(f"💰 Starting with ${initial_capital:,.2f} capital")

        return predictions, actual_returns, trades_made, portfolio_history, executed_trades, portfolio_value

        predictions = []

    def calculate_real_performance_metrics(self, predictions, actual_returns, trades_made,

                                          portfolio_history, executed_trades, final_portfolio_value, initial_capital=10000):        actual_returns = []        # Use model's preprocessing pipeline to ensure same features

        """Calculate honest performance metrics on unseen data with REAL portfolio tracking"""

        trades_made = []        test_df = model.load_market_data(test_data_path)  # This adds all calculated features

        print("\\n📊 REAL PORTFOLIO PERFORMANCE (Unseen 2025 Data)")

        print("=" * 60)        executed_trades = []        test_df = model.enrich_with_sentiment(test_df)



        # REAL Portfolio Performance        test_df = model.add_vgp_signals(test_df)

        total_return = (final_portfolio_value - initial_capital) / initial_capital

        total_profit = final_portfolio_value - initial_capital        print(f"🎯 Model will make predictions on {len(X_test) - 5} trading days...")



        print(f"💰 ACTUAL PORTFOLIO RESULTS:")        print(f"💰 Portfolio tracking: Starting with ${cash:,.2f} cash, {shares_held} shares")        # Prepare features

        print(f"   Starting Capital: ${initial_capital:,.2f}")

        print(f"   Final Portfolio Value: ${final_portfolio_value:,.2f}")        print("📊 Model now considers CASH AVAILABILITY and prioritizes VGP signals!")        X_test = model.prepare_features(test_df)

        print(f"   Total Profit/Loss: ${total_profit:,.2f}")

        print(f"   Total Return: {total_return:.1%}")



        # Trading activity        for i in range(len(X_test) - 5):  # Need 5 days ahead for returns        # REAL Portfolio tracking

        num_executed_trades = len(executed_trades)

        buy_trades = [t for t in executed_trades if t['action'] == 'BUY']            features = X_test[i]        portfolio_value = initial_capital

        sell_trades = [t for t in executed_trades if t['action'] in ['SELL', 'FINAL_SELL']]

            prediction = model.predict(features)        cash = initial_capital

        print(f"\\n📈 TRADING ACTIVITY:")

        print(f"   Total executed trades: {num_executed_trades}")        shares_held = 0

        print(f"   Buy transactions: {len(buy_trades)}")

        print(f"   Sell transactions: {len(sell_trades)}")            current_price = test_df.iloc[i]['Close']        portfolio_history = [portfolio_value]



        if buy_trades and sell_trades:            current_date = test_df.iloc[i]['Date']

            avg_buy_price = np.mean([t['price'] for t in buy_trades])

            avg_sell_price = np.mean([t['price'] for t in sell_trades if t['action'] != 'FINAL_SELL'])        # Get model predictions and execute trades

            print(f"   Average buy price: ${avg_buy_price:.2f}")

            print(f"   Average sell price: ${avg_sell_price:.2f}")            # Execute trades based on model prediction        predictions = []



        # Annualized return            trade_executed = False        actual_returns = []

        days_trading = len(portfolio_history)

        years = days_trading / 252        trades_made = []

        annualized_return = (final_portfolio_value / initial_capital) ** (1/years) - 1

            if prediction == 2 and cash >= current_price:  # BUY signal and have cash        executed_trades = []

        print(f"\\n📅 TIME-BASED METRICS:")

        print(f"   Trading period: {days_trading} days ({years:.2f} years)")                # Use only 15% of available cash per trade (better position sizing)

        print(f"   Annualized return: {annualized_return:.1%}")

                position_size = cash * 0.15  # Risk only 15% per trade        print(f\"🎯 Model will make predictions on {len(X_test) - 5} trading days...\")

        # Convert to numpy arrays

        predictions = np.array(predictions)                shares_to_buy = int(position_size / current_price)                      print(f\"💰 Portfolio tracking: Starting with ${cash:,.2f} cash, {shares_held} shares\")\n        print(\"📊 Model now considers CASH AVAILABILITY and prioritizes VGP signals!\")\n\n        for i in range(len(X_test) - 5):  # Need 5 days ahead for returns

        actual_returns = np.array(actual_returns)

                if shares_to_buy > 0:            features = X_test[i]

        # Basic metrics

        total_trades = len(predictions)                    cost = shares_to_buy * current_price            prediction = model.predict(features)

        buy_signals = np.sum(predictions == 2)  # Buy signals are prediction=2!

        hold_signals = np.sum(predictions == 1)  # Hold signals are prediction=1!                    cash -= cost

        sell_signals = np.sum(predictions == 0)  # Sell signals are prediction=0!

                    shares_held += shares_to_buy            current_price = test_df.iloc[i]['Close']

        print(f"📈 Total decisions made: {total_trades}")

        print(f"📈 Buy signals: {buy_signals} ({buy_signals/total_trades:.1%})")                    trade_executed = True            current_date = test_df.iloc[i]['Date']

        print(f"📈 Hold signals: {hold_signals} ({hold_signals/total_trades:.1%})")



        # Performance on buy signals only

        buy_mask = predictions == 2  # Buy signals are prediction=2!                    executed_trades.append({            # Execute trades based on model prediction

        buy_returns = actual_returns[buy_mask]

                        'date': current_date,            trade_executed = False

        # Initialize variables

        avg_return_per_trade = 0                        'action': 'BUY',

        win_rate = 0

        annualized_return = 0                        'shares': shares_to_buy,            if prediction == 2 and cash >= current_price:  # BUY signal and have cash



        if len(buy_returns) > 0:                        'price': current_price,                # Use only 15% of available cash per trade (better position sizing)

            avg_return_per_trade = np.mean(buy_returns)

            successful_buys = np.sum(buy_returns > 0)                        'cost': cost,                position_size = cash * 0.15  # Risk only 15% per trade

            win_rate = successful_buys / len(buy_returns)

                        'portfolio_value': cash + shares_held * current_price                shares_to_buy = int(position_size / current_price)

            print(f"\\n🎯 BUY SIGNAL PERFORMANCE:")

            print(f"   Average return per buy: {avg_return_per_trade:.2%}")                    })                if shares_to_buy > 0:

            print(f"   Win rate: {win_rate:.1%}")

            print(f"   Best trade: {np.max(buy_returns):.2%}")                    cost = shares_to_buy * current_price

            print(f"   Worst trade: {np.min(buy_returns):.2%}")

            elif prediction == 0 and shares_held > 0:  # SELL signal and have shares                    cash -= cost

            # Annualized performance (if sustained)

            periods_per_year = 252 / 5  # 50.4 periods per year                # Sell all shares                    shares_held += shares_to_buy

            annualized_return = (1 + avg_return_per_trade) ** periods_per_year - 1

            print(f"   Annualized return (if sustained): {annualized_return:.1%}")                proceeds = shares_held * current_price                    trade_executed = True

        else:

            print("\\n❌ NO BUY SIGNALS MADE!")                cash += proceeds

            print("   Model was too conservative and made no trades")

                    executed_trades.append({

        # Compare to buy-and-hold

        first_price = trades_made[0]['current_price']                executed_trades.append({                        'date': current_date,

        last_price = trades_made[-1]['future_price']

        buy_hold_return = (last_price - first_price) / first_price                    'date': current_date,                        'action': 'BUY',



        print(f"\\n📊 BENCHMARK COMPARISON:")                    'action': 'SELL',                        'shares': shares_to_buy,

        print(f"   Buy & Hold return (2025): {buy_hold_return:.2%}")

                    'shares': shares_held,                        'price': current_price,

        if len(buy_returns) > 0:

            print(f"   Model avg return per trade: {avg_return_per_trade:.2%}")                    'price': current_price,                        'cost': cost,

            alpha = avg_return_per_trade - (buy_hold_return / len(actual_returns))

            print(f"   Alpha (excess return): {alpha:.2%}")                    'proceeds': proceeds,                        'portfolio_value': cash + shares_held * current_price

        else:

            print(f"   Model return: 0.00% (no trades made)")                    'portfolio_value': cash                    })

            print(f"   Model underperformed by: {buy_hold_return:.2%}")

                })

        return {

            'avg_return_per_trade': avg_return_per_trade,            elif prediction == 0 and shares_held > 0:  # SELL signal and have shares

            'win_rate': win_rate,

            'total_trades': total_trades,                shares_held = 0                # Sell all shares

            'buy_signals': buy_signals,

            'buy_hold_return': buy_hold_return,                trade_executed = True                proceeds = shares_held * current_price

            'annualized_return': annualized_return

        }                cash += proceeds



    def plot_real_performance(self, trades_made, metrics):            # Calculate portfolio value (cash + value of shares)

        """Plot real performance on unseen data"""

            portfolio_value = cash + shares_held * current_price                executed_trades.append({

        dates = [trade['date'] for trade in trades_made]

        returns = [trade['actual_return_5d'] * 100 for trade in trades_made]  # Convert to %            portfolio_history.append(portfolio_value)                    'date': current_date,

        predictions = [trade['prediction'] for trade in trades_made]

                    'action': 'SELL',

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

            # Calculate actual 5-day return for analysis                    'shares': shares_held,

        # Plot 1: Returns over time

        colors = ['red' if pred == 2 else 'gray' for pred in predictions]            future_price = test_df.iloc[i + 5]['Close']                    'price': current_price,

        ax1.scatter(dates, returns, c=colors, alpha=0.7, s=30)

        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)            actual_return = (future_price - current_price) / current_price                    'proceeds': proceeds,

        ax1.axhline(y=np.mean(returns), color='blue', linestyle='-',

                   label=f'Mean: {np.mean(returns):.2f}%')                    'portfolio_value': cash

        ax1.set_title('Real Performance on Unseen 2025 Data\\n(Red=Buy Signal, Gray=Hold)',

                     fontsize=14, fontweight='bold')            predictions.append(prediction)                })

        ax1.set_ylabel('5-Day Return (%)')

        ax1.legend()            actual_returns.append(actual_return)

        ax1.grid(True, alpha=0.3)

                shares_held = 0

        # Plot 2: Buy signal returns distribution

        buy_returns = [r for r, p in zip(returns, predictions) if p == 2]            # Record all decisions (not just executed trades)                trade_executed = True

        if buy_returns:

            ax2.hist(buy_returns, bins=20, alpha=0.7, color='red', edgecolor='black')            trades_made.append({

            ax2.axvline(x=np.mean(buy_returns), color='blue', linestyle='--',

                       label=f'Mean Buy Return: {np.mean(buy_returns):.2f}%')                'date': current_date,            # Calculate portfolio value (cash + value of shares)

            ax2.set_title('Distribution of Returns on Buy Signals', fontweight='bold')

            ax2.set_xlabel('5-Day Return (%)')                'prediction': prediction,            portfolio_value = cash + shares_held * current_price

            ax2.set_ylabel('Frequency')

            ax2.legend()                'actual_return_5d': actual_return,            portfolio_history.append(portfolio_value)

            ax2.grid(True, alpha=0.3)

        else:                'current_price': current_price,

            ax2.text(0.5, 0.5, 'No Buy Signals Made', ha='center', va='center',

                    transform=ax2.transAxes, fontsize=16)                'future_price': future_price,            # Calculate actual 5-day return for analysis

            ax2.set_title('No Buy Signals to Analyze')

                'trade_executed': trade_executed,            future_price = test_df.iloc[i + 5]['Close']

        plt.tight_layout()

        plt.savefig('real_performance_2025.png', dpi=300, bbox_inches='tight')                'portfolio_value': portfolio_value            actual_return = (future_price - current_price) / current_price

        print("📊 Real performance chart saved: real_performance_2025.png")

            })

def main():

    """Run proper train/test evaluation"""            predictions.append(prediction)



    print("🎯 PROPER VGP-NEAT EVALUATION")        # Final portfolio value (sell any remaining shares)            actual_returns.append(actual_return)

    print("=" * 50)

    print("📚 Training: 2020-2024 (Historical)")        if shares_held > 0:

    print("🧪 Testing: 2025 (Completely Unseen)")

    print("=" * 50)            final_price = test_df.iloc[-1]['Close']            # Record all decisions (not just executed trades)



    evaluator = ProperTrainTestEvaluator()            final_proceeds = shares_held * final_price            trades_made.append({



    # Step 1: Split data            cash += final_proceeds                'date': current_date,

    train_data, test_data = evaluator.split_data_by_year('data/TSLA_enhanced_data.csv')

            portfolio_value = cash                'prediction': prediction,

    # Step 2: Load the aggressive model (or train if it doesn't exist)

    model = NEATTradingModel("neat_config.txt")                'actual_return_5d': actual_return,

    try:

        model.load_model("vgp_neat_AGGRESSIVE_trained.pkl")            executed_trades.append({                'current_price': current_price,

        print("✅ Loaded aggressive model with real VGP signals!")

    except FileNotFoundError:                'date': test_df.iloc[-1]['Date'],                'future_price': future_price,

        print("⚠️  Aggressive model not found, training new one with real VGP signals...")

        winner = model.train('data/TSLA_train_2020_2024.csv', generations=15)                'action': 'FINAL_SELL',                'trade_executed': trade_executed,

        model.save_model("vgp_neat_AGGRESSIVE_trained.pkl")

        print("✅ New aggressive model trained and saved!")                'shares': shares_held,                'portfolio_value': portfolio_value



    # Step 3: Test on completely unseen 2025 data with REAL portfolio tracking                'price': final_price,            })

    predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value = evaluator.evaluate_on_unseen_data(

        model, 'data/TSLA_test_2025.csv')                'proceeds': final_proceeds,



    # Step 4: Calculate real metrics with actual portfolio performance                'portfolio_value': portfolio_value        # Final portfolio value (sell any remaining shares)

    metrics = evaluator.calculate_real_performance_metrics(

        predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value)            })        if shares_held > 0:



    # Step 5: Plot results            final_price = test_df.iloc[-1]['Close']

    evaluator.plot_real_performance(trades_made, metrics)

        return predictions, actual_returns, trades_made, portfolio_history, executed_trades, portfolio_value            final_proceeds = shares_held * final_price

    print("\\n🏆 EVALUATION COMPLETE!")

    print("✅ These are REAL performance metrics on unseen data")            cash += final_proceeds

    print("💰 Model now considers CASH AVAILABILITY during training")

    print("🎯 VGP signals are PRIORITIZED with 2x weight in feature vector")    def calculate_real_performance_metrics(self, predictions, actual_returns, trades_made,            portfolio_value = cash

    print("📊 Check real_performance_2025.png for visualization")

                                          portfolio_history, executed_trades, final_portfolio_value, initial_capital=10000):

if __name__ == "__main__":

    main()        """Calculate honest performance metrics on unseen data with REAL portfolio tracking"""            executed_trades.append({

                'date': test_df.iloc[-1]['Date'],

        print("\n📊 REAL PORTFOLIO PERFORMANCE (Unseen 2025 Data)")                'action': 'FINAL_SELL',

        print("=" * 60)                'shares': shares_held,

                'price': final_price,

        # REAL Portfolio Performance                'proceeds': final_proceeds,

        total_return = (final_portfolio_value - initial_capital) / initial_capital                'portfolio_value': portfolio_value

        total_profit = final_portfolio_value - initial_capital            })



        print(f"💰 ACTUAL PORTFOLIO RESULTS:")        return predictions, actual_returns, trades_made, portfolio_history, executed_trades, portfolio_value

        print(f"   Starting Capital: ${initial_capital:,.2f}")

        print(f"   Final Portfolio Value: ${final_portfolio_value:,.2f}")    def calculate_real_performance_metrics(self, predictions, actual_returns, trades_made,

        print(f"   Total Profit/Loss: ${total_profit:,.2f}")                                          portfolio_history, executed_trades, final_portfolio_value, initial_capital=10000):

        print(f"   Total Return: {total_return:.1%}")        """Calculate honest performance metrics on unseen data with REAL portfolio tracking"""



        # Trading activity        print("\n📊 REAL PORTFOLIO PERFORMANCE (Unseen 2025 Data)")

        num_executed_trades = len(executed_trades)        print("=" * 60)

        buy_trades = [t for t in executed_trades if t['action'] == 'BUY']

        sell_trades = [t for t in executed_trades if t['action'] in ['SELL', 'FINAL_SELL']]        # REAL Portfolio Performance

        total_return = (final_portfolio_value - initial_capital) / initial_capital

        print(f"\n📈 TRADING ACTIVITY:")        total_profit = final_portfolio_value - initial_capital

        print(f"   Total executed trades: {num_executed_trades}")

        print(f"   Buy transactions: {len(buy_trades)}")        print(f"💰 ACTUAL PORTFOLIO RESULTS:")

        print(f"   Sell transactions: {len(sell_trades)}")        print(f"   Starting Capital: ${initial_capital:,.2f}")

        print(f"   Final Portfolio Value: ${final_portfolio_value:,.2f}")

        if buy_trades and sell_trades:        print(f"   Total Profit/Loss: ${total_profit:,.2f}")

            avg_buy_price = np.mean([t['price'] for t in buy_trades])        print(f"   Total Return: {total_return:.1%}")

            avg_sell_price = np.mean([t['price'] for t in sell_trades if t['action'] != 'FINAL_SELL'])

            print(f"   Average buy price: ${avg_buy_price:.2f}")        # Trading activity

            print(f"   Average sell price: ${avg_sell_price:.2f}")        num_executed_trades = len(executed_trades)

        buy_trades = [t for t in executed_trades if t['action'] == 'BUY']

        # Annualized return        sell_trades = [t for t in executed_trades if t['action'] in ['SELL', 'FINAL_SELL']]

        days_trading = len(portfolio_history)

        years = days_trading / 252        print(f"\n📈 TRADING ACTIVITY:")

        annualized_return = (final_portfolio_value / initial_capital) ** (1/years) - 1        print(f"   Total executed trades: {num_executed_trades}")

        print(f"   Buy transactions: {len(buy_trades)}")

        print(f"\n📅 TIME-BASED METRICS:")        print(f"   Sell transactions: {len(sell_trades)}")

        print(f"   Trading period: {days_trading} days ({years:.2f} years)")

        print(f"   Annualized return: {annualized_return:.1%}")        if buy_trades and sell_trades:

            avg_buy_price = np.mean([t['price'] for t in buy_trades])

        # Convert to numpy arrays            avg_sell_price = np.mean([t['price'] for t in sell_trades if t['action'] != 'FINAL_SELL'])

        predictions = np.array(predictions)            print(f"   Average buy price: ${avg_buy_price:.2f}")

        actual_returns = np.array(actual_returns)            print(f"   Average sell price: ${avg_sell_price:.2f}")



        # Basic metrics        # Annualized return

        total_trades = len(predictions)        days_trading = len(portfolio_history)

        buy_signals = np.sum(predictions == 2)  # Buy signals are prediction=2!        years = days_trading / 252

        hold_signals = np.sum(predictions == 1)  # Hold signals are prediction=1!        annualized_return = (final_portfolio_value / initial_capital) ** (1/years) - 1

        sell_signals = np.sum(predictions == 0)  # Sell signals are prediction=0!

        print(f"\n📅 TIME-BASED METRICS:")

        print(f"📈 Total decisions made: {total_trades}")        print(f"   Trading period: {days_trading} days ({years:.2f} years)")

        print(f"📈 Buy signals: {buy_signals} ({buy_signals/total_trades:.1%})")        print(f"   Annualized return: {annualized_return:.1%}")

        print(f"📈 Hold signals: {hold_signals} ({hold_signals/total_trades:.1%})")

        # Convert to numpy arrays

        # Performance on buy signals only        predictions = np.array(predictions)

        buy_mask = predictions == 2  # Buy signals are prediction=2!        actual_returns = np.array(actual_returns)

        buy_returns = actual_returns[buy_mask]

        # Basic metrics

        # Initialize variables        total_trades = len(predictions)

        avg_return_per_trade = 0        buy_signals = np.sum(predictions == 2)  # Buy signals are prediction=2!

        win_rate = 0        hold_signals = np.sum(predictions == 1)  # Hold signals are prediction=1!

        annualized_return = 0        sell_signals = np.sum(predictions == 0)  # Sell signals are prediction=0!



        if len(buy_returns) > 0:        print(f"📈 Total decisions made: {total_trades}")

            avg_return_per_trade = np.mean(buy_returns)        print(f"📈 Buy signals: {buy_signals} ({buy_signals/total_trades:.1%})")

            successful_buys = np.sum(buy_returns > 0)        print(f"📈 Hold signals: {hold_signals} ({hold_signals/total_trades:.1%})")

            win_rate = successful_buys / len(buy_returns)

        # Performance on buy signals only

            print(f"\n🎯 BUY SIGNAL PERFORMANCE:")        buy_mask = predictions == 2  # Buy signals are prediction=2!

            print(f"   Average return per buy: {avg_return_per_trade:.2%}")        buy_returns = actual_returns[buy_mask]

            print(f"   Win rate: {win_rate:.1%}")

            print(f"   Best trade: {np.max(buy_returns):.2%}")        # Initialize variables

            print(f"   Worst trade: {np.min(buy_returns):.2%}")        avg_return_per_trade = 0

        win_rate = 0

            # Annualized performance (if sustained)        annualized_return = 0

            periods_per_year = 252 / 5  # 50.4 periods per year

            annualized_return = (1 + avg_return_per_trade) ** periods_per_year - 1        if len(buy_returns) > 0:

            print(f"   Annualized return (if sustained): {annualized_return:.1%}")            avg_return_per_trade = np.mean(buy_returns)

        else:            successful_buys = np.sum(buy_returns > 0)

            print("\n❌ NO BUY SIGNALS MADE!")            win_rate = successful_buys / len(buy_returns)

            print("   Model was too conservative and made no trades")

            print(f"\n🎯 BUY SIGNAL PERFORMANCE:")

        # Compare to buy-and-hold            print(f"   Average return per buy: {avg_return_per_trade:.2%}")

        first_price = trades_made[0]['current_price']            print(f"   Win rate: {win_rate:.1%}")

        last_price = trades_made[-1]['future_price']            print(f"   Best trade: {np.max(buy_returns):.2%}")

        buy_hold_return = (last_price - first_price) / first_price            print(f"   Worst trade: {np.min(buy_returns):.2%}")



        print(f"\n📊 BENCHMARK COMPARISON:")            # Annualized performance (if sustained)

        print(f"   Buy & Hold return (2025): {buy_hold_return:.2%}")            periods_per_year = 252 / 5  # 50.4 periods per year

            annualized_return = (1 + avg_return_per_trade) ** periods_per_year - 1

        if len(buy_returns) > 0:            print(f"   Annualized return (if sustained): {annualized_return:.1%}")

            print(f"   Model avg return per trade: {avg_return_per_trade:.2%}")        else:

            alpha = avg_return_per_trade - (buy_hold_return / len(actual_returns))            print("\n❌ NO BUY SIGNALS MADE!")

            print(f"   Alpha (excess return): {alpha:.2%}")            print("   Model was too conservative and made no trades")

        else:

            print(f"   Model return: 0.00% (no trades made)")        # Compare to buy-and-hold

            print(f"   Model underperformed by: {buy_hold_return:.2%}")        first_price = trades_made[0]['current_price']

        last_price = trades_made[-1]['future_price']

        return {        buy_hold_return = (last_price - first_price) / first_price

            'avg_return_per_trade': avg_return_per_trade,

            'win_rate': win_rate,        print(f"\n📊 BENCHMARK COMPARISON:")

            'total_trades': total_trades,        print(f"   Buy & Hold return (2025): {buy_hold_return:.2%}")

            'buy_signals': buy_signals,

            'buy_hold_return': buy_hold_return,        if len(buy_returns) > 0:

            'annualized_return': annualized_return            print(f"   Model avg return per trade: {avg_return_per_trade:.2%}")

        }            alpha = avg_return_per_trade - (buy_hold_return / len(actual_returns))

            print(f"   Alpha (excess return): {alpha:.2%}")

    def plot_real_performance(self, trades_made, metrics):        else:

        """Plot real performance on unseen data"""            print(f"   Model return: 0.00% (no trades made)")

            print(f"   Model underperformed by: {buy_hold_return:.2%}")

        dates = [trade['date'] for trade in trades_made]

        returns = [trade['actual_return_5d'] * 100 for trade in trades_made]  # Convert to %        return {

        predictions = [trade['prediction'] for trade in trades_made]            'avg_return_per_trade': avg_return_per_trade,

            'win_rate': win_rate,

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))            'total_trades': total_trades,

            'buy_signals': buy_signals,

        # Plot 1: Returns over time            'buy_hold_return': buy_hold_return,

        colors = ['red' if pred == 2 else 'gray' for pred in predictions]            'annualized_return': annualized_return

        ax1.scatter(dates, returns, c=colors, alpha=0.7, s=30)        }

        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)

        ax1.axhline(y=np.mean(returns), color='blue', linestyle='-',    def plot_real_performance(self, trades_made, metrics):

                   label=f'Mean: {np.mean(returns):.2f}%')        """Plot real performance on unseen data"""

        ax1.set_title('Real Performance on Unseen 2025 Data\n(Red=Buy Signal, Gray=Hold)',

                     fontsize=14, fontweight='bold')        dates = [trade['date'] for trade in trades_made]

        ax1.set_ylabel('5-Day Return (%)')        returns = [trade['actual_return_5d'] * 100 for trade in trades_made]  # Convert to %

        ax1.legend()        predictions = [trade['prediction'] for trade in trades_made]

        ax1.grid(True, alpha=0.3)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

        # Plot 2: Buy signal returns distribution

        buy_returns = [r for r, p in zip(returns, predictions) if p == 2]        # Plot 1: Returns over time

        if buy_returns:        colors = ['red' if pred == 2 else 'gray' for pred in predictions]

            ax2.hist(buy_returns, bins=20, alpha=0.7, color='red', edgecolor='black')        ax1.scatter(dates, returns, c=colors, alpha=0.7, s=30)

            ax2.axvline(x=np.mean(buy_returns), color='blue', linestyle='--',        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)

                       label=f'Mean Buy Return: {np.mean(buy_returns):.2f}%')        ax1.axhline(y=np.mean(returns), color='blue', linestyle='-',

            ax2.set_title('Distribution of Returns on Buy Signals', fontweight='bold')                   label=f'Mean: {np.mean(returns):.2f}%')

            ax2.set_xlabel('5-Day Return (%)')        ax1.set_title('Real Performance on Unseen 2025 Data\n(Red=Buy Signal, Gray=Hold)',

            ax2.set_ylabel('Frequency')                     fontsize=14, fontweight='bold')

            ax2.legend()        ax1.set_ylabel('5-Day Return (%)')

            ax2.grid(True, alpha=0.3)        ax1.legend()

        else:        ax1.grid(True, alpha=0.3)

            ax2.text(0.5, 0.5, 'No Buy Signals Made', ha='center', va='center',

                    transform=ax2.transAxes, fontsize=16)        # Plot 2: Buy signal returns distribution

            ax2.set_title('No Buy Signals to Analyze')        buy_returns = [r for r, p in zip(returns, predictions) if p == 2]

        if buy_returns:

        plt.tight_layout()            ax2.hist(buy_returns, bins=20, alpha=0.7, color='red', edgecolor='black')

        plt.savefig('real_performance_2025.png', dpi=300, bbox_inches='tight')            ax2.axvline(x=np.mean(buy_returns), color='blue', linestyle='--',

        print("📊 Real performance chart saved: real_performance_2025.png")                       label=f'Mean Buy Return: {np.mean(buy_returns):.2f}%')

            ax2.set_title('Distribution of Returns on Buy Signals', fontweight='bold')

def main():            ax2.set_xlabel('5-Day Return (%)')

    """Run proper train/test evaluation"""            ax2.set_ylabel('Frequency')

            ax2.legend()

    print("🎯 PROPER VGP-NEAT EVALUATION")            ax2.grid(True, alpha=0.3)

    print("=" * 50)        else:

    print("📚 Training: 2020-2024 (Historical)")            ax2.text(0.5, 0.5, 'No Buy Signals Made', ha='center', va='center',

    print("🧪 Testing: 2025 (Completely Unseen)")                    transform=ax2.transAxes, fontsize=16)

    print("=" * 50)            ax2.set_title('No Buy Signals to Analyze')



    evaluator = ProperTrainTestEvaluator()        plt.tight_layout()

        plt.savefig('real_performance_2025.png', dpi=300, bbox_inches='tight')

    # Step 1: Split data        print("📊 Real performance chart saved: real_performance_2025.png")

    train_data, test_data = evaluator.split_data_by_year('data/TSLA_enhanced_data.csv')

def main():

    # Step 2: Load the aggressive model (or train if it doesn't exist)    """Run proper train/test evaluation"""

    model = NEATTradingModel("neat_config.txt")

    try:    print("🎯 PROPER VGP-NEAT EVALUATION")

        model.load_model("vgp_neat_AGGRESSIVE_trained.pkl")    print("=" * 50)

        print("✅ Loaded aggressive model with real VGP signals!")    print("📚 Training: 2020-2024 (Historical)")

    except FileNotFoundError:    print("🧪 Testing: 2025 (Completely Unseen)")

        print("⚠️  Aggressive model not found, training new one with real VGP signals...")    print("=" * 50)

        winner = model.train('data/TSLA_train_2020_2024.csv', generations=15)

        model.save_model("vgp_neat_AGGRESSIVE_trained.pkl")    evaluator = ProperTrainTestEvaluator()

        print("✅ New aggressive model trained and saved!")

    # Step 1: Split data

    # Step 3: Test on completely unseen 2025 data with REAL portfolio tracking    train_data, test_data = evaluator.split_data_by_year('data/TSLA_enhanced_data.csv')

    predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value = evaluator.evaluate_on_unseen_data(

        model, 'data/TSLA_test_2025.csv')    # Step 2: Load the aggressive model (or train if it doesn't exist)

    model = NEATTradingModel("neat_config.txt")

    # Step 4: Calculate real metrics with actual portfolio performance    try:

    metrics = evaluator.calculate_real_performance_metrics(        model.load_model("vgp_neat_AGGRESSIVE_trained.pkl")

        predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value)        print("✅ Loaded aggressive model with real VGP signals!")

    except FileNotFoundError:

    # Step 5: Plot results        print("⚠️  Aggressive model not found, training new one with real VGP signals...")

    evaluator.plot_real_performance(trades_made, metrics)        winner = model.train('data/TSLA_train_2020_2024.csv', generations=15)

        model.save_model("vgp_neat_AGGRESSIVE_trained.pkl")

    print("\n🏆 EVALUATION COMPLETE!")        print("✅ New aggressive model trained and saved!")

    print("✅ These are REAL performance metrics on unseen data")

    print("💰 Model now considers CASH AVAILABILITY during training")    # Step 3: Test on completely unseen 2025 data with REAL portfolio tracking

    print("🎯 VGP signals are PRIORITIZED with 2x weight in feature vector")    predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value = evaluator.evaluate_on_unseen_data(

    print("📊 Check real_performance_2025.png for visualization")        model, 'data/TSLA_test_2025.csv')



if __name__ == "__main__":    # Step 4: Calculate real metrics with actual portfolio performance

    main()    metrics = evaluator.calculate_real_performance_metrics(
        predictions, actual_returns, trades_made, portfolio_history, executed_trades, final_portfolio_value)

    # Step 5: Plot results
    evaluator.plot_real_performance(trades_made, metrics)

    print("\n🏆 EVALUATION COMPLETE!")
    print("✅ These are REAL performance metrics on unseen data")
    print("📊 Check real_performance_2025.png for visualization")

if __name__ == "__main__":
    main()