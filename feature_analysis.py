"""
Feature Analysis for VGP Trading System
=======================================

This script analyzes the statistical significance and importance of technical indicators
in the VGP trading system, providing p-values, correlations, and feature reduction recommendations.

Author: VGP Analysis Team
Date: September 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from sklearn.feature_selection import mutual_info_classif, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Import our VGP system
from python_vgp import TechnicalIndicators, VGPEngine, Backtester, MultiStockVGP

class VGPFeatureAnalyzer:
    """Comprehensive feature analysis for VGP trading system"""
    
    def __init__(self):
        self.feature_names = []
        self.feature_importance = {}
        self.correlation_matrix = None
        self.p_values = {}
        
    def load_and_prepare_data(self):
        """Load data and prepare features for analysis"""
        print("📊 Loading and preparing data for feature analysis...")
        
        # Load enhanced stock data using VGP system
        vgp_system = MultiStockVGP()
        data_dict = vgp_system.load_data("data")
        print(f"Loaded {len(data_dict)} stocks for analysis")
        
        # Combine all stock data for comprehensive analysis
        all_features = []
        all_returns = []
        
        for symbol, stock_data in data_dict.items():
            print(f"Processing {symbol}...")
            
            # Calculate technical indicators
            ti = TechnicalIndicators()
            features_df = ti.calculate_features(stock_data)
            
            # Calculate forward returns (target variable)
            # Use 5-day forward return as our prediction target
            forward_returns = stock_data['close'].pct_change(5).shift(-5)
            
            # Remove NaN values
            valid_indices = ~(features_df.isnull().any(axis=1) | forward_returns.isnull())
            clean_features = features_df[valid_indices]
            clean_returns = forward_returns[valid_indices]
            
            all_features.append(clean_features)
            all_returns.append(clean_returns)
            
        # Combine all data
        self.combined_features = pd.concat(all_features, ignore_index=True)
        self.combined_returns = pd.concat(all_returns, ignore_index=True)
        self.feature_names = list(self.combined_features.columns)
        
        # Create binary classification target (positive return = 1, negative = 0)
        self.binary_target = (self.combined_returns > 0).astype(int)
        
        print(f"✅ Data prepared: {len(self.combined_features)} samples, {len(self.feature_names)} features")
        return self.combined_features, self.combined_returns, self.binary_target
    
    def calculate_correlation_analysis(self):
        """Calculate correlation matrix and identify redundant features"""
        print("\n🔗 Calculating correlation analysis...")
        
        # Calculate correlation matrix
        self.correlation_matrix = self.combined_features.corr()
        
        # Find highly correlated feature pairs (>0.8)
        high_corr_pairs = []
        for i in range(len(self.correlation_matrix.columns)):
            for j in range(i+1, len(self.correlation_matrix.columns)):
                corr_val = abs(self.correlation_matrix.iloc[i, j])
                if corr_val > 0.8:
                    high_corr_pairs.append({
                        'feature1': self.correlation_matrix.columns[i],
                        'feature2': self.correlation_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        print(f"Found {len(high_corr_pairs)} highly correlated feature pairs (>0.8)")
        
        # Store high correlation pairs
        self.high_corr_pairs = pd.DataFrame(high_corr_pairs).sort_values('correlation', ascending=False)
        
        return self.correlation_matrix, self.high_corr_pairs
    
    def calculate_feature_importance_scores(self):
        """Calculate multiple feature importance metrics"""
        print("\n📈 Calculating feature importance scores...")
        
        # Standardize features for some analyses
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(self.combined_features)
        
        # 1. Correlation with target (Pearson)
        pearson_scores = []
        pearson_pvals = []
        for i, feature in enumerate(self.feature_names):
            corr, pval = pearsonr(self.combined_features.iloc[:, i], self.combined_returns)
            pearson_scores.append(abs(corr))
            pearson_pvals.append(pval)
        
        # 2. Spearman correlation (non-parametric)
        spearman_scores = []
        spearman_pvals = []
        for i, feature in enumerate(self.feature_names):
            corr, pval = spearmanr(self.combined_features.iloc[:, i], self.combined_returns)
            spearman_scores.append(abs(corr))
            spearman_pvals.append(pval)
        
        # 3. Mutual Information (non-linear relationships)
        mi_scores = mutual_info_classif(scaled_features, self.binary_target, random_state=42)
        
        # 4. F-statistic (ANOVA)
        f_scores, f_pvals = f_classif(scaled_features, self.binary_target)
        
        # 5. Logistic Regression Coefficients
        lr = LogisticRegression(random_state=42, max_iter=1000)
        lr.fit(scaled_features, self.binary_target)
        lr_coeffs = abs(lr.coef_[0])
        
        # Combine all importance scores
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'pearson_corr': pearson_scores,
            'pearson_pval': pearson_pvals,
            'spearman_corr': spearman_scores, 
            'spearman_pval': spearman_pvals,
            'mutual_info': mi_scores,
            'f_statistic': f_scores,
            'f_pval': f_pvals,
            'lr_coeff': lr_coeffs
        })
        
        # Calculate composite importance score
        # Normalize all metrics to 0-1 scale
        for col in ['pearson_corr', 'spearman_corr', 'mutual_info', 'f_statistic', 'lr_coeff']:
            max_val = self.feature_importance[col].max()
            if max_val > 0:
                self.feature_importance[f'{col}_norm'] = self.feature_importance[col] / max_val
        
        # Composite score (average of normalized metrics)
        importance_cols = ['pearson_corr_norm', 'spearman_corr_norm', 'mutual_info_norm', 'f_statistic_norm', 'lr_coeff_norm']
        self.feature_importance['composite_score'] = self.feature_importance[importance_cols].mean(axis=1)
        
        # Sort by composite score
        self.feature_importance = self.feature_importance.sort_values('composite_score', ascending=False)
        
        print("✅ Feature importance analysis completed")
        return self.feature_importance
    
    def identify_top_features(self, n_features=15):
        """Identify top N most important features"""
        print(f"\n🏆 Identifying top {n_features} most important features...")
        
        # Get top features by composite score
        top_features = self.feature_importance.head(n_features)
        
        # Also consider statistical significance (p < 0.05)
        significant_features = self.feature_importance[
            (self.feature_importance['pearson_pval'] < 0.05) | 
            (self.feature_importance['f_pval'] < 0.05)
        ]
        
        print(f"Top features by composite score:")
        for i, row in enumerate(top_features.iterrows(), 1):
            feature = row[1]
            print(f"  {i:2d}. {feature['feature'][:25]:25} | Score: {feature['composite_score']:.4f} | Pearson p: {feature['pearson_pval']:.4f}")
        
        print(f"\n📊 {len(significant_features)} features are statistically significant (p < 0.05)")
        
        return top_features, significant_features
    
    def test_reduced_model_performance(self, n_features_list=[5, 10, 15, 20, 25]):
        """Test performance of models with reduced feature sets"""
        print("\n🧪 Testing reduced model performance...")
        
        results = []
        
        # Full model baseline
        full_features = self.combined_features.values
        full_scaler = StandardScaler()
        full_scaled = full_scaler.fit_transform(full_features)
        
        # Split data for testing
        split_idx = int(0.8 * len(full_scaled))
        X_train_full, X_test_full = full_scaled[:split_idx], full_scaled[split_idx:]
        y_train, y_test = self.binary_target[:split_idx], self.binary_target[split_idx:]
        
        # Full model performance
        full_lr = LogisticRegression(random_state=42, max_iter=1000)
        full_lr.fit(X_train_full, y_train)
        full_pred = full_lr.predict(X_test_full)
        full_accuracy = accuracy_score(y_test, full_pred)
        
        results.append({
            'n_features': len(self.feature_names),
            'feature_set': 'Full Model',
            'accuracy': full_accuracy
        })
        
        print(f"Full model ({len(self.feature_names)} features): {full_accuracy:.4f} accuracy")
        
        # Test reduced models
        for n in n_features_list:
            if n >= len(self.feature_names):
                continue
                
            # Get top N features
            top_n_features = list(self.feature_importance.head(n)['feature'])
            top_n_indices = [self.feature_names.index(f) for f in top_n_features]
            
            # Train on reduced feature set
            X_train_reduced = X_train_full[:, top_n_indices]
            X_test_reduced = X_test_full[:, top_n_indices]
            
            reduced_lr = LogisticRegression(random_state=42, max_iter=1000)
            reduced_lr.fit(X_train_reduced, y_train)
            reduced_pred = reduced_lr.predict(X_test_reduced)
            reduced_accuracy = accuracy_score(y_test, reduced_pred)
            
            results.append({
                'n_features': n,
                'feature_set': f'Top {n} Features',
                'accuracy': reduced_accuracy,
                'accuracy_loss': full_accuracy - reduced_accuracy,
                'features': top_n_features
            })
            
            print(f"Reduced model ({n} features): {reduced_accuracy:.4f} accuracy | Loss: {full_accuracy - reduced_accuracy:+.4f}")
        
        self.model_comparison = pd.DataFrame(results)
        return self.model_comparison
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations"""
        print("\n📊 Generating visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Feature Importance Rankings
        plt.subplot(2, 3, 1)
        top_20 = self.feature_importance.head(20)
        bars = plt.barh(range(len(top_20)), top_20['composite_score'])
        plt.yticks(range(len(top_20)), [f[:15] for f in top_20['feature']])
        plt.xlabel('Composite Importance Score')
        plt.title('Top 20 Most Important Features')
        plt.gca().invert_yaxis()
        
        # Color bars by significance
        for i, (_, row) in enumerate(top_20.iterrows()):
            color = 'green' if row['pearson_pval'] < 0.01 else 'orange' if row['pearson_pval'] < 0.05 else 'red'
            bars[i].set_color(color)
        
        # 2. P-value Distribution
        plt.subplot(2, 3, 2)
        plt.hist(self.feature_importance['pearson_pval'], bins=20, alpha=0.7, label='Pearson p-values')
        plt.hist(self.feature_importance['f_pval'], bins=20, alpha=0.7, label='F-test p-values')
        plt.axvline(x=0.05, color='red', linestyle='--', label='p=0.05')
        plt.axvline(x=0.01, color='darkred', linestyle='--', label='p=0.01')
        plt.xlabel('P-value')
        plt.ylabel('Count')
        plt.title('Distribution of P-values')
        plt.legend()
        
        # 3. Correlation Heatmap (top features)
        plt.subplot(2, 3, 3)
        top_features = list(self.feature_importance.head(15)['feature'])
        corr_subset = self.correlation_matrix.loc[top_features, top_features]
        sns.heatmap(corr_subset, annot=False, cmap='RdBu_r', center=0, square=True, cbar_kws={'shrink': 0.8})
        plt.title('Correlation Matrix (Top 15 Features)')
        
        # 4. Model Performance Comparison
        plt.subplot(2, 3, 4)
        if hasattr(self, 'model_comparison'):
            comp = self.model_comparison[self.model_comparison['n_features'] <= 30]  # Only show reasonable sizes
            plt.plot(comp['n_features'], comp['accuracy'], 'o-', linewidth=2, markersize=8)
            plt.xlabel('Number of Features')
            plt.ylabel('Accuracy')
            plt.title('Model Performance vs Feature Count')
            plt.grid(True, alpha=0.3)
        
        # 5. Feature Type Analysis
        plt.subplot(2, 3, 5)
        feature_types = {}
        for feature in self.feature_names:
            if 'sma' in feature or 'ema' in feature:
                feature_types['Moving Averages'] = feature_types.get('Moving Averages', 0) + 1
            elif 'rsi' in feature:
                feature_types['RSI'] = feature_types.get('RSI', 0) + 1
            elif 'bb_' in feature:
                feature_types['Bollinger Bands'] = feature_types.get('Bollinger Bands', 0) + 1
            elif 'stoch' in feature:
                feature_types['Stochastic'] = feature_types.get('Stochastic', 0) + 1
            elif 'macd' in feature:
                feature_types['MACD'] = feature_types.get('MACD', 0) + 1
            elif 'momentum' in feature:
                feature_types['Momentum'] = feature_types.get('Momentum', 0) + 1
            elif any(x in feature for x in ['volume', 'price', 'gap', 'volatility']):
                feature_types['Basic Indicators'] = feature_types.get('Basic Indicators', 0) + 1
            else:
                feature_types['Other'] = feature_types.get('Other', 0) + 1
        
        plt.pie(feature_types.values(), labels=feature_types.keys(), autopct='%1.1f%%')
        plt.title('Feature Distribution by Type')
        
        # 6. Significance vs Importance Scatter
        plt.subplot(2, 3, 6)
        scatter = plt.scatter(self.feature_importance['composite_score'], 
                            -np.log10(self.feature_importance['pearson_pval'] + 1e-10),
                            c=self.feature_importance['mutual_info'], cmap='viridis', alpha=0.7)
        plt.xlabel('Composite Importance Score')
        plt.ylabel('-log10(p-value)')
        plt.title('Feature Significance vs Importance')
        plt.colorbar(scatter, label='Mutual Information')
        
        # Add significance threshold lines
        plt.axhline(y=-np.log10(0.05), color='red', linestyle='--', alpha=0.5, label='p=0.05')
        plt.axhline(y=-np.log10(0.01), color='darkred', linestyle='--', alpha=0.5, label='p=0.01')
        plt.legend()
        
        plt.tight_layout()
        
        # Save the plot
        plt.savefig('vgp_feature_analysis.png', dpi=300, bbox_inches='tight')
        print("📊 Visualizations saved as 'vgp_feature_analysis.png'")
        
        return fig
    
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print("\n📄 Generating analysis report...")
        
        report = []
        report.append("# VGP Trading System - Feature Analysis Report")
        report.append("=" * 50)
        report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total samples analyzed: {len(self.combined_features):,}")
        report.append(f"Total features analyzed: {len(self.feature_names)}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("-" * 20)
        
        # Count significant features
        sig_01 = len(self.feature_importance[self.feature_importance['pearson_pval'] < 0.01])
        sig_05 = len(self.feature_importance[self.feature_importance['pearson_pval'] < 0.05])
        
        report.append(f"• **{sig_01} features** are highly significant (p < 0.01)")
        report.append(f"• **{sig_05} features** are statistically significant (p < 0.05)")
        report.append(f"• **{len(self.high_corr_pairs)} feature pairs** are highly correlated (r > 0.8)")
        
        if hasattr(self, 'model_comparison'):
            best_reduced = self.model_comparison[self.model_comparison['n_features'] < len(self.feature_names)].iloc[0]
            report.append(f"• **Top {best_reduced['n_features']} features** achieve {best_reduced['accuracy']:.1%} accuracy")
            report.append(f"• **Performance loss** with reduced features: {best_reduced.get('accuracy_loss', 0):.3f}")
        
        report.append("")
        
        # Top Features
        report.append("## Top 15 Most Important Features")
        report.append("-" * 35)
        report.append("| Rank | Feature | Importance | P-value | Significance |")
        report.append("|------|---------|------------|---------|--------------|")
        
        for i, (_, row) in enumerate(self.feature_importance.head(15).iterrows(), 1):
            sig_level = "***" if row['pearson_pval'] < 0.001 else "**" if row['pearson_pval'] < 0.01 else "*" if row['pearson_pval'] < 0.05 else ""
            report.append(f"| {i:2d} | {row['feature'][:20]:20} | {row['composite_score']:.4f} | {row['pearson_pval']:.4f} | {sig_level:3s} |")
        
        report.append("")
        
        # Highly Correlated Features
        if len(self.high_corr_pairs) > 0:
            report.append("## Highly Correlated Feature Pairs (r > 0.8)")
            report.append("-" * 40)
            report.append("| Feature 1 | Feature 2 | Correlation |")
            report.append("|-----------|-----------|-------------|")
            
            for _, row in self.high_corr_pairs.head(10).iterrows():
                report.append(f"| {row['feature1'][:20]:20} | {row['feature2'][:20]:20} | {row['correlation']:.3f} |")
            
            if len(self.high_corr_pairs) > 10:
                report.append(f"| ... and {len(self.high_corr_pairs) - 10} more pairs ... | | |")
        
        report.append("")
        
        # Model Performance Comparison
        if hasattr(self, 'model_comparison'):
            report.append("## Model Performance with Reduced Features")
            report.append("-" * 42)
            report.append("| Features | Accuracy | Loss vs Full | Recommended |")
            report.append("|----------|----------|--------------|-------------|")
            
            for _, row in self.model_comparison.iterrows():
                loss = row.get('accuracy_loss', 0)
                recommended = "✓" if loss < 0.01 and row['n_features'] < len(self.feature_names) else ""
                report.append(f"| {row['n_features']:8d} | {row['accuracy']:.4f} | {loss:+.4f} | {recommended:11s} |")
        
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("-" * 17)
        
        # Find optimal reduced model
        if hasattr(self, 'model_comparison'):
            good_models = self.model_comparison[
                (self.model_comparison['n_features'] < len(self.feature_names)) &
                (self.model_comparison.get('accuracy_loss', 0) < 0.01)
            ]
            
            if len(good_models) > 0:
                best_model = good_models.iloc[0]
                report.append(f"1. **Recommended reduced model**: Use top {best_model['n_features']} features")
                report.append(f"   - Maintains {best_model['accuracy']:.1%} accuracy")
                report.append(f"   - Reduces complexity by {((len(self.feature_names) - best_model['n_features']) / len(self.feature_names) * 100):.0f}%")
            else:
                report.append("1. **Keep current model**: No significant performance gain from feature reduction")
        
        # Feature removal recommendations
        if len(self.high_corr_pairs) > 0:
            report.append("2. **Remove highly correlated features** to reduce multicollinearity:")
            for _, row in self.high_corr_pairs.head(5).iterrows():
                # Recommend removing the less important feature
                importance1 = self.feature_importance[self.feature_importance['feature'] == row['feature1']]['composite_score'].iloc[0]
                importance2 = self.feature_importance[self.feature_importance['feature'] == row['feature2']]['composite_score'].iloc[0]
                remove_feature = row['feature1'] if importance1 < importance2 else row['feature2']
                report.append(f"   - Remove '{remove_feature}' (correlated with {row['correlation']:.2f})")
        
        # Statistical significance
        non_sig_features = self.feature_importance[self.feature_importance['pearson_pval'] >= 0.05]
        if len(non_sig_features) > 0:
            report.append(f"3. **Consider removing {len(non_sig_features)} non-significant features** (p ≥ 0.05)")
        
        report.append("")
        report.append("## Notes")
        report.append("- *** p < 0.001, ** p < 0.01, * p < 0.05")
        report.append("- Composite score combines correlation, mutual information, F-statistic, and logistic regression coefficients")
        report.append("- Analysis based on 5-day forward return prediction")
        
        # Write report to file
        with open('vgp_feature_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print("📄 Analysis report saved as 'vgp_feature_analysis_report.md'")
        return '\n'.join(report)

def main():
    """Main analysis pipeline"""
    print("🚀 Starting VGP Feature Analysis Pipeline")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = VGPFeatureAnalyzer()
    
    # Load and prepare data
    features, returns, binary_target = analyzer.load_and_prepare_data()
    
    # Calculate correlations
    correlation_matrix, high_corr_pairs = analyzer.calculate_correlation_analysis()
    
    # Calculate feature importance
    feature_importance = analyzer.calculate_feature_importance_scores()
    
    # Identify top features
    top_features, significant_features = analyzer.identify_top_features(n_features=15)
    
    # Test reduced models
    model_comparison = analyzer.test_reduced_model_performance()
    
    # Generate visualizations
    analyzer.generate_visualizations()
    
    # Generate report
    report = analyzer.generate_analysis_report()
    
    print("\n" + "=" * 50)
    print("🎉 VGP Feature Analysis Complete!")
    print("=" * 50)
    print("Generated files:")
    print("  • vgp_feature_analysis.png - Comprehensive visualizations")
    print("  • vgp_feature_analysis_report.md - Detailed analysis report")
    print("\nKey findings:")
    print(f"  • {len(significant_features)} statistically significant features")
    print(f"  • {len(high_corr_pairs)} highly correlated feature pairs")
    if hasattr(analyzer, 'model_comparison'):
        best_reduced = analyzer.model_comparison[analyzer.model_comparison['n_features'] < len(analyzer.feature_names)].iloc[0]
        print(f"  • Optimal reduced model: {best_reduced['n_features']} features ({best_reduced['accuracy']:.1%} accuracy)")

if __name__ == "__main__":
    main()