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
        else:
            help_attribute = args[0]
            if help_attribute == "ta":
                self.show_help_title_artist(bot, user_id, lang)
            elif help_attribute == "url":
                self.show_help_url(bot, user_id, lang)
            elif help_attribute == 'h':
                self.show_help_history(bot, user_id, lang)
            elif help_attribute == "meta":
                self.show_help_metadata(bot, user_id, lang)
            else:
                self.__show_reply_unrecognized_attribute(bot, user_id, lang)

    def show_help_keyboard(self, bot: Bot, user_id: int, lang: str, message_id: int = None):
        help_message = self.__messages[lang][0]["help"]["msg"]
        tt_at_button = self.__messages[lang][0]["help"]["d_via_tt-at-but"]
        url_button = self.__messages[lang][0]["help"]["d_via_url-but"]
        history_button = self.__messages[lang][0]["help"]["d_via_history-but"]
        metadata_button = self.__messages[lang][0]["help"]["m_set_metadata-but"]
        support_button = self.__messages[lang][0]["help"]["support_but"]

        help_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(tt_at_button, callback_data="tt_at_button"),
                                               InlineKeyboardButton(url_button, callback_data="url_button")],
                                              [InlineKeyboardButton(history_button, callback_data="history_button"),
                                               InlineKeyboardButton(metadata_button, callback_data="metadata_button")],
                                              [InlineKeyboardButton(support_button, callback_data="support_button")]])
        if not message_id:
            bot.sendMessage(chat_id=user_id, text=help_message, reply_markup=help_keyboard,
                            parse_mode=ParseMode.MARKDOWN)
        else:
            bot.editMessageText(text=help_message, chat_id=user_id, message_id=message_id,
                                parse_mode=ParseMode.MARKDOWN)

    def show_help_title_artist(self, bot: Bot, user_id: int, lang: str, message_id: int = None):
        help_message = self.__messages[lang][0]["help"]["d_via_tt-at"]
        if not message_id:
            bot.sendMessage(chat_id=user_id, text=help_message, parse_mode=ParseMode.MARKDOWN)
        else:
            self.__show_keyboard_back_button(bot, user_id, lang, message_id, help_message)

    def show_help_url(self, bot: Bot, user_id: int, lang: str, message_id: int = None):
        help_message = self.__messages[lang][0]["help"]["d_via_url"]
        if not message_id:
            bot.sendMessage(chat_id=user_id, text=help_message, parse_mode=ParseMode.MARKDOWN)
        else:
            self.__show_keyboard_back_button(bot, user_id, lang, message_id, help_message)

    def show_help_history(self, bot: Bot, user_id: int, lang: str, message_id: int = None):
        help_message = self.__messages[lang][0]["help"]["d_via_history"]
        if not message_id:
            bot.sendMessage(chat_id=user_id, text=help_message, parse_mode=ParseMode.MARKDOWN)
        else:
            self.__show_keyboard_back_button(bot, user_id, lang, message_id, help_message)

    def show_help_metadata(self, bot: Bot, user_id: int, lang: str, message_id: int = None):
        help_message = self.__messages[lang][0]["help"]["m_set_metadata"]
        if not message_id:
            bot.sendMessage(chat_id=user_id, text=help_message, parse_mode=ParseMode.MARKDOWN)
        else:
            self.__show_keyboard_back_button(bot, user_id, lang, message_id, help_message)

    def __show_keyboard_back_button(self, bot: Bot, user_id: int, lang: str, message_id: int, text: str):
        back_button = self.__messages[lang][0]["help"]["back_button"]

        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(back_button, callback_data="help_back")]])
        bot.editMessageText(text=text, chat_id=user_id, message_id=message_id,
                            parse_mode=ParseMode.MARKDOWN, reply_markup=back_keyboard)

    def __show_reply_unrecognized_attribute(self, bot: Bot, user_id: int, lang: str):
        unrecognized_text = self.__messages[lang][0]["help"]["h_unrecognized"]
        bot.sendMessage(chat_id=user_id, text=unrecognized_text, parse_mode=ParseMode.MARKDOWN)
