import sqlite3
import numpy as np
import json

conn = sqlite3.connect("dataBase.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS artists (artist TEXT, song TEXT, votes INTEGER, link TEXT)")

def addSongScore(artist, song, link):
    cursor.execute("SELECT * FROM artists WHERE artist=?", (artist,))
    result = cursor.fetchone()

    if result:
        print("existing artist")
        
        cursor.execute("SELECT * FROM artists WHERE artist=? AND song=?", (artist, song))
        result = cursor.fetchone()

        if result:
            cursor.execute("UPDATE artists SET votes=votes+1 WHERE artist=? AND song=?", (artist, song))
        else:
            cursor.execute("INSERT INTO artists (artist, song, votes, link) VALUES (?, ?, ?, ?)", (artist, song, +1, link))
    else:
        print("new artist")
        cursor.execute("INSERT INTO artists (artist, song, votes, link) VALUES (?, ?, 1, ?)", (artist, song, link))
    conn.commit()


def printSongs():
    cursor.execute("SELECT * FROM artists")
    rows = cursor.fetchall()
    
    for row in rows:
        print(row)
        pass

def searchArtist(name):
    cursor.execute("SELECT * FROM artists WHERE artist=?", (name,))
    rows = cursor.fetchall()
    
    result = [rows[i] for i in range(min(6, len(rows) )) ]
    result = json.dumps(result)
    #result = tuple(map(tuple, result)) 

    return result




