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
from mutagen.mp4 import MP4
from mutagen.mp4 import MP4Cover
from io import BytesIO


class AudioMetadata:
    def __init__(self, audio: BytesIO):
        self._audio = MP4(audio)
        self._data = audio

    def set_title(self, title: str):
        self._audio[u"\xa9nam"] = title

    def set_artist(self, artist: str):
        self._audio[u"\xa9ART"] = artist

    def set_album(self, album: str):
        self._audio[u"\xa9alb"] = album

    def set_extras(self, extras: list):
        self._audio[u"\xa9cmt"] = '; '.join(map(str, extras))

    def set_cover(self, cover: bytes):
        mp4_cover = MP4Cover(cover, MP4Cover.FORMAT_JPEG)
        self._audio[u"covr"] = [mp4_cover]

    def save(self) -> BytesIO:
        self._data.seek(0)
        self._audio.save(self._data)
        return self._data
