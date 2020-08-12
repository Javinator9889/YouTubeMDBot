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
from datetime import datetime


class UserDB(PostgreSQLBase):
    def get_user_information(self, user_id: int) -> dict:
        data = self.fetchone(
            """SELECT id, name, tag, lang, first_access 
            FROM youtubemd.User WHERE id = %s""", (user_id,)
        )
        return {
            "id": data[0],
            "name": data[1],
            "tag": data[2],
            "lang": data[3],
            "first_access": data[4]
        }

    def get_user_history(self, user_id: int) -> list:
        data = self.fetchall(
            """SELECT id, file_id, metadata_id, date FROM youtubemd.History 
            WHERE user_id = %s""", (user_id,)
        )
        result = []
        for row in data:
            result.append({
                "id": row[0],
                "file_id": row[1],
                "metadata_id": row[2],
                "date": row[3]
            })
        return result

    def register_new_user(self, user_id: int, name: str, tag: str, lang: str,
                          returning_id: bool = False):
        now = datetime.now()
        query = """
        INSERT INTO youtubemd.User (id, name, tag, lang, first_access) 
        VALUES (%s, %s, %s, %s, %s)
        """
        self.insert(query, (user_id, name, tag, lang, now))
        return self.insert(
            """INSERT INTO youtubemd.Preferences (user_id) VALUES (%s)""",
            (user_id,), returning_id=returning_id
        )

    def update_username(self, user_id: int, name: str):
        self.update(
            """UPDATE youtubemd.User SET name = %s WHERE id = %s""",
            (name, user_id)
        )

    def update_user_lang(self, user_id: int, lang: str):
        self.update(
            """UPDATE youtubemd.User SET lang = %s WHERE id = %s""",
            (lang, user_id)
        )

    def update_user_tag(self, user_id: int, tag: str):
        self.update(
            """UPDATE youtubemd.User SET tag = %s WHERE id = %s""",
            (tag, user_id)
        )

    def register_new_download(self,
                              user_id: int,
                              file_id: str,
                              metadata_id: str):
        now = datetime.now()
        self.insert(
            """INSERT INTO youtubemd.History 
                (file_id, user_id, metadata_id, date) 
                VALUES (%s, %s, %s, %s)""",
            (file_id, metadata_id, user_id, now.date())
        )
