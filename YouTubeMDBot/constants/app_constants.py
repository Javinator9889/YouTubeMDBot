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

PROGRAM_ARGS = sys.argv
# YouTube DL options
YDL_CLI_OPTIONS = ["youtube-dl", "--format", "bestaudio[ext=m4a]", "--quiet", "--output",
                   "-"]

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
FFMPEG_CONVERTER = ["ffmpeg", "-i", "-", "-vn", "-map_metadata", "0",
                    "-movflags", "use_metadata_tags"]
