import sqlite3


DB_PATH = 'game.db'


def init_dbs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        '''
    CREATE TABLE IF NOT EXISTS map(
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            z INTEGER NOT NULL,
            value TEXT NOT NULL
    )'''
    )
