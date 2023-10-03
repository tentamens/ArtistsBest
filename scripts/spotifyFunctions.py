
import requests
import scripts.genFunctions as genFunc
import json
import index as index
import aiohttp


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
    
    justArtists = [{"name": artist["name"]} for artist in songs_and_links]
    inputnameMatch = genFunc.find_closest_word(inputSong, justArtists)

    output = [item for item in songs_and_links if item["name"] == inputnameMatch]

    return [output[0]["name"], output[0]["url"]]


async def getArtist(inputName, userToken):
    headers = {"Authorization": f"Bearer {userToken}"}
    params = {"q": inputName, "type": "artist"}

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.spotify.com/v1/search", headers=headers, params=params) as response:
            if response.status != 200:
                print(
                    f"there was an error fetching the data error code get artist {response.status}"
                )
                return [None, response.status]

            data = await response.json()
            artists = data["artists"]["items"]
            artistAndSongs = [
                {"name": artist["name"], "url": artist["external_urls"]["spotify"]}
                for artist in artists
            ]

            justArtists = [{"name": artist["name"]} for artist in artistAndSongs]
            closedOutput = genFunc.find_closest_word(inputName, justArtists)
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
    if name in index.searchArtistCache:
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

    index.searchArtistCache[name] = entry
    with open("searchArtistsCache.json", "w") as write_file:
        json.dump(index.searchArtistCache, write_file)
    return

def createPlaylist(userToken, name, description):
    
    headers = {
        "Authorization": f"Bearer {userToken}",
        "Content-Type": "application/json",
    }
    data = json.dumps({"name": name, "description": description})

    response = requests.post(
        "https://api.spotify.com/v1/users/03l6hosv3bjp1uk8kjk9ov4gf/playlists",
        headers=headers,
        data=data,
    )

    return response.json()["id"]


