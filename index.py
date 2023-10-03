import htppRequest
import scripts.dataBase as dataBase
import apikeys
import scripts.spotifyFunctions as spotFunc
import scripts.genFunctions as genFunc
import scripts.cacheUpdating as cache
import scripts.playlistcreation as playlistcreation


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

import Levenshtein
import json
import threading
import time
import requests
import string
import random
import base64


searchArtistCache = {}


activeThreads = {}

app = FastAPI()

client_id = "92a2dede3a44403ab62b7b38138c861b"
client_secret = "4951963c88db452da9c28003372b218e"

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




with open("searchArtistsCache.json", "r") as read_file:
    searchArtistCache = json.load(read_file)




def handleArtistsCache(name, userToken):
    cache.artistSearched(name, userToken)


@app.api_route("/", methods=["GET"])
async def gen():
    playlistcreation.refreshToken()
    await playlistcreation.updatePlaylist("NF")
    return 200




@app.api_route("/test/update")
def update():
    refresh_token = "BQBKSB5njDXM4Ej8FfH-tdIm07-r3kLIAAaIHAnVcyHnWIioFiz1xMqgKOH_yHf7HCHCQHQPUs6OuYNUYWduPmlr300KNKCE2QKSK4re6Bwx6K4Aj7KxHVt-PQi9bExHnz8gmEB_4Du2UENB53ost-qxQwVMLj080OQ71j_y5bLLfcA_UirKIANnRvCj3Q2q-x6V1icXvw93p1vnAfot7XPhNwihXtw096g2286I"
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
        "client_id": htppRequest.client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    url = "https://accounts.spotify.com/authorize?" + requests.compat.urlencode(params)
    return RedirectResponse(url)


@app.api_route("/api/load/bestSongs", methods=["POST"])
async def loadBestSongs(request: Request):
    data = await request.json()
    userToken = data["token"]

    artistTrueName = await spotFunc.getArtist(data["artistName"], userToken)

    if artistTrueName[0] == None:
        return JSONResponse(artistTrueName[1])

    result = await dataBase.searchArtist(artistTrueName[0])

    result = json.dumps(result)

    return JSONResponse(content=result, status_code=200)


@app.api_route("/api/load/searchArtist", methods=["POST"])
async def searchArtist(request: Request):
    data = await request.json()

    artistName = await spotFunc.getArtist(data["artistName"], data["token"])

    t = threading.Thread(target=handleArtistsCache, args=(artistName[0], data["token"]))
    t.start()

    return JSONResponse(content=artistName[0], status_code=200)


@app.api_route("/api/get/token", methods=["GET"])
async def createToken():
    authOptions = htppRequest.authOptions
    response = requests.post(
        authOptions["url"], headers=authOptions["headers"], data=authOptions["form"]
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return JSONResponse(content=token, status_code=200)

    print("there was an error fetching token error code: " + response.status_code)
    return JSONResponse(status_code=400)


@app.api_route("/api/post/vote", methods=["POST"])
async def vote(data: Request):
    data = await data.json()
    if data["artistName"] not in searchArtistCache:
        return JSONResponse("", status_code=400)
    allSongs = searchArtistCache[data["artistName"]]

    justName = [song for song in allSongs.keys()]

    correctSong = genFunc.findClosestWord(data["songName"], justName)

    await dataBase.addSongScore(data["artistName"], correctSong, allSongs[correctSong])


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
    votedArtistFalse = data["votedArtist"]

    votedArtistName = await spotFunc.getArtist(votedArtistFalse, userToken)

    dataBase.storeVoteSimilarity(artistName, votedArtistName[0])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
