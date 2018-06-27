from telegram import Bot, Update, ParseMode
from telegram.ext import run_async

from handlers import Handler


class VideoIDHandler(Handler):
    @run_async
    def video_handler(self, bot: Bot, update: Update):
        video_id = update.message.text
