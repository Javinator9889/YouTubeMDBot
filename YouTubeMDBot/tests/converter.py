import unittest
import mutagen

from io import BytesIO
from typing import Tuple

from YouTubeMDBot.tests.tagger import TaggerTest
from YouTubeMDBot.audio import FFmpegMP3
from YouTubeMDBot.audio import FFmpegOGG


class MyTestCase(TaggerTest):
    def find_metadata(self, future, downloader) -> Tuple[BytesIO, bytes, dict]:
        print(f"Running test: find_metadata in {__file__}")
        io, data, song_info = super().find_metadata(future, downloader)
        io.seek(0)
        mp3 = FFmpegMP3(data=data, bitrate="96k")  # downrate
        ogg = FFmpegOGG(data=data, bitrate="256k")  # uprate

        mp3.convert()
        ogg.convert()

        mp3_container = BytesIO(mp3.get_output())
        ogg_container = BytesIO(ogg.get_output())

        print(mp3.get_extra().decode("utf-8"))
        print(ogg.get_extra().decode("utf-8"))

        print(mutagen.File(mp3_container).pprint())
        print(mutagen.File(ogg_container).pprint())

        return io, data, song_info


if __name__ == '__main__':
    unittest.main()
