@echo off
echo Building VGP Algorithmic Trader...

REM Create build directory
if not exist "build" mkdir build
cd build

REM Run CMake
cmake .. -G "Visual Studio 17 2022" -A x64
if %ERRORLEVEL% neq 0 (
    echo CMake configuration failed!
    pause
    exit /b 1
)

REM Build the project
cmake --build . --config Release
if %ERRORLEVEL% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable location: build\Release\VGP_AlgoTrader.exe
pause