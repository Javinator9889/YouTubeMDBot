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
from typing import Any
from typing import Optional
from queue import Queue
from psycopg2 import pool
from psycopg2.pool import PoolError
from threading import Condition
from threading import Lock
from multiprocessing import Process

from . import Query
from .. import MAX_PROCESS
from .. import DB_USER
from .. import DB_PORT
from .. import DB_PASSWORD
from .. import DB_NAME
from .. import DB_HOST


class PostgresSQL:
    __instance = None

    def __new__(cls, **kwargs):
        if PostgresSQL.__instance is None:
            PostgresSQL.__instance = object.__new__(cls)
            PostgresSQL.__instance.__connection = \
                pool.ThreadedConnectionPool(minconn=1,
                                            maxconn=MAX_PROCESS,
                                            user=DB_USER,
                                            password=DB_PASSWORD,
                                            dbname=DB_NAME,
                                            host=DB_HOST,
                                            port=DB_PORT)
            PostgresSQL.__instance.__waiting_processes = Queue()
            PostgresSQL.__instance.__running_processes = 0
            PostgresSQL.__instance.__lock = Lock()
            PostgresSQL.__instance.__queue_consumer = \
                Process(target=cls.__consumer,
                        args=(cls, cls.__running_processes,))
            PostgresSQL.__instance.__queue_consumer.start()
        for key, value in kwargs.items():
            setattr(PostgresSQL.__instance, key, value)
        return PostgresSQL.__instance

    def __consumer(self, process_queue: Queue):
        condition = Condition()
        while self.__connection.closed == 0:
            with condition:
                condition.wait_for(lambda: self.__running_processes <= MAX_PROCESS)
                pending_process = process_queue.get()
                pending_process["fn"](pending_process["query"])

    def __get_connection(self) -> Optional[Any]:
        with self.__lock:
            if self.__running_processes <= MAX_PROCESS:
                self.__running_processes += 1
                try:
                    return self.__connection.getconn()
                except PoolError:
                    return None
        return None

    def __free_connection(self, connection):
        self.__connection.putconn(connection)
        with self.__lock:
            self.__running_processes -= 1

    def execute(self, query: Query):
        connection = self.__get_connection()
        if connection is not None:
            with connection.cursor() as cursor:
                cursor.execute(query.query)
                query._result = cursor.rowcount
                query.is_completed = True
            self.__free_connection(connection)
        else:
            self.__waiting_processes.put({"query": query, "fn": self.execute})

    def fetchone(self, query: Query):
        connection = self.__get_connection()
        if connection is not None:
            with connection.cursor() as cursor:
                cursor.execute(query.query)
                query._result = cursor.fetchone()
                query.is_completed = True
            self.__free_connection(connection)
        else:
            self.__waiting_processes.put({"query": query, "fn": self.fetchone})

    def fetchall(self, query: Query):
        connection = self.__get_connection()
        if connection is not None:
            with connection.cursor() as cursor:
                cursor.execute(query.query)
                query._result = cursor.fetchall()
                query.is_completed = True
            self.__free_connection(connection)
        else:
            self.__waiting_processes.put({"query": query, "fn": self.fetchall})

    def fetchiter(self, query: Query):
        connection = self.__get_connection()
        if connection is not None:
            with connection.cursor() as cursor:
                cursor.execute(query.query)

                def generate():
                    while True:
                        items = cursor.fetchmany()
                        if not items:
                            break
                        for item in items:
                            yield item

                query._result = generate()
                query.is_completed = True
            self.__free_connection(connection)
        else:
            self.__waiting_processes.put({"query": query, "fn": self.fetchiter})

    def __del__(self):
        if self.__connection.closed == 0:
            while not self.__waiting_processes.empty():
                continue
            self.__queue_consumer.terminate()
            self.__instance.__connection.closeall()
