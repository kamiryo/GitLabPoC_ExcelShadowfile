@echo off
cd /d %~dp0

echo [1/2] Installing/Verifying dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to install dependencies.
    echo Please check your internet connection and python installation.
    pause
    exit /b 1
)

echo.
echo [2/2] Running Shadow Generator...
python tools/generate_shadow_recursive.py %*

if %errorlevel% neq 0 (
    echo.
    echo Execution finished with error.
) else (
    echo.
    echo Done.
)
pause
