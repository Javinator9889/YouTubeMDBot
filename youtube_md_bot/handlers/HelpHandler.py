from telegram import Bot, Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import run_async

from handlers import Handler


class HelpHandler(Handler):
    @run_async
    def help(self, bot: Bot, update: Update, args: list):
        effective_user = update.effective_user
        user_id = effective_user.id
        lang = effective_user.language_code

        self.__update_operations.updateUserLastTimeActive(user_id)

        if len(args) == 0:
            self.show_help_keyboard(bot=bot, user_id=user_id, lang=lang)

    def show_help_keyboard(self, bot: Bot, user_id: int, lang: str, message_id: int=None):
        help_message = self.__messages[lang][0]["help"]["msg"]
        tt_at_button = self.__messages[lang][0]["help"]["d_via_tt-at-but"]
        url_button = self.__messages[lang][0]["help"]["d_via_url-but"]
        history_button = self.__messages[lang][0]["help"]["d_via_history-but"]
        support_button = self.__messages[lang][0]["help"]["support_but"]

        help_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(tt_at_button, callback_data="tt_at_button"),
                                               InlineKeyboardButton(url_button, callback_data="url_button")],
                                              [InlineKeyboardButton(history_button, callback_data="history_button"),
                                               InlineKeyboardButton(support_button, callback_data="support_button")]])
        if not message_id:
            bot.sendMessage(chat_id=user_id, text=help_message, reply_markup=help_keyboard,
                            parse_mode=ParseMode.MARKDOWN)
        else:
            bot.editMessageText(help_message, chat_id=user_id, message_id=message_id, parse_mode=ParseMode.MARKDOWN)
