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

from threading import Lock
from threading import Thread
from threading import Condition

from .. import MAX_PROCESS
from .. import FinishedException


class MultiprocessBase(ABC):
    __instance = None

    def __new__(cls,
                maxsize: int = 0,
                max_processes: int = MAX_PROCESS,
                **kwargs):
        if MultiprocessBase.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.waiting_processes = Queue(maxsize)
            cls.__instance.running_processes = 0
            cls.__instance.lock = Lock()
            cls.__instance.__finished = False
            cls.__instance.max_processes = max_processes
            cls.__instance.__condition = Condition()
            cls.__instance.queue_consumer = \
                Thread(target=cls.__instance.__consumer)
            cls.__instance.queue_consumer.start()
        for key, value in kwargs.items():
            setattr(cls.__instance, key, value)
        return cls.__instance

    def __process_ready(self) -> bool:
        return self.running_processes < self.max_processes and not \
            self.waiting_processes.empty() or self.finished

    def __consumer(self):
        while not self.finished:
            with self.__condition:
                self.__condition.wait_for(self.__process_ready)
            if not self.finished:
                process = self.waiting_processes.get()
                self.__spawn(process)
        return

    def __spawn(self, process: Dict[str, Any]):
        connection = self.get_connection()
        child_process = Thread(target=self.__run,
                               args=(process, connection,))
        child_process.start()

    @abstractmethod
    def get_connection(self) -> Optional[Any]:
        with self.lock:
            if self.running_processes <= self.max_processes:
                self.running_processes += 1
        return None

    @abstractmethod
    def free_connection(self, connection):
        with self.lock:
            self.running_processes -= 1
        with self.__condition:
            self.__condition.notify_all()

    def __run(self, *args) -> Optional[Any]:
        fn = args[0]["fn"]
        fn_args = args[0]["args"]
        result = fn(*fn_args, args[1]) if args[1] is not None else fn(*fn_args)
        self.free_connection(args[1])
        return result

    def new(self, fn: Callable, *args):
        if not self.finished:
            self.waiting_processes.put({"fn": fn, "args": args})
            with self.__condition:
                self.__condition.notify_all()
        else:
            raise FinishedException("The process has finished")

    @property
    def finished(self) -> bool:
        with self.lock:
            return self.__finished

    @finished.setter
    def finished(self, value: bool):
        with self.lock:
            self.__finished = value

    def __del__(self):
        if not self.finished:
            while not self.waiting_processes.empty():
                continue
            self.finished = True
