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


class PreferencesDB(PostgreSQLBase):
    def get_user_preferences(self, user_id: int) -> dict:
        data = self.fetchone(
            """SELECT audio_format, audio_quality, send_song_link, 
            song_behaviour FROM youtubemd.Preferences WHERE User_id = %s""",
            (user_id,)
        )
        return {
            "audio_format": data[0],
            "audio_quality": data[1],
            "send_song_link": data[2],
            "song_behaviour": data[3]
        }

    def update_user_audio_format(self, user_id: int, audio_format: str):
        self.update(
            """UPDATE youtubemd.Preferences SET audio_format = %s WHERE 
            user_id = %s""", (audio_format, user_id)
        )

    def update_user_audio_quality(self, user_id: int, audio_quality: str):
        self.update(
            """UPDATE youtubemd.Preferences SET audio_quality = %s WHERE 
            user_id = %s""", (audio_quality, user_id)
        )

    def update_user_behaviour(self, user_id: int, behaviour: str):
        self.update(
            """UPDATE youtubemd.Preferences SET song_behaviour = %s WHERE 
            user_id = %s""", (behaviour, user_id)
        )

    def update_user_send_song_link(self, user_id: int, send_song_link: bool):
        self.update(
            """UPDATE youtubemd.Preferences SET send_song_link = %s WHERE 
            user_id = %s""", (send_song_link, user_id)
        )
