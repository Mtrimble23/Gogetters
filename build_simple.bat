@echo off
echo Building VGP Algorithmic Trader with MSVC...

REM Create build directory
if not exist "build" mkdir build

REM Set up Visual Studio environment (adjust path as needed)
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64 2>nul
if %ERRORLEVEL% neq 0 (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64 2>nul
    if %ERRORLEVEL% neq 0 (
        echo Visual Studio environment not found. Please install Visual Studio or Build Tools.
        echo Or manually set up the compiler environment.
        pause
        exit /b 1
    )
)

echo Compiling source files...

REM Compile all source files
cl /EHsc /std:c++17 /O2 /Iinclude ^
   src\main.cpp ^
   src\market_data\market_data.cpp ^
   src\technical_indicators\technical_indicators.cpp ^
   src\vgp\vgp_engine.cpp ^
   src\backtesting\fitness_evaluator.cpp ^
   /Fe:build\VGP_AlgoTrader.exe

if %ERRORLEVEL% neq 0 (
    echo Compilation failed!
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable location: build\VGP_AlgoTrader.exe

REM Clean up temporary files
del *.obj 2>nul

pause