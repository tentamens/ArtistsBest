
import htppRequest
import scripts.dataBase as dataBase
import apikeys
import scripts.spotifyFunctions as spotFunc 
import scripts.genFunctions as genFunc

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import Levenshtein
import json
import threading
import time
import requests


searchArtistCache = {}


activeThreads = {}

app = FastAPI()

client_id = "92a2dede3a44403ab62b7b38138c861b"
client_secret = "4951963c88db452da9c28003372b218e"

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://localhost:5500",
    "https://127.0.0.1:5500",
]

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
    artistID = spotFunc.getArtistID(name, userToken)

    spotFunc.getArtistsSongs(artistID, userToken, name)


@app.api_route("/api/load/bestSongs", methods=["POST"])
async def loadBestSongs(request: Request):
    data = await request.json()
    userToken = data["token"]

    artistTrueName = await spotFunc.getArtist(data["artistName"], userToken)

    if artistTrueName[0] == None:
        return JSONResponse(artistTrueName[1])

    result = dataBase.searchArtist(artistTrueName[0])

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
        print(data["artistName"])
        return JSONResponse("",status_code=400)
    allSongs = searchArtistCache[data["artistName"]]
    
    justName = [song for song in allSongs.keys()]
    
    correctSong = genFunc.findClosestWord(data["songName"], justName)
    
    dataBase.addSongScore(
        data["artistName"], correctSong, allSongs[correctSong]
    )


@app.api_route("/", methods=["GET"])
async def gen():
    await dataBase.addSongScore("NF","HOPE","https://open.spotify.com/track/0EgLxY52mpGsXETyEsgVlP")
    dataBase.printSongs()
    print(time.time())
    return 200


@app.api_route("/api/get/artistsvotes", methods=["POST"])
async def retrieveVotes(data: Request):
    data = await data.json()
    keys = apikeys.apiKeys
    if data["apiKey"] in keys:
        print("you have a key")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
