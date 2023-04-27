@echo off

set VENV_NAME=archie_venv

echo Creating virtual environment...
python -m venv %VENV_NAME%

echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt