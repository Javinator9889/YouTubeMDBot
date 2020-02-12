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

from psycopg2 import pool
from psycopg2.pool import PoolError

from . import Query
from .. import DB_HOST
from .. import DB_NAME
from .. import DB_PASSWORD
from .. import DB_PORT
from .. import DB_USER
from .. import MAX_PROCESS


class PostgreSQL(MultiprocessBase):
    def __new__(cls, **kwargs):
        if cls.__instance is None:
            connection = pool.ThreadedConnectionPool(minconn=1,
                                                     maxconn=MAX_PROCESS,
                                                     user=DB_USER,
                                                     password=DB_PASSWORD,
                                                     dbname=DB_NAME,
                                                     host=DB_HOST,
                                                     port=DB_PORT)
            return super().__new__(cls, connection=connection)
        return super().__new__(cls)

    def free_connection(self, connection):
        super().free_connection(connection)
        self.connection.putconn(connection)

    def get_connection(self) -> Optional[Any]:
        super().get_connection()
        try:
            return self.connection.getconn()
        except PoolError:
            return None

    def execute(self, query: Query):
        super().new(self._execute, query)

    def fetchone(self, query: Query):
        super().new(self._fetchone, query)

    def fetchall(self, query: Query):
        super().new(self._fetchall, query)

    def fetchiter(self, query: Query):
        super().new(self._fetchiter, query)

    @staticmethod
    def _execute(self, query: Query, connection):
        with connection.cursor() as cursor:
            cursor.execute(query.query)
            query._result = cursor.rowcount
            query.is_completed = True

    @staticmethod
    def _fetchone(query: Query, connection):
        with connection.cursor() as cursor:
            cursor.execute(query.query)
            query._result = cursor.fetchone()
            query.is_completed = True

    @staticmethod
    def _fetchall(query: Query, connection):
        with connection.cursor() as cursor:
            cursor.execute(query.query)
            query._result = cursor.fetchall()
            query.is_completed = True

    @staticmethod
    def _fetchiter(query: Query, connection):
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

    def __del__(self):
        super().__del__()
        self.connection.closeall()
