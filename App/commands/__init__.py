from telegram import Bot, Update
from telegram.ext import run_async


class StartHandler:
    def __init__(self, start_messages: dict):
        self.__messages = start_messages

    @run_async
    def start(self, bot: Bot, update: Update):
        chat_id = update.message.chat_id
        user_id = update.message.user_id
        bot.sendMessage(chat_id, self.__messages["welcome"])


class HelpHandler:
    def __init__(self, help_messages: dict):
        self.__messages = help_messages

    @run_async
    def help(self, bot: Bot, update: Update, args: list):
        chat_id = update.message.chat_id
        if len(args) == 0:
            print("no args")
        else:
            bot.sendMessage(chat_id, self.__messages["help"])
