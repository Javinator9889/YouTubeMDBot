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
    """
    Wrapper class for setting the audio metadata to the downloaded YouTube video
    object. By using this class, it is possible to set the required information by
    using mutagen without having to remember the metadata keys.
    """
    def __init__(self, audio: BytesIO):
        """
        Generates a new instance.
        :param audio: the audio metadata, in BytesIO, in MP4 format.
        """
        self._audio = MP4(audio)
        self._data = audio

    def set_title(self, title: str):
        """
        Sets the audio title.
        :param title: the audio title.
        """
        self._audio[u"\xa9nam"] = title

    def set_artist(self, artist: str):
        """
        Sets the audio artist.
        :param artist: the audio artist.
        """
        self._audio[u"\xa9ART"] = artist

    def set_album(self, album: str):
        """
        Sets the audio album.
        :param album: the audio album
        """
        self._audio[u"\xa9alb"] = album

    def set_extras(self, extras: list):
        """
        Sets the audio extras.
        :param extras: a list of extras that will be added to the audio information.
        """
        self._audio[u"\xa9cmt"] = '; '.join(map(str, extras))

    def set_cover(self, cover: bytes):
        """
        Sets the audio cover.
        :param cover: the audio cover.
        """
        mp4_cover = MP4Cover(cover, MP4Cover.FORMAT_JPEG)
        self._audio[u"covr"] = [mp4_cover]

    def save(self) -> BytesIO:
        """
        Saves the new metadata into the audio file object.
        :return: the audio file object with the new metadata.
        """
        self._data.seek(0)
        self._audio.save(self._data)
        return self._data
