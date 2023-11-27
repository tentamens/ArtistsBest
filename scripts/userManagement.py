import scripts.dataBase as db


# uuid{theArtist{#Songs [IftheyhaveusedtheirFirst5Votes:bool, theNumberofVotes:int], WhichWeekTheyLastVoted:int}, #ArtistVote [IftheyhaveusedtheirFirst5Votes:bool, theNumberofVotes:int], WhichWeekTheyLastVoted:int}}
users = {}
currentWeek = 0

async def voteOnSong(artistName, uuid):
    if uuid in users:
        return 401
    
    if artistName not in users[uuid]:
        users[uuid][artistName] = [[False, 0], None]
        storeUsers()
        return

    if users[uuid][artistName][0][0] == False:
        result = userHaventVoted(users[uuid][artistName])
        return result
    
    if users[uuid][artistName][1] > currentWeek:
        return 410
    
    return 200

    


def storeUsers():
    pass


def userHaventVoted(uuid, artistName):
    if users[uuid][artistName][0][1] >= 5:
        users[uuid][artistName][0][0] = True
        users[uuid][artistName][1] = currentWeek
        return 410
    
    users[uuid][artistName][0][1] += 1
    return 200


def verifyStatusAndUpdate(status, artistName, songName, songLink):
    if status == 410:
        return [410, "the user was not allowed to vote again"]
    
    db.addSongScore(artistName, songName, songLink)
    return [200, "successfully vote on song"]