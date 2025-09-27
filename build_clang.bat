@echo off
echo Building VGP Algorithmic Trader with Clang...

REM Create build directory
if not exist "build" mkdir build

echo Checking for Clang...
clang++ --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Clang not found. Please make sure LLVM is installed and in PATH.
    pause
    exit /b 1
)

echo Compiling source files...

REM Use clang++ with proper Windows settings
clang++ -std=c++17 -O2 -Iinclude ^
    -target x86_64-pc-windows-msvc ^
    -fms-compatibility-version=19 ^
    src\main.cpp ^
    src\market_data\market_data.cpp ^
    src\technical_indicators\technical_indicators.cpp ^
    src\vgp\vgp_engine.cpp ^
    src\backtesting\fitness_evaluator.cpp ^
    -o build\VGP_AlgoTrader.exe

if %ERRORLEVEL% neq 0 (
    echo Compilation failed! Trying alternative approach...
    echo.
    
    REM Try with MinGW target instead
    echo Trying MinGW-compatible compilation...
    clang++ -std=c++17 -O2 -Iinclude ^
        -target x86_64-w64-mingw32 ^
        src\main.cpp ^
        src\market_data\market_data.cpp ^
        src\technical_indicators\technical_indicators.cpp ^
        src\vgp\vgp_engine.cpp ^
        src\backtesting\fitness_evaluator.cpp ^
        -o build\VGP_AlgoTrader.exe -static-libgcc -static-libstdc++
    
    if %ERRORLEVEL% neq 0 (
        echo Both compilation attempts failed!
        echo You may need to install Visual Studio Build Tools or use a different compiler.
        pause
        exit /b 1
    )
)

echo Build completed successfully!
echo Executable location: build\VGP_AlgoTrader.exe
pause