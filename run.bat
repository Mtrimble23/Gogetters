@echo off
echo Running VGP Algorithmic Trader...

if not exist "build\Release\VGP_AlgoTrader.exe" (
    echo Executable not found! Please build the project first using build.bat
    pause
    exit /b 1
)

cd build\Release
VGP_AlgoTrader.exe ..\..\config.txt

echo.
echo Results should be saved in vgp_trading_results.txt
pause