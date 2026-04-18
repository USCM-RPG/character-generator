@echo off
setlocal

REM Go to script directory
cd /d %~dp0

where uv >nul 2>nul
if %ERRORLEVEL%==0 goto RUN

echo.
echo uv not found.

set /p CHOICE=The tool 'uv' is needed to run the Character Generator. Do you want to install 'uv' now? (Y/N): 

if /I "%CHOICE%" NEQ "Y" (
    echo Aborting.
    pause
    exit /b 1
)

echo Installing uv...
powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"

REM Add to PATH for this session
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

REM Re-check uv
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo uv installation failed. Please restart and try again.
    pause
    exit /b 1
)

:RUN
uv sync
echo Starting USCM Character Generator...

uv run character_gui\character_generator.py
pause