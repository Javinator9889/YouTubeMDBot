import unittest
import mutagen

from YouTubeMDBot.downloader import M4AYouTubeDownloader
from YouTubeMDBot.audio import FFmpegM4A


class MyTestCase(unittest.TestCase):
    def test_download(self):
        print(f"Running test: test_download in {__file__}")
        dl = M4AYouTubeDownloader(
            url="https://www.youtube.com/watch?v=s6VaeFCxta8",
            bitrate="128k")
        io, data = dl.download()
        with open("outex.m4a", "wb") as of:
            of.write(data)
        print(mutagen.File(io).pprint())
        io.seek(0)
        return io, data

    def test_normalization(self):
        print(f"Running test: test_normalization in {__file__}")
        io, data = self.test_download()
        ctr = FFmpegM4A(data, "filename")
        assert ctr.get_volume() == 0.0


if __name__ == '__main__':
    unittest.main()
