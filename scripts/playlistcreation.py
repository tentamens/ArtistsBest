from dotenv import load_dotenv
import os
import base64
import requests




load_dotenv()

access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

client_id = "92a2dede3a44403ab62b7b38138c861b"
client_secret = "4951963c88db452da9c28003372b218e"

def refreshToken():
    refresh_token = refresh_token
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    authOptions = {
        "url": "https://accounts.spotify.com/api/token",
        "headers": {"Authorization": f"Basic {auth_header}"},
        "data": {"grant_type": "refresh_token", "refresh_token": refresh_token},
    }

    response = requests.post(**authOptions)
    print(response.json())
    if response.status_code == 200:
        access_token = response.json()["access_token"]


def createPlaylist(name, description):
    pass 

