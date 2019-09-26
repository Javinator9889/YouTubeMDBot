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
import re
from subprocess import PIPE
from subprocess import Popen

from ..constants import FPCALC


def is_fpcalc_available() -> bool:
    try:
        proc = Popen(["fpcalc", "-v"], stdout=PIPE, stderr=PIPE)
    except OSError:
        return False
    else:
        proc.wait()


class FPCalc(object):
    def __init__(self, audio: bytes):
        fpcalc = Popen(FPCALC, stdout=PIPE, stdin=PIPE)
        out, _ = fpcalc.communicate(audio)
        res = out.decode("utf-8")

        duration_pattern = "[^=]\\d+\\n"
        fingerprint_pattern = "[^=]*$"
        duration = re.search(duration_pattern, res)
        fingerprint = re.search(fingerprint_pattern, res)

        self.__duration: int = int(duration.group(0))
        self.__fp: str = str(fingerprint.group(0))

    def duration(self) -> int:
        return self.__duration

    def fingerprint(self) -> str:
        return self.__fp
