#                             YouTubeMDBot
#                  Copyright (C) 2020 - Javinator9889
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
import redis

try:
    import ujson as json
except ImportError:
    import json
from abc import ABC
from typing import Union, Optional
from threading import Lock

from .. import PostgreSQLItem
from .. import REDIS_UNIX_SOCKET

wrapper_lock = Lock()


class BaseWrapper:
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        with wrapper_lock:
            if not BaseWrapper.__instance__:
                cls.__instance__ = object.__new__(cls)
                cls.__instance__.__must_initialize = True
            return cls.__instance__

    def __init__(self):
        if self.__must_initialize:
            pool = redis.ConnectionPool(
                redis.UnixDomainSocketConnection(path=REDIS_UNIX_SOCKET),
                max_connections=16)
            self.redis = redis.Redis(connection_pool=pool,
                                     decode_responses=True)
            self.redis.config_set("MAXMEMORY-POLICY", "volatile-lfu")
            self.__must_initialize = False


class DatabaseWrapper(ABC):
    def __init__(self, identifier: str, **kwargs):
        super().__init__()
        self.item = PostgreSQLItem()
        self.__wrapper = BaseWrapper()
        self.redis = self.__wrapper.redis
        self.name = identifier
        for key, value in kwargs.items():
            setattr(self, key, value)

    def set(self,
            key: Union[str, bytes, int, float],
            value: Union[dict, Union[str, bytes, int, float]]):
        self.redis.hset(self.name, key, json.dumps(value))

    def get(self, key: Union[str, bytes, int, float]) -> \
            Optional[Union[str, bytes, int, float, dict]]:
        if not self.exists(key):
            return None
        return json.loads(self.redis.hget(self.name, key))

    def exists(self, key: str) -> bool:
        return self.redis.hexists(self.name, key)

    def delete(self, *keys: str):
        self.redis.hdel(name=self.name, *keys)

    def update(self,
               key: Union[str, bytes, int, float],
               value: Union[dict, Union[str, bytes, int, float]]):
        return self.set(key, value)

    def __getitem__(self,
                    item: Union[str, bytes, int, float]) -> \
            Optional[Union[str, bytes, int, float, dict]]:
        return self.get(item)

    def __setitem__(self,
                    key: Union[str, bytes, int, float],
                    value: Union[dict, Union[str, bytes, int, float]]):
        return self.set(key, value)
