#This file is for Unix-like systems only.

if [ ! -d "miamiEnv" ]; then
    python3 -m venv miamiEnv
fi

#Activate the virtual environment
. miamiEnv/bin/activate

#Install the required dependencies
pip install -r requirements.txt

#Go to the flaskProject folder
cd Backend/flaskProject

echo "TAIGA_URL=https://api.taiga.io/api/v1" > .env

#Run the flask app
flask --app main run

