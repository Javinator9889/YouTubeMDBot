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
from typing import Any
from typing import Callable
from typing import Tuple
from tempfile import NamedTemporaryFile

from .. import ThreadPoolBase
from .. import FFmpegM4A
from ..constants.app_constants import YDL_CLI_OPTIONS


class YouTubeDownloader:
    """
    Download a YouTube video directly into memory.
    """

    def __init__(self, url: str):
        """
        Creates the YouTubeDownloader object. Call "download" for obtaining
        the video.
        :param url: the video URL.
        """
        self.__url: str = url
        self.__options: list = YDL_CLI_OPTIONS.copy()
        self.__options.append(self.__url)

    def download(self) -> Tuple[BytesIO, bytes]:
        """
        Downloads the YouTube video directly into memory by using pipes.
        :return: a tuple with "BytesIO" and "bytes".
        """
        import subprocess

        proc = subprocess.Popen(self.__options,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        retcode = proc.returncode
        if retcode == 0:
            return BytesIO(stdout), stdout
        else:
            raise RuntimeError("youtube-dl downloader exception - more info: " +
                               str(stderr.decode("utf-8")))

    def get_url(self) -> str:
        """
        Obtains the video URL.
        :return: str with the URL.
        """
        return self.__url


class M4AYouTubeDownloader(YouTubeDownloader):
    def __init__(self, url: str, bitrate: str = None):
        super().__init__(url)
        self.user_bitrate = bitrate

    def download(self) -> Tuple[BytesIO, bytes]:
        io, data = super().download()
        m4a_file = NamedTemporaryFile(suffix=".m4a")
        m4a_converter = FFmpegM4A(data=data,
                                  filename=m4a_file.name,
                                  bitrate=self.user_bitrate)
        ret = m4a_converter.convert()
        if ret != 0:
            raise RuntimeError("ffmpeg is unable to convert file - output: "
                               + m4a_converter.get_extra().decode("utf-8"))
        with open(m4a_file.name, "rb") as out_m4a:
            m4a_data = out_m4a.read()
        m4a_file.close()
        return BytesIO(m4a_data), m4a_data


class MultipleYouTubeDownloader(ThreadPoolBase):
    def __new__(cls,
                max_processes: int = 4,
                name: str = "YouTubeDownloader",
                **kwargs):
        return super().__new__(cls, max_processes, name, **kwargs)

    def download(self, yt_obj: YouTubeDownloader) -> Tuple[BytesIO, bytes]:
        return super().wait_execute(yt_obj.download)

    def download_async(self,
                       yt_obj: YouTubeDownloader,
                       callback: Callable[[Any], Any] = None,
                       error_callback: Callable[[Any], Any] = None):
        return super().execute(yt_obj.download,
                               callback=callback,
                               err_callback=error_callback)
