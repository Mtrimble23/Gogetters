#!/usr/bin/env python3
"""
VGP Model Weight Extractor
==========================

This script extracts the weights/parameters from the best performing VGP model
using the reduced 36-feature set, formatted for use in deep learning algorithms.

The VGP model contains:
- Gene weights (importance of each feature)
- Operation weights (importance of each mathematical operation)
- Individual coefficients (model parameters)

Output formats:
- JSON for easy integration
- CSV for spreadsheet analysis
- Python dict for direct import
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Any
import time

# Import VGP components
from python_vgp import VGPEngine, FitnessEvaluator, MultiStockVGP, Individual, Operation
from reduced_features_vgp import ReducedTechnicalIndicators

class VGPWeightExtractor:
    """Extract and format VGP model weights for deep learning"""
    
    def __init__(self):
        self.reduced_features = [
            'close', 'open', 'high', 'low', 'volume', 'price_change',
            'sma_5', 'sma_5_ratio', 'sma_10', 'sma_10_ratio', 'sma_20', 'sma_50', 'sma_50_ratio',
            'sma_200', 'ema_8', 'ema_8_ratio', 'ema_12', 'ema_12_ratio', 'ema_21', 'ema_21_ratio',
            'ema_26', 'ema_26_ratio', 'ema_50', 'rsi_14', 'bb_upper_20', 'bb_lower_20',
            'bb_position_20', 'bb_upper_10', 'bb_lower_10', 'bb_position_10', 'stoch_k_14',
            'stoch_k_9', 'stoch_d_9', 'volume_sma', 'momentum_5', 'volatility'
        ]
        print(f"Expected 36 reduced features for weight extraction")
    
    def train_best_model(self) -> Individual:
        """Train and return the best VGP model using reduced features"""
        print("🔄 Training VGP model with reduced features to extract weights...")
        
        # Load data
        vgp_system = MultiStockVGP()
        data_dict = vgp_system.load_data("data")
        
        if not data_dict:
            raise ValueError("No data loaded - please ensure CSV files are in 'data' directory")
        
        print(f"Loaded {len(data_dict)} stocks for training")
        
        # Use a representative stock for training (e.g., AAPL or best performing)
        representative_stock = 'AAPL' if 'AAPL' in data_dict else list(data_dict.keys())[0]
        stock_data = data_dict[representative_stock]
        
        print(f"Training on {representative_stock} as representative stock...")
        
        # Calculate reduced features
        ti = ReducedTechnicalIndicators()
        features_df = ti.calculate_features(stock_data)
        features = features_df.values
        prices = stock_data['close'].values
        
        # Use 80% for training
        split_idx = int(0.8 * len(features))
        train_features = features[:split_idx]
        train_prices = prices[:split_idx]
        
        print(f"Training samples: {len(train_features)}")
        print(f"Features per sample: {len(train_features[0])}")
        
        # Train VGP model
        vgp_engine = VGPEngine()
        fitness_evaluator = FitnessEvaluator()
        
        # Initialize population
        vgp_engine.initialize_population(len(train_features[0]))
        population = vgp_engine.population
        
        print("Training VGP model (this may take a few minutes)...")
        
        # Training loop with progress tracking
        for generation in range(10):  # More generations for better model
            start_time = time.time()
            
            for individual in population:
                fitness = fitness_evaluator.evaluate(individual, train_features, train_prices, debug=False)
                individual.fitness = fitness
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            elapsed = time.time() - start_time
            best_fitness = population[0].fitness
            print(f"Generation {generation+1:2d}: Best fitness = {best_fitness:.6f} (took {elapsed:.1f}s)")
        
        best_model = population[0]
        print(f"✅ Training completed! Best model fitness: {best_model.fitness:.6f}")
        
        return best_model
    
    def extract_model_weights(self, model: Individual) -> Dict[str, Any]:
        """Extract all weights and parameters from the VGP model"""
        print("📊 Extracting model weights and parameters...")
        
        weights = {
            'model_metadata': {
                'model_type': 'VGP_Reduced_Features',
                'num_features': len(self.reduced_features),
                'num_genes': len(model.genes),
                'fitness_score': float(model.fitness),
                'feature_reduction': '36_of_49_original_features',
                'excluded_features': [
                    'macd_histogram', 'gap', 'rsi_21', 'macd', 'ema_50_ratio', 
                    'macd_signal', 'momentum_10', 'volume_ratio', 'sma_20_ratio',
                    'stoch_d_14', 'rsi_7', 'price_range', 'sma_200_ratio'
                ]
            },
            
            'feature_names': self.reduced_features,
            
            'gene_weights': [],
            'operation_weights': {},
            'feature_importance': {},
            
            # Aggregated weights for deep learning
            'dl_ready_weights': {
                'feature_weights': [],
                'operation_coefficients': [],
                'bias_terms': []
            }
        }
        
        # Extract individual gene information
        operation_counts = {}
        feature_usage = {}
        constants = []
        
        for i, gene in enumerate(model.genes):
            gene_info = {
                'gene_id': i,
                'type': 'unknown',
                'operation': None,
                'feature_index': None,
                'constant_value': None,
                'weight': 1.0
            }
            
            # Determine gene type based on actual Gene structure
            if gene.op is not None:
                # Operation gene
                gene_info['type'] = 'operation'
                gene_info['operation'] = gene.op.value if hasattr(gene.op, 'value') else str(gene.op)
                gene_info['weight'] = 1.0
                
                op_name = gene_info['operation']
                operation_counts[op_name] = operation_counts.get(op_name, 0) + 1
                
            elif gene.feature_idx is not None:
                # Feature gene
                gene_info['type'] = 'feature'
                gene_info['feature_index'] = gene.feature_idx
                gene_info['weight'] = 1.0
                
                # Add feature name if in range
                if gene.feature_idx < len(self.reduced_features):
                    gene_info['feature_name'] = self.reduced_features[gene.feature_idx]
                    feature_usage[self.reduced_features[gene.feature_idx]] = feature_usage.get(self.reduced_features[gene.feature_idx], 0) + 1
                    
            elif gene.value is not None:
                # Constant gene
                gene_info['type'] = 'constant'
                gene_info['constant_value'] = gene.value
                gene_info['weight'] = gene.value
                constants.append(gene.value)
                
            weights['gene_weights'].append(gene_info)
        
        # Store operation weights
        total_operations = sum(operation_counts.values())
        weights['operation_weights'] = {
            op: count / total_operations if total_operations > 0 else 0 
            for op, count in operation_counts.items()
        }
        
        # Store feature importance
        total_feature_usage = sum(feature_usage.values())
        weights['feature_importance'] = {
            feature: usage / total_feature_usage if total_feature_usage > 0 else 0 
            for feature, usage in feature_usage.items()
        }
        
        # Ensure all features are included
        for feature in self.reduced_features:
            if feature not in weights['feature_importance']:
                weights['feature_importance'][feature] = 0.0
        
        # Create deep learning ready weights
        weights['dl_ready_weights']['feature_weights'] = [
            weights['feature_importance'].get(feature, 0.0) for feature in self.reduced_features
        ]
        
        weights['dl_ready_weights']['operation_coefficients'] = list(weights['operation_weights'].values())
        
        # Create bias terms from constants
        weights['dl_ready_weights']['bias_terms'] = constants if constants else [0.0]
        
        print(f"✅ Extracted weights for {len(self.reduced_features)} features and {len(model.genes)} genes")
        return weights
    
    def save_weights(self, weights: Dict[str, Any], base_filename: str = "vgp_model_weights"):
        """Save weights in multiple formats"""
        print("💾 Saving weights in multiple formats...")
        
        # 1. JSON format (most compatible)
        json_file = f"{base_filename}.json"
        with open(json_file, 'w') as f:
            json.dump(weights, f, indent=2, default=str)
        print(f"   ✅ Saved JSON: {json_file}")
        
        # 2. CSV format for spreadsheet analysis
        # Feature weights CSV
        feature_df = pd.DataFrame({
            'feature_name': weights['feature_names'],
            'importance_weight': weights['dl_ready_weights']['feature_weights'],
            'usage_count': [weights['feature_importance'][f] * sum(weights['feature_importance'].values()) 
                           for f in weights['feature_names']]
        })
        feature_csv = f"{base_filename}_features.csv"
        feature_df.to_csv(feature_csv, index=False)
        print(f"   ✅ Saved Feature CSV: {feature_csv}")
        
        # Gene weights CSV  
        gene_df = pd.DataFrame(weights['gene_weights'])
        gene_csv = f"{base_filename}_genes.csv"
        gene_df.to_csv(gene_csv, index=False)
        print(f"   ✅ Saved Gene CSV: {gene_csv}")
        
        # 3. Python format for direct import
        python_file = f"{base_filename}.py"
        with open(python_file, 'w') as f:
            f.write("# VGP Model Weights for Deep Learning Integration\\n")
            f.write("# Generated from reduced 36-feature VGP model\\n\\n")
            f.write(f"MODEL_METADATA = {repr(weights['model_metadata'])}\\n\\n")
            f.write(f"FEATURE_NAMES = {repr(weights['feature_names'])}\\n\\n")
            f.write(f"FEATURE_WEIGHTS = {repr(weights['dl_ready_weights']['feature_weights'])}\\n\\n")
            f.write(f"OPERATION_COEFFICIENTS = {repr(weights['dl_ready_weights']['operation_coefficients'])}\\n\\n")
            f.write(f"BIAS_TERMS = {repr(weights['dl_ready_weights']['bias_terms'])}\\n\\n")
            f.write(f"FEATURE_IMPORTANCE = {repr(weights['feature_importance'])}\\n\\n")
            f.write(f"OPERATION_WEIGHTS = {repr(weights['operation_weights'])}\\n\\n")
        print(f"   ✅ Saved Python: {python_file}")
        
        return json_file, feature_csv, gene_csv, python_file
    
    def print_weight_summary(self, weights: Dict[str, Any]):
        """Print a summary of the extracted weights"""
        print("\\n" + "="*60)
        print("VGP MODEL WEIGHT SUMMARY")
        print("="*60)
        
        print(f"Model Type: {weights['model_metadata']['model_type']}")
        print(f"Features: {weights['model_metadata']['num_features']}")
        print(f"Genes: {weights['model_metadata']['num_genes']}")
        print(f"Fitness Score: {weights['model_metadata']['fitness_score']:.6f}")
        
        print(f"\\n📊 TOP 10 MOST IMPORTANT FEATURES:")
        feature_importance = weights['feature_importance']
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for i, (feature, importance) in enumerate(sorted_features[:10], 1):
            print(f"  {i:2d}. {feature:20} | Weight: {importance:.6f}")
        
        print(f"\\n⚙️ OPERATION USAGE:")
        for op, weight in weights['operation_weights'].items():
            print(f"  {op:20} | Usage: {weight:.3f} ({weight*100:.1f}%)")
        
        print(f"\\n🎯 DEEP LEARNING READY WEIGHTS:")
        print(f"  Feature weights: {len(weights['dl_ready_weights']['feature_weights'])} values")
        print(f"  Operation coeffs: {len(weights['dl_ready_weights']['operation_coefficients'])} values") 
        print(f"  Bias terms: {len(weights['dl_ready_weights']['bias_terms'])} values")
        
        # Show weight ranges for scaling reference
        fw = weights['dl_ready_weights']['feature_weights']
        print(f"  Feature weight range: {min(fw):.6f} to {max(fw):.6f}")
        
        bt = weights['dl_ready_weights']['bias_terms']
        if bt:
            print(f"  Bias term range: {min(bt):.6f} to {max(bt):.6f}")

def main():
    """Main execution"""
    print("🚀 VGP Model Weight Extractor")
    print("="*50)
    
    try:
        # Initialize extractor
        extractor = VGPWeightExtractor()
        
        # Train the best model
        best_model = extractor.train_best_model()
        
        # Extract weights
        weights = extractor.extract_model_weights(best_model)
        
        # Save in multiple formats
        files = extractor.save_weights(weights)
        
        # Print summary
        extractor.print_weight_summary(weights)
        
        print("\\n" + "="*60)
        print("✅ WEIGHT EXTRACTION COMPLETE!")
        print("="*60)
        print("Generated files for your coworker:")
        for file in files:
            print(f"  📄 {file}")
        
        print(f"\\n💡 INTEGRATION TIPS:")
        print(f"  • Use JSON format for most programming languages")
        print(f"  • Use CSV for data analysis and visualization")
        print(f"  • Use Python file for direct import in Python projects")
        print(f"  • Feature weights are normalized (0-1 scale)")
        print(f"  • Operation coefficients show relative usage")
        print(f"  • Bias terms are normalized gene weights")
        
        return weights
        
    except Exception as e:
        print(f"❌ Error during weight extraction: {e}")
        raise

if __name__ == "__main__":
    main()