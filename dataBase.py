import sqlite3

conn = sqlite3.connect("dataBase.db")
cursor = conn.cursor()

def addSongScore(artist, song):
    cursor.execute("CREATE TABLE IF NOT EXISTS artist (id INTEGER PRIMARY KEY, name TEXT, song TEXT, votes INTEGER)")
    
    cursor.execute("SELECT votes FROM artist WHERE name = ?", (artist,))
    row = cursor.fetchone()
    if row is not None:
        votes = row[0]
        cursor.execute("UPDATE artist SET votes = ? WHERE name = ?", (votes + 1, artist))
        conn.commit()
        return
    
    cursor.execute("INSERT INTO artist (name, song, votes) VALUES (?, ?, ?)", (artist, song, 1))
    conn.commit()

def printSongs():
    cursor.execute("SELECT * FROM artist")
    rows = cursor.fetchall()
    
    for row in rows:
        pass

def searchArtist(name):
    cursor.execute("SELECT * FROM artist WHERE name=?", (name,))
    rows = cursor.fetchall()
    
    result = [rows[i] for i in range(min(5, len(rows) )) ]
    return result




