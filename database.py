import sqlite3
import arcade

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


SPARK_TEX = [
    arcade.make_soft_circle_texture(22, (120, 140, 255)),
    arcade.make_soft_circle_texture(22, (155, 110, 255)),
    arcade.make_soft_circle_texture(22, (135, 120, 230)),
]
