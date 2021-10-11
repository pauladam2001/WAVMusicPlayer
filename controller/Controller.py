
class Controller:
    def __init__(self, repository):
        self._repository = repository

    def get_songs(self):
        return self._repository.get_songs()

    def add_one_song(self, song_name):
        self._repository.add_one_song(song_name)

    def add_many_songs(self, songs_list):
        self._repository.add_many_songs(songs_list)

    def delete_song(self, song_name):
        self._repository.delete_song(song_name)

    def close_connection(self):
        self._repository.close_connection()
