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
from io import BytesIO
from subprocess import PIPE
from subprocess import Popen


def ffmpeg_available() -> bool:
    try:
        proc = Popen(["ffmpeg", "-version"],
                     stdout=PIPE,
                     stderr=PIPE)
    except OSError:
        return False
    else:
        proc.wait()
        return proc.returncode == 0


class FFmpegOpener(object):
    def __init__(self, data: bytes):
        self._data = data
        self.__ffmpeg_proc = Popen(["ffmpeg", "-i", "-", "-f", "s16le", "-"],
                                   stdout=PIPE, stderr=PIPE, stdin=PIPE)
        self.__out = None
        self.__err = None

    def open(self) -> int:
        self.__out, self.__err = self.__ffmpeg_proc.communicate(self._data)
        return self.__ffmpeg_proc.returncode

    def get_output(self) -> bytes:
        return self.__out

    def get_extra(self) -> bytes:
        return self.__err
