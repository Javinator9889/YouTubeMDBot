import unittest
import logging

from threading import Lock

from YouTubeMDBot.downloader import YouTubeDownloader
from YouTubeMDBot.downloader import M4AYouTubeDownloader
from YouTubeMDBot.downloader import MultipleYouTubeDownloader

log = logging.basicConfig()


class DownloadTest(unittest.TestCase):
    lock = Lock()

    @property
    def finished(self):
        with self.lock:
            return self.__finished

    @finished.setter
    def finished(self, value):
        with self.lock:
            self.__finished = value

    def test_single_download(self):
        downloader = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=Inm-N5rLUSI"
        )
        self._test_download(downloader)

    def test_single_download_to_m4a(self):
        downloader = M4AYouTubeDownloader(
            url="https://www.youtube.com/watch?v=Inm-N5rLUSI"
        )
        self._test_download(downloader)

    def test_multiple_downloader(self):
        downloader = MultipleYouTubeDownloader()
        self.finished = 0
        urls = {
            "https://www.youtube.com/watch?v=Inm-N5rLUSI",
            "https://www.youtube.com/watch?v=-_ZwpOdXXcA",
            "https://www.youtube.com/watch?v=WOGWZD5iT10",
            "https://www.youtube.com/watch?v=GfKV9KaNJXc",
            "https://www.youtube.com/watch?v=DiItGE3eAyQ",
            "https://www.youtube.com/watch?v=GuZzuQvv7uc"
        }
        for url in urls:
            yt_downloader = YouTubeDownloader(url)
            downloader.download_async(yt_downloader,
                                      callback=self._download_finished_callback,
                                      error_callback=self._download_failed_callback)
        while self.finished != 6:
            sleep(1)

    def _test_download(self, downloader: YouTubeDownloader):
        io, data = downloader.download()
        self.assertEqual(io.read(), data)

    def _download_finished_callback(self, data):
        log.info("Video download finished")
        log.debug(type(data))
        self.finished += 1

    def _download_failed_callback(self, err):
        log.error(f"Captured error: {err}")


if __name__ == '__main__':
    unittest.main()
