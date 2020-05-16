#                             YouTubeMDBot
#                  Copyright (C) 2019 - Javinator9889
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#                   (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#               GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
from abc import ABC
from concurrent.futures import Future
from datetime import datetime
from threading import Condition
from threading import Lock
from threading import Thread
from typing import List
from typing import Optional
from collections import deque

import os
import psycopg2

from .. import CQueue
from .. import DB_HOST
from .. import DB_NAME
from .. import DB_PASSWORD
from .. import DB_PORT
from .. import DB_USER

instance_lock = Lock()


class Query:
    def __init__(self,
                 statement: str,
                 values: tuple = None,
                 returning_id: bool = False):
        self.statement = statement
        self.values = values
        self.returning_id = returning_id
        self.return_value: Future = Future()


class PostgreSQLItem:
    __instance = None

    def __new__(cls,
                **kwargs):
        with instance_lock:
            if PostgreSQLItem.__instance is None:
                cls.__instance = object.__new__(cls)
                cls.__instance.must_initialize = True
            return cls.__instance

    def __init__(self, min_ops: int = 100, **kwargs):
        print("init called")
        print(f"Must init?: {self.must_initialize}")
        if self.must_initialize:
            self.connection = psycopg2.connect(user=DB_USER,
                                               password=DB_PASSWORD,
                                               host=DB_HOST,
                                               port=DB_PORT,
                                               dbname=DB_NAME)
            self.min_ops = min_ops
            self.lock = Lock()
            self.__close = False
            self.pending_ops = deque()
            self.waiting_ops = deque()
            self.updating_database = False
            self.iucond = Condition()
            self.qcond = Condition()
            self._iuthread = Thread(target=self.__iuhandler,
                                    name="iuthread")
            self._qthread = Thread(target=self.__qhandler,
                                   name="qthread")
            if not self._iuthread.is_alive():
                self._iuthread.start()
            if not self._qthread.is_alive():
                self._qthread.start()
            self.must_initialize = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def close(self) -> bool:
        with self.lock:
            return self.__close

    @close.setter
    def close(self, value: bool):
        with self.lock:
            self.__close = value

    @property
    def updating_database(self) -> bool:
        with self.lock:
            return self.__updating_database

    @updating_database.setter
    def updating_database(self, value: bool):
        with self.lock:
            self.__updating_database = value

    def __iuhandler(self):
        while not self.close:
            with self.iucond:
                self.iucond.wait_for(
                    lambda: len(self.pending_ops) >= self.min_ops or self.close
                )
            print(
                f"pending_ops {len(self.pending_ops)} >= min_ops {self.min_ops}")
            print(hex(id(self.pending_ops)))
            self.updating_database = True
            with self.connection.cursor() as cursor:
                while len(self.pending_ops) > 0:
                    query = self.pending_ops.pop()
                    if query is None:
                        continue
                    cursor.execute(query.statement, query.values)
                    if query.returning_id:
                        query.return_value.set_result(cursor.fetchone()[0])
            self.connection.commit()
            self.updating_database = False
            with self.qcond:
                self.qcond.notify_all()

    def __qhandler(self):
        while not self.close:
            with self.qcond:
                self.qcond.wait_for(
                    lambda: len(self.waiting_ops) > 0 and
                            not self.updating_database or self.close
                )
            print("qhandler - new item inserted")
            print(hex(id(self.waiting_ops)))
            print(hex(id(self.pending_ops)))
            while len(self.waiting_ops) > 0:
                query = self.waiting_ops.pop()
                if query is None:
                    continue
                print(f"inserting item: {query}")
                self.pending_ops.append(query)
            with self.iucond:
                self.iucond.notify_all()

    def insert(self, query: str, args=(), returning_id: bool = False) -> Query:
        if not self.close:
            insert_query = Query(query, args, returning_id)
            self.waiting_ops.append(insert_query)
            with self.qcond:
                self.qcond.notify_all()
            return insert_query

    def update(self, query: str, args=()):
        if not self.close:
            update_query = Query(query, args)
            self.waiting_ops.append(update_query)
            with self.qcond:
                self.qcond.notify_all()

    def fetchone(self, query: str, args=()) -> list:
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchone()

    def fetchmany(self, query: str, rows: int, args=()) -> list:
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchmany(rows)

    def fetchall(self, query: str, args=()) -> list:
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchall()

    def delete(self, query: str, args=()):
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
            self.connection.commit()

    def callproc(self, proc: str, args=()) -> list:
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.callproc(proc, args)
                return cursor.fetchall()

    def __del__(self):
        print("deleting class")
        self.close = True
        print(f"is there any waiting operation? {len(self.waiting_ops) > 0}")
        # if len(self.waiting_ops) > 0:
        with self.qcond:
            self.qcond.notify_all()
        self._qthread.join()
        print(f"is there any pending operation? {len(self.pending_ops) > 0}")
        # if len(self.pending_ops) > 0:
        with self.iucond:
            self.iucond.notify_all()
        self._iuthread.join()
        print("closing db connection")
        self.connection.close()

        print("removing queues")
        del self.waiting_ops
        del self.pending_ops


class PostgreSQLBase(ABC):
    def __init__(self, item: PostgreSQLItem):
        self.postgres_item = item

    @property
    def connection(self):
        return self.postgres_item.connection

    def insert(self, query: str, args=(), returning_id: bool = False) -> Query:
        return self.postgres_item.insert(query, args, returning_id)

    def update(self, query: str, args=()):
        self.postgres_item.update(query, args)

    def fetchone(self, query: str, args=()) -> list:
        return self.postgres_item.fetchone(query, args)

    def fetchmany(self, query: str, rows: int, args=()) -> list:
        return self.postgres_item.fetchmany(query, rows, args)

    def fetchall(self, query: str, args=()) -> list:
        return self.postgres_item.fetchall(query, args)

    def delete(self, query: str, args=()):
        self.postgres_item.delete(query, args)

    def callproc(self, proc: str, args=()) -> list:
        return self.callproc(proc, args)


class Initializer(PostgreSQLBase):
    def init(self):
        import re

        self.postgres_item.updating_database = True
        dirname = os.path.dirname(os.path.realpath(__file__))
        filename = f"{dirname}/psql_model.sql"
        re_combine_whitespace = re.compile(r"\s+")
        print(f"Found file: {filename}")
        instructions = list()
        current_instruction = ''
        with open(filename, 'r') as file:
            while (line := file.readline()) != '':
                if line.startswith("--") and line[2] != '#':
                    continue
                elif line.startswith("--#"):
                    current_instruction = re_combine_whitespace \
                        .sub(' ', current_instruction).strip()
                    instructions.append(current_instruction)
                    current_instruction = ''
                else:
                    line = re_combine_whitespace.sub(' ', line)
                    current_instruction += line
        print("Executing instructions")
        with self.connection.cursor() as cursor:
            for instruction in instructions:
                print(f"Running instruction {instruction}")
                cursor.execute(instruction)
        self.connection.commit()
        self.postgres_item.updating_database = False
        with self.postgres_item.qcond:
            self.postgres_item.qcond.notify_all()


class UserDB(PostgreSQLBase):
    def get_user_information(self, user_id: int) -> dict:
        data = self.fetchone(
            """SELECT id, name, tag, lang, first_access 
            FROM youtubemd.User WHERE id = %s""", (user_id,)
        )
        return {
            "id": data[0],
            "name": data[1],
            "tag": data[2],
            "lang": data[3],
            "first_access": data[4]
        }

    def get_user_history(self, user_id: int) -> list:
        data = self.fetchall(
            """SELECT id, file_id, metadata_id, date FROM youtubemd.History 
            WHERE user_id = %s""", (user_id,)
        )
        result = []
        for row in data:
            result.append({
                "id": row[0],
                "file_id": row[1],
                "metadata_id": row[2],
                "date": row[3]
            })
        return result

    def register_new_user(self, user_id: int, name: str, tag: str, lang: str):
        now = datetime.now()
        query = """
        INSERT INTO youtubemd.User (id, name, tag, lang, first_access) 
        VALUES (%s, %s, %s, %s, %s)
        """
        self.insert(query, (user_id, name, tag, lang, now))
        self.insert(
            """INSERT INTO youtubemd.Preferences (user_id) VALUES (%s)""",
            (user_id,)
        )

    def update_username(self, user_id: int, name: str):
        self.update(
            """UPDATE youtubemd.User SET name = %s WHERE user_id = %s""",
            (name, user_id)
        )

    def update_user_lang(self, user_id: int, lang: str):
        self.update(
            """UPDATE youtubemd.User SET lang = %s WHERE user_id = %s""",
            (lang, user_id)
        )

    def update_user_tag(self, user_id: int, tag: str):
        self.update(
            """UPDATE youtubemd.User SET tag = %s WHERE user_id = %s""",
            (tag, user_id)
        )

    def register_new_download(self,
                              user_id: int,
                              file_id: str,
                              metadata_id: str):
        now = datetime.now()
        self.insert(
            """INSERT INTO youtubemd.History 
                (file_id, user_id, metadata_id, date) 
                VALUES (%s, %s, %s, %s)""",
            (file_id, metadata_id, user_id, now.date())
        )


class PreferencesDB(PostgreSQLBase):
    def get_user_preferences(self, user_id: int) -> dict:
        data = self.fetchone(
            """SELECT audio_format, audio_quality, send_song_link, 
            ask_for_metadata FROM youtubemd.Preferences WHERE User_id = %s""",
            (user_id,)
        )
        return {
            "audio_format": data[0],
            "audio_quality": data[1],
            "send_song_link": data[2],
            "ask_for_metadata": data[3]
        }

    def update_user_audio_format(self, user_id: int, audio_format: str):
        self.update(
            """UPDATE youtubemd.Preferences SET audio_format = %s WHERE 
            user_id = %s""", (audio_format, user_id)
        )

    def update_user_audio_quality(self, user_id: int, audio_quality: str):
        self.update(
            """UPDATE youtubemd.Preferences SET audio_quality = %s WHERE 
            user_id = %s""", (audio_quality, user_id)
        )

    def update_user_behaviour(self, user_id: int, behaviour: str):
        self.update(
            """UPDATE youtubemd.Preferences SET song_behaviour = %s WHERE 
            user_id = %s""", (behaviour, user_id)
        )

    def update_user_send_song_link(self, user_id: int, send_song_link: bool):
        self.update(
            """UPDATE youtubemd.Preferences SET send_song_link = %s WHERE 
            user_id = %s""", (send_song_link, user_id)
        )


class YouTubeDB(PostgreSQLBase):
    def set_youtube_id(self, youtube_id: str):
        self.insert(
            """INSERT INTO youtubemd.YouTube(id) VALUES (%s) 
            ON CONFLICT DO NOTHING""",
            (youtube_id,)
        )

    def increment_times_requested(self, youtube_id: str):
        self.update(
            """UPDATE youtubemd.YouTube SET 
            times_requested = times_requested + 1 WHERE id = %s""",
            (youtube_id,)
        )

    def is_id_registered(self, youtube_id: str) -> bool:
        return self.fetchone(
            """SELECT EXISTS(SELECT 1 FROM youtubemd.YouTube WHERE id = %s)""",
            (youtube_id,)
        )[0]


class MetadataDB(PostgreSQLBase):
    def register_new_metadata(self,
                              artist: str,
                              album: str,
                              cover: bytes,
                              release_id: str,
                              recording_id: str,
                              duration: int,
                              title: str,
                              youtube_id: str,
                              is_custom_metadata: bool = False) -> int:
        metadata_id = self.insert(
            """INSERT INTO youtubemd.Metadata(artist, album, cover, 
            release_id, recording_id, duration, title, custom_metadata) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (artist, album, cover, release_id, recording_id, duration, title,
             is_custom_metadata), returning_id=True
        ).return_value.result()
        self.insert(
            """INSERT INTO youtubemd.Video_Has_Metadata(id, metadata_id) 
            VALUES (%s, %s)""", (youtube_id, metadata_id)
        )
        return metadata_id

    def get_metadata_for_id(self, metadata_id: int) -> dict:
        data = self.fetchone(
            """SELECT artist, album, cover, release_id, recording_id, 
            duration, title, custom_metadata FROM youtubemd.Metadata 
            WHERE id = %s""", (metadata_id,)
        )
        return {
            "artist": data[0],
            "album": data[1],
            "cover": data[2],
            "release_id": data[3],
            "recording_id": data[4],
            "duration": data[5],
            "title": data[6],
            "custom_metadata": data[7]
        }

    def get_metadata_for_youtube_id(self, youtube_id: str) -> dict:
        data = self.get_metadata_id_for_youtube_id(youtube_id)
        return self.get_metadata_for_id(data)

    def get_metadata_id_for_youtube_id(self, youtube_id: str) -> int:
        return self.fetchone(
            """SELECT metadata_id FROM youtubemd.Video_Has_Metadata 
            WHERE id = %s""", (youtube_id,)
        )[0]

    def update_metadata(self,
                        metadata_id: int,
                        artist: str,
                        album: str,
                        cover: bytes,
                        release_id: str,
                        recording_id: str,
                        duration: int,
                        title: str,
                        is_custom_metadata: bool = False):
        self.update(
            """UPDATE youtubemd.Metadata SET 
            artist = %s,
             album = %s,
             cover = %s,
             release_id = %s,
             recording_id = %s,
             duration = %s,
             title = %s,
             custom_metadata = %s WHERE id = %s""",
            (artist, album, cover, release_id, recording_id, duration, title,
             is_custom_metadata, metadata_id)
        )


class FileDB(PostgreSQLBase):
    def new_file(self,
                 file_id: str,
                 metadata_id: int,
                 audio_quality: str,
                 size: int,
                 user_id: int):
        self.insert(
            """INSERT INTO youtubemd.File(id, metadata_id, audio_quality, size)
             VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (file_id, metadata_id, audio_quality, size)
        )
        date = datetime.now().date()
        self.insert(
            """INSERT INTO youtubemd.History(file_id, user_id, metadata_id, 
            date) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (file_id, user_id, metadata_id, date)
        )

    def get_file_info_by_id(self, file_id: str) -> dict:
        data = self.fetchone(
            """SELECT id, metadata_id, audio_quality, size 
            FROM youtubemd.File WHERE file_id = %s""", (file_id,)
        )
        return {
            "id": data[0],
            "metadata_id": data[1],
            "audio_quality": data[2],
            "size": data[3]
        }

    def get_file_for_youtube_id(self, youtube_id: str) -> Optional[str]:
        youtube_database = YouTubeDB(self.postgres_item)
        if youtube_database.is_id_registered(youtube_id):
            metadata = MetadataDB(self.postgres_item)
            metadata_id = metadata.get_metadata_id_for_youtube_id(youtube_id)
            return self.get_file_for_metadata_id(metadata_id)
        else:
            return None

    def get_file_for_metadata_id(self, metadata_id: int) -> str:
        return self.fetchone(
            """SELECT file_id FROM youtubemd.File WHERE metadata_id = %s""",
            (metadata_id,)
        )[0]


class HistoryDB(PostgreSQLBase):
    def get_history_for_user_id(self, user_id: int) -> List[dict]:
        data = self.fetchall(
            """SELECT id, file_id, user_id, metadata_id, date FROM 
            youtubemd.History WHERE user_id = %s""", (user_id,)
        )
        history = list()
        for value in data:
            history.append(
                {
                    "id": value[0],
                    "file_id": value[1],
                    "user_id": value[2],
                    "metadata_id": value[3]
                }
            )
        return history

    def remove_history_entry(self, history_id: int):
        self.delete(
            """DELETE FROM youtubemd.History WHERE id = %s""", (history_id,)
        )

    def remove_all_history_for_user(self, user_id: int):
        self.delete(
            """DELETE FROM youtubemd.History WHERE user_id = %s""", (user_id,)
        )


class YouTubeStatsDB(PostgreSQLBase):
    def _get_top_ten(self, procedure: str, name: str) -> List[dict]:
        data = self.callproc(procedure)
        top_ten = list()
        for values in data:
            top_ten.append(
                {
                    "id": values[0],
                    name: values[1]
                }
            )
        return top_ten

    def get_top_ten_daily(self) -> List[dict]:
        return self._get_top_ten("youtubemd.top_10_daily", "daily_requests")

    def get_top_ten_weekly(self) -> List[dict]:
        return self._get_top_ten("youtubemd.top_10_weekly", "weekly_requests")

    def get_top_ten_monthly(self) -> List[dict]:
        return self._get_top_ten("youtubemd.top_10_monthly", "monthly_requests")

    def clear_top_ten_daily(self):
        self.callproc("youtubemd.clear_daily_stats")

    def clear_top_ten_weekly(self):
        self.callproc("youtubemd.clear_weekly_stats")

    def clear_top_ten_monthly(self):
        self.callproc("youtubemd.clear_monthly_stats")
