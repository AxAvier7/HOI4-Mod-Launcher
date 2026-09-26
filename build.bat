@echo off
title Build HOI4 Mod Launcher
cd /d "%~dp0"

echo ============================================
echo  Compilando HOI4 Mod Launcher
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado en el PATH.
    pause
    exit /b 1
)

echo [1/3] Instalando PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo [ERROR] No se pudo instalar PyInstaller.
    pause
    exit /b 1
)

echo.
echo [2/3] Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist "%~dp0HOI4 Mod Launcher.spec" del /q "%~dp0HOI4 Mod Launcher.spec"

echo.
echo [3/3] Generando ejecutable...
python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name "HOI4 Mod Launcher" ^
    --exclude-module unittest ^
    --exclude-module email ^
    --exclude-module http ^
    --exclude-module xml ^
    --exclude-module pydoc ^
    hoi4_launcher.py

if errorlevel 1 (
    echo.
    echo [ERROR] La compilacion fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Compilacion completada
echo ============================================
echo.
echo  Ejecutable: "%~dp0dist\HOI4 Mod Launcher.exe"
echo.
echo  Colocalo en una carpeta donde tengas permisos
echo  de escritura (NO en C:\Program Files), ya que
echo  guarda config.json junto al .exe
echo.
pause
