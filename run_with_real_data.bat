@echo off
echo 🍎 Apple Stock Data Setup for VGP Trader
echo ==========================================
echo.

echo 📦 Setting up Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.7+ from https://python.org
    echo    Make sure to add Python to your PATH during installation
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo 📥 Fetching Apple stock data...
python fetch_data.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Data fetch failed!
    echo 💡 Try installing dependencies manually:
    echo    pip install yfinance pandas
    pause
    exit /b 1
)

echo.
echo 🔨 Building VGP Trader...
call build_real_data.bat

if %errorlevel% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo 🚀 Running VGP Trader with real Apple data...
echo ==========================================
.\vgp_trader.exe

echo.
echo ✅ VGP trading analysis completed!
pause