@echo off
echo Building VGP Algorithmic Trader with GCC...

REM Create build directory
if not exist "build" mkdir build

echo Checking for GCC...
gcc --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo GCC not found. Please install MinGW-w64 or MSYS2.
    echo Alternative: Use Visual Studio and build_msvc.bat
    pause
    exit /b 1
)

echo Compiling source files...

REM Compile all source files
gcc -std=c++17 -O2 -Iinclude ^
    src\main.cpp ^
    src\market_data\market_data.cpp ^
    src\market_data\data_loader.cpp ^
    src\technical_indicators\technical_indicators.cpp ^
    src\vgp\vgp_engine.cpp ^
    src\backtesting\fitness_evaluator.cpp ^
    -o build\VGP_AlgoTrader.exe -lstdc++

if %ERRORLEVEL% neq 0 (
    echo Compilation failed!
    echo Make sure you have a C++17 compatible compiler installed.
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable location: build\VGP_AlgoTrader.exe
pause