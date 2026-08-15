import sqlite3
from pathlib import Path

db_path = Path("database/bot.db")

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS forum_channels 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         guild_id INTEGER NOT NULL UNIQUE,
         forum_channel_id INTEGER NOT NULL)"""
    )
    print("The forum channel db has been created.")
    conn.commit()
    conn.close()

def set_the_forum_channel_to_db(guild_id:int, forum_channel_id:int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
                INSERT INTO forum_channels 
                (guild_id, forum_channel_id)
                VALUES (?,?)
                    """,
                    (guild_id,forum_channel_id))
    conn.commit()
    conn.close()

def guild_verification(guild_id:int)->bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT forum_channel_id FROM forum_channels WHERE guild_id = ?""", (guild_id,)
    )
    result = cursor.fetchone()[0]
    
    conn.close()
    return bool(result) if result else False

def get_forum_channel(guild_id:int):
    """Get the forum channel id from the forum_channels db"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT forum_channel_id FROM forum_channels
        WHERE guild_id = ?""",(guild_id,)
    )
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None
