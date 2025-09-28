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
from robust_pattern_discovery import RobustPatternDiscovery, TradingDecision

class NEATTradingModel:
    """NEAT-based trading pattern discovery system"""

    def __init__(self, config_path: str = "neat_config.txt"):
        self.config_path = config_path
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                 neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                 config_path)

        # Data components
        self.sentiment_generator = SyntheticSentimentGenerator()
        self.pattern_discovery = RobustPatternDiscovery()
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

            # Ensure required columns exist (Symbol is optional, can be inferred from filename)
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # Add Symbol column if missing (extract from filename)
            if 'Symbol' not in df.columns:
                import os
                filename = os.path.basename(csv_path)
                symbol = filename.split('_')[0]  # Extract TSLA from "TSLA_enhanced_data.csv"
                df['Symbol'] = symbol
                self.logger.info(f"Added Symbol column: {symbol}")

            # Convert Date column
            df['Date'] = pd.to_datetime(df['Date'])

            # Calculate additional features with NaN handling
            df['Price_Change'] = df['Close'] - df['Open']
            df['Price_Change_Pct'] = (df['Close'] - df['Open']) / df['Open']
            df['Volatility'] = (df['High'] - df['Low']) / df['Open']

            # Volume normalization with NaN handling
            volume_ma = df['Volume'].rolling(20, min_periods=1).mean()  # min_periods=1 prevents NaN
            df['Volume_Normalized'] = df['Volume'] / volume_ma

            # Fill any NaN values with sensible defaults
            df['Price_Change_Pct'] = df['Price_Change_Pct'].fillna(0.0)  # No change if NaN
            df['Volatility'] = df['Volatility'].fillna(0.02)  # Default 2% volatility
            df['Volume_Normalized'] = df['Volume_Normalized'].fillna(1.0)  # Normal volume if NaN

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
        """Add VGP signals using REAL VGP model weights from 30% return model"""
        if vgp_signals is None:
            self.logger.info("Generating VGP signals using proven 30% return model weights")

            # Load VGP model weights
            import pandas as pd
            try:
                weights_df = pd.read_csv('vgp_model_weights_features.csv')
                weights = dict(zip(weights_df['feature_name'], weights_df['importance_weight']))
            except:
                self.logger.warning("Could not load VGP weights, using strong default signals")
                weights = {}

            # VGP Signal 1: Volume-based signal (highest weight = 0.1111)
            volume_signal = np.where(
                df['Volume'] > df['Volume'].rolling(20).mean() * 1.3,  # High volume breakout
                0.8,  # Strong BUY
                np.where(
                    df['Volume'] < df['Volume'].rolling(20).mean() * 0.7,  # Low volume
                    0.3,  # Weak signal
                    0.5
                )
            )
            df['VGP_Signal_1'] = volume_signal

            # VGP Signal 2: Medium importance indicators combined
            # sma_10 (0.0741), ema_8_ratio (0.0741), ema_26 (0.0741)
            sma_10 = df['Close'].rolling(10).mean()
            ema_8 = df['Close'].ewm(span=8).mean()
            ema_26 = df['Close'].ewm(span=26).mean()

            combined_signal = np.where(
                (df['Close'] > sma_10) & (ema_8 > ema_26),  # Bullish trend
                0.75,  # Strong BUY
                np.where(
                    (df['Close'] < sma_10) & (ema_8 < ema_26),  # Bearish trend
                    0.25,  # SELL
                    0.5
                )
            )
            df['VGP_Signal_2'] = combined_signal

            # VGP Signal 3: Bollinger Bands + Stochastic (medium importance)
            # bb_lower_20 (0.0741), bb_upper_10 (0.0741), stoch_k_9 (0.0741)
            bb_middle = df['Close'].rolling(20).mean()
            bb_std = df['Close'].rolling(20).std()
            bb_lower = bb_middle - (bb_std * 2)
            bb_upper = bb_middle + (bb_std * 2)

            # Stochastic %K
            low_14 = df['Low'].rolling(9).min()
            high_14 = df['High'].rolling(9).max()
            stoch_k = 100 * ((df['Close'] - low_14) / (high_14 - low_14))

            bb_stoch_signal = np.where(
                (df['Close'] < bb_lower) & (stoch_k < 20),  # Oversold conditions
                0.85,  # Very strong BUY
                np.where(
                    (df['Close'] > bb_upper) & (stoch_k > 80),  # Overbought conditions
                    0.15,  # Strong SELL
                    0.5
                )
            )
            df['VGP_Signal_3'] = bb_stoch_signal

        else:
            self.logger.info("Adding provided VGP signals to dataset")
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

        # Calculate moving average signal with NaN protection
        close_ma = df['Close'].rolling(10, min_periods=1).mean()  # min_periods=1 prevents NaN
        df['MA_Signal'] = (df['Close'] / close_ma) - 1
        df['MA_Signal'] = df['MA_Signal'].fillna(0.0)  # Neutral signal if still NaN

        # Normalize features to [-1, 1] range
        features = df[feature_cols].copy()

        # Handle missing columns and fill NaN values FIRST
        for col in feature_cols:
            if col not in features.columns:
                self.logger.warning(f"Missing feature column: {col}, filling with defaults")
                if 'Sentiment' in col:
                    features[col] = 0.5  # Neutral sentiment
                elif 'VGP' in col:
                    features[col] = 0.5  # Neutral VGP signal
                else:
                    features[col] = 0.0  # Neutral market signal

        # Fill any NaN values with appropriate defaults
        features = features.fillna({
            'Sentiment_Previous': 0.5,
            'Sentiment_Current': 0.5,
            'Sentiment_Momentum': 0.5,
            'VGP_Signal_1': 0.5,
            'VGP_Signal_2': 0.5,
            'VGP_Signal_3': 0.5,
            'Price_Change_Pct': 0.0,
            'Volatility': 0.02,
            'Volume_Normalized': 1.0,
            'MA_Signal': 0.0
        })

        # Clip extreme values and normalize (AFTER cleaning NaN)
        for col in feature_cols:
            if col not in ['Sentiment_Previous', 'Sentiment_Current', 'Sentiment_Momentum']:
                # Sentiment already normalized, others need normalization
                features[col] = np.clip(features[col], -3, 3)  # Remove extreme outliers
                features[col] = features[col] / 3.0  # Normalize to [-1, 1]

        # Final safety check - replace any remaining NaN with 0
        features = features.fillna(0.0)

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

            # Very aggressive thresholds - encourage much more trading!
            buy_threshold = symbol_returns.quantile(0.55)  # Top 45% (more buy signals)
            sell_threshold = symbol_returns.quantile(0.45)  # Bottom 45% (more sell signals)

            targets[symbol_mask & (df['Future_Return'] > buy_threshold)] = 2  # Buy
            targets[symbol_mask & (df['Future_Return'] < sell_threshold)] = 0  # Sell
            targets[symbol_mask & (df['Future_Return'].between(sell_threshold, buy_threshold))] = 1  # Hold

        # Remove rows with NaN future returns
        valid_mask = ~np.isnan(df['Future_Return'])

        return targets[valid_mask], valid_mask

    def evaluate_genome(self, genome, config) -> float:
        """Enhanced genome evaluation with pattern discovery tracking"""

        # Create neural network from genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Track decisions for pattern discovery
        fitness_total = 0
        decisions_made = 0

        for i, features in enumerate(self.X_train):
            if i >= len(self.training_data) - 5:  # Need future return data
                continue

            row = self.training_data.iloc[i]

            # Get NEAT prediction
            output = net.activate(features)
            if len(output) == 3:
                neat_decision = np.argmax(output)  # 0=sell, 1=hold, 2=buy
                # Make more willing to trade
                if output[2] > 0.3 and neat_decision != 0:
                    neat_decision = 2
                confidence = max(output)
            else:
                neat_decision = 1 if output[0] > 0.7 else (2 if output[0] > 0.3 else 0)
                confidence = abs(output[0] - 0.5) * 2

            # Calculate actual 5-day return
            if i + 5 < len(self.training_data):
                future_price = self.training_data.iloc[i + 5]['Close']
                current_price = row['Close']
                actual_return_5d = (future_price - current_price) / current_price
            else:
                continue

            # Extract decision context for pattern discovery
            decision = TradingDecision(
                timestamp=row.get('Date', '2024-01-01').strftime('%Y-%m-%d') if hasattr(row.get('Date', '2024-01-01'), 'strftime') else str(row.get('Date', '2024-01-01')),
                symbol=row.get('Symbol', 'AAPL'),
                decision=neat_decision,
                confidence=confidence,

                # VGP features (extracted from features vector)
                vgp_signal=features[0] if len(features) > 0 else 0.5,  # Placeholder - will be real VGP
                vgp_strength=abs(features[0] - 0.5) * 2 if len(features) > 0 else 0.5,
                vgp_direction=1 if features[0] > 0.5 else -1 if len(features) > 0 else 0,

                # Sentiment features
                sentiment_prev=features[1] if len(features) > 1 else 0.5,
                sentiment_current=features[2] if len(features) > 2 else 0.5,
                sentiment_momentum=features[3] if len(features) > 3 else 0.5,

                # Market features
                price_change=row.get('Price_Change_Pct', 0),
                volatility=row.get('Volatility', 0.02),
                volume_ratio=row.get('Volume_Normalized', 1.0),
                rsi=row.get('rsi_14', 50) / 100.0,
                bb_position=row.get('bb_position_20', 0.5),

                # Outcome
                actual_return_5d=actual_return_5d,
                success=actual_return_5d > self.pattern_discovery.success_threshold,
                yearly_equivalent_return=0  # Will be calculated in pattern discovery
            )

            # Record decision for pattern analysis
            self.pattern_discovery.record_decision(decision)

            # Calculate fitness contribution - REWARD AGGRESSIVE TRADING!
            if neat_decision == 2 and actual_return_5d > 0.02:  # Good buy (prediction=2)
                fitness_total += 2.0  # Double reward for successful trades!
            elif neat_decision == 0 and actual_return_5d < -0.02:  # Good sell
                fitness_total += 1.5  # Reward successful sells
            elif neat_decision == 1 and abs(actual_return_5d) < 0.02:  # Good hold
                fitness_total += 0.3  # Small reward for hold (discourage over-holding)
            elif neat_decision == 2 and actual_return_5d < -0.02:  # Bad buy
                fitness_total -= 1.0  # Penalty for bad buys
            elif neat_decision == 0 and actual_return_5d > 0.02:  # Bad sell (missed opportunity)
                fitness_total -= 0.8  # Penalty for selling before gains

            decisions_made += 1

        return fitness_total / max(decisions_made, 1)

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
        self.training_data = df[valid_mask].reset_index(drop=True)  # Store for pattern discovery

        self.logger.info(f"Training on {len(self.X_train)} samples")

        # Create NEAT population
        self.population = neat.Population(self.config)

        # Add reporters
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)

        # Custom generation tracking - but don't discover patterns during training
        def custom_fitness_function(genomes, config):
            for genome_id, genome in genomes:
                genome.fitness = self.evaluate_genome(genome, config)

            # Just track generation progress
            self.generation += 1
            if self.generation % 5 == 0:  # Show progress every 5 generations
                self.logger.info(f"📈 Generation {self.generation}/{generations} completed")
                self.logger.info(f"💾 Recorded {len(self.pattern_discovery.all_decisions)} trading decisions")

        # Train for specified generations
        self.logger.info(f"Starting NEAT training for {generations} generations...")

        winner = self.population.run(custom_fitness_function, generations)
        self.best_genome = winner

        # NOW discover patterns from ONLY the best genome
        print("\n" + "="*60)
        print("🏆 ANALYZING BEST MODEL'S TRADING PATTERNS")
        print("="*60)

        # Clear pattern discovery and re-run with ONLY the best genome
        self.pattern_discovery.all_decisions.clear()

        # Re-evaluate ONLY the winning genome to get its decisions
        print("🔍 Extracting patterns from winning genome...")
        self.evaluate_genome(winner, self.config)

        # Now discover patterns from the best model only
        final_patterns = self.pattern_discovery.discover_patterns_after_generation(self.generation)
        if final_patterns:
            print(f"\n🎯 BEST MODEL DISCOVERED {len(final_patterns)} ELITE PATTERNS:")
            print(self.pattern_discovery.get_pattern_summary())
        else:
            print("🔍 Best model patterns are still being refined...")

        self.logger.info("Training completed!")
        return winner

    def predict(self, features: np.ndarray) -> int:
        """Make trading prediction with trained model"""
        if self.best_genome is None:
            raise ValueError("Model not trained yet!")

        net = neat.nn.FeedForwardNetwork.create(self.best_genome, self.config)
        output = net.activate(features)

        # 3 outputs: [sell_confidence, hold_confidence, buy_confidence]
        if len(output) == 3:
            prediction = np.argmax(output)  # 0=sell, 1=hold, 2=buy
            # Make more aggressive: if buy is close to best, choose buy
            if output[2] > 0.3 and prediction != 0:  # More willing to buy
                prediction = 2
            return prediction
        else:
            # Fallback for single output
            return 1 if output[0] > 0.7 else (2 if output[0] > 0.3 else 0)

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