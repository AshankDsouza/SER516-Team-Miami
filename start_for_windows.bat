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
flask --app main run
