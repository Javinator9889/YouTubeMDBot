from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from handlers import Handler


class TextHandler(Handler):
    @run_async
    def message_handler(self, bot: Bot, update: Update):
        text = update.message.text
