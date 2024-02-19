REM Turn off command echo
@echo off

REM Create a python virtual environment
IF NOT EXIST miamiEnv python3 -m venv miamiEnv

REM Activate the virtual environment
env\Scripts\activate.bat

REM Install the required packages
pip install -r requirements.txt

REM Run the application
cd Backend\flaskProject

echo TAIGA_URL=https://api.taiga.io/api/v1 > .env

flask --app main run
