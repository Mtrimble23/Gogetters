# VGP Algorithmic Trader

An algorithmic trading system using Vector Genetic Programming (VGP) to evolve trading strategies.

## 🎯 Project Overview

This hackathon project implements a sophisticated VGP-based algorithmic trading system that:
- **Processes market data** (OHLCV) and derives comprehensive features
- **Calculates technical indicators** (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, etc.)
- **Uses genetic programming** to evolve profitable trading rules
- **Backtests strategies** with comprehensive fitness evaluation including Sharpe ratio, drawdown analysis, and PnL optimization

## 🏗️ Architecture

```
VTHacks26/
├── include/
│   ├── market_data/         # Market data structures and processing
│   ├── technical_indicators/ # 15+ technical analysis indicators  
│   ├── vgp/                # Vector Genetic Programming engine
│   └── backtesting/        # Strategy evaluation and backtesting
├── src/                    # Implementation files
├── data/                   # Market data directory
├── config.txt              # Configuration file
├── build_gcc.bat          # GCC build script
├── build.sh               # Linux/Mac build script
└── run.bat                # Windows run script
```

## ✨ Key Features

### 📈 Market Data Processing
- **OHLCV data structures** with candlestick pattern analysis
- **Price returns, log returns** calculation
- **Price velocity and acceleration** for momentum analysis  
- **Volume analysis** and volume-weighted features
- **Time-based features** (hour, day, month encoding)

### 📊 Technical Indicators (15+ Implemented)
- **Moving Averages**: SMA, EMA, WMA
- **Momentum**: RSI, Stochastic Oscillator, Williams %R
- **Trend**: MACD, ADX, CCI
- **Volatility**: ATR, Bollinger Bands
- **Volume**: OBV, Chaikin Money Flow (CMF)

### 🧬 VGP Engine
- **Vector-based genetic programming** with linear gene expression
- **Advanced operations**: Math functions, logical operators, conditional statements
- **Multi-objective fitness** optimization (return, Sharpe, drawdown, stability)
- **Tournament selection**, crossover, and mutation operators
- **Configurable population** size and evolution parameters

### 📉 Backtesting Framework
- **Portfolio simulation** with position management
- **Risk metrics**: Sharpe ratio, Sortino ratio, max drawdown, Calmar ratio
- **Trading metrics**: Win rate, profit factor, average trade analysis
- **Transaction costs** and slippage modeling
- **Stop-loss and take-profit** implementation

## 🚀 Getting Started

### Building the Project

#### Option 1: Using GCC/MinGW (Windows)
```bash
.\build_gcc.bat
```

#### Option 2: Using GCC (Linux/Mac)
```bash
chmod +x build.sh
./build.sh
```

#### Option 3: Manual Compilation
```bash
g++ -std=c++17 -O2 -Iinclude src/main.cpp src/market_data/market_data.cpp src/technical_indicators/technical_indicators.cpp src/vgp/vgp_engine.cpp src/backtesting/fitness_evaluator.cpp -o VGP_AlgoTrader
```

### Running the System

#### Windows
```bash
.\run.bat
```

#### Linux/Mac
```bash
./build/VGP_AlgoTrader config.txt
```

## ⚙️ Configuration

Edit `config.txt` to customize:

```ini
# Evolution Parameters
population_size=100        # VGP population size
max_generations=100       # Maximum evolution cycles
mutation_rate=0.1         # Gene mutation probability

# Trading Parameters  
initial_capital=10000.0   # Starting capital
transaction_cost=0.001    # 0.1% transaction cost

# Fitness Weights (must sum to 1.0)
return_weight=0.4         # Profit optimization
sharpe_weight=0.3         # Risk-adjusted returns
drawdown_weight=0.2       # Drawdown minimization  
stability_weight=0.1      # Strategy consistency
```

## 📊 Sample Output

```
VGP Algorithmic Trader v1.0
============================
Generated 1000 data points for symbol 
Starting VGP evolution...
Training data: 800 points
Test data: 200 points
Population size: 100
Max generations: 100
---------------------------------------------------
Generation 0 - Best fitness: 0.234567 - Avg fitness: 0.123456
Generation 1 - Best fitness: 0.345678 - Avg fitness: 0.156789
...
Generation 95 - Best fitness: 0.789012 - Avg fitness: 0.567890

Evolution completed in 45 seconds!

=== Strategy Evaluation ===
Training fitness: 0.789012

--- Test Results ---
Total Return: 15.34%
Sharpe Ratio: 1.2345
Max Drawdown: 8.92%
Win Rate: 58.33%
Number of Trades: 24
Profit Factor: 1.67
Average Trade: $63.92
```

## 🎯 Hackathon Innovation

This project demonstrates:

1. **Advanced AI/ML**: Vector Genetic Programming for automated strategy discovery
2. **Financial Engineering**: Comprehensive technical analysis and risk management
3. **Real-world Application**: Production-ready backtesting with realistic trading costs
4. **Performance Optimization**: Multi-objective fitness functions balancing profit and risk
5. **Extensibility**: Modular design allowing easy addition of new indicators and strategies

## 🛠️ Technical Details

- **Language**: C++17 with STL only (no external dependencies)
- **Algorithm**: Vector-based Genetic Programming with tournament selection
- **Fitness Function**: Multi-objective optimization (Sharpe, return, drawdown, stability)
- **Backtesting**: Event-driven simulation with position management
- **Data Processing**: OHLCV with derived features and technical indicators

## 💡 Future Enhancements

- Neural network integration (NEAT)
- Real-time data feeds
- Multi-asset portfolio optimization
- Walk-forward analysis
- Web dashboard for results visualization

## 📝 Dependencies

- **C++17** compatible compiler (GCC, Clang, MSVC)
- **Standard library only** - no external dependencies required!

---

**Built for VTHacks26** 🏆 - A sophisticated algorithmic trading system showcasing the power of genetic programming in financial markets.