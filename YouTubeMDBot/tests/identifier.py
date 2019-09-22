import unittest
from pprint import pprint

from YouTubeMDBot.downloader import YouTubeDownloader
from YouTubeMDBot.metadata import MetadataIdentifier


class IdentifierTest(unittest.TestCase):
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
              .format(identifier.get_title(), identifier.get_artist(),
                      identifier.get_score(),
                      identifier.get_recording_id(), identifier.get_release_id()))
        with open("cover.jpg", "wb") as cover:
            cover.write(identifier.get_cover())

        pprint(results)


if __name__ == '__main__':
    unittest.main()
