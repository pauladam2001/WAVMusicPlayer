import sqlite3


class DatabaseRepository:
    def __init__(self):
        self.connection = sqlite3.connect('MusicPlayer.db')
        self.cursor = self.connection.cursor()
        # self.create_table()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE songs (
                        song blob UNIQUE
                        )""")

    def get_songs(self):
        self.cursor.execute("SELECT * FROM songs")
        items = self.cursor.fetchall()
        return items

    def add_one_song(self, song_name):
        self.cursor.execute("INSERT INTO songs VALUES (?)", (song_name,))

    def add_many_songs(self, songs_list):
        self.cursor.executemany("INSERT INTO songs VALUES (?)", (songs_list,))

    def delete_song(self, song_name):
        self.cursor.execute("DELETE FROM songs WHERE song = (?)", (song_name,))

    def close_connection(self):
        self.connection.commit()
        self.connection.close()
