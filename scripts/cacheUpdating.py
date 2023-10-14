import time
import scripts.spotifyFunctions as index

artistsUpdateTime = {}


def artistSearched(name, token):
    print(artistsUpdateTime)
    if name in artistsUpdateTime:
        checkTimeLeft(name, token)
        return

    addArtist(name, token)


def checkTimeLeft(name, token):
    global artistsUpdateTime

    print("world")
    if artistsUpdateTime[name] < time.time():
        return
    times = time.time()
    artistsUpdateTime[name] = times + 10 * 60
    updateCache(name, token)


def addArtist(name, token):
    global artistsUpdateTime

    times = time.time()
    artistsUpdateTime[name] = times + 10 * 60
    updateCache(name, token)
    print(artistsUpdateTime)


def updateCache(name, token):
    id = index.getArtistID(name, token)

    index.getArtistsSongs(id, token, name)
