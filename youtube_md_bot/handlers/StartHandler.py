from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from datetime import datetime

from handlers import Handler
from utils import Constants


class StartHandler(Handler):
    def __init__(self, handler_messages: dict):
        super().__init__(handler_messages=handler_messages)

    @run_async
    def start(self, bot: Bot, update: Update):
        import os
        import pickle

        effective_user = update.effective_user
        user_id = effective_user.id
        username = effective_user.username
        name = effective_user.first_name
        lang = effective_user.language_code

        user_path = Constants.P_USERS_PATH + user_id + '/'
        db_insert = self.__insert_operations
        if not os.path.exists(user_path):
            os.mkdir(user_path)
            with open(user_path + Constants.P_USERS_FILE, "wb") as user_info:
                pickle.dump(Constants.D_USER_DICT, user_info)
            db_insert.registerNewUser(user_id=user_id, username=username, name=name)
            db_insert.registerStatistics(user_id, lang, 0, datetime.now())
        message = self.__messages[lang][0]["welcome"][0]["msg"].format(username)
        bot.sendMessage(chat_id=user_id, text=message, parse_mode=ParseMode.MARKDOWN)
