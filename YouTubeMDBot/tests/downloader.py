import threading
import unittest

from YouTubeMDBot.downloader import YouTubeDownloader


class DownloadTest(unittest.TestCase):
    def test_multithread_download(self):
        yt1 = YouTubeDownloader(url="https://www.youtube.com/watch?v=Inm-N5rLUSI")
        yt2 = YouTubeDownloader(url="https://www.youtube.com/watch?v=-_ZwpOdXXcA")
        yt3 = YouTubeDownloader(url="https://www.youtube.com/watch?v=WOGWZD5iT10")
        yt4 = YouTubeDownloader(url="https://www.youtube.com/watch?v=9HfoNUjw5u8")
        t1 = threading.Thread(target=self.write_to_file, args=(yt1, "v1.m4a",))
        t2 = threading.Thread(target=self.write_to_file, args=(yt2, "v2.m4a",))
        t3 = threading.Thread(target=self.write_to_file, args=(yt3, "v3.m4a",))
        t4 = threading.Thread(target=self.write_to_file, args=(yt4, "v4.m4a",))

        t1.start()
        t2.start()
        t3.start()
        t4.start()

    @staticmethod
    def write_to_file(yt: YouTubeDownloader, name: str):
        _, data = yt.download()
        print(name + " downloaded")
        with open(name, "wb") as f:
            f.write(data)


if __name__ == '__main__':
    unittest.main()
