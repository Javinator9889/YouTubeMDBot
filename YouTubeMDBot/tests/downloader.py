import threading
import unittest
from threading import Barrier

from YouTubeMDBot.downloader import MultipleYouTubeDownloader
from YouTubeMDBot.downloader import YouTubeDownloader


class DownloadTest(unittest.TestCase):
    _elements = 0
    _lock = threading.Lock()
    _barrier = Barrier(parties=5)

    def test_multithread_download(self):
        print(f"Running test: test_multithread_download in {__file__}")
        yt1 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=Inm-N5rLUSI")
        yt2 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=-_ZwpOdXXcA")
        yt3 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=WOGWZD5iT10")
        yt4 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=9HfoNUjw5u8")

        ytdl = MultipleYouTubeDownloader()
        ft1 = ytdl.download_async(yt1, error_callback=handle_error)
        ft2 = ytdl.download_async(yt2, error_callback=handle_error)
        ft3 = ytdl.download_async(yt3, error_callback=handle_error)
        ft4 = ytdl.download_async(yt4, error_callback=handle_error)

        t1 = threading.Thread(target=self.write_to_file, args=(ft1, "v1.m4a",))
        t2 = threading.Thread(target=self.write_to_file, args=(ft2, "v2.m4a",))
        t3 = threading.Thread(target=self.write_to_file, args=(ft3, "v3.m4a",))
        t4 = threading.Thread(target=self.write_to_file, args=(ft4, "v4.m4a",))

        t1.start()
        t2.start()
        t3.start()
        t4.start()

        self._barrier.wait()

        del ytdl

    def write_to_file(self, future, name: str):
        _, data = future.get()
        print(name + " downloaded")
        with open(name, "wb") as f:
            f.write(data)
        self._barrier.wait()


def handle_error(exception):
    print("Unexpected exception: " + str(exception))
    raise exception()


if __name__ == '__main__':
    unittest.main()
