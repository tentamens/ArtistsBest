import google.auth
from google.auth import compute_engine 
from google.auth.transport import requests
from google.oauth2 import id_token




credentials = compute_engine.Credentials()


async def validateGoogleToken(token):
    clientID = "11977394787-3upvfn4uf0lsc6i5119j1aa2gr3d6gis.apps.googleusercontent.com"
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), clientID)
        userId = idinfo['sub']
        print(userId)
        print(idinfo)
        return True
    except:
        return False
        pass


async def signin(token):
    if await validateGoogleToken(token):
        return True
    return False
