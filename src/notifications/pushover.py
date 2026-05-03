import requests
from src.config import config


PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

def send_push(message: str, title: str = "Study Companion") -> dict:
    payload = {
        "token": config.pushover_token,
        "user": config.pushover_user,
        "title": title,
        "message": message,
    }

    response = requests.post(PUSHOVER_URL, data=payload, timeout=10)
    response.raise_for_status()
    return response.json()