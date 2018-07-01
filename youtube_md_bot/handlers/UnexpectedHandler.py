from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from handlers import Handler


class UnexpectedHandler(Handler):
    @run_async
    def unexpected(self, bot: Bot, update: Update):
        msg_type = update.message.text
