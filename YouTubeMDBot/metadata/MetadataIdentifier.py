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
from ..constants import ACOUSTID_KEY


class MetadataIdentifier(object):
    def __init__(self, audio: bytes):
        self.__fingerprint = FPCalc(audio)
        self.__result: json = None
        self.__artist: str = ""
        self.__title: str = ""
        self.__release_id: str = ""
        self.__recording_id: str = ""
        self.__score: float = 0.0
        self.__cover: bytes = bytes(0)

    def identify_audio(self) -> json:
        data: json = acoustid.lookup(apikey=ACOUSTID_KEY,
                                     fingerprint=self.__fingerprint.fingerprint(),
                                     duration=self.__fingerprint.duration(),
                                     meta="recordings releaseids")
        self.__result = data
        if data["status"] == "ok" and "results" in data:
            result = data["results"][0]
            score = result["score"]
            recording = result["recordings"][0]
            if recording.get("artists"):
                names = [artist["name"] for artist in recording["artists"]]
                artist_name = "; ".join(names)
            else:
                artist_name = None
            title = recording.get("title")
            release_id = recording["releases"][0]["id"]
            recording_id = recording.get("id")

            self.__score = score
            self.__title = title
            self.__recording_id = recording_id
            self.__release_id = release_id
            self.__artist = artist_name
            self.__cover = musicbrainzngs.get_image_front(release_id)
        return data

    def get_title(self) -> str:
        return self.__title

    def get_score(self) -> float:
        return self.__score

    def get_artist(self) -> str:
        return self.__artist

    def get_recording_id(self) -> str:
        return self.__recording_id

    def get_release_id(self) -> str:
        return self.__release_id

    def get_cover(self) -> bytes:
        return self.__cover

    def get_results(self) -> json:
        return self.__result
