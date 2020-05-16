import unittest
import time

from YouTubeMDBot.database import *


class DatabaseTesting(unittest.TestCase):
    def test_creation(self):
        db_item = PostgreSQLItem(min_ops=3)
        db = Initializer(db_item)
        db.init()

        db_item2 = PostgreSQLItem()
        db_item3 = PostgreSQLItem()
        db_item4 = PostgreSQLItem()

        user_db = UserDB(db_item)
        print(hex(id(db)))
        print(hex(id(user_db)))

        user_db.register_new_user(12334, "test", "test", "en")
        user_db.register_new_user(12335, "test", "test", "en")
        user_db.register_new_user(12336, "test", "test", "en")
        user_db.register_new_user(12337, "test", "test", "en")
        user_db.register_new_user(12338, "test", "test", "en")
        user_db.register_new_user(12339, "test", "test", "en")
        user_db.register_new_user(12330, "test", "test", "en")
        user_db.register_new_user(12331, "test", "test", "en")
        user_db.register_new_user(12332, "test", "test", "en")
        user_db.register_new_user(12333, "test", "test", "en")
        user_db.register_new_user(12344, "test", "test", "en")

        time.sleep(1)

        for uid in (12334, 12335, 12336, 12337, 12338, 12339, 12330, 12331,
                    12332, 12333, 12344):
            print(user_db.get_user_information(uid))

        del db_item


if __name__ == '__main__':
    unittest.main()
