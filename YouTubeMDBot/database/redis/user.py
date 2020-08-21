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
from typing import Optional, Any
from datetime import datetime
from .. import UserDB
from . import DatabaseWrapper


class History(DatabaseWrapper):
    pass


class User(DatabaseWrapper):
    def __init__(self, user_id: int):
        super(User, self).__init__(name=str(user_id))
        self.user_id = user_id
        self._user = UserDB(self.item)

    @property
    def name(self) -> str:
        return self._get_or_query("name")

    @name.setter
    def name(self, value: str):
        self.delete("name")
        self._user.update_username(self.user_id, name=value)

    @property
    def tag(self) -> Optional[str]:
        return self._get_or_query("tag")

    @tag.setter
    def tag(self, value: Optional[str]):
        self.delete("tag")
        self._user.update_user_tag(self.user_id, tag=value)

    @property
    def lang(self) -> str:
        return self._get_or_query("lang")

    @lang.setter
    def lang(self, value: str):
        self.delete("lang")
        self._user.update_user_lang(self.user_id, lang=value)

    @property
    def first_access(self) -> datetime:
        return self._get_or_query("first_access")

    @property
    def history(self) -> History:
        pass  # TODO

    def _get_or_query(self, attr: str) -> Any:
        value = self.get(attr)
        if value:
            return value
        value = self._user.get_user_information(self.user_id)[attr]
        self.set(attr, value)
        return value
