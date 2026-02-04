@echo off
echo Installing dependencies from local 'packages' folder...
echo.

if not exist packages (
    echo Error: 'packages' folder not found.
    echo Please run 'download_deps.bat' on an internet-connected PC first,
    echo and ensure the 'packages' folder is copied here.
    pause
    exit /b 1
)

echo [1/1] Installing requirements...
python -m pip install --no-index --find-links=./packages -r requirements.txt

echo.
echo Installation Complete.
echo You can now run the tool using: python tools/generate_shadow_recursive.py
pause
