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
try:
    import ujson as json
except ImportError:
    import json
from urllib.request import urlopen

import isodate
from googleapiclient.discovery import build

from ..constants import YOUTUBE
from ..errors import EmptyBodyError


class YouTubeVideoData(object):
    def __init__(self, data: dict):
        if not data.get("items"):
            raise EmptyBodyError("The data object has no items")
        if len(data.get("items")) >= 1:
            content = data.get("items")[0]
            snippet = content.get("snippet")
            details = content.get("contentDetails")
            statistics = content.get("statistics")
            if not snippet:
                raise EmptyBodyError("No information available to requested video")
            if not details:
                raise EmptyBodyError("No video details available")
            if not statistics:
                raise EmptyBodyError("No statistics available")
            self.title = snippet["title"]
            self.thumbnail = snippet["thumbnails"]["maxres"]["url"]
            self.artist = snippet["channelTitle"]
            self.duration = isodate.parse_duration(details["duration"]).total_seconds()
            self.view = int(statistics["viewCount"])
            self.like = int(statistics["likeCount"])
            self.dislike = int(statistics["dislikeCount"])


class YouTubeAPI(object):
    def __init__(self):
        self.__youtube = build(serviceName=YOUTUBE["api"]["name"],
                               version=YOUTUBE["api"]["version"],
                               developerKey=YOUTUBE["key"])

    def search(self, term: str):
        return self.__youtube.search().list(
            q=term,
            type="video",
            part="id,snippet",
            maxResults=1
        ).execute()

    @staticmethod
    def video_details(video_id: str) -> YouTubeVideoData:
        api_url = YOUTUBE["endpoint"].format(video_id, YOUTUBE["key"])
        print(api_url)
        data = urlopen(url=api_url)
        return YouTubeVideoData(data=json.loads(data.read()))
