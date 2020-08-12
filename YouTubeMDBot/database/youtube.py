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


class YouTubeDB(PostgreSQLBase):
    def set_youtube_id(self, youtube_id: str):
        self.insert(
            """INSERT INTO youtubemd.YouTube(id) VALUES (%s) 
            ON CONFLICT DO NOTHING""",
            (youtube_id,)
        )

    def increment_times_requested(self, youtube_id: str):
        self.update(
            """UPDATE youtubemd.YouTube SET 
            times_requested = times_requested + 1 WHERE id = %s""",
            (youtube_id,)
        )

    def is_id_registered(self, youtube_id: str) -> bool:
        return self.fetchone(
            """SELECT EXISTS(SELECT 1 FROM youtubemd.YouTube WHERE id = %s)""",
            (youtube_id,)
        )[0]
