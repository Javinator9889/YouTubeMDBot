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
from abc import abstractmethod

from typing import Any
from typing import Dict
from typing import Optional
from typing import Callable

from queue import Queue

from threading import Condition
from threading import Lock

from multiprocessing import Process

from .. import MAX_PROCESS


class MultiprocessBase(ABC):
    __instance = None
    inst = None

    def __new__(cls, maxsize: int = 0, **kwargs):
        if MultiprocessBase.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.waiting_processes = Queue(maxsize)
            cls.__instance.running_processes = 0
            cls.__instance.lock = Lock()
            cls.__instance.finished = False
            cls.__instance.queue_consumer = \
                Process(target=cls.__consumer)
            cls.__instance.queue_consumer.start()
        for key, value in kwargs.items():
            setattr(cls.__instance, key, value)
        return cls.__instance

    def __consumer(self):
        condition = Condition()
        while not self.finished:
            with condition:
                condition.wait_for(
                    lambda: self.running_processes <= MAX_PROCESS and not
                    self.waiting_processes.empty())
            process = self.waiting_processes.get()
            self.__spawn(process)

    def __spawn(self, process: Dict[str, Any]):
        connection = self.get_connection()
        child_process = Process(target=self.__run,
                                args=(process, connection,))
        child_process.start()

    @abstractmethod
    def get_connection(self) -> Optional[Any]:
        with self.lock:
            if self.running_processes <= MAX_PROCESS:
                self.running_processes += 1
        return None

    @abstractmethod
    def free_connection(self, connection):
        with self.lock:
            self.running_processes -= 1

    def __run(self, *args) -> Optional[Any]:
        fn = args[0]["fn"]
        fn_args = args[0]["args"]
        result = fn(*fn_args, args[1])
        self.free_connection(args[1])
        return result

    def new(self, fn: Callable, *args):
        self.waiting_processes.put({"fn": fn, "args": args})

    def __del__(self):
        if not self.finished:
            self.finished = True
            while not self.waiting_processes.empty():
                continue
            self.queue_consumer.terminate()
