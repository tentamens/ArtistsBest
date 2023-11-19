import requests
import scripts.genFunctions as genFunc
import json
import index as index
import aiohttp
import scripts.playlistcreation as playlistcreation


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


def getArtist(inputName, userToken):
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

    data = response.json()
    
    
    
    artists = data["artists"]["items"]
    

    return [artists[0]["name"], artists[0]["external_urls"]["spotify"]]


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
    params = {
        "include_groups": "album,single,appears_on,compilation",
        "limit": 50,  # Maximum limit
    }
    headers = {"Authorization": f"Bearer {userToken}"}
    albums_url = f"https://api.spotify.com/v1/artists/{inputID}/albums"
    albums_response = requests.get(albums_url, headers=headers, params=params)
    albums_response = albums_response.json()

    albumID = [i["id"] for i in albums_response["items"]]

    entry = {}
    for album_id in albumID:
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tracks = response.json()["items"]

            for track in tracks:
                entry[track["name"]] = track["external_urls"]["spotify"]
            continue

        print(
            f"there was an error fetching the data error code get artists songs {response.status_code}"
        )

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

    response = genFunc.make_request(
        "https://api.spotify.com/v1/users/03l6hosv3bjp1uk8kjk9ov4gf/playlists",
        headers,
        data,
        whereCalledFrom="createdPlaylist line 115 spotifyFunctions.py",
    )
    
    if type(response) == list:
        error = response[1]["error"]
        if error["status"] == 401:
            token = playlistcreation.refreshToken()
            return createPlaylist(token, name, description)
        return

    return response.json()["id"]


def fetchSong(artistName, name, userToken):
    headers = {
        "Authorization": f"Bearer {userToken}",
    }

    query = f"track:{name} artist:{artistName}"
    data = {
        "q": query,
        "type": "track",
        "market": "US"
    }


    response = genFunc.makeGetRequest(
        "https://api.spotify.com/v1/search",
        headers,
        data,
        whereCalledFrom="fetchSong line 140 spotifyFunctions.py",
    )


    if type(response) == list:
        return ["error"]

    

    return response.json()["tracks"]["items"][0]
