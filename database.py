import sqlite3
import arcade

DB_PATH = 'game.db'


def init_db():
    'Init the database. Does none if it exists.'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS map(
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            value TEXT NOT NULL,
            primary key (x, y)
    )'''
    )

    c.execute('''
    CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            value TEXT NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TINYINT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS game_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
    ''')

    conn.commit()
    conn.close()


SPARK_TEX = [
    arcade.make_soft_circle_texture(22, (120, 140, 255)),
    arcade.make_soft_circle_texture(22, (155, 110, 255)),
    arcade.make_soft_circle_texture(22, (135, 120, 230)),
]

SETTINGS = ['music_volume', 'sfx_volume']