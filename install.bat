@echo off
cd /d "%~dp0"

if not exist "python\python.exe" (
    echo.
    echo  Error: python\python.exe not found.
    echo  Please extract the ZIP file correctly.
    echo.
    pause
    exit /b 1
)

python\python.exe -m patcher.install_mod
set RETCODE=%ERRORLEVEL%

echo.
pause
exit /b %RETCODE%
