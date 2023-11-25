import sqlite3
import json
import libsql_client
from dotenv import load_dotenv
import os
import time

load_dotenv()


c = libsql_client.create_client_sync(
    url=os.getenv("URL"), auth_token=os.getenv("TOKEN")
)
c.execute(
    "CREATE TABLE IF NOT EXISTS artists (artist TEXT, song TEXT, votes INTEGER, link TEXT)"
)



c.execute("CREATE INDEX IF NOT EXISTS votes_index ON artists(votes)")


def addSongScore(artist, song, link):
    returnResult = c.execute("SELECT * FROM artists WHERE artist=?", (artist,))

    result = returnResult.rows

    if result:
        returnResult = c.execute(
            "SELECT * FROM artists WHERE artist=? AND song=?", (artist, song)
        )
        result = returnResult.rows

        if result:
            print("exists")
            c.execute(
                "UPDATE artists SET votes=votes+1 WHERE artist=? AND song=?",
                (artist, song),
            )
        else:
            print("insert")
            c.execute(
                "INSERT INTO artists (artist, song, votes, link) VALUES (?, ?, 1, ?)",
                (artist, song, link),
            )
    else:
        c.execute(
            "INSERT INTO artists (artist, song, votes, link) VALUES (?, ?, 1, ?)",
            (artist, song, link),
        )
        print("EXE")


def printSongs():
    select = c.execute("SELECT * FROM artists")
    rows = select.rows

    return
    for row in rows:
        print(row)
        pass


def searchArtist(name):
    result_set = c.execute(
        f"SELECT artist, song, link FROM artists WHERE artist='{name}' ORDER BY votes DESC LIMIT 6"
    )
    rows = result_set.rows

    result = [tuple(row) for row in rows]
    return result


def storeArtistSearch():
    pass


def storeArtistSearchs(name):
    c.execute(f"CREATE TABLE IF NOT EXISTS timesSearched (name text, score integer)")

    returnResult = c.execute(f"SELECT * FROM timesSearched WHERE name='{name}'")
    result = returnResult.rows

    if result:
        c.execute(f"UPDATE timesSearched SET score=score+1 WHERE name='{name}'")
        return
    c.execute(f"INSERT into timesSearched (name, score) VALUES ('{name}', 1)")


def storeVoteSimilarity(artistName, votedArtistName, link):
    c.execute(
        f"CREATE TABLE IF NOT EXISTS artistVoteSim (name text, votedName text, score integer, link text)"
    )

    returnResult = c.execute(f"SELECT * FROM artistVoteSim WHERE name ='{artistName}'")
    result = returnResult.rows

    if result:
        c.execute(f"UPDATE artistVoteSim SET score=score+1 WHERE name='{artistName}'")
        return

    c.execute(
        f"INSERT into artistVoteSim (name, votedName, score, link) VALUES ('{artistName}', '{votedArtistName}', 1, '{link}')"
    )
    return


def loadVoteSimilarity(name):
    c.execute(
        f"CREATE TABLE IF NOT EXISTS artistVoteSim (name text, votedName text, score integer, link text)"
    )
    returnResult = c.execute(
        f"SELECT votedName, link FROM artistVoteSim WHERE name='{name}' ORDER BY score DESC LIMIT 3"
    )
    rows = returnResult.rows
    result = [tuple(row) for row in rows]
    return result


def storePlaylists(name, id):

    c.execute("CREATE TABLE IF NOT EXISTS playlists (name text, id text)")

    returnResult = c.execute("SELECT * FROM playlists WHERE name=?", (name,))
    result = returnResult.rows

    if result:
        c.execute("UPDATE playlists SET id=? WHERE name=?", (id, name))
        return

    c.execute("INSERT into playlists (name, id) VALUES (?, ?)", (name, id))


def loadPlaylists():
    c.execute(f"CREATE TABLE IF NOT EXISTS playlists (name text, id text)")
    returnResult = c.execute(f"SELECT * FROM playlists")

    result = returnResult.rows
    print(result)
    result = [tuple(row) for row in result]
    trueResult = {}
    for row in result:
        trueResult[row[0]] = [row[1], time.time()]
        pass

    return trueResult


def storeUserGoogle(uuid, googleToken):
    
    c.execute(f"CREATE TABLE IF NOT EXISTS users (googleToken text, uuid text)")

    returnResult = c.execute("SELECT * FROM users WHERE googleToken=?", (googleToken,))
    result = returnResult.rows

    if result:
        c.execute("UPDATE users SET googleToken=? WHERE uuid=?", (googleToken, uuid))
        return

    c.execute("INSERT into users (googleToken, uuid) VALUES (?, ?)", (googleToken, uuid))


def loadUserGoogle(token):
    c.execute(f"CREATE TABLE IF NOT EXISTS users (googleToken text, uuid text)")
    returnResult = c.execute("SELECT googleToken FROM users WHERE googleToken=?", (token,))
    result = returnResult.rows
    print(result, " hello world")
    if result:
        return [True, result[0][0]]
    return [False]