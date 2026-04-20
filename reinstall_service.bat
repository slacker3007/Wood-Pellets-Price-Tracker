@echo off
setlocal
cd /d "%~dp0"

REM Stops, removes, and re-registers the Windows service from THIS folder.
REM Requires Administrator. Uses "python" like run.bat; if only "py" works, edit the commands below.

net session >nul 2>&1
if errorlevel 1 (
    echo This script must be run as Administrator.
    echo Right-click the file and choose "Run as administrator".
    pause
    exit /b 1
)

echo Stopping WoodPelletsScraperService...
python service.py stop 2>nul
timeout /t 2 /nobreak >nul

echo Removing service registration...
python service.py remove
if errorlevel 1 (
    echo ERROR: remove failed.
    pause
    exit /b 1
)

echo Installing service...
python service.py install
if errorlevel 1 (
    echo ERROR: install failed.
    pause
    exit /b 1
)

echo Starting service...
python service.py start
if errorlevel 1 (
    echo ERROR: start failed.
    pause
    exit /b 1
)

echo Done. Service reinstalled from: %CD%
endlocal
