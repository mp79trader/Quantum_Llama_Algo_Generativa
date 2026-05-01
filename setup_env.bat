@echo off
:: Setup script for Quantum Llama (Windows)

echo Setting up Quantum Llama environment...

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found!
)

echo Setup complete. To activate the environment, run: venv\Scripts\activate
pause
