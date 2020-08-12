import unittest

from YouTubeMDBot.database import *


class DatabaseTest(unittest.TestCase):
    item = PostgreSQLItem(min_ops=0)
    base = Initializer(item)

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.base.init()

    def test_insertion(self):
        user = UserDB(item=self.item)
        user.register_new_user(user_id=1, name="John", tag="@John", lang="es")
        info = user.get_user_information(user_id=1)
        print(info)

    def __del__(self):
        self.item.stop()


if __name__ == '__main__':
    unittest.main()
