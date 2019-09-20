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
import logging
import youtube_dl

from contextlib import redirect_stdout as save_to
from io import BytesIO

from ..constants.app_constants import ydl_options
from ..constants.app_constants import STREAM_OFFSET


class YouTubeDownloader(object):
    def __init__(self, url: str,
                 logger: logging = logging.getLogger("empty-logger")):
        self.__url: str = url
        self.__options: dict = ydl_options
        self.__options["logger"] = logger

    def download(self, io: BytesIO = BytesIO()) -> BytesIO:
        with save_to(io):
            with youtube_dl.YoutubeDL(self.__options) as yt_downloader:
                yt_downloader.download([self.__url])

        io.seek(STREAM_OFFSET)
        return io
