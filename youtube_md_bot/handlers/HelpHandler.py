from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from handlers import Handler


class HelpHandler(Handler):
    @run_async
    def help(self, bot: Bot, update: Update, args: list):
        chat_id = update.message.chat_id
        if len(args) == 0:
            print("no args")
        else:
            bot.sendMessage(chat_id, self.__messages["help"])
