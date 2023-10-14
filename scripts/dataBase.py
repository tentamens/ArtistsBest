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


async def addSongScore(artist, song, link):
    returnResult = c.execute(f"SELECT * FROM artists WHERE artist='{artist}'")

    result = returnResult.rows

    if result:
        returnResult = c.execute(
            f"SELECT * FROM artists WHERE artist='{artist}' AND song='{song}'"
        )
        result = returnResult.rows

        if result:
            c.execute(
                f"UPDATE artists SET votes=votes+1 WHERE artist='{artist}' AND song='{song}'"
            )
        else:
            c.execute(
                f"INSERT INTO artists (artist, song, votes, link) VALUES ('{artist}', '{song}', 1, '{link}')"
            )
    else:
        c.execute(
            f"INSERT INTO artists (artist, song, votes, link) VALUES ('{artist}', '{song}', 1, '{link}')"
        )


conn = sqlite3.connect("dataBase.db")
cursor = conn.cursor()


def printSongs():
    select = c.execute("SELECT * FROM artists")
    rows = select.rows
    print(rows)
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
    print(result)

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
    print(rows)
    result = [tuple(row) for row in rows]
    return result


def storePlaylists(name, id):
    print(name)
    print(id)

    c.execute("CREATE TABLE IF NOT EXISTS playlists (name text, id text)")

    returnResult = c.execute("SELECT * FROM playlists WHERE name=?", (name,))
    result = returnResult.rows

    if result:
        c.execute("UPDATE playlists SET id=? WHERE name=?", (id, name))
        return

    c.execute("INSERT into playlists (name, id) VALUES (?, ?)", (name, id))

c.execute(f"Delete FROM playlists where name='Logic'")

def loadPlaylists():
    c.execute(f"CREATE TABLE IF NOT EXISTS playlists (name text, id text)")
    returnResult = c.execute(f"SELECT * FROM playlists")

    result = returnResult.rows
    result = [tuple(row) for row in result]
    trueResult = {}
    for row in result:
        trueResult[row[0]] = [row[1], time.time()]
        pass

    return trueResult
