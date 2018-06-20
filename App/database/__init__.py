from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


# Singleton class
class DatabaseOperations(object):
    __instance = None

    def __new__(cls, username: str, password: str):
        if DatabaseOperations.__instance is None:
            DatabaseOperations.__instance = object.__new__(cls)
        auth_provider = PlainTextAuthProvider(username=username, password=password)
        cluster = Cluster(auth_provider=auth_provider)
        DatabaseOperations.__instance.__session = cluster.connect()
        DatabaseOperations.__instance.__createTables()
        return DatabaseOperations.__instance

    def __createTables(self):
        with open("../../Design/db_script.cql", "r") as sql_script:
            queries = sql_script.read().splitlines()
            for query in queries:
                self.__session.execute(query)

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
