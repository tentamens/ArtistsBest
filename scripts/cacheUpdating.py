import time
import scripts.spotifyFunctions as index

artistsUpdateTime = {}


def artistSearched(name, token):
    print(artistsUpdateTime)
    if name in artistsUpdateTime:
        checkTimeLeft(name, token)

    addArtist(name)


def checkTimeLeft(name, token):
    global artistsUpdateTime

    print("world")
    if artistsUpdateTime[name] < time.time():
        return
    times = time.time()
    artistsUpdateTime[name] = times + 10*60
    updateCache(name, token)


def addArtist(name):
    global artistsUpdateTime

    print("hello")
    times = time.time()
    artistsUpdateTime[name] = times + 10*60


async def updateCache(name, token):
    id = index.getArtistID(name, token)

    index.getArtistsSongs(id, token, name)
