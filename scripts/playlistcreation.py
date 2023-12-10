from dotenv import load_dotenv
import os
import base64
import requests
import time
import scripts.spotifyFunctions as spotFunc
import scripts.dataBase as db
import json
import threading
import scripts.genFunctions as genFunc



load_dotenv()
access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# name of the artists: [id, checkTime]
createdPlaylistes = db.loadPlaylists()

accessTokenExpire = None


async def getPlaylist(name):
    global createdPlaylistes
    if name in createdPlaylistes:
        #t = threading.Thread(target=playlistCreated, args=(name,))
        #t.start()
        

        if time.time() < createdPlaylistes[name][1]:  
            return createdPlaylistes[name]
        
        playlistID = createdPlaylistes[name][0]
        updatePlaylist(name, playlistID, createdPlaylistes)

        return createdPlaylistes[name]
    
    return await createPlaylist(name)




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



async def createPlaylist(name):
    global createdPlaylistes
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
    t = t + 5 * 60
    createdPlaylistes[name] = [id, t]
    db.storePlaylists(name, id)

    return



def updatePlaylist(name, id, createdPlayisteds):
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    CurrentHighestVotedSongs = db.searchArtist(name)

    playlistSongs = genFunc.makeGetRequest(
        f"https://api.spotify.com/v1/playlists/{id}/tracks",
        headers=headers,
        data="",
        whereCalledFrom="update playlist line 119 in playlistcreation"
    )

    if type(playlistSongs) == list:
        error = playlistSongs[1]["error"]
        if error["status"] == 401:
            token = refreshToken()
            return updatePlaylist(name, id, createdPlaylistes)
        return

    playlistSongs = playlistSongs.json()["items"]

    # {uri: "spotify:track:"}
    removeSongUrls = []

    # Has the Change entry with link
    SongsThatAreOnTheList = []

    for i in playlistSongs:
        nameed = i["track"]["name"]

        result = checkForSongInResponse(nameed, CurrentHighestVotedSongs)

        if result is not None:
            SongsThatAreOnTheList.append(result)
            continue

        removeSongUrls.append({"uri": "spotify:track:" + i["track"]["id"]})


    t = time.time()
    t = t + 5 * 60
    createdPlaylistes[name][1] = t

    if len(SongsThatAreOnTheList) == len(CurrentHighestVotedSongs):
        return createdPlaylistes

    addSongsUrls = []
    

    SongsThatAreOnTheList = [song for sublist in SongsThatAreOnTheList for song in sublist]

    for i, item in enumerate(CurrentHighestVotedSongs):
        # Check if the track is already in the playlist
        if item not in SongsThatAreOnTheList:
            addSongsUrls.append("spotify:track:" + item[2][31:])


    data = {"tracks": removeSongUrls}

    deleteSongsUrl(data, id)

    datas = {"uris": addSongsUrls}

    addSongsRequest(datas, id)




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
    
    return
