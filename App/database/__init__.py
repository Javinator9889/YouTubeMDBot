from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


# Singleton class
class DatabaseOperationsBase(object):
    __instance = None

    def __new__(cls, username: str=None, password: str=None):
        if DatabaseOperationsBase.__instance is None:
            if username is None or password is None:
                raise ValueError("You must provide the DB user and password at least the first time")
            DatabaseOperationsBase.__instance = object.__new__(cls)
            auth_provider = PlainTextAuthProvider(username=username, password=password)
            cluster = Cluster(auth_provider=auth_provider)
            DatabaseOperationsBase.__instance.__session = cluster.connect()
            DatabaseOperationsBase.__instance.__createTables()
        return DatabaseOperationsBase.__instance

    def getInstance(self):
        return self.__instance

    def __createTables(self):
        with open("../../Design/db_script.cql", "r") as sql_script:
            queries = sql_script.read().splitlines()
            for query in queries:
                self.__session.execute(query)


class InsertOperations(DatabaseOperationsBase):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def registerNewUser(self, user_id: int, username: str, name: str):
        query = """INSERT INTO YouTubeMDApp.User(user_id, username, name) VALUES (%s, %s, %s);"""
        self.__session.execute(query, (user_id, username, name))

    def registerPreferences(self, user_id: int, audio_quality: str, audio_format: str, os: str,
                            should_ask_metadata: bool):
        query = """
        INSERT INTO YouTubeMDApp.preferences(audio_quality, audio_format, os, should_ask_metadata, user_id) 
        VALUES (%s, %s, %s, %s, %s);
        """
        self.__session.execute(query, (audio_quality, audio_format, os, should_ask_metadata, user_id))

    def registerStatistics(self, user_id: int, lang: str, downloads: int, last_time_active):
        query = """
        INSERT INTO YouTubeMDApp.Statistics(lang, downloads, last_time_active, user_id) VALUES (%s, %s, %s, %s);
        """
        self.__session.execute(query, (lang, downloads, last_time_active, user_id))

    def registerNewSong(self, file_id: str, video_id: str, audio_quality: int, audio_format: int, times_requested: int,
                        is_metadata_by_user: bool):
        query = """
        INSERT INTO YouTubeMDApp.music (file_id, video_id, audio_quality, audio_format, times_requested, 
        is_metadata_by_user) VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.__session.execute(query, (file_id, video_id, audio_quality, audio_format, times_requested,
                                       is_metadata_by_user))

    def registerNewPlaylist(self, playlist_id: str, number_elements: int, times_requested: int):
        query = """
        INSERT INTO YouTubeMDApp.playlist(playlist_id, number_elements, times_requested) VALUES (%s, %s, %s)
        """
        self.__session.execute(query, (playlist_id, number_elements, times_requested))

    def registerNewSongForPlaylist(self, playlist_id: str, file_id: str, playlist_quality: str, playlist_format: str):
        query = """
        INSERT INTO YouTubeMDApp.playlist_has_music 
        (playlist_playlist_id, music_file_id, playlist_quality, playlist_format) VALUES (%s, %s, %s, %s)
        """
        self.__session.execute(query, (playlist_id, file_id, playlist_quality, playlist_format))

    def registerNewSongMetadata(self, title: str, artist: str, cover: str, duration: str, file_id: str):
        query = """
        INSERT INTO YouTubeMDApp.metadata(title, artist, cover, duration, music_file_id) VALUES (%s, %s, %s, %s, %s)
        """
        self.__session.execute(query, (title, artist, cover, duration, file_id))

    def registerNewSongInHistory(self, user_id: int, file_id: str):
        query = """
        INSERT INTO YouTubeMDApp.history(user_id, file_id) VALUES (%s, %s)
        """
        self.__session.execute(query, (user_id, file_id))


class UpdateOperations(DatabaseOperationsBase):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def updateUserUsername(self, new_username: str, user_id: int):
        query = """
        UPDATE YouTubeMDApp.user SET username = %s WHERE user_id = %s
        """
        self.__session.execute(query, (new_username, user_id))

    def updateUserAudioQuality(self, user_id: int, audio_quality: str):
        query = """
        UPDATE YouTubeMDApp.preferences SET audio_quality = %s WHERE user_id = %s
        """
        self.__session.execute(query, (audio_quality, user_id))

    def updateUserAudioFormat(self, user_id: int, audio_format: str):
        query = """
        UPDATE YouTubeMDApp.preferences SET audio_format = %s WHERE user_id = %s
        """
        self.__session.execute(query, (audio_format, user_id))

    def updateUserOS(self, user_id: int, os: str):
        query = """
        UPDATE YouTubeMDApp.preferences SET os = %s WHERE user_id = %s
        """
        self.__session.execute(query, (os, user_id))

    def updateIfUserMustBeRequestedForMetadata(self, user_id: int, shouldAskForMetadata: bool):
        query = """
        UPDATE YouTubeMDApp.preferences SET should_ask_metadata = %s WHERE user_id = %s
        """
        self.__session.execute(query, (shouldAskForMetadata, user_id))

    def updateUserLang(self, user_id: int, lang: str):
        query = """
        UPDATE YouTubeMDApp.statistics SET lang = %s WHERE user_id = %s
        """
        self.__session.execute(query, (lang, user_id))

    def updateUserDownloads(self, user_id: int):
        query = """
        UPDATE YouTubeMDApp.statistics SET downloads = downloads + 1 WHERE user_id = %s
        """
        self.__session.execute(query, (user_id, ))

    def updateUserLastTimeActive(self, user_id: int):
        from datetime import datetime
        query = """
        UPDATE YouTubeMDApp.statistics SET last_time_active = %s WHERE user_id = %s
        """
        self.__session.execute(query, (datetime.now(), user_id))

    def updatePlaylistNumberOfElements(self, playlist_id: str, number_of_elements: int):
        query = """
        UPDATE YouTubeMDApp.playlist SET number_elements = %s WHERE playlist_id = %s
        """
        self.__session.execute(query, (number_of_elements, playlist_id))

    def updatePlaylistTimesRequested(self, playlist_id: str):
        query = """
        UPDATE YouTubeMDApp.playlist SET times_requested = times_requested + 1 WHERE playlist_id = %s
        """
        self.__session.execute(query, (playlist_id, ))


class SelectOperations(DatabaseOperationsBase):
    def __new__(cls, *args, **kwargs):
        super().__new__(cls)


