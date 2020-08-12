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
from datetime import datetime
from . import PostgreSQLBase, YouTubeDB, MetadataDB


class FileDB(PostgreSQLBase):
    def new_file(self,
                 file_id: str,
                 metadata_id: int,
                 audio_quality: str,
                 size: int,
                 user_id: int):
        self.insert(
            """INSERT INTO youtubemd.File(id, metadata_id, audio_quality, size)
             VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (file_id, metadata_id, audio_quality, size)
        )
        date = datetime.now().date()
        self.insert(
            """INSERT INTO youtubemd.History(file_id, user_id, metadata_id, 
            date) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (file_id, user_id, metadata_id, date)
        )

    def get_file_info_by_id(self, file_id: str) -> dict:
        data = self.fetchone(
            """SELECT id, metadata_id, audio_quality, size 
            FROM youtubemd.File WHERE file_id = %s""", (file_id,)
        )
        return {
            "id": data[0],
            "metadata_id": data[1],
            "audio_quality": data[2],
            "size": data[3]
        }

    def get_file_for_youtube_id(self, youtube_id: str) -> Optional[str]:
        youtube_database = YouTubeDB(self.postgres_item)
        if youtube_database.is_id_registered(youtube_id):
            metadata = MetadataDB(self.postgres_item)
            metadata_id = metadata.get_metadata_id_for_youtube_id(youtube_id)
            return self.get_file_for_metadata_id(metadata_id)
        else:
            return None

    def get_file_for_metadata_id(self, metadata_id: int) -> str:
        return self.fetchone(
            """SELECT file_id FROM youtubemd.File WHERE metadata_id = %s""",
            (metadata_id,)
        )[0]
