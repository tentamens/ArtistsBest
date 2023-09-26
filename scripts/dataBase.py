import sqlite3
import json
import libsql_client
from dotenv import load_dotenv
import os
load_dotenv()


c = libsql_client.create_client_sync(url=os.getenv("URL"), auth_token=os.getenv("TOKEN"))
c.execute("CREATE TABLE IF NOT EXISTS artists (artist TEXT, song TEXT, votes INTEGER, link TEXT)")

async def addSongScore(artist,song,link):
    
    returnResult = c.execute(f"SELECT * FROM artists WHERE artist='{artist}'")
    
    result = returnResult.rows

    if result:
        
        print("existing artist")
        returnResult = c.execute(f"SELECT * FROM artists WHERE artist='{artist}' AND song='{song}'")
        result = returnResult.rows

        if result:
            c.execute(f"UPDATE artists SET votes=votes+1 WHERE artist='{artist}' AND song='{song}'")
        else:
            c.execute(f"INSERT INTO artists (artist, song, votes, link) VALUES ('{artist}', '{song}', 1, '{link}')")
    else:
        print("new artist")
        c.execute(f"INSERT INTO artists (artist, song, votes, link) VALUES ('{artist}', '{song}', 1, '{link}')")




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
    result_set = c.execute(f"SELECT * FROM artists WHERE artist='{name}'")
    rows = result_set.rows
    
    result = [rows[i] for i in range(min(6, len(rows) )) ]
    result = json.dumps(result)
    #result = tuple(map(tuple, result)) 

    return result

def storeArtistSearch():
    pass

def storeArtistSearchs(name):
    c.execute(f"CREATE TABLE IF NOT EXISTS timesSearched (name text, score integer)")

    c.execute(f"SELECT score FROM timesSearched WHERE name = ?", (name,))





