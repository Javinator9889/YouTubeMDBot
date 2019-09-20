#                             YouTubeMDBot
#                  Copyright (C) 2019 - Javinator9889
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#                   (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#               GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
from telegram.ext import Updater
from telegram.ext import CommandHandler

PROGRAM_ARGS = None


def main(args: dict):
    global PROGRAM_ARGS
    PROGRAM_ARGS = args
    updater = Updater(args["token"], workers=args["workers"])

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("hello", main))

    if args["use_webhook"]:
        updater.start_webhook(listen=args["ip"],
                              port=args["port"],
                              url_path=args["token"],
                              webhook_url=args["public_url"] + '/' + args["token"])
    else:
        updater.start_polling(args["poll_interval"])
    updater.idle()
