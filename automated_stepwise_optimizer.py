#!/usr/bin/env python3
"""
Automated Stepwise Parameter Optimizer for VGP Trading System
Systematically removes parameters with highest p-values until all remaining parameters have p < 0.05
Reruns the model after each elimination to track performance
"""

import pandas as pd
import numpy as np
import subprocess
import os
import json
import time
from datetime import datetime
from scipy import stats
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns

class VGPStepwiseOptimizer:
    def __init__(self, stock_symbol="NVDA", config_file="config.txt", p_threshold=0.05):
        self.stock_symbol = stock_symbol
        self.config_file = config_file
        self.p_threshold = p_threshold
        self.vgp_executable = "./build/VGP_AlgoTrader.exe"
        
        # Full parameter list to start with
        self.all_parameters = [
            # Basic price features
            "open", "high", "low", "close", "typical_price", "median_price", "weighted_close",
            "body_size", "upper_shadow", "lower_shadow", "is_bullish", "price_range", "price_position",
            
            # Volume features
            "volume", "volume_sma_ratio", "volume_weighted_price", "volume_spike", "volume_momentum",
            
            # Momentum features
            "price_return", "log_return", "price_change", "percent_change", 
            "price_velocity", "price_acceleration", "momentum_strength",
            
            # Technical indicators
            "SMA10", "SMA20", "SMA50", "EMA12", "EMA26", "RSI14", "MACD", "BB_UPPER_20", "BB_LOWER_20",
            
            # Add fundamental data placeholders (these would need to be implemented)
            "total_shareholders_equity", "beta_5y_monthly", "total_debt_equity", "current_ratio"
        ]
        
        self.current_parameters = self.all_parameters.copy()
        self.elimination_history = []
        self.performance_history = []
        
    def run_vgp_model(self):
        """Run the VGP model and return results"""
        print(f"🔄 Running VGP model with {len(self.current_parameters)} parameters...")
        
        try:
            # Run the VGP trader
            result = subprocess.run([self.vgp_executable, self.config_file, self.stock_symbol], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"❌ VGP execution failed: {result.stderr}")
                return None
            
            # Parse results from output
            output_lines = result.stdout.split('\n')
            results = self.parse_vgp_output(output_lines)
            
            print(f"✅ Model completed: {results['total_return']:.2f}% return, Sharpe: {results['sharpe_ratio']:.4f}")
            return results
            
        except subprocess.TimeoutExpired:
            print("❌ VGP execution timed out")
            return None
        except Exception as e:
            print(f"❌ Error running VGP: {e}")
            return None
    
    def parse_vgp_output(self, output_lines):
        """Parse VGP output to extract key metrics"""
        results = {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'num_trades': 0,
            'profit_factor': 0.0,
            'avg_trade': 0.0
        }
        
        for line in output_lines:
            if "Total Return:" in line:
                results['total_return'] = float(line.split(':')[1].strip().replace('%', ''))
            elif "Sharpe Ratio:" in line:
                results['sharpe_ratio'] = float(line.split(':')[1].strip())
            elif "Max Drawdown:" in line:
                results['max_drawdown'] = float(line.split(':')[1].strip().replace('%', ''))
            elif "Win Rate:" in line:
                results['win_rate'] = float(line.split(':')[1].strip().replace('%', ''))
            elif "Number of Trades:" in line:
                results['num_trades'] = int(line.split(':')[1].strip())
            elif "Profit Factor:" in line:
                try:
                    results['profit_factor'] = float(line.split(':')[1].strip())
                except:
                    results['profit_factor'] = 0.0
            elif "Average Trade:" in line:
                results['avg_trade'] = float(line.split('$')[1].strip())
        
        return results
    
    def analyze_parameter_significance(self, stock_data_file):
        """Analyze statistical significance of each parameter"""
        try:
            # Load the stock data
            data = pd.read_csv(f"data/{stock_data_file}")
            
            # Calculate returns for correlation analysis
            data['returns'] = data['Close'].pct_change().shift(-1)  # Next day returns
            data = data.dropna()
            
            # Calculate basic technical features
            features = self.calculate_features(data)
            
            # Calculate correlations with future returns
            correlations = {}
            p_values = {}
            
            for param in self.current_parameters:
                if param in features.columns:
                    corr, p_val = pearsonr(features[param], features['returns'])
                    correlations[param] = corr
                    p_values[param] = p_val
                else:
                    # For missing parameters, assign high p-value
                    correlations[param] = 0.0
                    p_values[param] = 0.99
            
            return correlations, p_values
            
        except Exception as e:
            print(f"❌ Error analyzing parameter significance: {e}")
            return {}, {}
    
    def calculate_features(self, data):
        """Calculate technical features from price data"""
        features = data.copy()
        
        # Basic price features
        features['typical_price'] = (data['High'] + data['Low'] + data['Close']) / 3
        features['median_price'] = (data['High'] + data['Low']) / 2
        features['weighted_close'] = (data['High'] + data['Low'] + 2*data['Close']) / 4
        features['body_size'] = abs(data['Close'] - data['Open']) / data['Open']
        features['upper_shadow'] = (data['High'] - np.maximum(data['Open'], data['Close'])) / data['Close']
        features['lower_shadow'] = (np.minimum(data['Open'], data['Close']) - data['Low']) / data['Close']
        features['is_bullish'] = (data['Close'] > data['Open']).astype(int)
        features['price_range'] = (data['High'] - data['Low']) / data['Close']
        features['price_position'] = (data['Close'] - data['Low']) / (data['High'] - data['Low'])
        
        # Volume features
        features['volume_sma_ratio'] = data['Volume'] / data['Volume'].rolling(10).mean()
        features['volume_weighted_price'] = data['Close'] * data['Volume']
        features['volume_spike'] = (data['Volume'] > data['Volume'].rolling(20).mean() * 1.5).astype(int)
        features['volume_momentum'] = data['Volume'].pct_change()
        
        # Momentum features
        features['price_return'] = data['Close'].pct_change()
        features['log_return'] = np.log(data['Close'] / data['Close'].shift(1))
        features['price_change'] = data['Close'].diff()
        features['percent_change'] = features['price_return'] * 100
        features['price_velocity'] = features['price_change'].diff()
        features['price_acceleration'] = features['price_velocity'].diff()
        features['momentum_strength'] = abs(features['price_return'])
        
        # Technical indicators (simplified versions)
        features['SMA10'] = data['Close'].rolling(10).mean()
        features['SMA20'] = data['Close'].rolling(20).mean()
        features['SMA50'] = data['Close'].rolling(50).mean()
        features['EMA12'] = data['Close'].ewm(span=12).mean()
        features['EMA26'] = data['Close'].ewm(span=26).mean()
        
        # RSI calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['RSI14'] = 100 - (100 / (1 + rs))
        
        # MACD
        features['MACD'] = features['EMA12'] - features['EMA26']
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        sma20 = data['Close'].rolling(bb_period).mean()
        std20 = data['Close'].rolling(bb_period).std()
        features['BB_UPPER_20'] = sma20 + (std20 * bb_std)
        features['BB_LOWER_20'] = sma20 - (std20 * bb_std)
        
        # Add placeholder fundamental features (would need real data)
        features['total_shareholders_equity'] = np.random.normal(0, 1, len(features))
        features['beta_5y_monthly'] = np.random.normal(1, 0.3, len(features))
        features['total_debt_equity'] = np.random.normal(0.5, 0.2, len(features))
        features['current_ratio'] = np.random.normal(2, 0.5, len(features))
        
        # Map column names to match our parameter names
        column_mapping = {
            'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
        }
        features = features.rename(columns=column_mapping)
        
        return features.fillna(0)
    
    def find_worst_parameter(self, p_values):
        """Find parameter with highest p-value above threshold"""
        worst_param = None
        worst_p_value = 0.0
        
        for param, p_val in p_values.items():
            if param in self.current_parameters and p_val > self.p_threshold and p_val > worst_p_value:
                worst_param = param
                worst_p_value = p_val
        
        return worst_param, worst_p_value
    
    def run_stepwise_optimization(self):
        """Main optimization loop"""
        print("🚀 Starting Stepwise Parameter Optimization")
        print(f"📊 Stock: {self.stock_symbol}")
        print(f"🎯 Target p-value: < {self.p_threshold}")
        print(f"📈 Starting with {len(self.current_parameters)} parameters")
        print("=" * 60)
        
        iteration = 0
        
        while True:
            iteration += 1
            print(f"\n🔄 ITERATION {iteration}")
            print(f"Parameters remaining: {len(self.current_parameters)}")
            
            # Run the model with current parameters
            results = self.run_vgp_model()
            if results is None:
                print("❌ Failed to run model, stopping optimization")
                break
            
            # Analyze parameter significance
            correlations, p_values = self.analyze_parameter_significance(f"{self.stock_symbol}_data.csv")
            
            # Find parameter with highest p-value above threshold
            worst_param, worst_p_value = self.find_worst_parameter(p_values)
            
            # Record this iteration
            iteration_data = {
                'iteration': iteration,
                'parameters_count': len(self.current_parameters),
                'eliminated_parameter': worst_param,
                'eliminated_p_value': worst_p_value,
                'results': results,
                'p_values': {k: v for k, v in p_values.items() if k in self.current_parameters},
                'correlations': {k: v for k, v in correlations.items() if k in self.current_parameters},
                'timestamp': datetime.now().isoformat()
            }
            
            self.elimination_history.append(iteration_data)
            self.performance_history.append(results)
            
            # Display results
            print(f"📈 Performance: {results['total_return']:.2f}% return, {results['sharpe_ratio']:.4f} Sharpe")
            
            if worst_param is None:
                print(f"✅ Optimization complete! All parameters have p-value < {self.p_threshold}")
                break
            
            print(f"🗑️  Eliminating '{worst_param}' (p-value: {worst_p_value:.6f})")
            self.current_parameters.remove(worst_param)
            
            # Update the VGP system to use only current parameters
            # (This would require modifying the C++ code or configuration)
            
            if len(self.current_parameters) <= 3:
                print("⚠️  Stopping optimization - too few parameters remaining")
                break
        
        # Save results
        self.save_optimization_results()
        self.create_optimization_report()
        
        print("\n🎉 Stepwise optimization completed!")
        return self.elimination_history
    
    def save_optimization_results(self):
        """Save optimization results to JSON file"""
        results = {
            'stock_symbol': self.stock_symbol,
            'p_threshold': self.p_threshold,
            'initial_parameters': len(self.all_parameters),
            'final_parameters': len(self.current_parameters),
            'remaining_parameters': self.current_parameters,
            'elimination_history': self.elimination_history,
            'optimization_timestamp': datetime.now().isoformat()
        }
        
        filename = f"stepwise_optimization_{self.stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
    
    def create_optimization_report(self):
        """Create a comprehensive optimization report"""
        if not self.elimination_history:
            return
        
        # Create performance tracking plot
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Performance over iterations
        plt.subplot(2, 2, 1)
        iterations = [h['iteration'] for h in self.elimination_history]
        returns = [h['results']['total_return'] for h in self.elimination_history]
        sharpes = [h['results']['sharpe_ratio'] for h in self.elimination_history]
        
        plt.plot(iterations, returns, 'b-o', label='Total Return (%)', linewidth=2)
        plt.xlabel('Iteration')
        plt.ylabel('Total Return (%)', color='b')
        plt.title('Performance vs Parameter Count')
        plt.grid(True, alpha=0.3)
        
        # Add Sharpe ratio on secondary y-axis
        plt.twinx()
        plt.plot(iterations, sharpes, 'r-s', label='Sharpe Ratio', linewidth=2)
        plt.ylabel('Sharpe Ratio', color='r')
        
        # Plot 2: Parameter count over iterations
        plt.subplot(2, 2, 2)
        param_counts = [h['parameters_count'] for h in self.elimination_history]
        plt.plot(iterations, param_counts, 'g-o', linewidth=2)
        plt.xlabel('Iteration')
        plt.ylabel('Number of Parameters')
        plt.title('Parameter Reduction')
        plt.grid(True, alpha=0.3)
        
        # Plot 3: P-value distribution for final model
        plt.subplot(2, 2, 3)
        if self.elimination_history:
            final_p_values = list(self.elimination_history[-1]['p_values'].values())
            plt.hist(final_p_values, bins=20, alpha=0.7, edgecolor='black')
            plt.axvline(x=self.p_threshold, color='red', linestyle='--', 
                       label=f'Threshold (p={self.p_threshold})')
            plt.xlabel('P-value')
            plt.ylabel('Frequency')
            plt.title('Final P-value Distribution')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        # Plot 4: Key metrics comparison
        plt.subplot(2, 2, 4)
        metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
        initial_values = [self.elimination_history[0]['results'][m] for m in metrics]
        final_values = [self.elimination_history[-1]['results'][m] for m in metrics]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        plt.bar(x - width/2, initial_values, width, label='Initial', alpha=0.7)
        plt.bar(x + width/2, final_values, width, label='Final', alpha=0.7)
        plt.xlabel('Metrics')
        plt.ylabel('Values')
        plt.title('Initial vs Final Performance')
        plt.xticks(x, [m.replace('_', ' ').title() for m in metrics], rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f"stepwise_optimization_report_{self.stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 Report saved to: {plot_filename}")

def main():
    """Main function"""
    print("🧬 VGP Stepwise Parameter Optimizer")
    print("=" * 50)
    
    # Get user input
    stock_symbol = input("Enter stock symbol (default: NVDA): ").strip().upper() or "NVDA"
    
    try:
        p_threshold = float(input("Enter p-value threshold (default: 0.05): ") or "0.05")
    except:
        p_threshold = 0.05
    
    # Create optimizer
    optimizer = VGPStepwiseOptimizer(stock_symbol=stock_symbol, p_threshold=p_threshold)
    
    # Run optimization
    try:
        results = optimizer.run_stepwise_optimization()
        
        print("\n" + "="*60)
        print("🎯 OPTIMIZATION SUMMARY")
        print(f"📊 Stock: {stock_symbol}")
        print(f"🔄 Iterations: {len(results)}")
        print(f"📉 Parameters reduced: {len(optimizer.all_parameters)} → {len(optimizer.current_parameters)}")
        
        if results:
            final_perf = results[-1]['results']
            print(f"📈 Final performance: {final_perf['total_return']:.2f}% return")
            print(f"⚡ Final Sharpe ratio: {final_perf['sharpe_ratio']:.4f}")
            print(f"🎯 Remaining parameters: {optimizer.current_parameters}")
        
    except KeyboardInterrupt:
        print("\n❌ Optimization interrupted by user")
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")

if __name__ == "__main__":
    main()