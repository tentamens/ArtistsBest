import sqlite3
import json
import libsql_client
from dotenv import load_dotenv
import os

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


async def searchArtist(name):
    result_set = c.execute(f"SELECT artist, song, link FROM artists WHERE artist='{name}' ORDER BY votes DESC LIMIT 6")
    rows = result_set.rows
    
    result  = [tuple(row) for row in rows]
    return result


def storeArtistSearch():
    pass


def storeArtistSearchs(name):
    c.execute(f"CREATE TABLE IF NOT EXISTS timesSearched (name text, score integer)")

    returnResult = c.execute(f"SELECT * FROM timesSearched WHERE name={name}")
    result = returnResult.rows

    if result:
        c.execute(f"UPDATE timesSearched SET score=score+1 WHERE name={name}")
        return
    c.execute(f"INSERT into timesSearched (name, song) VALUES", (f"{name}", "1"))


def storeVoteSimilarity(artistName, votedArtistName):
    c.execute(
        f"CREATE TABLE IF NOT EXISTS artistVoteSim (name text, votedName text, score integer)"
    )

    returnResult = c.execute(f"SELECT * FROM artistVoteSim WHERE name ={artistName}")
    result = returnResult.rows

    if result:
        c.execute(f"UPDATE artistVoteSim SET score=score+1 WHERE name={artistName}")
        return

    c.execute(
        f"INSERT into artistVoteSim (name, votedName, score) VALUES",
        (f"{artistName}", f"{votedArtistName}", 1),
    )



