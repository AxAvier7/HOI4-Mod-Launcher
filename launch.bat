@echo off
title HOI4 Mod Launcher
cd /d "%~dp0"

if exist "%~dp0HOI4 Mod Launcher.exe" (
    start "" "%~dp0HOI4 Mod Launcher.exe"
    exit /b 0
)

if exist "%~dp0dist\HOI4 Mod Launcher.exe" (
    start "" "%~dp0dist\HOI4 Mod Launcher.exe"
    exit /b 0
)

python "%~dp0hoi4_launcher.py"
if errorlevel 1 (
    echo Python no encontrado o error al ejecutar.
    pause
)
