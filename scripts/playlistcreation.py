from dotenv import load_dotenv
import os
import base64
import requests
import time 
import scripts.spotifyFunctions as spotFunc
import scripts.dataBase as db
import json



load_dotenv()
access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

client_id = "92a2dede3a44403ab62b7b38138c861b"
client_secret = "4951963c88db452da9c28003372b218e"

# name of the artists: [id, checkTime]
createdPlaylists = {}

accessTokenExpire = None


def getPlaylist(name):
    if name in createdPlaylists:
        result = playlistCreated(name)
        return result



def playlistCreated(name):
    if time.time() > createdPlaylists[name][1]:
        return None
    return createdPlaylists[name][0]

def refreshToken():
    global refresh_token
    refresh_token = refresh_token
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    authOptions = {
        "url": "https://accounts.spotify.com/api/token",
        "headers": {"Authorization": f"Basic {auth_header}"},
        "data": {"grant_type": "refresh_token", "refresh_token": os.getenv("SPOTIFY_REFRESH_ACCESS_TOKEN")},
    }

    response = requests.post(**authOptions)
    print(response.status_code)
    if response.status_code == 200:
        global access_token
        global accessTokenExpire

        access_token = response.json()["access_token"]
        accessTokenExpire = time.time() + response.json()["expires_in"]



async def createPlaylist(name):
    
    id = spotFunc.createPlaylist(
        access_token,
        f"{name} Best Songs",
        f"The highest-voted songs by {name}. To vote for their best songs, or your favorite artist’s best songs, visit app.artistsbest.ai",
    )

    headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
    }

    songs = await db.searchArtist(name)
    songsLinks = []
    for i in range(len(songs)):
        this = songs[i][2]
        that = this[31:]
        songsLinks.append("spotify:track:" + that)

    data = {
    "uris": songsLinks
    }

    response = requests.post(f"https://api.spotify.com/v1/playlists/{id}/tracks", data=json.dumps(data), headers=headers)
    
    t = time.time()
    createdPlaylists[name] = [id, t + 5*60]
    updatePlaylist(name)
    return



def checkPlaylistCreation(name):
    if not name in createPlaylist:
        createPlaylist(name)
        return
    
    if time.time() > createdPlaylists[name][1]:
        updatePlaylist(name)
    

async def updatePlaylist(name):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    #print(createdPlaylists[name][0])

    CurrentHighestVotedSongs = await db.searchArtist(name)

    playlistSongs = requests.get(f"https://api.spotify.com/v1/playlists/1fxElOZiQNBLCNvbznTHKZ/tracks", headers=headers)
    playlistSongs = playlistSongs.json()["items"]
    
    #{uri: "spotify:track:"}
    removeSongUrls = []

    #Has the Change entry with link
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


    #removeSongLinks = getRemoveSongs(SongsThatAreOnTheList, addSongs)

    addSongsUrls = []

    for i, item in enumerate(SongsThatAreOnTheList):
        print(SongsThatAreOnTheList[i])
        print(CurrentHighestVotedSongs[i])
        if SongsThatAreOnTheList[i] not in CurrentHighestVotedSongs[i]:
            addSongsUrls.append("spotify:track:" + CurrentHighestVotedSongs[i][2][31:])
            

    data = {"tracks": removeSongUrls}

    print(addSongsUrls)

    deleteSongsUrl(data)    

    datas = {"uris": addSongsUrls}
    
    addSongsRequest(datas)

    return


def getRemoveSongs(songs, song):
    removeSongs = []
    for i in songs:
        if i not in song:
            removeSongs.append({"uri": "spotify:track:" + i[2][31:]})
    return removeSongs


def checkForSongInResponse(name, songs,):
    song = None
    for i in songs:
        if i[1] == name:
            song = []
            song.append(i)
            return song
    return song


def addSongsRequest(data):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }    

    response = requests.post(f"https://api.spotify.com/v1/playlists/1fxElOZiQNBLCNvbznTHKZ/tracks", data=json.dumps(data), headers=headers)
    print(response.json())
    return




def deleteSongsUrl(data):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.delete(f"https://api.spotify.com/v1/playlists/1fxElOZiQNBLCNvbznTHKZ/tracks", data=json.dumps(data), headers=headers)
    print(response.json())
    return


