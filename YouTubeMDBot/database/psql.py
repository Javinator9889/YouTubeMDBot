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
from threading import Condition
from threading import Lock
from threading import Thread
from collections import deque

import os
import psycopg2

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
        self.return_value = Future()


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
        if self.must_initialize:
            self.connection = psycopg2.connect(user=DB_USER,
                                               password=DB_PASSWORD,
                                               host=DB_HOST,
                                               port=DB_PORT,
                                               dbname=DB_NAME)
            self.min_ops = min_ops
            self.lock = Lock()
            self.close = False
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
            print(f"[iuhandler] - condition is true: pending ops: "
                  f"{len(self.pending_ops)} or closed: {self.close}")
            self.updating_database = True
            with self.connection.cursor() as cursor:
                while len(self.pending_ops) > 0:
                    query = self.pending_ops.pop()
                    if query is None:
                        continue
                    cursor.execute(query.statement, query.values)
                    if query.returning_id:
                        try:
                            query.return_value.set_result(cursor.fetchone()[0])
                        except psycopg2.ProgrammingError:
                            query.return_value.set_result(query.values)
            self.connection.commit()
            self.updating_database = False
            if not self.close:
                with self.qcond:
                    self.qcond.notify_all()
        print("iuhandler exited")

    def __qhandler(self):
        while not self.close:
            with self.qcond:
                self.qcond.wait_for(
                    lambda: len(self.waiting_ops) > 0 and
                            not self.updating_database or self.close
                )
            print(f"[qhandler] - condition is true: waiting ops: "
                  f"{len(self.waiting_ops)} and not {self.updating_database} "
                  f"or closed: {self.close}")
            while len(self.waiting_ops) > 0:
                query = self.waiting_ops.pop()
                if query is None:
                    continue
                self.pending_ops.append(query)
            with self.iucond:
                self.iucond.notify_all()
        print("qhandler exited")

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

    def stop(self):
        print("deleting class")
        self.close = True
        print(f"is there any waiting operation? {len(self.waiting_ops) > 0}")
        with self.qcond:
            self.qcond.notify_all()
        self._qthread.join()
        self._iuthread.join()
        print("closing db connection")
        if self.lock.locked():
            self.lock.release()
        self.connection.close()

    def __del__(self):
        try:
            self.stop()
        except Exception as e:
            print(e)


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
