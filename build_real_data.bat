@echo off
echo Building VGP Trader with Real Data Support...
echo.

REM Build the project
g++ -std=c++17 -Wall -Wextra -O2 ^
    -I"include" ^
    src/main.cpp ^
    src/market_data/market_data.cpp ^
    src/market_data/data_loader.cpp ^
    src/technical_indicators/technical_indicators.cpp ^
    src/vgp/vgp_engine.cpp ^
    src/backtesting/fitness_evaluator.cpp ^
    -o vgp_trader.exe

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo Build successful!
echo.

REM Check if data directory exists
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

REM Check if AAPL data exists
if not exist "data\AAPL_data.csv" (
    echo.
    echo ============================================
    echo  APPLE STOCK DATA REQUIRED
    echo ============================================
    echo.
    echo To run with real data, download Apple stock data:
    echo 1. Go to: https://finance.yahoo.com/quote/AAPL/history
    echo 2. Set date range: 2017-01-01 to 2024-12-01
    echo 3. Click "Download" and save as "data\AAPL_data.csv"
    echo.
    echo The program will fall back to synthetic data if file is missing.
    echo.
)

echo Ready to run! Execute: vgp_trader.exe
pause