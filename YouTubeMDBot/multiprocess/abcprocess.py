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
from multiprocessing.pool import ThreadPool
from threading import Lock
from typing import Any
from typing import Callable

from .. import FinishedException
from .. import MAX_PROCESS


class ThreadPoolBase(ABC):
    __instance = None

    def __new__(cls,
                max_processes: int = MAX_PROCESS,
                name: str = "ThreadBase",
                **kwargs):
        if ThreadPoolBase.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.__pool = ThreadPool(processes=max_processes)
            cls.__instance.__lock = Lock()
            cls.__instance.__finished = False
            cls.__instance.name = name
        for key, value in kwargs.items():
            setattr(cls.__instance, key, value)
        return cls.__instance

    @property
    def finished(self) -> bool:
        with self.__lock:
            return self.__finished

    @finished.setter
    def finished(self, value: bool):
        with self.__lock:
            self.__finished = value

    def __del__(self):
        if not self.finished:
            self.__pool.close()
            self.__pool.join()
            self.finished = True

    def wait_execute(self, func: Callable, *args, **kwargs) -> Any:
        if not self.finished:
            return self.__pool.apply(func=func, args=args, kwds=kwargs)
        else:
            raise FinishedException(f"The thread pool {self.name} has finished")

    def execute(self,
                func: Callable,
                args=(),
                kwds={},
                callback: Callable[[Any], Any] = None,
                err_callback: Callable[[Any], Any] = None):
        if not self.finished:
            return self.__pool.apply_async(func=func,
                                           args=args,
                                           kwds=kwds,
                                           callback=callback,
                                           error_callback=err_callback)
        else:
            raise FinishedException(f"The thread pool {self.name} has finished")
