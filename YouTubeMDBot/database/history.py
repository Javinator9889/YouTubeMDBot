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
from typing import List

from . import PostgreSQLBase


class HistoryDB(PostgreSQLBase):
    def get_history_for_user_id(self, user_id: int) -> List[dict]:
        data = self.fetchall(
            """SELECT id, file_id, user_id, metadata_id, date FROM 
            youtubemd.History WHERE user_id = %s""", (user_id,)
        )
        history = list()
        for value in data:
            history.append(
                {
                    "id": value[0],
                    "file_id": value[1],
                    "user_id": value[2],
                    "metadata_id": value[3]
                }
            )
        return history

    def remove_history_entry(self, history_id: int):
        self.delete(
            """DELETE FROM youtubemd.History WHERE id = %s""", (history_id,)
        )

    def remove_all_history_for_user(self, user_id: int):
        self.delete(
            """DELETE FROM youtubemd.History WHERE user_id = %s""", (user_id,)
        )
