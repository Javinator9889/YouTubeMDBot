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
from typing import List
from subprocess import PIPE
from subprocess import Popen

from ..constants import FFMPEG_OPENER
from ..constants import FFMPEG_CONVERTER
from ..constants import FFMPEG_VOLUME


def ffmpeg_available() -> bool:
    """
    Checks if "ffmpeg" is installed or not.
    :return: True if installed, else False
    """
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
    """
    Base abstract class for the FFmpeg operators. All classes that works with FFmpeg
    must inherit from this class in order to maintain readability and code optimization.

    Allows execution of the ffmpeg command by using the subprocess module. Everything
    is working with PIPEs, so there is no directly discs operations (everything is
    loaded and working with RAM).
    """

    def __init__(self, data: bytes, command: List[str] = None):
        """
        Creates the class by passing the data which will be processed and the command (
        by default, None).
        :param data: audio data that will be processed.
        :param command: the ffmpeg command.
        """
        self._data = data
        self.__command = command
        self.__out = None
        self.__err = None

    def process(self) -> int:
        """
        Runs the ffmpeg command in a separate process and pipes both stdout and stderr.
        :return: the return code of the operation ('0' if everything is OK, > 0 if not).
        """
        proc = Popen(self.__command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        self.__out, self.__err = proc.communicate(self._data)
        return proc.returncode

    def get_command(self) -> List[str]:
        """
        Get the command for editing.
        :return: List[str] with the command - as this is a pointer, all editions done
        to the list are directly changing the self object.
        """
        return self.__command

    def set_command(self, command: List[str]):
        """
        Sets the new list, overriding every old implementation.
        :param command: the new command.
        """
        self.__command = command

    def get_output(self) -> bytes:
        """
        Gets the stdout of the process.
        :return: bytes with the command output.
        """
        return self.__out

    def get_extra(self) -> bytes:
        """
        Gets the stderr of the process.
        :return: bytes with extra information.
        """
        return self.__err

    def get_volume(self) -> float:
        """
        Gets the maximum volume of the data input.
        :return: the volume.
        """
        command = FFMPEG_VOLUME
        proc = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        out, err = proc.communicate(self._data)
        return float(out.decode("utf-8")) if out.decode("utf-8") != '' else 0.0


class FFmpegOpener(FFmpeg):
    """
    Opens and produces and audio in PWM mode.
    """

    def __init__(self, data: bytes):
        super().__init__(data=data, command=FFMPEG_OPENER.copy())


class FFmpegExporter(FFmpeg):
    """
    Base class for the exporter options available in ffmpeg.
    All classes that are developed for converting audio files must inherit from this
    class and implement the "convert" method.
    """

    def __init__(self, data: bytes, bitrate: str = None):
        """
        Generates a new instance of the class.
        :param data: the audio data.
        :param bitrate: the new bitrate of the audio data, or None for keeping its
        default.
        """
        super().__init__(data=data, command=FFMPEG_CONVERTER.copy())
        self._bitrate = bitrate

    @abstractmethod
    def convert(self) -> int:
        """
        Converts the audio to the desired format.
        :return: the operation result code.
        :raises NotImplementedError when trying to access this method directly on super
        class.
        """
        raise NotImplementedError


class FFmpegMP3(FFmpegExporter):
    """
    Exports audio data to MP3 format.
    """
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
    """
    Exports audio data to OGG format.
    """
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


class FFmpegM4A(FFmpegExporter):
    def __init__(self, data: bytes, filename: str, bitrate: str = None):
        super().__init__(data, bitrate)
        self.filename = filename

    def convert(self) -> int:
        command = super().get_command()
        vol = self.get_volume() * -1
        command.append("-af")
        command.append(f"volume={vol}dB")
        if self._bitrate:
            command.append("-b:a")
            command.append(self._bitrate)
        command.append("-c:a")
        command.append("aac")
        command.append("-movflags")
        command.append("faststart")
        command.append("-f")
        command.append("ipod")
        command.append(self.filename)
        return self.process()
