import unittest
from io import BytesIO
from typing import Tuple

import mutagen

from YouTubeMDBot.metadata import AudioMetadata
from YouTubeMDBot.tests.identifier import IdentifierTest
from YouTubeMDBot.utils import youtube_utils


class TaggerTest(IdentifierTest):
    def find_metadata(self, future, downloader) -> Tuple[BytesIO, bytes, dict]:
        print(f"Running test: find_metadata in {__file__}")
        io, data, song_info = super().find_metadata(future, downloader)
        tagger = AudioMetadata(io)
        url = downloader.get_url()

        tagger.set_title(song_info[url]["title"])
        tagger.set_artist(song_info[url]["artist"])
        tagger.set_cover(song_info[url]["cover"])
        extra = ["YouTube URL: " + url]
        if not song_info[url].get("youtube_data"):
            tagger.set_album(song_info[url]["album"])
            extra.append("MusicBrainz Record ID: " + song_info[url][
                "record_id"])
            extra.append("MusicBrainz Release ID: " + song_info[url][
                "release_id"])
            tagger.set_extras(extra)
        else:
            tagger.set_extras(["YouTube ID: {}".format(song_info[url]["id"])])
        yid = youtube_utils.get_yt_video_id(url)
        rs = tagger.save()
        rs.seek(0)
        print(mutagen.File(rs).pprint())
        rs.seek(0)
        with open(yid + ".m4a", "wb") as f:
            f.write(rs.read())
        rs.seek(0)
        return rs, rs.read(), song_info


if __name__ == '__main__':
    unittest.main()
