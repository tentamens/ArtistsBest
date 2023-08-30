import spotify.sync as spotify
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


app = FastAPI()

token = None

client_id = '92a2dede3a44403ab62b7b38138c861b'
client_secret = '4951963c88db452da9c28003372b218e'

origins = ['http://localhost:5500', 'http://127.0.0.1:5500',
           'https://localhost:5500', 'https://127.0.0.1:5500'] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


authOptions = htppRequest.authOptions
response = requests.post(authOptions['url'], headers=authOptions['headers'], data=authOptions['form'])
if response.status_code == 200:
    token = response.json()['access_token']


def find_closest_word(input_str, word_list):

    closest_word = None
    min_distance = float('inf')
    word_list = [item['name'] for item in word_list]
    for word  in word_list:
        distance = Levenshtein.distance(input_str.lower(), word.lower())
        if distance < min_distance:
            closest_word = word
            min_distance = distance
    return closest_word




async def getArtistID(inputName):
    search_url = f"https://api.spotify.com/v1/search?q={inputName}&type=artist"
    headers = {'Authorization': f"Bearer {token}"}
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print(f"there was an error fetching the data error code {response.status_code}")
        return
    
    artists = response.json()['artists']['items']
    if len(artists) > 0:
        artist_id = artists[0]['id']
        return artist_id
    
    else:
        return None


async def getArtistSongs(inputName, inputSong):
    headers = {'Authorization': f"Bearer {token}"}
    artistId = await getArtistID(inputName)
    if artistId == None:
        return
    
    params = {'q': f"{inputName} {inputSong}", 'type': 'track'}
    
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"there was an error fetching the data error code {response.status_code}")
        return
    
    tracks = response.json()['tracks']['items']
    songs_and_links = [{'name': track['name'], 'url': track['external_urls']['spotify']} for track in tracks]
    
    return [songs_and_links[0]['name'], songs_and_links[0]['url']]


async def getArtist(inputName):
    
    artistId = await getArtistID(inputName)
    if artistId == None:
        return

    headers = {'Authorization': f"Bearer {token}"}
    params = {'q': inputName, 'type': 'artist'}
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"there was an error fetching the data error code get artist {response.status_code}")
        return
    
    artists = response.json()['artists']['items']
    artistAndSongs = [{'name': artist['name'], 'url': artist['external_urls']['spotify']} for artist in artists]
    
    return [artistAndSongs[0]['name'], artistAndSongs[0]['url']]



def search_track(table, track_name):
    for row in table._rows:
        if row[1] == track_name:
            return True
    return False


async def testing(artist, song):
    result = await getArtistSongs(artist, song)
    
    artistTrueName = await getArtist(artist)

    # add sone to score with url and name and song
    dataBase.addSongScore(artistTrueName[0], result[0], result[1])
    
    dataBase.searchArtist(artistTrueName[0])

    return



@app.api_route("/api/load/bestSongs", methods=["POST"])
async def loadBestSongs(request: Request):
    await testing("post malone", "Something Real")
    data = await request.json()
    
    ip = str(request.client.host)

    artistTrueName = await getArtist(data["artistName"])

    result = dataBase.searchArtist(artistTrueName[0])

    return JSONResponse(content=result, status_code=200)



@app.api_route("/api/load/searchArtist", methods=["POST"])
async def searchArtist(request: Request):
    data = await request.json()
    ip = str(request.client.host)
    print("hello world")
    print(data)

    headers = {'Authorization': f"Bearer {data['token']}"}
    params = {'q': "post malone", 'type': 'artist'}
    response = requests.get(f'https://api.spotify.com/v1/search?q={"Post malone"}&type=artist', headers=headers)
    
    if response.status_code != 200:
        print(f"there was an error fetching the data error code get artist {response.status_code}")
        return
    
    artists = response.json()['artists']['items']

    artistAndSongsURLS = [{'name': artist['name'], 'url': artist['external_urls']['spotify']} for artist in artists]
    justArtists = [{'name': artist["name"]} for artist in artistAndSongsURLS]

    justArtists = find_closest_word(data['artistName'], justArtists) # throws an error saying that justArtists is a dictionary

    response = [justArtists]

    return JSONResponse(content=response, status_code=200)



@app.api_route("/api/get/token", methods=["GET"])
async def createToken():
    authOptions = htppRequest.authOptions
    response = requests.post(authOptions['url'], headers=authOptions['headers'], data=authOptions['form'])
    if response.status_code == 200:
        token = response.json()['access_token']
        return JSONResponse(content=token, status_code=200)
    
    print("there was an error fetching token error code: " + response.status_code)
    return JSONResponse(status_code=400)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

