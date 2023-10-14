import scripts.dataBase as db




def voteOnArtist(artist, vote):
    db.storeVoteSimilarity(artist, vote)


def fetchHighestVotes(artist):
    result = db.loadVoteSimilarity(artist)
    return result

