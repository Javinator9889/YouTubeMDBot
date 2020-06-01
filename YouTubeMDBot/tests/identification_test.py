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
import unittest
import logging

from YouTubeMDBot.downloader import YouTubeDownloader
from YouTubeMDBot.metadata import YouTubeMetadataIdentifier


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


class IdentificationTest(unittest.TestCase):
    def test_knwon_identification(self):
        downloader = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=YQHsXMglC9A"
        )
        _, data = downloader.download()
        identifier = YouTubeMetadataIdentifier(data)
        identifier.identify_audio()
        logging.info(identifier)

    def test_unknown_identification(self):
        downloader = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=BL4dnvBytLA"
        )
        _, data = downloader.download()
        identifier = YouTubeMetadataIdentifier(data, downloader)
        identifier.identify_audio()
        logging.info(identifier)
