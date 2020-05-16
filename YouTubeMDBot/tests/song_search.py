import unittest

from YouTubeMDBot.api import YouTubeAPI
from YouTubeMDBot.api import YouTubeVideoData


class TestSearch(unittest.TestCase):
    def test_search(self):
        print(f"Running test: test_search in {__file__}")
        s = YouTubeAPI()
        search: dict = s.search(term="test")
        data = YouTubeVideoData(data=search, ignore_errors=True)
        print("Title: {0}\n"
              "Artist: {1}\n"
              "Thumbnail: {2}\n"
              "Duration: {3}\n"
              "Views: {4}\n"
              "Likes: {5}\n"
              "Dislikes: {6}\n"
              "Id: {7}".format(data.title, data.artist, data.thumbnail,
                               data.duration, data.views, data.likes,
                               data.dislikes, data.id))


if __name__ == '__main__':
    unittest.main()
