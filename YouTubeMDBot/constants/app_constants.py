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
import sys

from logging import INFO, WARNING, DEBUG
from multiprocessing import cpu_count

PROGRAM_ARGS = sys.argv
# YouTube DL options
YDL_CLI_OPTIONS = ["youtube-dl", "--format", "bestaudio[ext=m4a]", "--quiet",
                   "--output", "-"]

# FPCalc command
FPCALC = ["fpcalc", "-"]

# API keys
ACOUSTID_KEY = os.environ["ACOUSTID_KEY"]
YOUTUBE = {
    "key": os.environ["YOUTUBE_KEY"],
    "api": {
        "name": "youtube",
        "version": "v3"
    },
    "endpoint":
        "https://www.googleapis.com/youtube/v3/videos?"
        "part=id,snippet,contentDetails,statistics&id={0}&key={1}"
}

# FFmpeg commands
FFMPEG_OPENER = "ffmpeg -i - -f s16le -".split(" ")
FFMPEG_CONVERTER = ["ffmpeg", "-y", "-i", "-", "-vn", "-map_metadata", "0",
                    "-map", "a:a", "-movflags", "use_metadata_tags"]
FFMPEG_VOLUME = "ffmpeg -i - -af \"volumedetect\" -f null /dev/null 2>&1 | " \
                "grep \"max_volume\" | awk -F': ' '{print $2}' | cut -d ' ' -f1"

MAX_PROCESS = cpu_count()

# Database constants
DB_NAME = os.environ["DATABASE_NAME"]
DB_USER = os.environ["DATABASE_USER"]
DB_PASSWORD = os.environ["DATABASE_PASSWORD"]
DB_HOST = "127.0.0.1"
DB_PORT = 5432

# Redis constants
REDIS_UNIX_SOCKET = os.environ["REDIS_SOCKET"]

# Logging constants
LOGGER_NAME = "youtubemd:logger"
LOG_FILE = "youtubemd.log"
LOG_DEFAULT_FORMAT = \
    "%(process)d[%(thread)d] - %(asctime)s | [%(levelname)s]: %(message)s"

PRODUCTION_CONSOLE_LOG_LEVEL = INFO
PRODUCTION_FILE_LOG_LEVEL = WARNING

DEV_CONSOLE_LOG_LEVEL = DEBUG
DEV_FILE_LOG_LEVEL = DEBUG
