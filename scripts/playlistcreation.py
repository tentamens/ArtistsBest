from dotenv import load_dotenv
import os
import base64
import requests
import time
import scripts.spotifyFunctions as spotFunc
import scripts.dataBase as db
import json
import threading


load_dotenv()
access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

client_id = "92a2dede3a44403ab62b7b38138c861b"
client_secret = "4951963c88db452da9c28003372b218e"

# name of the artists: [id, checkTime]
createdPlaylists = db.loadPlaylists()

accessTokenExpire = None

print(createdPlaylists)

async def getPlaylist(name):
    if name in createdPlaylists:
        t = threading.Thread(target=playlistCreated, args=(name,))
        t.start()

        return createdPlaylists[name]
    
    return await createPlaylist(name)


def playlistCreated(name):
    if time.time() > createdPlaylists[name][1]:
        return

    playlistID = createdPlaylists[name][0]

    updatePlaylist(name, playlistID)


def refreshToken():
    global refresh_token
    refresh_token = refresh_token
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    authOptions = {
        "url": "https://accounts.spotify.com/api/token",
        "headers": {"Authorization": f"Basic {auth_header}"},
        "data": {
            "grant_type": "refresh_token",
            "refresh_token": os.getenv("SPOTIFY_REFRESH_ACCESS_TOKEN"),
        },
    }

    response = requests.post(**authOptions)

    if response.status_code == 200:
        global access_token
        global accessTokenExpire

        access_token = response.json()["access_token"]
        accessTokenExpire = time.time() + response.json()["expires_in"]
        return access_token

refreshToken()

async def createPlaylist(name):
    id = spotFunc.createPlaylist(
        access_token,
        f"{name} Best Songs",
        f"The highest-voted songs by {name}. To vote for their best songs, or your favorite artist’s best songs, visit app.artistsbest.ai",
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    songs = db.searchArtist(name)
    print(songs)
    songsLinks = []
    for i in range(len(songs)):
        this = songs[i][2]
        that = this[31:]
        songsLinks.append("spotify:track:" + that)

    data = {"uris": songsLinks}

    requests.post(
        f"https://api.spotify.com/v1/playlists/{id}/tracks",
        data=json.dumps(data),
        headers=headers,
    )

    t = time.time()
    createdPlaylists[name] = [id, t + 5 * 60]
    db.storePlaylists(name, id)

    return createdPlaylists[name]


def checkPlaylistCreation(name):
    if name not in createPlaylist:
        createPlaylist(name)
        return

    if time.time() > createdPlaylists[name][1]:
        updatePlaylist(name)


def updatePlaylist(name, id):
    print(id)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    CurrentHighestVotedSongs = db.searchArtist(name)

    playlistSongs = requests.get(
        f"https://api.spotify.com/v1/playlists/{id}/tracks", headers=headers
    )

    playlistSongs = playlistSongs.json()["items"]

    # {uri: "spotify:track:"}
    removeSongUrls = []

    # Has the Change entry with link
    SongsThatAreOnTheList = []

    for i in playlistSongs:
        name = i["track"]["name"]

        result = checkForSongInResponse(name, CurrentHighestVotedSongs)

        if result is not None:
            SongsThatAreOnTheList.append(result)
            continue

        removeSongUrls.append({"uri": "spotify:track:" + i["track"]["id"]})

    if len(SongsThatAreOnTheList) == len(CurrentHighestVotedSongs):
        return

    addSongsUrls = []

    for i, item in enumerate(SongsThatAreOnTheList):
        if SongsThatAreOnTheList[i] not in CurrentHighestVotedSongs[i]:
            addSongsUrls.append("spotify:track:" + CurrentHighestVotedSongs[i][2][31:])

    data = {"tracks": removeSongUrls}

    deleteSongsUrl(data, id)

    datas = {"uris": addSongsUrls}

    addSongsRequest(datas, id)

    return


def getRemoveSongs(songs, song):
    removeSongs = []
    for i in songs:
        if i not in song:
            removeSongs.append({"uri": "spotify:track:" + i[2][31:]})
    return removeSongs


def checkForSongInResponse(
    name,
    songs,
):
    song = None
    for i in songs:
        if i[1] == name:
            song = []
            song.append(i)
            return song
    return song


def addSongsRequest(data, id):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"https://api.spotify.com/v1/playlists/{id}/tracks",
        data=json.dumps(data),
        headers=headers,
    )
    print(response.json())
    return


def deleteSongsUrl(data, id):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(
        f"https://api.spotify.com/v1/playlists/{id}/tracks",
        data=json.dumps(data),
        headers=headers,
    )
    print(response.json())
    return
