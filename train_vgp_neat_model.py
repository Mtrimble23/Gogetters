#!/usr/bin/env python3
"""
VGP-NEAT Model Training Script
Train the enhanced NEAT model with VGP signals and pattern discovery
"""

import sys
import logging
from pathlib import Path
from neat_trading_model import NEATTradingModel

def main():
    """Train the VGP-NEAT hybrid model"""

    print("🚀 VGP-NEAT Algorithmic Trading Model")
    print("=" * 50)
    print("🧬 Vector Genetic Programming + NEAT Evolution")
    print("📊 Automatic Pattern Discovery")
    print("🎯 Target: >10% yearly returns")
    print("=" * 50)

    # Setup logging to both console and file (UTF-8 for emojis)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vgp_neat_training.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Check for data files
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Error: 'data' directory not found!")
        print("Run fetch_enhanced_data.py first to download stock data")
        return

    # Find available data files
    data_files = list(data_dir.glob("*_enhanced_data.csv"))
    if not data_files:
        print("❌ Error: No enhanced data files found!")
        print("Run fetch_enhanced_data.py first to download stock data")
        return

    print(f"📁 Found {len(data_files)} stock data files")

    # Use TSLA as primary training data (high volatility, good for pattern discovery)
    primary_data = "data/TSLA_enhanced_data.csv"
    if not Path(primary_data).exists():
        # Use first available file
        primary_data = str(data_files[0])
        print(f"📊 Using {primary_data} for training")
    else:
        print(f"📊 Using {primary_data} for training (Tesla - high volatility)")

    # Create and train model
    try:
        print("\n🤖 Initializing NEAT Trading Model...")
        model = NEATTradingModel("neat_config.txt")

        print("🎓 Starting training...")
        print("⏱️  This may take several minutes...")
        print("🔍 Pattern discovery will run after each generation")
        print("-" * 50)

        # Train for 10 generations (faster for testing)
        winner = model.train(primary_data, generations=10)

        print("\n" + "=" * 60)
        print("🏆 TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 60)

        # Save the trained model
        model_path = "trained_vgp_neat_model.pkl"
        model.save_model(model_path)
        print(f"💾 Model saved to: {model_path}")

        # Display final statistics
        print(f"\n📈 Training Summary:")
        print(f"• Total decisions recorded: {len(model.pattern_discovery.all_decisions)}")
        print(f"• Successful decisions: {sum(1 for d in model.pattern_discovery.all_decisions if d.success)}")
        print(f"• Patterns discovered: {len(model.pattern_discovery.discovered_patterns)}")

        if model.pattern_discovery.discovered_patterns:
            best_pattern = max(model.pattern_discovery.discovered_patterns,
                             key=lambda p: p.avg_yearly_return)
            print(f"• Best pattern return: {best_pattern.avg_yearly_return:.1%} yearly")
            print(f"• Best pattern success rate: {best_pattern.success_rate:.1%}")

        print("\n🎯 Model ready for live trading and demo!")

    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)