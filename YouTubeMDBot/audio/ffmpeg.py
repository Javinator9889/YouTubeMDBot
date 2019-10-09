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
from io import BytesIO
from typing import List
from subprocess import PIPE
from subprocess import Popen

from ..constants import FFMPEG_OPENER
from ..constants import FFMPEG_CONVERTER
from ..constants import FFMPEG_PROCESSOR


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


class FFmpeg(ABC):
    def __init__(self, data: bytes, command: List[str] = None):
        self._data = data
        self.__command = command
        self.__out = None
        self.__err = None

    def process(self) -> int:
        proc = Popen(self.__command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        self.__out, self.__err = proc.communicate(self._data)
        return proc.returncode

    def get_command(self) -> List[str]:
        return self.__command

    def set_command(self, command: List[str]):
        self.__command = command

    def get_output(self) -> bytes:
        return self.__out

    def get_extra(self) -> bytes:
        return self.__err


class FFmpegProcessor(FFmpeg):
    def __init__(self, data: bytes):
        super().__init__(data=data, command=FFMPEG_PROCESSOR.copy())


class FFmpegOpener(FFmpeg):
    def __init__(self, data: bytes):
        super().__init__(data=data, command=FFMPEG_OPENER.copy())


class FFmpegExporter(FFmpeg):
    def __init__(self, data: bytes, bitrate: str = None):
        super().__init__(data=data, command=FFMPEG_CONVERTER.copy())
        self._bitrate = bitrate

    @abstractmethod
    def convert(self) -> int:
        raise NotImplementedError


class FFmpegMP3(FFmpegExporter):
    def convert(self) -> int:
        command = super().get_command()
        if self._bitrate:
            command.append("-b:a")
            command.append(self._bitrate)
        command.append("-acodec")
        command.append("libmp3lame")
        command.append("-f")
        command.append("mp3")
        command.append("-")
        return self.process()


class FFmpegOGG(FFmpegExporter):
    def convert(self) -> int:
        command = super().get_command()
        if self._bitrate:
            command.append("-b:a")
            command.append(self._bitrate)
        command.append("-c:a")
        command.append("libvorbis")
        command.append("-f")
        command.append("ogg")
        command.append("-")
        return self.process()
