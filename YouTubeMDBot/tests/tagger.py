import unittest
import mutagen

from typing import Tuple
from io import BytesIO

from YouTubeMDBot.tests.identifier import IdentifierTest
from YouTubeMDBot.downloader import YouTubeDownloader
from YouTubeMDBot.metadata import AudioMetadata
from YouTubeMDBot.utils import youtube_utils


class TaggerTest(IdentifierTest):
    def find_metadata(self, downloader: YouTubeDownloader) -> Tuple[BytesIO, bytes]:
        io, data = super().find_metadata(downloader)
        tagger = AudioMetadata(io)
        url = downloader.get_url()

        tagger.set_title(super().song_info[url]["title"])
        tagger.set_artist(super().song_info[url]["artist"])
        tagger.set_cover(super().song_info[url]["cover"])
        extra = ["YouTube URL: " + url]
        if not super().song_info[url].get("youtube_data"):
            tagger.set_album(super().song_info[url]["album"])
            extra.append("MusicBrainz Record ID: " + super().song_info[url][
                "record_id"])
            extra.append("MusicBrainz Release ID: " + super().song_info[url][
                "release_id"])
            tagger.set_extras(extra)
        else:
            tagger.set_extras(["YouTube ID: {}".format(super().song_info[url]["id"])])
        yid = youtube_utils.get_yt_video_id(url)
        rs = tagger.save()
        rs.seek(0)
        print(mutagen.File(rs).pprint())
        rs.seek(0)
        with open(yid + ".m4a", "wb") as f:
            f.write(rs.read())
        rs.seek(0)
        return rs, rs.read()


if __name__ == '__main__':
    unittest.main()
