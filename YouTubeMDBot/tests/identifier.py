import threading
import unittest
from pprint import pprint
from time import sleep
from time import time

from YouTubeMDBot.downloader import YouTubeDownloader
from YouTubeMDBot.metadata import MetadataIdentifier


class IdentifierTest(unittest.TestCase):
    lock = threading.Lock()
    threads = 0
    max = 0
    song_info = {}

    def test_identification(self):
        url = "https://www.youtube.com/watch?v=YQHsXMglC9A"
        downloader = YouTubeDownloader(url=url)
        audio, data = downloader.download()
        with open("hello.m4a", "wb") as song:
            song.write(data)
        identifier = MetadataIdentifier(audio=data)

        results = identifier.identify_audio()
        print("{0} by {1} - score: {2} / 1\n"
              "\thttps://musicbrainz.org/recording/{3}\n"
              "\thttps://musicbrainz.org/release/{4}\n\n"
              .format(identifier.title, identifier.artist,
                      identifier.score,
                      identifier.recording_id, identifier.release_id))
        with open("cover.jpg", "wb") as cover:
            cover.write(identifier.cover)

        pprint(results)

    def test_multiple_download_identification(self):
        yt1 = YouTubeDownloader(url="https://www.youtube.com/watch?v=Inm-N5rLUSI")
        yt2 = YouTubeDownloader(url="https://www.youtube.com/watch?v=-_ZwpOdXXcA")
        yt3 = YouTubeDownloader(url="https://www.youtube.com/watch?v=WOGWZD5iT10")
        yt4 = YouTubeDownloader(url="https://www.youtube.com/watch?v=GfKV9KaNJXc")

        t1 = threading.Thread(target=self.find_metadata, args=(yt1,))
        t2 = threading.Thread(target=self.find_metadata, args=(yt2,))
        t3 = threading.Thread(target=self.find_metadata, args=(yt3,))
        t4 = threading.Thread(target=self.find_metadata, args=(yt4,))

        self.max = 4

        t1.start()
        t2.start()
        t3.start()
        t4.start()

        while self.threads < self.max:
            sleep(1)

        pprint(self.song_info)

    def barrier(self):
        with self.lock:
            self.threads += 1

    def getThreads(self):
        with self.lock:
            return self.threads

    def find_metadata(self, downloader: YouTubeDownloader):
        st_dl_t = time()
        _, data = downloader.download()
        f_dl_t = time()
        print("Downloaded {} - elapsed time: {:.1f}s".format(downloader.get_url(),
                                                             f_dl_t - st_dl_t))
        identifier = MetadataIdentifier(audio=data, downloader=downloader)
        identifier.identify_audio()
        self.song_info[downloader.get_url()] = {
            "title": identifier.title,
            "artist": identifier.artist
        }
        if not identifier.youtube_data:
            self.song_info[downloader.get_url()]["score"] = identifier.score
            self.song_info[downloader.get_url()]["record_id"] = \
                "https://musicbrainz.org/recording/{0}".format(identifier.recording_id)
            self.song_info[downloader.get_url()]["release_id"] = \
                "https://musicbrainz.org/release/{0}".format(identifier.release_id)
        else:
            self.song_info[downloader.get_url()]["duration"] = identifier.duration
            self.song_info[downloader.get_url()]["id"] = identifier.youtube_id
            self.song_info[downloader.get_url()]["youtube_data"] = True
        self.barrier()


if __name__ == '__main__':
    unittest.main()
