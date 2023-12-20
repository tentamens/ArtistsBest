import sqlite3
import json
import libsql_client
from dotenv import load_dotenv
import os
import time
import scripts.userManagement as userManagement

load_dotenv()


c = libsql_client.create_client_sync(
    url=os.getenv("URL"), auth_token=os.getenv("TOKEN")
)

c.execute(
    "CREATE TABLE IF NOT EXISTS artists (artist TEXT, song TEXT, votes INTEGER, link TEXT)"
)



c.execute(f"CREATE TABLE IF NOT EXISTS searches (UserInput text, result text, times int)")
c.execute(f"CREATE TABLE IF NOT EXISTS currentWeek (week int)")
c.execute(f"CREATE TABLE IF NOT EXISTS userVoteDict (voteDict text)")
c.execute("CREATE INDEX IF NOT EXISTS votes_index ON artists(votes)")
c.execute(f"CREATE TABLE IF NOT EXISTS timesSearched (name text, score integer)")
c.execute(f"CREATE TABLE IF NOT EXISTS artistVoteSim (name text, votedName text, score integer, link text)")
c.execute("CREATE TABLE IF NOT EXISTS playlists (name text, id text)")
c.execute(f"CREATE TABLE IF NOT EXISTS users (googleToken text, uuid text)")



def addSongScore(artist, song, link):
    returnResult = c.execute("SELECT * FROM artists WHERE artist=?", (artist,))

    result = returnResult.rows

    if result:
        returnResult = c.execute(
            "SELECT * FROM artists WHERE artist=? AND song=?", (artist, song)
        )
        result = returnResult.rows
        
        if result:
            
            c.execute(
                "UPDATE artists SET votes=votes+1 WHERE artist=? AND song=?",
                (artist, song),
            )
        else:
            c.execute(
                "INSERT INTO artists (artist, song, votes, link) VALUES (?, ?, 1, ?)",
                (artist, song, link),
            )
    else:
        c.execute(
            "INSERT INTO artists (artist, song, votes, link) VALUES (?, ?, 1, ?)",
            (artist, song, link),
        )


def printSongs():
    select = c.execute("SELECT * FROM artistVoteSim")
    rows = select.rows

    for row in rows:
        print(row)
        pass


def searchArtist(name):
    result_set = c.execute(
        f"SELECT artist, song, link FROM artists WHERE artist='{name}' ORDER BY votes DESC LIMIT 6"
    )
    rows = result_set.rows

    result = [tuple(row) for row in rows]
    print(result)
    return result


def storeArtistSearch():
    pass


def storeArtistSearchs(name):
    

    returnResult = c.execute(f"SELECT * FROM timesSearched WHERE name='{name}'")
    result = returnResult.rows

    if result:
        c.execute(f"UPDATE timesSearched SET score=score+1 WHERE name='{name}'")
        return
    c.execute(f"INSERT into timesSearched (name, score) VALUES ('{name}', 1)")


def storeVoteSimilarity(artistName, votedArtistName, link):

    returnResult = c.execute(f"SELECT * FROM artistVoteSim WHERE name =? and votedName=?", (artistName, votedArtistName))
    result = returnResult.rows

    if result:
        c.execute(f"UPDATE artistVoteSim SET score=score+1 WHERE name=? and votedName=?", (artistName, votedArtistName))
        return
    c.execute(
        f"INSERT into artistVoteSim (name, votedName, score, link) VALUES ('{artistName}', '{votedArtistName}', 1, '{link}')"
    )
    return


def loadVoteSimilarity(name):
    returnResult = c.execute(
        f"SELECT votedName, link FROM artistVoteSim WHERE name='{name}' ORDER BY score DESC LIMIT 3"
    )
    rows = returnResult.rows
    result = [tuple(row) for row in rows]
    return result


def storePlaylists(name, id):

    returnResult = c.execute("SELECT * FROM playlists WHERE name=?", (name,))
    result = returnResult.rows

    if result:
        c.execute("UPDATE playlists SET id=? WHERE name=?", (id, name))
        return

    c.execute("INSERT into playlists (name, id) VALUES (?, ?)", (name, id))


def loadPlaylists():

    returnResult = c.execute(f"SELECT * FROM playlists")

    result = returnResult.rows
    result = [tuple(row) for row in result]
    trueResult = {}
    for row in result:
        trueResult[row[0]] = [row[1], time.time()]
        pass

    return trueResult


def storeUserGoogle(googleToken, uuid):

    returnResult = c.execute("SELECT * FROM users WHERE googleToken=?", (googleToken,))
    result = returnResult.rows

    if result:
        c.execute("UPDATE users SET googleToken=? WHERE uuid=?", (googleToken, uuid))
        return

    c.execute("INSERT into users (googleToken, uuid) VALUES (?, ?)", (googleToken, uuid))


def loadUserGoogle(token):
    
    returnResult = c.execute("SELECT * FROM users WHERE googleToken=?", (token,))
    result = returnResult.rows
    if result:
        return [True, result[0][0]]
    return [False]

def storeUserVoteDict():
    c.execute(f"UPDATE userVoteDict SET voteDict=?", (str(userManagement.users),))
    


def loadUserVoteDict():
    returnResult = c.execute("SELECT * FROM userVoteDict")
    result = returnResult.rows
    if result == []:
        return {}
    userManagement.users = json.loads(result[0])


def storeCurrentWeek():
    c.execute(f"UPDATE currentWeek SET week=?", (userManagement.currentWeek,))

def loadCurrentWeek():
    returnResult = c.execute("SELECT * FROM currentWeek")
    result = returnResult.rows
    if result == []:
        userManagement.currentWeek = 0
        return
    userManagement.currentWeek = result[0][0]

loadCurrentWeek()

def storeEachSearch(input, result):
    returnResult = c.execute("SELECT * FROM searches WHERE UserInput=? and result=?", (input, result))
    returns = returnResult.rows

    if returns:
        c.execute("UPDATE searches SET times=times+1 WHERE UserInput=? and result=?", (input, result))
        return
    
    c.execute("INSERT INTO searches (UserInput, result, times) VALUES (?, ?, 1)", (input, result))




