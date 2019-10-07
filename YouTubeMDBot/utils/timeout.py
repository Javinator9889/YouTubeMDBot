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
import signal


class timeout:
    def __init__(self, secs: int):
        self.__secs = secs

    def _raise_timeout(self, signum, frame):
        raise TimeoutError("Function timeout! - {0}s".format(self.__secs))

    def __enter__(self):
        if self.__secs <= 0:
            self._raise_timeout(0, 0)

        signal.signal(signal.SIGALRM, self._raise_timeout)
        signal.alarm(self.__secs)
        yield

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
        return exc_val is not None


'''@contextmanager
def timeout(secs: int):
    def raise_timeout(signum=None, frame=None):
        raise TimeoutError("Function timeout! - {0}s".format(secs))

    if secs <= 0:
        secs = 0
        raise_timeout()

    signal.signal(signalnum=signal.SIGALRM, handler=raise_timeout)
    signal.alarm(secs)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        signal.signal(signalnum=signal.SIGALRM, handler=signal.SIG_IGN)'''
