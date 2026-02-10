@echo off
echo Downloading dependencies for Offline Installation...
echo.

if not exist packages mkdir packages

echo [1/2] Upgrading pip...
python -m pip install --upgrade pip

echo [2/2] Downloading Wheels...
rem Download dependencies specifically for Windows x64 and Python 3.13 (Target Environment)
rem If your offline machine is Python 3.12, change '313' to '312' below.
rem --platform win_amd64: Force Windows x64 wheels
rem --python-version 3.13: Force wheels compatible with Python 3.13
rem --only-binary=:all:: Prefer wheels over source (avoids compile errors)

python -m pip download -d ./packages -r requirements.txt --platform win_amd64 --python-version 3.13 --only-binary=:all:

echo.
echo Download Complete.
echo Please copy the whole 'PoC3_LocalShadow' folder to your air-gapped machine.
echo Then run 'install_offline.bat'.
pause
