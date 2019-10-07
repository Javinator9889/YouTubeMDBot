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
from typing import Tuple

from ..constants.app_constants import YDL_CLI_OPTIONS
from ..audio.ffmpeg import FFmpegOpener


class YouTubeDownloader(object):
    def __init__(self, url: str):
        self.__url: str = url
        self.__options: list = YDL_CLI_OPTIONS.copy()
        self.__options.append(self.__url)

    def download(self, ffmpeg: bool = False) -> Tuple[BytesIO, bytes]:
        import subprocess

        proc = subprocess.Popen(self.__options,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        retcode = proc.returncode
        if retcode == 0:
            # if ffmpeg:
            #    opener = FFmpegOpener(stdout)
            #     opener.open()
            #     stdout = opener.get_output()
            #     err = opener.get_extra()
            #     if err:
            #         print(err.decode("utf-8"))
            return BytesIO(stdout), stdout
        else:
            raise RuntimeError("youtube-dl downloader exception - more info: " +
                               str(stderr.decode("utf-8")))

    def get_url(self) -> str:
        return self.__url
