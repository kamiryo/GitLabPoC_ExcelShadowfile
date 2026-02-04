@echo off
echo Downloading dependencies for Offline Installation...
echo.

if not exist packages mkdir packages

echo [1/2] Upgrading pip...
python -m pip install --upgrade pip

echo [2/2] Downloading Wheels...
rem Download dependencies for Windows (assuming target is Windows x64)
rem If target Python version is different, you might need --python-version 3.11 etc.
python -m pip download -d ./packages -r requirements.txt

echo.
echo Download Complete.
echo Please copy the whole 'PoC3_LocalShadow' folder to your air-gapped machine.
echo Then run 'install_offline.bat'.
pause
