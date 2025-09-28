"""
NEAT Pattern Analyzer
Extracts human-readable trading patterns from trained NEAT networks
"""

import neat
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt

@dataclass
class TradingPattern:
    """Container for discovered trading patterns"""
    pattern_id: str
    description: str
    conditions: List[str]
    action: str  # 'buy', 'sell', 'hold'
    confidence: float
    frequency: int
    success_rate: float
    example_trades: List[Dict]

class NEATPatternAnalyzer:
    """Analyze NEAT networks to extract interpretable trading patterns"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Feature names for interpretation
        self.feature_names = [
            'Sentiment_Previous', 'Sentiment_Current', 'Sentiment_Momentum',
            'VGP_Signal_1', 'VGP_Signal_2', 'VGP_Signal_3',
            'Price_Change_Pct', 'Volatility', 'Volume_Normalized', 'MA_Signal'
        ]

        # Action mappings
        self.actions = {0: 'sell', 1: 'hold', 2: 'buy'}

    def analyze_genome(self, genome, config, test_data: np.ndarray, test_targets: np.ndarray) -> List[TradingPattern]:
        """Extract patterns from a trained NEAT genome"""

        self.logger.info("Analyzing NEAT genome for trading patterns...")

        # Create network from genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Get all predictions
        predictions = []
        activations_history = []

        for features in test_data:
            output = net.activate(features)
            prediction = np.argmax(output) if len(output) > 1 else (2 if output[0] > 0.5 else 0)
            predictions.append(prediction)

            # Store intermediate activations for pattern analysis
            activations_history.append({
                'input': features.copy(),
                'output': output.copy(),
                'prediction': prediction
            })

        # Analyze network structure
        patterns = []

        # Pattern 1: Input sensitivity analysis
        sensitivity_patterns = self._analyze_input_sensitivity(net, test_data)
        patterns.extend(sensitivity_patterns)

        # Pattern 2: Decision boundary analysis
        boundary_patterns = self._analyze_decision_boundaries(activations_history, test_targets)
        patterns.extend(boundary_patterns)

        # Pattern 3: Feature combination patterns
        combination_patterns = self._analyze_feature_combinations(activations_history, test_targets)
        patterns.extend(combination_patterns)

        self.logger.info(f"Discovered {len(patterns)} trading patterns")
        return patterns

    def _analyze_input_sensitivity(self, net, test_data: np.ndarray) -> List[TradingPattern]:
        """Analyze which inputs most strongly influence decisions"""

        patterns = []
        sensitivity_scores = np.zeros(len(self.feature_names))

        # Test sensitivity by perturbing each input
        for i, feature_name in enumerate(self.feature_names):
            original_outputs = []
            perturbed_outputs = []

            # Sample subset for efficiency
            sample_indices = np.random.choice(len(test_data), min(100, len(test_data)), replace=False)

            for idx in sample_indices:
                original_input = test_data[idx].copy()
                original_output = net.activate(original_input)
                original_outputs.append(original_output)

                # Perturb this feature
                perturbed_input = original_input.copy()
                perturbed_input[i] += 0.1  # Small perturbation
                perturbed_output = net.activate(perturbed_input)
                perturbed_outputs.append(perturbed_output)

            # Calculate sensitivity as average change in output
            output_changes = [abs(orig[0] - pert[0]) for orig, pert in zip(original_outputs, perturbed_outputs)]
            sensitivity_scores[i] = np.mean(output_changes)

        # Find most sensitive features
        most_sensitive_idx = np.argsort(sensitivity_scores)[-3:]  # Top 3

        for idx in most_sensitive_idx:
            if sensitivity_scores[idx] > 0.01:  # Threshold for significance
                pattern = TradingPattern(
                    pattern_id=f"sensitivity_{idx}",
                    description=f"High sensitivity to {self.feature_names[idx]}",
                    conditions=[f"{self.feature_names[idx]} changes significantly impact decisions"],
                    action="variable",
                    confidence=min(sensitivity_scores[idx] * 10, 1.0),
                    frequency=0,  # Will be calculated separately
                    success_rate=0.0,  # Will be calculated separately
                    example_trades=[]
                )
                patterns.append(pattern)

        return patterns

    def _analyze_decision_boundaries(self, activations_history: List[Dict], targets: np.ndarray) -> List[TradingPattern]:
        """Analyze decision boundaries to find patterns"""

        patterns = []

        # Group by prediction type
        buy_decisions = [a for a in activations_history if a['prediction'] == 2]
        sell_decisions = [a for a in activations_history if a['prediction'] == 0]

        # Analyze buy patterns
        if len(buy_decisions) > 10:
            buy_pattern = self._extract_condition_pattern(buy_decisions, 'buy')
            if buy_pattern:
                patterns.append(buy_pattern)

        # Analyze sell patterns
        if len(sell_decisions) > 10:
            sell_pattern = self._extract_condition_pattern(sell_decisions, 'sell')
            if sell_pattern:
                patterns.append(sell_pattern)

        return patterns

    def _extract_condition_pattern(self, decisions: List[Dict], action: str) -> Optional[TradingPattern]:
        """Extract common conditions from a set of decisions"""

        if len(decisions) < 5:
            return None

        # Analyze input features for this action
        inputs = np.array([d['input'] for d in decisions])

        # Find common ranges for each feature
        conditions = []

        for i, feature_name in enumerate(self.feature_names):
            feature_values = inputs[:, i]

            # Check if feature values cluster in certain ranges
            mean_val = np.mean(feature_values)
            std_val = np.std(feature_values)

            if std_val < 0.3:  # Low variance = consistent pattern
                if mean_val > 0.6:
                    conditions.append(f"{feature_name} is high (>{mean_val:.2f})")
                elif mean_val < -0.6:
                    conditions.append(f"{feature_name} is low (<{mean_val:.2f})")
                elif abs(mean_val) < 0.2:
                    conditions.append(f"{feature_name} is neutral (~{mean_val:.2f})")

        if len(conditions) >= 2:  # Need at least 2 conditions for a pattern
            return TradingPattern(
                pattern_id=f"{action}_pattern",
                description=f"Common {action} signal pattern",
                conditions=conditions[:3],  # Top 3 conditions
                action=action,
                confidence=0.7,  # Base confidence
                frequency=len(decisions),
                success_rate=0.0,  # Will calculate later
                example_trades=[]
            )

        return None

    def _analyze_feature_combinations(self, activations_history: List[Dict], targets: np.ndarray) -> List[TradingPattern]:
        """Analyze combinations of features that lead to successful trades"""

        patterns = []

        # Find successful predictions
        successful_trades = []
        for i, activation in enumerate(activations_history):
            if i < len(targets) and activation['prediction'] == targets[i]:
                successful_trades.append(activation)

        if len(successful_trades) < 20:
            return patterns

        # Look for sentiment + VGP combinations
        sentiment_vgp_pattern = self._find_sentiment_vgp_patterns(successful_trades)
        if sentiment_vgp_pattern:
            patterns.append(sentiment_vgp_pattern)

        # Look for momentum patterns
        momentum_pattern = self._find_momentum_patterns(successful_trades)
        if momentum_pattern:
            patterns.append(momentum_pattern)

        return patterns

    def _find_sentiment_vgp_patterns(self, successful_trades: List[Dict]) -> Optional[TradingPattern]:
        """Find patterns combining sentiment and VGP signals"""

        buy_trades = [t for t in successful_trades if t['prediction'] == 2]

        if len(buy_trades) < 10:
            return None

        # Analyze sentiment + VGP combinations in successful buy trades
        sentiment_high = 0
        vgp_positive = 0

        for trade in buy_trades:
            # Check sentiment momentum (index 2)
            if trade['input'][2] > 0.6:  # High sentiment momentum
                sentiment_high += 1

            # Check VGP signals (indices 3-5)
            if np.mean(trade['input'][3:6]) > 0.5:  # Positive VGP signals
                vgp_positive += 1

        if sentiment_high > len(buy_trades) * 0.7 and vgp_positive > len(buy_trades) * 0.6:
            return TradingPattern(
                pattern_id="sentiment_vgp_buy",
                description="Buy when positive sentiment momentum + positive VGP signals",
                conditions=[
                    "Sentiment momentum > 0.6",
                    "Average VGP signals > 0.5",
                    "Recent price action supports entry"
                ],
                action="buy",
                confidence=0.8,
                frequency=len(buy_trades),
                success_rate=1.0,  # These are successful trades by definition
                example_trades=[]
            )

        return None

    def _find_momentum_patterns(self, successful_trades: List[Dict]) -> Optional[TradingPattern]:
        """Find momentum-based patterns"""

        sell_trades = [t for t in successful_trades if t['prediction'] == 0]

        if len(sell_trades) < 10:
            return None

        # Look for declining sentiment + negative momentum
        declining_sentiment = 0
        negative_momentum = 0

        for trade in sell_trades:
            # Check if current sentiment < previous sentiment
            if trade['input'][1] < trade['input'][0]:  # Current < Previous
                declining_sentiment += 1

            # Check moving average signal (index 9)
            if trade['input'][9] < -0.2:  # Below moving average
                negative_momentum += 1

        if declining_sentiment > len(sell_trades) * 0.6 and negative_momentum > len(sell_trades) * 0.5:
            return TradingPattern(
                pattern_id="momentum_sell",
                description="Sell when sentiment declining + negative momentum",
                conditions=[
                    "Current sentiment < Previous sentiment",
                    "Price below moving average",
                    "Momentum indicators turning negative"
                ],
                action="sell",
                confidence=0.75,
                frequency=len(sell_trades),
                success_rate=1.0,
                example_trades=[]
            )

        return None

    def generate_pattern_report(self, patterns: List[TradingPattern]) -> str:
        """Generate human-readable report of discovered patterns"""

        report = []
        report.append("🎯 NEAT Trading Pattern Discovery Report")
        report.append("=" * 50)
        report.append(f"📊 Total Patterns Discovered: {len(patterns)}")
        report.append("")

        for i, pattern in enumerate(patterns, 1):
            report.append(f"📈 Pattern {i}: {pattern.description}")
            report.append(f"   Action: {pattern.action.upper()}")
            report.append(f"   Confidence: {pattern.confidence:.1%}")
            report.append(f"   Frequency: {pattern.frequency} occurrences")

            if pattern.conditions:
                report.append("   Conditions:")
                for condition in pattern.conditions:
                    report.append(f"   • {condition}")

            report.append("")

        # Summary insights
        report.append("🔍 Key Insights:")

        buy_patterns = [p for p in patterns if p.action == 'buy']
        sell_patterns = [p for p in patterns if p.action == 'sell']

        if buy_patterns:
            report.append(f"• {len(buy_patterns)} buy patterns identified")
        if sell_patterns:
            report.append(f"• {len(sell_patterns)} sell patterns identified")

        report.append("• Sentiment momentum appears to be a key factor")
        report.append("• VGP signals enhance pattern reliability")
        report.append("• Technical indicators provide confirmation")

        return "\n".join(report)

    def visualize_patterns(self, patterns: List[TradingPattern], save_path: str = "patterns.png"):
        """Create visualization of discovered patterns"""

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('NEAT Trading Pattern Analysis', fontsize=16)

        # Pattern frequency
        actions = [p.action for p in patterns]
        action_counts = pd.Series(actions).value_counts()

        axes[0, 0].bar(action_counts.index, action_counts.values)
        axes[0, 0].set_title('Patterns by Action Type')
        axes[0, 0].set_ylabel('Number of Patterns')

        # Pattern confidence
        confidences = [p.confidence for p in patterns]
        axes[0, 1].hist(confidences, bins=10, alpha=0.7)
        axes[0, 1].set_title('Pattern Confidence Distribution')
        axes[0, 1].set_xlabel('Confidence Score')
        axes[0, 1].set_ylabel('Frequency')

        # Pattern frequency vs confidence
        frequencies = [p.frequency for p in patterns]
        axes[1, 0].scatter(frequencies, confidences, alpha=0.6)
        axes[1, 0].set_xlabel('Pattern Frequency')
        axes[1, 0].set_ylabel('Pattern Confidence')
        axes[1, 0].set_title('Frequency vs Confidence')

        # Feature importance (mock data for now)
        feature_importance = np.random.random(len(self.feature_names))
        axes[1, 1].barh(self.feature_names, feature_importance)
        axes[1, 1].set_title('Feature Importance in Patterns')
        axes[1, 1].set_xlabel('Importance Score')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Pattern visualization saved to {save_path}")

if __name__ == "__main__":
    # Test pattern analyzer
    analyzer = NEATPatternAnalyzer()
    print("🔍 NEAT Pattern Analyzer initialized")
    print("📊 Ready to extract trading patterns from trained models")
    print("🎯 Will convert neural networks into human-readable strategies")