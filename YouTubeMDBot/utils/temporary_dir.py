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
import os
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory


class TemporaryDir:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if TemporaryDir.__instance is None:
            cls.__instance = object.__new__(cls)
            user_id = os.getuid()
            temporary_location = f"/run/user/{user_id}/"
            cls.__instance.dir = TemporaryDirectory(dir=temporary_location)
            for key, value in kwargs.items():
                setattr(cls.__instance, key, value)
        return cls.__instance

    def create_new_file(self,
                        mode: str = "w+b",
                        buffering=-1,
                        encoding=None,
                        newline=None,
                        suffix=None,
                        prefix=None,
                        delete=True,
                        *,
                        errors=None) -> NamedTemporaryFile:
        return NamedTemporaryFile(mode, buffering, encoding, newline, suffix,
                                  prefix,
                                  dir=self.dir.name,
                                  delete=delete,
                                  errors=errors)

    def close(self):
        self.dir.cleanup()

    def __del__(self):
        self.close()
