import os
import requests
from dotenv import load_dotenv

load_dotenv()


def authenticate(username, password):
    taiga_url = os.getenv('TAIGA_URL')
    payload = {
        "type": "normal",
        "username": username,
        "password": password,
    }

    try:
        response = requests.post(f"{taiga_url}/auth", json=payload)
        response.raise_for_status()
        auth_token = response.json().get("auth_token")
        return auth_token

    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {e}")
        return None
