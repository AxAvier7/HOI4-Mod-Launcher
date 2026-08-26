@echo off
title HOI4 Mod Launcher
python "%~dp0hoi4_launcher.py"
if errorlevel 1 (
    echo Python no encontrado o error al ejecutar.
    pause
)
