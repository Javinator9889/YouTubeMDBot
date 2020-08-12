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


class YouTubeStatsDB(PostgreSQLBase):
    def _get_top_ten(self, procedure: str, name: str) -> List[dict]:
        data = self.callproc(procedure)
        top_ten = list()
        for values in data:
            top_ten.append(
                {
                    "id": values[0],
                    name: values[1]
                }
            )
        return top_ten

    def get_top_ten_daily(self) -> List[dict]:
        return self._get_top_ten("youtubemd.top_10_daily", "daily_requests")

    def get_top_ten_weekly(self) -> List[dict]:
        return self._get_top_ten("youtubemd.top_10_weekly", "weekly_requests")

    def get_top_ten_monthly(self) -> List[dict]:
        return self._get_top_ten("youtubemd.top_10_monthly", "monthly_requests")

    def clear_top_ten_daily(self):
        self.callproc("youtubemd.clear_daily_stats")

    def clear_top_ten_weekly(self):
        self.callproc("youtubemd.clear_weekly_stats")

    def clear_top_ten_monthly(self):
        self.callproc("youtubemd.clear_monthly_stats")
