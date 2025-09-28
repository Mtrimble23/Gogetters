#!/usr/bin/env python3
"""
DBSCAN Clustering Visualization
Shows the embedding space where patterns are discovered
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import pandas as pd
from typing import List
from robust_pattern_discovery import TradingDecision

class ClusteringVisualizer:
    """Visualize DBSCAN clustering in 2D embedding space"""

    def __init__(self):
        self.colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

    def visualize_clusters(self, feature_vectors: np.ndarray, cluster_labels: np.ndarray,
                          decisions: List[TradingDecision], method='PCA'):
        """Visualize clusters in 2D embedding space"""

        # Reduce to 2D for visualization
        if method == 'PCA':
            reducer = PCA(n_components=2)
            embedding = reducer.fit_transform(feature_vectors)
            title_suffix = "PCA Embedding"
        else:  # t-SNE
            reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(feature_vectors)//4))
            embedding = reducer.fit_transform(feature_vectors)
            title_suffix = "t-SNE Embedding"

        # Create the plot
        plt.figure(figsize=(14, 10))

        # Plot each cluster
        unique_labels = set(cluster_labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)

        for i, label in enumerate(unique_labels):
            if label == -1:
                # Noise points
                mask = cluster_labels == label
                plt.scatter(embedding[mask, 0], embedding[mask, 1],
                           c='black', marker='x', alpha=0.6, s=50, label='Noise')
            else:
                # Cluster points
                mask = cluster_labels == label
                color = self.colors[i % len(self.colors)]
                cluster_size = np.sum(mask)

                plt.scatter(embedding[mask, 0], embedding[mask, 1],
                           c=color, alpha=0.7, s=60,
                           label=f'Pattern {label+1} ({cluster_size} trades)')

        plt.title(f'DBSCAN Clustering of Trading Decisions - {title_suffix}\n'
                 f'{n_clusters} Patterns Discovered from {len(decisions)} Successful Trades',
                 fontsize=14, fontweight='bold')
        plt.xlabel('First Component', fontsize=12)
        plt.ylabel('Second Component', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save the plot
        filename = f'clustering_visualization_{method.lower()}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 Saved clustering visualization: {filename}")

        return embedding

    def analyze_feature_importance(self, feature_vectors: np.ndarray, cluster_labels: np.ndarray):
        """Analyze which features drive the clustering"""

        feature_names = [
            'VGP_Signal', 'VGP_Strength', 'VGP_Direction',           # VGP (40%)
            'Sentiment_Prev', 'Sentiment_Current', 'Sentiment_Mom',  # Sentiment (30%)
            'Price_Change', 'Volatility', 'Volume', 'RSI', 'BB_Pos'  # Market (30%)
        ]

        # Calculate feature means per cluster
        unique_labels = [l for l in set(cluster_labels) if l != -1]

        if len(unique_labels) == 0:
            print("No clusters found for feature analysis")
            return

        cluster_profiles = {}
        for label in unique_labels:
            mask = cluster_labels == label
            cluster_features = feature_vectors[mask]
            cluster_profiles[f'Pattern_{label+1}'] = np.mean(cluster_features, axis=0)

        # Create DataFrame for visualization
        profile_df = pd.DataFrame(cluster_profiles, index=feature_names)

        # Plot heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(profile_df, annot=True, cmap='RdYlBu_r', center=0,
                   fmt='.3f', linewidths=0.5)
        plt.title('Feature Profiles of Discovered Patterns\n'
                 'Higher values = More important for that pattern',
                 fontsize=14, fontweight='bold')
        plt.ylabel('Features (Weighted by Importance)', fontsize=12)
        plt.xlabel('Discovered Patterns', fontsize=12)
        plt.tight_layout()

        # Save the heatmap
        plt.savefig('pattern_feature_heatmap.png', dpi=300, bbox_inches='tight')
        print("💾 Saved feature heatmap: pattern_feature_heatmap.png")

        return profile_df

    def plot_return_distribution(self, decisions: List[TradingDecision], cluster_labels: np.ndarray):
        """Plot return distribution by cluster"""

        # Use 5-day returns instead of broken yearly calculation
        returns = [d.actual_return_5d for d in decisions if d.actual_return_5d is not None]

        # Convert to percentages for display
        returns = [r * 100 for r in returns]  # Convert to percentage

        plt.figure(figsize=(12, 6))

        # Plot overall distribution
        plt.subplot(1, 2, 1)
        plt.hist(returns, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(x=np.mean(returns), color='red', linestyle='--',
                   label=f'Mean: {np.mean(returns):.2f}%')
        plt.title('Overall Return Distribution\nAll Successful Trades (5-day periods)', fontweight='bold')
        plt.xlabel('5-Day Return (%)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plot by cluster
        plt.subplot(1, 2, 2)
        unique_labels = [l for l in set(cluster_labels) if l != -1]

        for i, label in enumerate(unique_labels):
            mask = cluster_labels == label
            cluster_returns = [returns[j] for j in range(len(returns)) if mask[j]]
            color = self.colors[i % len(self.colors)]

            if cluster_returns:  # Only plot if we have data
                plt.hist(cluster_returns, bins=15, alpha=0.6, color=color,
                        label=f'Pattern {label+1} (μ={np.mean(cluster_returns):.2f}%)')

        plt.title('Return Distribution by Pattern\nClustered Trades (5-day periods)', fontweight='bold')
        plt.xlabel('5-Day Return (%)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('return_distributions.png', dpi=300, bbox_inches='tight')
        print("💾 Saved return analysis: return_distributions.png")

if __name__ == "__main__":
    print("📊 DBSCAN Clustering Visualizer")
    print("💡 Use this after training to see the embedding space")
    print("🎯 Shows how NEAT discovers patterns in multi-dimensional space")