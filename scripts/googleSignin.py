import google.auth
from google.auth import compute_engine 
from google.auth.transport import requests
from google.oauth2 import id_token
import scripts.dataBase as db
import scripts.userManagement as usMNG
import uuid
import json

credentials = compute_engine.Credentials()


signedUser = {}


async def validateGoogleToken(token):
    clientID = "11977394787-3upvfn4uf0lsc6i5119j1aa2gr3d6gis.apps.googleusercontent.com"
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), clientID)
        userId = idinfo['sub']
        return [True, userId]
    except:
        return [False]
        pass


async def signin(token):
    user = await validateGoogleToken(token)
    if user[0] == False:
        return False

    if user[1] in signedUser:
        return signedUser[user[1]]

    userNewUuid = uuid.uuid4().hex

    signedUser[user[1]] = userNewUuid

    usMNG.users[userNewUuid] = {}

    storeLoggedInUser()

    with open("/data/usersHolder.json", "w") as f:
        json.dump(usMNG.users, f)
    return userNewUuid


def storeLoggedInUser():
    with open("/data/loggedInUsers.json", "w") as f:
        json.dump(signedUser, f)