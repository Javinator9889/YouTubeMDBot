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
import os
import threading

from typing import Optional, Any, Callable

from .. import MultiprocessBase


class MPTest(MultiprocessBase):
    def get_connection(self) -> Optional[Any]:
        return super().get_connection()

    def free_connection(self, connection):
        super().free_connection(connection)


def main():
    from time import time
    from time import sleep
    from random import random

    test = MPTest(max_processes=4)
    startt = time()
    print(f"Test created - start time: {startt:.3f}s")

    def pinfo(x):
        print(f"Process #{x} - executing at {(time() - startt):.3f}s")
        t = (random() * 10) + 1
        print(f"Process #{x} waiting {t:.3f}s")
        st = time()
        sleep(t)
        print(f"Process #{x} wakes-up after {(time() - st):.3f}s and finishes")
        print(f"Thread {os.getpid()} finished!")
        return

    print(f"Main PID: {os.getpid()}")

    for i in range(20):
        # print(f"Giving new function {i}")
        f = pinfo
        test.new(f, i)

    while not test.waiting_processes.empty():
        print("                                              ", end="\r")
        print(f"Threads: {threading.active_count() - 2}", end="\r")
        sleep(0.1)
    # del test
    test.finished = True
    print(f"Main finished: {os.getpid()}")
    return
