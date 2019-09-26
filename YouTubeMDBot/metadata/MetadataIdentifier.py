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
import acoustid
import musicbrainzngs

try:
    import ujson as json
except ImportError:
    import json

from ..audio import FPCalc
from ..api import YouTubeAPI
from ..utils import youtube_utils
from ..constants import ACOUSTID_KEY
from ..downloader import YouTubeDownloader


class MetadataIdentifier(object):
    def __init__(self, audio: bytes, downloader: YouTubeDownloader = None):
        self.audio = audio
        self.result: json = None
        self.artist: str = ""
        self.title: str = ""
        self.release_id: str = ""
        self.recording_id: str = ""
        self.score: float = 0.0
        self.cover: bytes = bytes(0)
        self.duration: int = 0
        self.youtube_data: bool = False
        self.youtube_id: str = ""
        self._downloader = downloader

    @staticmethod
    def _is_valid_result(data: json) -> bool:
        if "results" not in data:
            return False
        elif data["status"] != "ok":
            return False
        elif len(data["results"]) == 0:
            return False
        else:
            if "recordings" not in data["results"][0]:
                return False
            else:
                return True

    def identify_audio(self) -> json:
        fingerprint = FPCalc(self.audio)
        data: json = acoustid.lookup(apikey=ACOUSTID_KEY,
                                     fingerprint=fingerprint.fingerprint(),
                                     duration=fingerprint.duration(),
                                     meta="recordings releaseids")
        self.result = data
        if self._is_valid_result(data):
            for result in data["results"]:
                if "recordings" not in result:
                    break
                self.score = result["score"]
                for recording in result["recordings"]:
                    if recording.get("artists"):
                        names = [artist["name"] for artist in recording["artists"]]
                        self.artist = "; ".join(names)
                    else:
                        self.artist = "Unknown"
                    self.title = recording["title"]
                    self.release_id = recording["releases"][0]["id"]
                    self.recording_id = recording["id"]
                    self.duration = recording["duration"]
                    self.cover = musicbrainzngs.get_image_front(self.release_id)
                    break
                break
        elif self._downloader:
            from urllib.request import urlopen

            video_id = youtube_utils.get_yt_video_id(self._downloader.get_url())
            video_data = YouTubeAPI.video_details(video_id)
            self.title = video_data.title
            self.artist = video_data.artist
            self.duration = video_data.duration
            self.cover = urlopen(video_data.thumbnail).read()
            self.youtube_id = video_data.id
            self.youtube_data = True
        return data
