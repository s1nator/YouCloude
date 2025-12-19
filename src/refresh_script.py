from config import app_key_dropbox, app_secret_dropbox, refresh_token_for_dropbox
import requests


def get_dropbox_token() -> str | None:
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_for_dropbox,
        "client_id": app_key_dropbox,
        "client_secret": app_secret_dropbox,
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Ошибка обновления токена")
