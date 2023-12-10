import htppRequest
import scripts.dataBase as dataBase
import apikeys
import scripts.spotifyFunctions as spotFunc
import scripts.genFunctions as genFunc
import scripts.cacheUpdating as cache
import scripts.playlistcreation as playlistcreation
import scripts.userManagement as userManagement


from fastapi import FastAPI, Request, Form, Depends, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

import json
import threading
import requests
import string
import random
import base64
import logging
import scripts.spotifyPreviewUrls as previewUrl
import scripts.googleSignin as googleSignin
import os
import dotenv

searchArtistCache = {}

songCache = {}



activeThreads = {}

app = FastAPI()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

origins = ["*"]

log = logging.getLogger("uvicorn")
log.setLevel(logging.ERROR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


with open("searchArtistsCache.json", "r") as read_file:
    searchArtistCache = json.load(read_file)

with open("songCache.json", "r") as read_file:
    songCache = json.load(read_file)


def handleArtistsCache(name, userToken):
    print("THIS IS IN HANDLE CACHE " + str(name))

    cache.artistSearched(name, userToken)


@app.api_route("/", methods=["GET"])
async def gen():
    playlistcreation.refreshToken()
    data = await playlistcreation.getPlaylist("NF")
    print(data[0])
    return JSONResponse(status_code=200, content=data)


@app.api_route("/test/update")
def update():
    return
    refresh_token = "hello there"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    authOptions = {
        "url": "https://accounts.spotify.com/api/token",
        "headers": {"Authorization": f"Basic {auth_header}"},
        "data": {"grant_type": "refresh_token", "refresh_token": refresh_token},
    }

    response = requests.post(**authOptions)

    if response.status_code == 200:
        print(response.json())


@app.get("/callback")
def callback(request: Request):
    return 200
    redirect_uri = "http://localhost:8000/callback"
    global code
    global state
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    print(code)
    if state is None:
        return RedirectResponse(
            "/#" + requests.compat.urlencode({"error": "state_mismatch"})
        )
    else:
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        authOptions = {
            "url": "https://accounts.spotify.com/api/token",
            "data": {
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            "headers": {"Authorization": f"Basic {auth_header}"},
        }
        response = requests.post(**authOptions)
        print(response.json())
        return response.json()


@app.api_route("/login")
def login():
    return 200
    redirect_uri = "http://localhost:8000/callback"

    state = "".join(random.choices(string.ascii_uppercase + string.digits, k=16))
    scope = "playlist-modify-public user-read-email"
    params = {
        "response_type": "code",
        "client_id": "hi there",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    url = "https://accounts.spotify.com/authorize?" + requests.compat.urlencode(params)
    return RedirectResponse(url)


@app.api_route("/api/load/bestSongs", methods=["POST"])
async def loadBestSongs(request: Request):
    data = await request.json()
    print(data)
    userToken = data["token"]
    artistTrueName = data["artistName"]


    playlist = await playlistcreation.getPlaylist(artistTrueName)

    voteSimilarity = dataBase.loadVoteSimilarity(artistTrueName)
    
    result = dataBase.searchArtist(artistTrueName)
    result = {"songs": result, "playlist": playlist[0], "similartyVotes": voteSimilarity}
    result = json.dumps(result)


    return JSONResponse(content=result, status_code=200)


@app.api_route("/api/load/searchArtist", methods=["POST"])
async def searchArtist(request: Request):
    
    data = await request.json()
    

    artistName = spotFunc.getArtist(data["artistName"], data["token"])

    dataBase.storeEachSearch(data["artistName"], artistName[0], )

    return JSONResponse(content=artistName[0], status_code=200)




@app.api_route("/api/get/token", methods=["GET"])
async def createToken():
    authOptions = htppRequest.authOptions
    response = requests.post(
        authOptions["url"], headers=authOptions["headers"], data=authOptions["form"]
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return token

    print(
        "there was an error fetching token error code: "
        + response.status_code)

    return JSONResponse(status_code=400, content="")


@app.api_route("/api/post/vote", methods=["POST"])
async def vote(data: Request):
    global songCache
    data = await data.json()
    artistname = data["artistName"]
    token = data["token"]
    songName = data["songName"]
    uuid = data["uuid"]
    
    if token == None:
        return JSONResponse(status_code=400, content={"response": "no token", "exitCode": "128"})
    
    if token == "Null":
        return JSONResponse(status_code=400, content={"response": "no token", "exitCode": "129"})

    status = await userManagement.voteOnSong(artistname, uuid)
    
    if  artistname not in songCache:
        songCache[artistname] = {}

    if songName in songCache[artistname]:
            
        returnResult = userManagement.verifyStatusAndUpdate(status, artistname, songName, songCache[artistname][songName])
        return JSONResponse(status_code=returnResult[0], content=returnResult[1])


    result = spotFunc.fetchSong(artistname, songName, token)

    if result == None:
        return JSONResponse(status_code=401, content={"exitCode": 130})

    if type(result) == list:
        return JSONResponse(status_code=400, content={"response": "no token", "exitCode": 157})

    dataBase.storeEachSearch(artistname, result["name"])

    returnResult = userManagement.verifyStatusAndUpdate(status, artistname, result["name"], result["external_urls"]["spotify"])

    if result["name"] in songCache[artistname]:
        return JSONResponse(status_code=returnResult[0], content=returnResult[1])
    
    songCache[artistname][result["name"]] = result["external_urls"]["spotify"]

    with open("songCache.json", "w") as write_file:
        json.dump(songCache, write_file)
    
    return JSONResponse(status_code=returnResult[0], content=returnResult[1])


@app.api_route("/api/get/artistsvotes", methods=["POST"])
async def retrieveVotes(data: Request):
    data = await data.json()
    keys = apikeys.apiKeys
    if data["apiKey"] in keys:
        print("you have a key")


@app.api_route("/api/post/vote/similarity", methods=["POST"])
async def similarityVote(data: Request):
    data = await data.json()
    userToken = data["token"]
    artistName = data["artistName"]
        
    if userToken == None:
        return JSONResponse(status_code=400, content={"response": "no token", "exitCode": "128"})
    
    if userToken == "Null":
        return JSONResponse(status_code=400, content={"response": "no token", "exitCode": "129"})
    votedArtistFalse = data["votedArtist"]
    votedArtistName = spotFunc.getArtist(votedArtistFalse, userToken)
    status = userManagement.VoteOnArtist(votedArtistName[0], data["uuid"])
    
    dataBase.storeEachSearch(artistName, votedArtistName[0])

    if status == 401:
        return JSONResponse(status_code=status, content={"response": "invalid Token", "exitCode": "130"})

    returnResult = userManagement.verifyStatusAndUpdateArtist(status, artistName, votedArtistName[0], votedArtistName[1])
    return JSONResponse(status_code=returnResult[0], content=returnResult[1])

@app.api_route("/api/post/signin", methods=["POST"])
async def signIn(data: Request):
    data = await data.json()
    token = data["token"]
    uuid = await googleSignin.signin(token)
    
    return JSONResponse(status_code=200, content=uuid)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=6969)
