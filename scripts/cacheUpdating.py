import time
import index

artistsUpdateTime = {}


def artistSearched(name, token):

    if name in artistsUpdateTime:
        checkTimeLeft(name, token)

    addArtist(name)



def checkTimeLeft(name):
    if artistsUpdateTime[name] < time.time():
        return
    
    artistsUpdateTime[name] = time.time() + 10*60
    updateCache(name)


def addArtist(name):
    pass

async def updateCache(name, token):
    id = index.getArtistID(name, token)

    index.getArtistsSongs(id, token, name)

