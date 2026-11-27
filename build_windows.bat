@echo off
setlocal
cd /d "%~dp0"

python -m pip install -r requirements-build.txt
if errorlevel 1 exit /b %errorlevel%

python -m PyInstaller --noconfirm --clean --onedir --name PTCalculator --distpath "%~dp0Executable" --workpath "%~dp0build" --add-data "%~dp0..\UI;UI" --add-data "%~dp0README.md;." "%~dp0Calculator.py"
if errorlevel 1 exit /b %errorlevel%

echo.
echo Application ready: "%~dp0Executable\PTCalculator\PTCalculator.exe"
