from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from handlers import Handler


class DeveloperHandler(Handler):
    @run_async
    def develop(self, bot: Bot, update: Update):
        # to do