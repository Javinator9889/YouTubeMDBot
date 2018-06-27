from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from handlers import Handler


class URLHandler(Handler):
    @run_async
    def url_handler(self, bot: Bot, update: Update):
        message = update.message.text
