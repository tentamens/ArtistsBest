import scripts.dataBase as db
import json


# uuid{theArtist{#Songs [IftheyhaveusedtheirFirst5Votes:bool, theNumberofVotes:int], WhichWeekTheyLastVoted:int}, #ArtistVote [IftheyhaveusedtheirFirst5Votes:bool, theNumberofVotes:int], WhichWeekTheyLastVoted:int}}
users = {}

with open("userHolder.json", "r") as file:
    users = json.load(file)
    file.close()

currentWeek = 0

async def voteOnSong(artistName, uuid):
    if uuid not in users:
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
    db.storeUserVoteDict()
    with open("usersHolder.json", "w") as f:
        json.dump(users, f)
        f.close()


def userHaventVoted(uuid, artistName):
    if users[uuid][artistName][0][1] >= 5:
        users[uuid][artistName][0][0] = True
        users[uuid][artistName][1] = currentWeek
        storeUsers()
        return 410
    
    users[uuid][artistName][0][1] += 1
    storeUsers()
    return 200


def verifyStatusAndUpdate(status, artistName, songName, songLink):
    if status == 401:
        return [401, {"exitCode": 550}]
    if status == 409:
        return [409, {}]
    if status == 410:
        return [410, {}]
    
    db.addSongScore(artistName, songName, songLink)
    return [200, "successfully vote on artist"]

