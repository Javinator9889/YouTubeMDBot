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
import psycopg2

from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import Optional

from threading import Lock
from threading import Thread
from threading import Condition

from .. import CQueue
from .. import DB_HOST
from .. import DB_NAME
from .. import DB_PASSWORD
from .. import DB_PORT
from .. import DB_USER


class Query:
    def __init__(self, statement: str, values: tuple = None):
        self.statement = statement
        self.values = values


class PostgreSQLBase(ABC):
    __instance = None

    def __new__(cls,
                min_ops: int = 100,
                **kwargs):
        if PostgreSQLBase.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.connection = psycopg2.connect(user=DB_USER,
                                                         password=DB_PASSWORD,
                                                         host=DB_HOST,
                                                         port=DB_PORT,
                                                         dbname=DB_NAME)
            cls.__instance.min_ops = min_ops
            cls.__instance._iuthread = Thread(target=cls.__iuhandler,
                                              name="iuthread")
            cls.__instance._qthread = Thread(name="qthread")
            cls.__instance.lock = Lock()
            cls.__instance.__close = False
            cls.__instance.pending_ops = CQueue()
            cls.__instance.waiting_ops = CQueue()
            cls.__instance.updating_database = False
            cls.__instance.iucond = Condition()
            cls.__instance.qcond = Condition()
            cls.__instance._iuthread.start()
        for key, value in kwargs.items():
            setattr(cls.__instance, key, value)
        return cls.__instance

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
                    lambda: self.pending_ops.qsize() >= self.min_ops or
                            self.close
                )
            self.updating_database = True
            with self.connection.cursor() as cursor:
                for query in self.pending_ops:
                    cursor.execute(query.statement, query.values)
            self.connection.commit()
            self.updating_database = False
            self.qcond.notify_all()

    def __qhandler(self):
        while not self.close:
            with self.qcond:
                self.qcond.wait_for(
                    lambda: not self.waiting_ops.empty() and
                            not self.updating_database or self.close
                )
            for query in self.waiting_ops:
                self.pending_ops.put(query)
            self.iucond.notify_all()

    def insert(self, query: str, args=()):
        if not self.close:
            insert_query = Query(query, args)
            self.waiting_ops.put(insert_query)
            self.qcond.notify_all()

    def update(self, query: str, args=()):
        if not self.close:
            update_query = Query(query, args)
            self.waiting_ops.put(update_query)
            self.qcond.notify_all()

    def fetchone(self, query: str, args=()):
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchone()

    def fetchmany(self, query: str, rows: int, args=()):
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchmany(rows)

    def fetchall(self, query: str, args=()):
        if not self.close:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchall()

    def __del__(self):
        self.close = True
        if not self.waiting_ops.empty():
            self.qcond.notify_all()
            self._qthread.join()
        if not self.pending_ops.empty():
            self.iucond.notify_all()
            self._iuthread.join()
        self.connection.close()

        del self.waiting_ops
        del self.pending_ops


class YouTubeDB(PostgreSQLBase):
    pass
