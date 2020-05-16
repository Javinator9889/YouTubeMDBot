import threading
import unittest
from io import BytesIO
from pprint import pprint
from time import sleep
from time import time
from typing import Tuple
from threading import Barrier

from YouTubeMDBot.downloader import MultipleYouTubeDownloader
from YouTubeMDBot.downloader import YouTubeDownloader
from YouTubeMDBot.metadata import YouTubeMetadataIdentifier


class IdentifierTest(unittest.TestCase):
    lock = threading.Lock()
    song_info = {}
    barrier = Barrier(parties=7)

    def test_identification(self):
        print(f"Running test: test_identification in {__file__}")
        url = "https://www.youtube.com/watch?v=YQHsXMglC9A"
        downloader = YouTubeDownloader(url=url)
        audio, data = downloader.download()
        with open("hello.m4a", "wb") as song:
            song.write(data)
        identifier = YouTubeMetadataIdentifier(audio=data,
                                               downloader=downloader)

        valid = identifier.identify_audio()
        assert valid
        print("{0} by {1} - score: {2} / 1\n"
              "\thttps://musicbrainz.org/recording/{3}\n"
              "\thttps://musicbrainz.org/release/{4}\n\n"
              .format(identifier.title, identifier.artist,
                      identifier.score,
                      identifier.recording_id, identifier.release_id))
        with open("cover.jpg", "wb") as cover:
            cover.write(identifier.cover)

    def test_multiple_download_identification(self):
        print(f"Running test: test_multiple_download_identification in"
              f" {__file__}")
        yt1 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=Inm-N5rLUSI")
        yt2 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=-_ZwpOdXXcA")
        yt3 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=WOGWZD5iT10")
        yt4 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=GfKV9KaNJXc")
        yt5 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=DiItGE3eAyQ")
        yt6 = YouTubeDownloader(
            url="https://www.youtube.com/watch?v=GuZzuQvv7uc")

        ytdl = MultipleYouTubeDownloader()

        f1 = ytdl.download_async(yt1, error_callback=handle_error)
        f2 = ytdl.download_async(yt2, error_callback=handle_error)
        f3 = ytdl.download_async(yt3, error_callback=handle_error)
        f4 = ytdl.download_async(yt4, error_callback=handle_error)
        f5 = ytdl.download_async(yt5, error_callback=handle_error)
        f6 = ytdl.download_async(yt6, error_callback=handle_error)

        t1 = threading.Thread(target=self.find_metadata, args=(f1, yt1,))
        t2 = threading.Thread(target=self.find_metadata, args=(f2, yt2,))
        t3 = threading.Thread(target=self.find_metadata, args=(f3, yt3,))
        t4 = threading.Thread(target=self.find_metadata, args=(f4, yt4,))
        t5 = threading.Thread(target=self.find_metadata, args=(f5, yt5,))
        t6 = threading.Thread(target=self.find_metadata, args=(f6, yt6,))

        self.max = 6

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()

        self.barrier.wait()

        pprint("Finished")

        del ytdl

    def find_metadata(self, future, downloader) -> Tuple[BytesIO, bytes, dict]:
        st_dl_t = time()
        io, data = future.get()
        f_dl_t = time()
        print("Downloaded {} - elapsed time: {:.1f}s"
              .format(downloader.get_url(), f_dl_t - st_dl_t))
        identifier = \
            YouTubeMetadataIdentifier(audio=data, downloader=downloader)
        valid = identifier.identify_audio()
        assert valid
        song_info = {downloader.get_url(): {
            "title": identifier.title,
            "artist": identifier.artist,
            "cover": identifier.cover
        }}
        if not identifier.youtube_data:
            song_info[downloader.get_url()]["score"] = identifier.score
            song_info[downloader.get_url()]["record_id"] = \
                "https://musicbrainz.org/recording/{0}".format(
                    identifier.recording_id)
            song_info[downloader.get_url()]["release_id"] = \
                "https://musicbrainz.org/release/{0}".format(
                    identifier.release_id)
            song_info[downloader.get_url()]["album"] = identifier.album
        else:
            song_info[downloader.get_url()][
                "duration"] = identifier.duration
            song_info[downloader.get_url()]["id"] = identifier.youtube_id
            song_info[downloader.get_url()]["youtube_data"] = True
        self.barrier.wait()
        return io, data, song_info


def handle_error(exception):
    raise RuntimeError("Catch exception while running a thread: "
                       + str(exception))


if __name__ == '__main__':
    unittest.main()
