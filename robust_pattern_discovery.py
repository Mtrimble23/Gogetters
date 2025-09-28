#!/usr/bin/env python3
"""
Robust Pattern Discovery via Clustering
Finds natural patterns in NEAT trading decisions without hardcoded rules
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import logging

@dataclass
class TradingDecision:
    """Records every NEAT trading decision"""
    timestamp: str
    symbol: str
    decision: int  # -1=sell, 0=hold, 1=buy
    confidence: float

    # VGP Features (40% weight)
    vgp_signal: float
    vgp_strength: float
    vgp_direction: int

    # Sentiment Features (30% weight)
    sentiment_prev: float
    sentiment_current: float
    sentiment_momentum: float

    # Market Features (30% weight)
    price_change: float
    volatility: float
    volume_ratio: float
    rsi: float
    bb_position: float

    # Outcome
    actual_return_5d: float
    success: bool
    yearly_equivalent_return: float

@dataclass
class DiscoveredPattern:
    """Naturally discovered trading pattern from clustering"""
    pattern_id: int
    cluster_size: int
    success_rate: float
    avg_yearly_return: float

    # Feature ranges that define this pattern
    vgp_signal_range: Tuple[float, float]
    vgp_strength_range: Tuple[float, float]
    sentiment_current_range: Tuple[float, float]
    sentiment_momentum_range: Tuple[float, float]
    volatility_range: Tuple[float, float]
    rsi_range: Tuple[float, float]

    # Human description
    description: str
    confidence_score: float
    example_decisions: List[TradingDecision]

class RobustPatternDiscovery:
    """Discovers trading patterns through unsupervised clustering"""

    def __init__(self):
        self.all_decisions: List[TradingDecision] = []
        self.discovered_patterns: List[DiscoveredPattern] = []
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)

        # Success threshold: 10% yearly return ≈ 1.5% per 5-day period
        self.yearly_target = 0.10
        self.period_days = 5
        self.trading_days_per_year = 252
        self.success_threshold = self.calculate_period_threshold()

    def calculate_period_threshold(self) -> float:
        """Convert 10% yearly return to 5-day period equivalent"""
        periods_per_year = self.trading_days_per_year / self.period_days
        period_return = (1 + self.yearly_target) ** (1/periods_per_year) - 1
        self.logger.info(f"Success threshold: {period_return:.4f} per {self.period_days}-day period ({self.yearly_target:.1%} yearly)")
        return period_return

    def record_decision(self, decision: TradingDecision):
        """Record a NEAT trading decision with full context"""
        # Calculate yearly equivalent return (FIXED - use realistic scaling)
        if decision.actual_return_5d is not None:
            # Use simple linear scaling - more realistic for trading analysis
            periods_per_year = self.trading_days_per_year / self.period_days  # 252/5 = 50.4 periods per year

            # Simple scaling: if you get X% every 5 days, yearly = X% * 50.4
            # This assumes you can consistently achieve this return (optimistic but realistic)
            yearly_equiv = decision.actual_return_5d * periods_per_year

            # Cap at reasonable limits: -95% to +500% yearly (still aggressive but not insane)
            yearly_equiv = max(-0.95, min(5.0, yearly_equiv))

            decision.yearly_equivalent_return = yearly_equiv
            decision.success = decision.actual_return_5d > self.success_threshold

        self.all_decisions.append(decision)

    def extract_feature_vector(self, decision: TradingDecision) -> np.ndarray:
        """Extract weighted feature vector from decision"""

        # VGP features (40% weight = 0.4 total)
        vgp_features = np.array([
            decision.vgp_signal,
            decision.vgp_strength,
            decision.vgp_direction
        ]) * 0.4 / 3  # Normalize to 40% total weight

        # Sentiment features (30% weight = 0.3 total)
        sentiment_features = np.array([
            decision.sentiment_prev,
            decision.sentiment_current,
            decision.sentiment_momentum
        ]) * 0.3 / 3  # Normalize to 30% total weight

        # Market features (30% weight = 0.3 total)
        market_features = np.array([
            decision.price_change,
            decision.volatility,
            decision.volume_ratio,
            decision.rsi,
            decision.bb_position
        ]) * 0.3 / 5  # Normalize to 30% total weight

        return np.concatenate([vgp_features, sentiment_features, market_features])

    def discover_patterns_after_generation(self, generation: int) -> List[DiscoveredPattern]:
        """Run clustering after each NEAT generation to find patterns"""

        self.logger.info(f"🔍 Discovering patterns after generation {generation}")

        # Filter to successful decisions only
        successful_decisions = [d for d in self.all_decisions if d.success and d.decision == 1]

        if len(successful_decisions) < 20:  # Reduced threshold for faster testing
            self.logger.info(f"Only {len(successful_decisions)} successful decisions. Need ≥20 for clustering.")
            return []

        # Extract feature vectors
        feature_vectors = np.array([self.extract_feature_vector(d) for d in successful_decisions])

        # Standardize features for clustering
        feature_vectors_scaled = self.scaler.fit_transform(feature_vectors)

        # DBSCAN clustering to find natural patterns
        eps, min_samples = self.optimize_dbscan_params(feature_vectors_scaled)

        clustering = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = clustering.fit_predict(feature_vectors_scaled)

        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        self.logger.info(f"Found {n_clusters} potential patterns")

        # Extract patterns from clusters
        patterns = []
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Skip noise points
                continue

            cluster_decisions = [successful_decisions[i] for i, label in enumerate(cluster_labels) if label == cluster_id]

            if len(cluster_decisions) < 10:  # Relaxed for testing (was 20)
                continue

            pattern = self.analyze_cluster(cluster_id, cluster_decisions)
            # Relaxed criteria for testing: 70% success rate + 10% yearly return
            if pattern.success_rate > 0.7 and pattern.avg_yearly_return > 0.10:
                patterns.append(pattern)

        self.discovered_patterns = patterns

        # ALWAYS visualize if we have any successful decisions (relaxed requirements)
        if len(successful_decisions) >= 10:  # Much lower threshold
            try:
                from visualize_clustering import ClusteringVisualizer
                visualizer = ClusteringVisualizer()

                print(f"\n🎨 Generating clustering visualizations ({len(patterns)} elite patterns, {n_clusters} total clusters)...")
                visualizer.visualize_clusters(feature_vectors_scaled, cluster_labels, successful_decisions, 'PCA')
                visualizer.analyze_feature_importance(feature_vectors, cluster_labels)
                visualizer.plot_return_distribution(successful_decisions, cluster_labels)
                print("📊 Visualizations saved! Check clustering_visualization_pca.png, pattern_feature_heatmap.png, return_distributions.png")
            except Exception as e:
                self.logger.warning(f"Visualization failed: {e}")
                import traceback
                traceback.print_exc()  # Show full error for debugging
        else:
            self.logger.info(f"Need more successful decisions for visualization: {len(successful_decisions)} found, need ≥10")

        return patterns

    def optimize_dbscan_params(self, feature_vectors: np.ndarray) -> Tuple[float, int]:
        """Find optimal DBSCAN parameters"""

        best_score = -1
        best_eps = 0.5
        best_min_samples = 5

        # Grid search for best parameters (more restrictive for fewer, better clusters)
        eps_values = [0.4, 0.5, 0.6, 0.7, 0.8]
        min_samples_values = [15, 20, 25, 30]  # Larger minimum cluster sizes

        for eps in eps_values:
            for min_samples in min_samples_values:
                if min_samples > len(feature_vectors) // 3:  # Too restrictive
                    continue

                clustering = DBSCAN(eps=eps, min_samples=min_samples)
                labels = clustering.fit_predict(feature_vectors)

                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

                # Good clustering: 2-5 clusters (fewer, higher quality patterns)
                if 2 <= n_clusters <= 5:
                    noise_ratio = np.sum(labels == -1) / len(labels)
                    if noise_ratio < 0.3:  # Less than 30% noise
                        try:
                            score = silhouette_score(feature_vectors, labels)
                            if score > best_score:
                                best_score = score
                                best_eps = eps
                                best_min_samples = min_samples
                        except:
                            continue

        return best_eps, best_min_samples

    def analyze_cluster(self, cluster_id: int, decisions: List[TradingDecision]) -> DiscoveredPattern:
        """Analyze a cluster to extract pattern characteristics"""

        # Calculate cluster statistics
        returns = [d.yearly_equivalent_return for d in decisions if d.yearly_equivalent_return is not None]
        avg_return = np.mean(returns) if returns else 0
        success_rate = np.mean([d.success for d in decisions])

        # Calculate feature ranges that define this cluster
        vgp_signals = [d.vgp_signal for d in decisions]
        vgp_strengths = [d.vgp_strength for d in decisions]
        sentiment_currents = [d.sentiment_current for d in decisions]
        sentiment_momentums = [d.sentiment_momentum for d in decisions]
        volatilities = [d.volatility for d in decisions]
        rsis = [d.rsi for d in decisions]

        # Define ranges (10th to 90th percentile to avoid outliers)
        def get_range(values):
            return (np.percentile(values, 10), np.percentile(values, 90))

        pattern = DiscoveredPattern(
            pattern_id=cluster_id,
            cluster_size=len(decisions),
            success_rate=success_rate,
            avg_yearly_return=avg_return,
            vgp_signal_range=get_range(vgp_signals),
            vgp_strength_range=get_range(vgp_strengths),
            sentiment_current_range=get_range(sentiment_currents),
            sentiment_momentum_range=get_range(sentiment_momentums),
            volatility_range=get_range(volatilities),
            rsi_range=get_range(rsis),
            description=self.generate_pattern_description(decisions),
            confidence_score=success_rate * min(1.0, len(decisions) / 20),  # Confidence based on success rate and sample size
            example_decisions=decisions[:3]  # Keep a few examples
        )

        return pattern

    def generate_pattern_description(self, decisions: List[TradingDecision]) -> str:
        """Generate human-readable description of the pattern"""

        # Calculate average characteristics
        avg_vgp = np.mean([d.vgp_signal for d in decisions])
        avg_sentiment = np.mean([d.sentiment_current for d in decisions])
        avg_volatility = np.mean([d.volatility for d in decisions])
        avg_rsi = np.mean([d.rsi for d in decisions])

        description_parts = []

        # VGP component
        if avg_vgp > 0.7:
            description_parts.append("Strong VGP Buy Signal")
        elif avg_vgp > 0.6:
            description_parts.append("Moderate VGP Signal")

        # Sentiment component
        if avg_sentiment > 0.7:
            description_parts.append("Very Positive Sentiment")
        elif avg_sentiment > 0.6:
            description_parts.append("Positive Sentiment")
        elif avg_sentiment < 0.4:
            description_parts.append("Negative Sentiment")

        # Market conditions
        if avg_volatility > 0.05:
            description_parts.append("High Volatility")
        elif avg_volatility > 0.03:
            description_parts.append("Moderate Volatility")

        if avg_rsi < 0.35:
            description_parts.append("Oversold Conditions")
        elif avg_rsi > 0.65:
            description_parts.append("Overbought Conditions")

        return " + ".join(description_parts) if description_parts else "Mixed Market Conditions"

    def get_pattern_summary(self) -> str:
        """Generate summary of discovered patterns"""

        if not self.discovered_patterns:
            return "🔍 No consistent profitable patterns discovered yet."

        summary = f"🎯 **DISCOVERED {len(self.discovered_patterns)} PROFITABLE PATTERNS**\n\n"

        # Sort patterns by return potential
        sorted_patterns = sorted(self.discovered_patterns, key=lambda p: p.avg_yearly_return, reverse=True)

        for i, pattern in enumerate(sorted_patterns, 1):
            summary += f"**Pattern #{i}: {pattern.description}**\n"
            summary += f"• Yearly Return: {pattern.avg_yearly_return:.1%}\n"
            summary += f"• Success Rate: {pattern.success_rate:.1%}\n"
            summary += f"• Occurrences: {pattern.cluster_size} times\n"
            summary += f"• Confidence: {pattern.confidence_score:.1%}\n\n"

        return summary

if __name__ == "__main__":
    print("🚀 Robust Pattern Discovery via Clustering")
    print(f"💡 Success Threshold: >10% yearly return")
    print("🔍 Discovers patterns automatically without hardcoded rules")

    discovery = RobustPatternDiscovery()
    print(f"📊 Period threshold: {discovery.success_threshold:.3%} per 5-day period")