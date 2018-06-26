from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from utils import Constants
from database import InsertOperations


class Handler:
    def __init__(self, handler_messages: dict):
        self.__messages = handler_messages

class StartHandler(Handler):
    @run_async
    def start(self, bot: Bot, update: Update):
        import os
        import pickle

        effective_user = update.effective_user
        user_id = effective_user.id
        username = effective_user.username
        name = effective_user.first_name
        user_path = Constants.P_USERS_PATH + user_id + '/'
        db_insert: InsertOperations = InsertOperations()
        if not os.path.exists(user_path):
            os.mkdir(user_path)
            with open(user_path + Constants.P_USERS_FILE, "wb") as user_info:
                pickle.dump(Constants.D_USER_DICT, user_info)
            db_insert.registerNewUser(user_id=user_id, username=username, name=name)
        bot.sendMessage(chat_id=user_id, text=self.__messages["msg"], parse_mode=ParseMode.MARKDOWN)


class HelpHandler(Handler):
    @run_async
    def help(self, bot: Bot, update: Update, args: list):
        chat_id = update.message.chat_id
        if len(args) == 0:
            print("no args")
        else:
            bot.sendMessage(chat_id, self.__messages["help"])


class DeveloperHandler(Handler):
    @run_async
    def develop(self, bot: Bot, update: Update):
        # to do


class VideoIDHandler(Handler):
    @run_async
    def video_handler(self, bot: Bot, update: Update):
        video_id = update.message.text

