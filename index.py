import spotify.sync as spotify
import base64
import requests
import htppRequest
import asyncio
from prettytable import PrettyTable
import dataBase
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

token = None

client_id = '92a2dede3a44403ab62b7b38138c861b'
client_secret = '4951963c88db452da9c28003372b218e'





authOptions = htppRequest.authOptions
response = requests.post(authOptions['url'], headers=authOptions['headers'], data=authOptions['form'])
if response.status_code == 200:
    token = response.json()['access_token']



async def getArtistID(inputName):
    search_url = f"https://api.spotify.com/v1/search?q={inputName}&type=artist"
    headers = {'Authorization': f"Bearer {token}"}
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print("there was an error fetching the data error code " + response.status_code)
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
    headers = {'Authorization': f"Bearer {token}"}
    artistId = await getArtistID(inputName)
    if artistId == None:
        return
    
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

    dataBase.addSongScore(artistTrueName[0], result[0])

    dataBase.searchArtist(artistTrueName[0])

    return


@app.api_route("/api/load/bestSongs", methods=["POST"])
async def loadBestSongs(request: Request):
    data = await request.json()
    artistTrueName = await getArtist(data[0])



    dataBase.addSongScore(data['artist'], data['song'])
    return JSONResponse(status_code=200)

# an api end point that gets the best songs from a given artist 
@app.api_route("/api/load/bestSongs/{artist}", methods=["GET"])
async def loadBestSongs(artist: str):
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)