"""
NEAT Trading Model Framework
Combines sentiment analysis + VGP signals + market data for pattern discovery
"""

import neat
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import pickle
import json
from datetime import datetime

from synthetic_sentiment_generator import SyntheticSentimentGenerator

class NEATTradingModel:
    """NEAT-based trading pattern discovery system"""

    def __init__(self, config_path: str = "neat_config.txt"):
        self.config_path = config_path
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                 neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                 config_path)

        # Data components
        self.sentiment_generator = SyntheticSentimentGenerator()
        self.training_data = None
        self.validation_data = None

        # Model state
        self.population = None
        self.best_genome = None
        self.generation = 0

        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_market_data(self, csv_path: str) -> pd.DataFrame:
        """Load market data from yfinance CSV"""
        self.logger.info(f"Loading market data from {csv_path}")

        try:
            df = pd.read_csv(csv_path)

            # Ensure required columns exist
            required_cols = ['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # Convert Date column
            df['Date'] = pd.to_datetime(df['Date'])

            # Calculate additional features
            df['Price_Change'] = df['Close'] - df['Open']
            df['Price_Change_Pct'] = (df['Close'] - df['Open']) / df['Open']
            df['Volatility'] = (df['High'] - df['Low']) / df['Open']
            df['Volume_Normalized'] = df['Volume'] / df['Volume'].rolling(20).mean()

            self.logger.info(f"Loaded {len(df)} records for {df['Symbol'].nunique()} symbols")
            return df

        except Exception as e:
            self.logger.error(f"Error loading market data: {e}")
            raise

    def enrich_with_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add synthetic sentiment data to market data"""
        self.logger.info("Enriching market data with sentiment...")

        sentiment_data = []

        for idx, row in df.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            symbol = row['Symbol']

            # Get synthetic sentiment for this date/symbol
            sentiment = self.sentiment_generator.get_sentiment_for_date(symbol, date_str)

            sentiment_data.append({
                'Sentiment_Previous': sentiment[0],
                'Sentiment_Current': sentiment[1],
                'Sentiment_Momentum': sentiment[2]
            })

        # Add sentiment columns to dataframe
        sentiment_df = pd.DataFrame(sentiment_data)
        enriched_df = pd.concat([df, sentiment_df], axis=1)

        self.logger.info("Sentiment enrichment completed")
        return enriched_df

    def add_vgp_signals(self, df: pd.DataFrame, vgp_signals: Optional[Dict] = None) -> pd.DataFrame:
        """Add VGP signals when available"""
        if vgp_signals is None:
            self.logger.info("No VGP signals provided, using placeholder values")
            # Placeholder VGP signals for now
            df['VGP_Signal_1'] = 0.5  # Will be replaced with real VGP outputs
            df['VGP_Signal_2'] = 0.5
            df['VGP_Signal_3'] = 0.5
        else:
            self.logger.info("Adding VGP signals to dataset")
            # TODO: Integrate real VGP signals when provided
            for signal_name, signal_values in vgp_signals.items():
                df[signal_name] = signal_values

        return df

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare input features for NEAT network"""

        # Feature columns for NEAT input
        feature_cols = [
            # Sentiment features (3)
            'Sentiment_Previous', 'Sentiment_Current', 'Sentiment_Momentum',

            # VGP signals (3)
            'VGP_Signal_1', 'VGP_Signal_2', 'VGP_Signal_3',

            # Market features (4)
            'Price_Change_Pct', 'Volatility', 'Volume_Normalized',

            # Technical indicator (1) - simple moving average signal
            'MA_Signal'
        ]

        # Calculate moving average signal
        df['MA_Signal'] = (df['Close'] / df['Close'].rolling(10).mean()) - 1
        df['MA_Signal'] = df['MA_Signal'].fillna(0)

        # Normalize features to [-1, 1] range
        features = df[feature_cols].copy()

        # Clip extreme values and normalize
        for col in feature_cols:
            if col not in ['Sentiment_Previous', 'Sentiment_Current', 'Sentiment_Momentum']:
                # Sentiment already normalized, others need normalization
                features[col] = np.clip(features[col], -3, 3)  # Remove extreme outliers
                features[col] = features[col] / 3.0  # Normalize to [-1, 1]

        features = features.fillna(0)  # Fill any remaining NaN values

        self.logger.info(f"Prepared {len(feature_cols)} features for NEAT input")
        return features.values

    def calculate_targets(self, df: pd.DataFrame, forward_days: int = 5) -> np.ndarray:
        """Calculate target labels: future price movement"""

        # Calculate future returns
        df = df.sort_values(['Symbol', 'Date'])
        df['Future_Return'] = df.groupby('Symbol')['Close'].pct_change(forward_days).shift(-forward_days)

        # Convert to classification: 0=sell, 1=hold, 2=buy
        targets = np.zeros(len(df))

        for symbol in df['Symbol'].unique():
            symbol_mask = df['Symbol'] == symbol
            symbol_returns = df.loc[symbol_mask, 'Future_Return']

            # Use symbol-specific thresholds
            buy_threshold = symbol_returns.quantile(0.7)  # Top 30%
            sell_threshold = symbol_returns.quantile(0.3)  # Bottom 30%

            targets[symbol_mask & (df['Future_Return'] > buy_threshold)] = 2  # Buy
            targets[symbol_mask & (df['Future_Return'] < sell_threshold)] = 0  # Sell
            targets[symbol_mask & (df['Future_Return'].between(sell_threshold, buy_threshold))] = 1  # Hold

        # Remove rows with NaN future returns
        valid_mask = ~np.isnan(df['Future_Return'])

        return targets[valid_mask], valid_mask

    def evaluate_genome(self, genome, config) -> float:
        """Evaluate a single NEAT genome's trading performance"""

        # Create neural network from genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Get predictions for all training data
        predictions = []
        for features in self.X_train:
            output = net.activate(features)
            # Convert network output to trading decision
            predictions.append(np.argmax(output) if len(output) > 1 else (2 if output[0] > 0.5 else 0))

        predictions = np.array(predictions)

        # Calculate fitness based on trading performance
        fitness = self.calculate_trading_fitness(predictions, self.y_train)

        return fitness

    def calculate_trading_fitness(self, predictions: np.ndarray, actual: np.ndarray) -> float:
        """Calculate fitness based on trading performance"""

        # Simple fitness: accuracy + return bias
        accuracy = np.mean(predictions == actual)

        # Bonus for predicting profitable moves correctly
        buy_correct = np.sum((predictions == 2) & (actual == 2))
        sell_correct = np.sum((predictions == 0) & (actual == 0))
        total_buy_sell = np.sum((actual == 2) | (actual == 0))

        profit_accuracy = (buy_correct + sell_correct) / max(total_buy_sell, 1)

        # Combined fitness
        fitness = 0.6 * accuracy + 0.4 * profit_accuracy

        return fitness

    def train(self, market_data_path: str, generations: int = 50):
        """Train NEAT model on market data"""

        # Load and prepare data
        self.logger.info("Preparing training data...")
        df = self.load_market_data(market_data_path)
        df = self.enrich_with_sentiment(df)
        df = self.add_vgp_signals(df)

        # Prepare features and targets
        X = self.prepare_features(df)
        y, valid_mask = self.calculate_targets(df)

        # Filter to valid samples
        self.X_train = X[valid_mask]
        self.y_train = y

        self.logger.info(f"Training on {len(self.X_train)} samples")

        # Create NEAT population
        self.population = neat.Population(self.config)

        # Add reporters
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)

        # Train for specified generations
        self.logger.info(f"Starting NEAT training for {generations} generations...")

        winner = self.population.run(self.evaluate_genome, generations)
        self.best_genome = winner

        self.logger.info("Training completed!")
        return winner

    def predict(self, features: np.ndarray) -> int:
        """Make trading prediction with trained model"""
        if self.best_genome is None:
            raise ValueError("Model not trained yet!")

        net = neat.nn.FeedForwardNetwork.create(self.best_genome, self.config)
        output = net.activate(features)

        return np.argmax(output) if len(output) > 1 else (2 if output[0] > 0.5 else 0)

    def save_model(self, filepath: str):
        """Save trained model"""
        model_data = {
            'best_genome': self.best_genome,
            'config_path': self.config_path,
            'generation': self.generation
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        self.logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.best_genome = model_data['best_genome']
        self.generation = model_data['generation']

        self.logger.info(f"Model loaded from {filepath}")

if __name__ == "__main__":
    # Test the NEAT trading model framework
    model = NEATTradingModel()

    print("🚀 NEAT Trading Model Framework Initialized")
    print("📊 Ready to load market data and train model")
    print("⚡ VGP signals can be added when available")
    print("🎯 Synthetic sentiment data integrated")

    # This will be used once you have the CSV data:
    # model.train("market_data.csv", generations=20)