import base64
import requests
import htppRequest
import asyncio
from prettytable import PrettyTable
import dataBase
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pprint
import Levenshtein
import json
import threading


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


def find_closest_word(input_str, word_list):
    closest_word = None
    min_distance = float("inf")
    word_list = [item["name"] for item in word_list]
    for word in word_list:
        distance = Levenshtein.distance(input_str.lower(), word.lower())
        if distance < min_distance:
            closest_word = word
            min_distance = distance
    return closest_word


async def getArtistSongs(inputName, inputSong, userToken):
    headers = {"Authorization": f"Bearer {userToken}"}

    params = {"q": f"{inputName} {inputSong}", "type": "track"}

    response = requests.get(
        "https://api.spotify.com/v1/search", headers=headers, params=params
    )

    if response.status_code != 200:
        print(f"there was an error fetching the data error code {response.status_code}")
        return [None, response.status_code]

    tracks = response.json()["tracks"]["items"]
    songs_and_links = [
        {"name": track["name"], "url": track["external_urls"]["spotify"]}
        for track in tracks
    ]
    print(songs_and_links)
    justArtists = [{"name": artist["name"]} for artist in songs_and_links]
    inputnameMatch = find_closest_word(inputSong, justArtists)

    output = [item for item in songs_and_links if item["name"] == inputnameMatch]

    return [output[0]["name"], output[0]["url"]]


async def getArtist(inputName, userToken):
    headers = {"Authorization": f"Bearer {userToken}"}
    params = {"q": inputName, "type": "artist"}
    response = requests.get(
        "https://api.spotify.com/v1/search", headers=headers, params=params
    )

    if response.status_code != 200:
        print(
            f"there was an error fetching the data error code get artist {response.status_code}"
        )
        return [None, response.status_code]

    artists = response.json()["artists"]["items"]
    artistAndSongs = [
        {"name": artist["name"], "url": artist["external_urls"]["spotify"]}
        for artist in artists
    ]

    justArtists = [{"name": artist["name"]} for artist in artistAndSongs]
    closedOutput = find_closest_word(inputName, justArtists)
    output = [item for item in artistAndSongs if item["name"] == closedOutput]

    return [output[0]["name"], output[0]["url"]]


def getArtistID(inputName, userToken):
    headers = {
        "Authorization": f"Bearer {userToken}",
    }
    search_url = f"https://api.spotify.com/v1/search?q={inputName}&type=artist"
    search_response = requests.get(search_url, headers=headers)
    search_response = search_response.json()
    aristID = None

    for i in search_response["artists"]["items"]:
        if i["name"] == inputName:
            aristID = i["id"]
            break

    return aristID


def getArtistsSongs(inputID, userToken, name):
    if name in searchArtistCache:
        print("hello world")
        return

    headers = {"Authorization": f"Bearer {userToken}"}
    albums_url = f"https://api.spotify.com/v1/artists/{inputID}/albums"
    albums_response = requests.get(albums_url, headers=headers)
    albums_response = albums_response.json()

    albumID = [i["id"] for i in albums_response["items"]]
    entry = {
        i["name"]: i["external_urls"]["spotify"]
        for response in albumID
        for i in response["items"]
    }

    searchArtistCache[name] = entry
    with open("searchArtistsCache.json", "w") as write_file:
        json.dump(searchArtistCache, write_file)


def handleArtistsCache(name, userToken):
    artistID = getArtistID(name, userToken)

    getArtistsSongs(artistID, userToken, name)


@app.api_route("/api/load/bestSongs", methods=["POST"])
async def loadBestSongs(request: Request):
    data = await request.json()
    userToken = data["token"]

    artistTrueName = await getArtist(data["artistName"], userToken)

    if artistTrueName[0] == None:
        return JSONResponse(artistTrueName[1])

    result = dataBase.searchArtist(artistTrueName[0])

    return JSONResponse(content=result, status_code=200)


@app.api_route("/api/load/searchArtist", methods=["POST"])
async def searchArtist(request: Request):
    data = await request.json()

    artistName = await getArtist(data["artistName"], data["token"])

    t = threading.Thread(target=handleArtistsCache, args=(artistName[0], data["token"]))
    t.start()

    return JSONResponse(content=response, status_code=200)


@app.api_route("/api/get/token", methods=["GET"])
async def createToken():
    authOptions = htppRequest.authOptions
    response = requests.post(
        authOptions["url"], headers=authOptions["headers"], data=authOptions["form"]
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(token)
        return JSONResponse(content=token, status_code=200)

    print("there was an error fetching token error code: " + response.status_code)
    return JSONResponse(status_code=400)


@app.api_route("/api/post/vote", methods=["POST"])
async def vote(data: Request):
    data = await data.json()
    if data["artistName"] not in searchArtistCache:
        return JSONResponse(status_code=400)
    allSongs = searchArtistCache["artistName"]
    
    
    artistSongAndLink = await getArtistSongs(
        , data["songName"], data["token"]
    )
    dataBase.addSongScore(
        data["artistName"], artistSongAndLink[0], artistSongAndLink[1]
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
