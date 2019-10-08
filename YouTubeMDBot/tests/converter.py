import unittest
import mutagen

from typing import Tuple
from io import BytesIO

from YouTubeMDBot.tests.tagger import TaggerTest
from YouTubeMDBot.downloader import YouTubeDownloader
from YouTubeMDBot.audio import FFmpegMP3
from YouTubeMDBot.audio import FFmpegOGG


class MyTestCase(TaggerTest):
    def find_metadata(self, downloader: YouTubeDownloader) -> Tuple[BytesIO, bytes]:
        io, data = super().find_metadata(downloader)
        io.seek(0)
        mp3 = FFmpegMP3(data=io)
        ogg = FFmpegOGG(data=io)

        mp3.convert()
        io.seek(0)
        ogg.convert()

        mp3_container = BytesIO(mp3.get_output())
        ogg_container = BytesIO(ogg.get_output())

        print(mp3.get_err().decode("utf-8"))
        print(ogg.get_err().decode("utf-8"))

        print(mutagen.File(mp3_container).pprint())
        print(mutagen.File(ogg_container).pprint())

        return io, data


if __name__ == '__main__':
    unittest.main()
