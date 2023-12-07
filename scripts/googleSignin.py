import google.auth
from google.auth import compute_engine 
from google.auth.transport import requests
from google.oauth2 import id_token
import scripts.dataBase as db
import scripts.userManagement as usMNG
import uuid
import json

credentials = compute_engine.Credentials()


async def validateGoogleToken(token):
    clientID = "11977394787-3upvfn4uf0lsc6i5119j1aa2gr3d6gis.apps.googleusercontent.com"
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), clientID)
        print(idinfo)
        userId = idinfo['sub']
        return [True, userId]
    except:
        return [False]
        pass


async def signin(token):
    user = await validateGoogleToken(token)
    if user[0] == False:
        return False
    
    ifUserInDB = db.loadUserGoogle(user[1])

    if ifUserInDB[0] == True:
        return ifUserInDB[1]

    userNewUuid = uuid.uuid4().hex

    db.storeUserGoogle(user[1], userNewUuid)

    usMNG.users[userNewUuid] = {}

    with open("userHolder.json", "w") as f:
        json.dump(usMNG.users, f)

    db.storeUserVoteDict()

    return userNewUuid
