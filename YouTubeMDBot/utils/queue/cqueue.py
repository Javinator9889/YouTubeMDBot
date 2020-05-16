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
from queue import Queue

from threading import Lock

from typing import Any
from typing import Optional


class CQueue(Queue):
    def __init__(self, maxsize=0):
        print(f"New queue created - {hex(id(self))}")
        super().__init__(maxsize=maxsize)
        self._lock = Lock()
        self.size = 0

    @property
    def size(self) -> int:
        with self._lock:
            return self.__size

    @size.setter
    def size(self, value):
        with self._lock:
            self.__size = value

    def put(self,
            obj: Any,
            block: bool = True,
            timeout: Optional[float] = None):
        self.size += 1
        print(f"Item inserted in {hex(id(self))}: {obj}")
        super().put(obj, block, timeout)

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        self.size -= 1
        super().get(block, timeout)

    def qsize(self) -> int:
        return self.size

    def empty(self) -> bool:
        return not self.qsize()

    def __iter__(self):
        while not self.empty():
            yield self.get()
