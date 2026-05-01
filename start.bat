@echo off
title Sistema de Prediccion de Futuros - Instalacion Automatica
cls
echo ========================================================
echo   INICIANDO SISTEMA DE PREDICCION DE FUTUROS (AI)
echo ========================================================
echo.

:: 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 goto ErrorPython

:: 2. Crear Entorno Virtual si no existe
if exist "venv" goto VenvExists

echo [INFO] Creando entorno virtual (venv)...
python -m venv venv
if %errorlevel% neq 0 goto ErrorVenv
echo [OK] Entorno virtual creado exitosamente.
goto ActivateVenv

:VenvExists
echo [INFO] Entorno virtual detectado.

:ActivateVenv
:: 3. Activar Entorno Virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 goto ErrorActivate

:: 4. Actualizar pip e Instalar Dependencias
echo [INFO] Verificando e instalando dependencias...
python -m pip install --upgrade pip

:: Instalar PyTorch con soporte CUDA (NVIDIA GPU)
echo [INFO] Instalando PyTorch con soporte para GPU (CUDA)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

pip install -r requirements.txt
if %errorlevel% neq 0 goto ErrorInstall
echo [OK] Todas las dependencias estan listas.

:: 5. Ejecutar el Sistema
echo.
echo [INFO] Iniciando la interfaz del sistema...
echo.
python run.py
goto End

:ErrorPython
echo.
echo [ERROR] Python no esta instalado o no esta en el PATH.
echo Por favor instala Python 3.9+ desde python.org y asegurate de marcar "Add to PATH".
pause
exit /b

:ErrorVenv
echo.
echo [ERROR] Fallo al crear el entorno virtual.
pause
exit /b

:ErrorActivate
echo.
echo [ERROR] No se pudo activar el entorno virtual.
pause
exit /b

:ErrorInstall
echo.
echo [ERROR] Fallo al instalar las dependencias. Revisa tu conexion a internet.
pause
exit /b

:End
pause
