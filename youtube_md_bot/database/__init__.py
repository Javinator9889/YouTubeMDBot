import uuid

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from collections import namedtuple

from datetime import datetime


# Singleton class
class DatabaseOperationsBase(object):
    __instance = None

    def __new__(cls, username: str=None, password: str=None):
        if DatabaseOperationsBase.__instance is None:
            if username is None or password is None:
                raise ValueError("You must provide the DB user and password at least the first time")
            DatabaseOperationsBase.__instance = object.__new__(cls)
            DatabaseOperationsBase.__instance.__username = username
            DatabaseOperationsBase.__instance.__password = password
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

    def finishConnection(self):
        self.__session.shutdown()


class InsertOperations(DatabaseOperationsBase):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def registerNewUser(self, user_id: int, username: str, name: str):
        query = """INSERT INTO YouTubeMDApp.User(user_id, username, name, first_use) VALUES (%s, %s, %s, %s);"""
        self.__session.execute(query, (user_id, username, name, datetime.now()))

    def registerPreferences(self, user_id: int, audio_quality: str, audio_format: str, os: str,
                            should_ask_metadata: bool):
        query = """
        INSERT INTO YouTubeMDApp.preferences(audio_quality, audio_format, os, should_ask_metadata, user_id) 
        VALUES (%s, %s, %s, %s, %s);
        """
        self.__session.execute(query, (audio_quality, audio_format, os, should_ask_metadata, user_id))

    def registerStatistics(self, user_id: int, lang: str, downloads: int, last_time_active: datetime):
        query = """
        INSERT INTO YouTubeMDApp.Statistics(lang, downloads, last_time_active, user_id) VALUES (%s, %s, %s, %s);
        """
        self.__session.execute_async(query, (lang, downloads, last_time_active, user_id))

    def registerNewSong(self, file_id: str, video_id: str, audio_quality: int, audio_format: int, times_requested: int,
                        is_metadata_by_user: bool):
        query = """
        INSERT INTO YouTubeMDApp.music (file_id, video_id, audio_quality, audio_format, times_requested, 
        is_metadata_by_user) VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.__session.execute_async(query, (file_id, video_id, audio_quality, audio_format, times_requested,
                                       is_metadata_by_user))

    def registerNewPlaylist(self, playlist_id: str, number_elements: int, times_requested: int):
        query = """
        INSERT INTO YouTubeMDApp.playlist(playlist_id, number_elements, times_requested) VALUES (%s, %s, %s)
        """
        self.__session.execute_async(query, (playlist_id, number_elements, times_requested))

    def registerNewSongForPlaylist(self, playlist_id: str, file_id: str, playlist_quality: str, playlist_format: str):
        query = """
        INSERT INTO YouTubeMDApp.playlist_has_music 
        (playlist_playlist_id, music_file_id, playlist_quality, playlist_format) VALUES (%s, %s, %s, %s)
        """
        self.__session.execute(query, (playlist_id, file_id, playlist_quality, playlist_format))

    def registerNewSongMetadata(self, title: str, artist: str, cover: str, duration: str, file_id: str):
        query = """
        INSERT INTO YouTubeMDApp.metadata(title, artist, cover, song_duration, music_file_id) 
        VALUES (%s, %s, %s, %s, %s)
        """
        self.__session.execute_async(query, (title, artist, cover, duration, file_id))

    def registerNewSongInHistory(self, user_id: int, file_id: str):
        query = """
        INSERT INTO YouTubeMDApp.history(user_id, file_id) VALUES (%s, %s)
        """
        self.__session.execute_async(query, (user_id, file_id))


class UpdateOperations(DatabaseOperationsBase):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def updateUserUsername(self, new_username: str, user_id: int):
        query = """
        UPDATE YouTubeMDApp.user SET username = %s WHERE user_id = %s
        """
        self.__session.execute_async(query, (new_username, user_id))

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
        self.__session.execute_async(query, (lang, user_id))

    def updateUserDownloads(self, user_id: int):
        query = """
        UPDATE YouTubeMDApp.statistics SET downloads = downloads + 1 WHERE user_id = %s
        """
        self.__session.execute_async(query, (user_id, ))

    def updateUserLastTimeActive(self, user_id: int):
        query = """
        UPDATE YouTubeMDApp.statistics SET last_time_active = %s WHERE user_id = %s
        """
        self.__session.execute_async(query, (datetime.now(), user_id))

    def updatePlaylistNumberOfElements(self, playlist_id: str, number_of_elements: int):
        query = """
        UPDATE YouTubeMDApp.playlist SET number_elements = %s WHERE playlist_id = %s
        """
        self.__session.execute_async(query, (number_of_elements, playlist_id))

    def updatePlaylistTimesRequested(self, playlist_id: str):
        query = """
        UPDATE YouTubeMDApp.playlist SET times_requested = times_requested + 1 WHERE playlist_id = %s
        """
        self.__session.execute_async(query, (playlist_id, ))


class SelectOperations(DatabaseOperationsBase):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def selectUserData(self, user_id: int):
        # type: () -> namedtuple
        query = """SELECT username, name FROM YouTubeMDApp.User WHERE user_id = %s"""
        return self.__session.execute(query, (user_id, ))

    def selectUserPreferences(self, user_id: int):
        # type: () -> namedtuple
        query = """
        SELECT audio_quality, audio_format, os, should_ask_metadata FROM YouTubeMDApp.preferences WHERE user_id = %s
        """
        return self.__session.execute(query, (user_id, ))

    def selectUserHistoryForUserID(self, user_id: int):
        # type: () -> namedtuple
        query = """SELECT file_id FROM YouTubeMDApp.history WHERE user_id = %s"""
        return self.__session.execute(query, (user_id,))

    def selectMetadataForMusicID(self, music_id: str):
        # type: () -> namedtuple
        query = """SELECT title, artist, cover, song_duration FROM YouTubeMDApp.metadata WHERE music_file_id = %s"""
        return self.__session.execute(query, (music_id,))

    def searchMusicByVideoIDAndExtras(self, video_id: str, audio_quality: int, audio_format: int):
        # type: () -> namedtuple
        query = """
        SELECT file_id FROM YouTubeMDApp.music WHERE (video_id = %s, audio_quality = %s, audio_format = %s, 
        is_metadata_by_user = %s)
        """
        return self.__session.execute(query, (video_id, audio_quality, audio_format, False))

    def searchPlaylistByIDAndExtras(self, playlist_id: str, playlist_quality: int, playlist_format: int):
        # type: () -> namedtuple
        query = """
        SELECT playlist_unique_id FROM YouTubeMDApp.playlist WHERE (playlist_id = %s, playlist_quality = %s,
         playlist_format = %s)
        """
        return self.__session.execute(query, (playlist_id, playlist_quality, playlist_format))

    def selectSongsOfPlaylist(self, playlist_unique_id: uuid):
        # type: () -> namedtuple
        query = """
        SELECT music_file_id FROM YouTubeMDApp.playlist_has_music WHERE playlist_unique_id = %s
        """
        return self.__session.execute(query, (playlist_unique_id, ))

    def selectStatisticsForUser(self, user_id: int):
        # type: () -> namedtuple
        query = """
        SELECT lang, downloads, last_time_active FROM YouTubeMDApp.Statistics WHERE user_id = %s
        """
        return self.__session.execute(query, (user_id, ))

    def selectTotal24ActiveUsers(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(user_id) FROM YouTubeMDApp.Statistics WHERE last_time_active >= (%s - 1d)
        """
        return self.__session.execute(query, (datetime.now(), ))

    def selectMostDownloadedSong(self):
        # type: () -> namedtuple
        query = """
        SELECT MAX(times_requested) FROM YouTubeMDApp.music
        """
        return self.__session.execute(query)

    def selectMostDownloadedPlaylist(self):
        # type: () -> namedtuple
        query = """
        SELECT MAX(times_requested) FROM YouTubeMDApp.playlist
        """
        return self.__session.execute(query)

    def selectMostUsedGeoLocation(self):
        # type: () -> namedtuple
        query = """
        SELECT lang, COUNT(lang) AS most_used_lang FROM YouTubeMDApp.Statistics GROUP BY lang ORDER BY most_used_lang
        DESC
        """
        return self.__session.execute(query)

    def selectTotalUsers(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(user_id) FROM YouTubeMDApp.User
        """
        return self.__session.execute(query)

    def selectTotalRequestedSongs(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(file_id) FROM YouTubeMDApp.music
        """
        return self.__session.execute(query)

    def selectTotalSongsRequests(self):
        # type: () -> namedtuple
        query = """
        SELECT SUM(times_requested) FROM YouTubeMDApp.music
        """
        return self.__session.execute(query)

    def selectTotalRequestedPlaylists(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(playlist_unique_id) FROM YouTubeMDApp.playlist
        """
        return self.__session.execute(query)

    def selectTotalPlaylistsRequests(self):
        # type: () -> namedtuple
        query = """
        SELECT SUM(times_requested) FROM YouTubeMDApp.playlist
        """
        return self.__session.execute(query)

    def selectMostCommonQuality(self):
        # type: () -> namedtuple
        query = """
        SELECT audio_quality, COUNT(audio_quality) AS most_used_audio_quality FROM YouTubeMDApp.preferences 
        GROUP BY audio_quality ORDER BY most_used_audio_quality DESC 
        """
        return self.__session.execute(query)

    def selectMostCommonFormat(self):
        # type: () -> namedtuple
        query = """
        SELECT audio_format, COUNT(audio_format) AS most_used_audio_format FROM YouTubeMDApp.preferences
        GROUP BY audio_format ORDER BY most_used_audio_format DESC 
        """
        return self.__session.execute(query)

    def selectMostCommonOS(self):
        # type: () -> namedtuple
        query = """
        SELECT os, COUNT(os) AS most_used_os FROM YouTubeMDApp.preferences GROUP BY os ORDER BY most_used_os DESC 
        """
        return self.__session.execute(query)

    def selectUsersRegistered30DaysAgo(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(user_id) FROM YouTubeMDApp.User WHERE first_use >= (%s - 1mo)
        """
        return self.__session.execute(query, (datetime.now(), ))

    def selectUsersRegistered7DaysAgo(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(user_id) FROM YouTubeMDApp.User WHERE first_use >= (%s - 1w)
        """
        return self.__session.execute(query, (datetime.now(), ))

    def selectUsersRegisteredLatest24Hours(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(user_id) FROM YouTubeMDApp.User WHERE first_use >= (%s - 1d)
        """
        return self.__session.execute(query, (datetime.now(), ))

    def selectUsersRegisteredAYearAgo(self):
        # type: () -> namedtuple
        query = """
        SELECT COUNT(user_id) FROM YouTubeMDApp.User WHERE first_use >= (%s - 1y)
        """
        return self.__session.execute(query, (datetime.now(), ))

    def selectLatestRegisteredUSer(self):
        # type: () -> namedtuple
        query = """
        SELECT user_id FROM YouTubeMDApp.User WHERE first_use = (SELECT MAX(first_use) FROM YouTubeMDApp.User)
        """
        return self.__session.execute(query)
