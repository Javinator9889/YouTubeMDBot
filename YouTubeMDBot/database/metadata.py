#                             YouTubeMDBot
#                  Copyright (C) 2020 - Javinator9889
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
from . import PostgreSQLBase


class MetadataDB(PostgreSQLBase):
    def register_new_metadata(self,
                              artist: str,
                              album: str,
                              cover: bytes,
                              release_id: str,
                              recording_id: str,
                              duration: int,
                              title: str,
                              youtube_id: str,
                              is_custom_metadata: bool = False) -> int:
        metadata_id = self.insert(
            """INSERT INTO youtubemd.Metadata(artist, album, cover, 
            release_id, recording_id, duration, title, custom_metadata) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (artist, album, cover, release_id, recording_id, duration, title,
             is_custom_metadata), returning_id=True
        ).return_value.result()
        self.insert(
            """INSERT INTO youtubemd.Video_Has_Metadata(id, metadata_id) 
            VALUES (%s, %s)""", (youtube_id, metadata_id)
        )
        return metadata_id

    def get_metadata_for_id(self, metadata_id: int) -> dict:
        data = self.fetchone(
            """SELECT artist, album, cover, release_id, recording_id, 
            duration, title, custom_metadata FROM youtubemd.Metadata 
            WHERE id = %s""", (metadata_id,)
        )
        return {
            "artist": data[0],
            "album": data[1],
            "cover": data[2],
            "release_id": data[3],
            "recording_id": data[4],
            "duration": data[5],
            "title": data[6],
            "custom_metadata": data[7]
        }

    def get_metadata_for_youtube_id(self, youtube_id: str) -> dict:
        data = self.get_metadata_id_for_youtube_id(youtube_id)
        return self.get_metadata_for_id(data)

    def get_metadata_id_for_youtube_id(self, youtube_id: str) -> int:
        return self.fetchone(
            """SELECT metadata_id FROM youtubemd.Video_Has_Metadata 
            WHERE id = %s""", (youtube_id,)
        )[0]

    def update_metadata(self,
                        metadata_id: int,
                        artist: str,
                        album: str,
                        cover: bytes,
                        release_id: str,
                        recording_id: str,
                        duration: int,
                        title: str,
                        is_custom_metadata: bool = False):
        self.update(
            """UPDATE youtubemd.Metadata SET 
            artist = %s,
             album = %s,
             cover = %s,
             release_id = %s,
             recording_id = %s,
             duration = %s,
             title = %s,
             custom_metadata = %s WHERE id = %s""",
            (artist, album, cover, release_id, recording_id, duration, title,
             is_custom_metadata, metadata_id)
        )
