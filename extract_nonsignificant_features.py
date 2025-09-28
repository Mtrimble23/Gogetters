#!/usr/bin/env python3
"""
Extract features with p-value > 0.05
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from feature_analysis import VGPFeatureAnalyzer

def main():
    print("Loading feature analysis data...")
    
    # Load the analyzer and run the feature importance calculation
    analyzer = VGPFeatureAnalyzer()
    features, returns, binary_target = analyzer.load_and_prepare_data()
    print("Calculating correlations...")
    correlation_matrix, high_corr_pairs = analyzer.calculate_correlation_analysis()
    print("Calculating feature importance...")
    feature_importance = analyzer.calculate_feature_importance_scores()

    # Filter features with p-value > 0.05
    non_significant = feature_importance[feature_importance['pearson_pval'] > 0.05]
    non_significant_sorted = non_significant.sort_values('pearson_pval', ascending=False)

    print('\nFeatures with p-value > 0.05 (sorted by p-value, highest first):')
    print('=' * 70)
    print(f"{'Rank':<4} {'Feature':<25} {'P-value':<12} {'Composite Score':<15}")
    print('-' * 70)

    for i, (_, row) in enumerate(non_significant_sorted.iterrows(), 1):
        feature_name = row['feature']
        p_val = row['pearson_pval']
        comp_score = row['composite_score']
        print(f"{i:<4} {feature_name:<25} {p_val:<12.6f} {comp_score:<15.6f}")

    print(f'\nTotal non-significant features (p > 0.05): {len(non_significant_sorted)}')
    
    # Also show the breakdown
    print(f"Total features analyzed: {len(feature_importance)}")
    print(f"Significant features (p <= 0.05): {len(feature_importance[feature_importance['pearson_pval'] <= 0.05])}")
    print(f"Non-significant features (p > 0.05): {len(non_significant_sorted)}")

if __name__ == "__main__":
    main()