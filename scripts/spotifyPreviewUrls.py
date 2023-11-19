import requests
from bs4 import BeautifulSoup
import re



def getPreviewUrl(url):
    try:
        # Construct the URL to the Spotify oEmbed API
        oembed_url = f'https://open.spotify.com/oembed?url={url}'

        # Send a GET request to the Spotify oEmbed API with a timeout (e.g., 10 seconds)
        response = requests.get(oembed_url, timeout=10)

        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        return data.get('preview_url', None)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

