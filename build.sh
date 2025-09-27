#!/bin/bash
# Simple build script for VGP Algorithmic Trader

echo "Building VGP Algorithmic Trader..."

# Create build directory
mkdir -p build

# Compile with g++
g++ -std=c++17 -O2 -Iinclude \
    src/main.cpp \
    src/market_data/market_data.cpp \
    src/technical_indicators/technical_indicators.cpp \
    src/vgp/vgp_engine.cpp \
    src/backtesting/fitness_evaluator.cpp \
    -o build/VGP_AlgoTrader

if [ $? -eq 0 ]; then
    echo "Build completed successfully!"
    echo "Executable location: build/VGP_AlgoTrader"
else
    echo "Build failed!"
    exit 1
fi