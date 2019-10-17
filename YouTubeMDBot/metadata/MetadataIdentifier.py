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
try:
    import ujson as json
except ImportError:
    import json
import acoustid
import musicbrainzngs

from ..audio import FPCalc
from ..api import YouTubeAPI
from ..utils import youtube_utils
from ..constants import ACOUSTID_KEY
from ..downloader import YouTubeDownloader


class MetadataIdentifier:
    """
    Base identifier class. By using the audio data, calculates and generates a
    fingerprint for searching across the MusicBrainz database.

    Once the audio has been identified, the available params and information are:
     - audio (bytes)
     - result (json)
     - artist (str)
     - title (str)
     - release_id (str)
     - recording_id (str)
     - score (float)
     - cover (bytes)
     - album (str)
     - duration (int)
     - youtube_data (bool)
     - youtube_id (str)
    """
    def __init__(self, audio: bytes):
        """
        Generates a new instance of the MetadataIdentifier class.
        :param audio: the audio data, in bytes.
        """
        self.audio = audio
        self.result: json = None
        self.artist: str = ""
        self.title: str = ""
        self.release_id: str = ""
        self.recording_id: str = ""
        self.score: float = 0.0
        self.cover: bytes = bytes(0)
        self.album: str = ""
        self.duration: int = 0
        self.youtube_data: bool = False
        self.youtube_id: str = ""

    @staticmethod
    def _is_valid_result(data: json) -> bool:
        """
        Checks whether the obtained result, in json, is valid or not, by checking for
        certain keys that must exist.
        :param data: the result in json.
        :return: 'True' if the result is valid, else 'False'.
        """
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

    def identify_audio(self) -> bool:
        """
        Tries to identify the audio by using the audio fingerprint. If the audio has
        been successfully identified, then obtains all the data related to it.
        :return: 'True' if the result is valid (the audio was correctly identified),
        else 'False'.
        """
        fingerprint = FPCalc(self.audio)
        data: json = acoustid.lookup(apikey=ACOUSTID_KEY,
                                     fingerprint=fingerprint.fingerprint(),
                                     duration=fingerprint.duration(),
                                     meta="recordings releaseids releasegroups")
        self.result = data
        is_valid = self._is_valid_result(data)
        if is_valid:
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
                    if recording.get("releasegroups"):
                        self.release_id = \
                            recording["releasegroups"][0]["releases"][0]["id"]
                        self.album = recording["releasegroups"][0]["title"]
                        self.cover = musicbrainzngs.get_image_front(self.release_id)
                    self.recording_id = recording["id"]
                    self.duration = recording["duration"]
                    is_valid = True
                    break
                break
        return is_valid


class YouTubeMetadataIdentifier(MetadataIdentifier):
    """
    Identifies YouTube metadata by using MusicBrainz database and YouTube metadata. If
    the first identification (MusicBrainz) fails, then fallback to YouTube
    identification if the "downloader" was provided.

    Once the audio has been identified, the available params and information are:
     - audio (bytes)
     - result (json)
     - artist (str)
     - title (str)
     - release_id (str)
     - recording_id (str)
     - score (float)
     - cover (bytes)
     - album (str)
     - duration (int)
     - youtube_data (bool)
     - youtube_id (str)

    If "youtube_data" is True, then only audio, title, artist, duration, cover and
    youtube_id are available.
    """
    def __init__(self, audio: bytes, downloader: YouTubeDownloader = None):
        """
        Generates a new instance of the MetadataIdentifier class.
        :param audio: the audio data, in bytes.
        :param downloader: a downloader object, for obtaining the video information if
        MusicBrainz fails.
        """
        super().__init__(audio)
        self._downloader = downloader

    def identify_audio(self) -> bool:
        valid = super().identify_audio()
        if not valid:
            if self._downloader:
                from urllib.request import urlopen

                video_id = youtube_utils.get_yt_video_id(self._downloader.get_url())
                video_data = YouTubeAPI.video_details(video_id)
                self.title = video_data.title
                self.artist = video_data.artist
                self.duration = video_data.duration
                self.cover = urlopen(video_data.thumbnail).read()
                self.youtube_id = video_data.id
                self.youtube_data = True

                valid = True
        return valid
