try:
    from argparse import ArgumentParser, Namespace
except (ImportError, ModuleNotFoundError) as e:
    print("Modules needed not found: " + str(e))

from .out import cPrint, Colors
from .upgrader import PiPUpgrader
from .database import DatabaseOperationsBase
from .utils import Constants, logger
from .handlers.StartHandler import StartHandler
from .handlers.HelpHandler import HelpHandler
from .handlers.DeveloperHandler import DeveloperHandler
from .handlers.VideoIDHandler import VideoIDHandler
from .handlers.URLHandler import URLHandler
from .handlers.TextHandler import TextHandler
from .handlers.UnexpectedHandler import UnexpectedHandler


def handler_definer():
    # type: () -> list
    from telegram import MessageEntity
    from telegram.ext import CommandHandler, MessageHandler, Filters

    handlers = []
    with open(Constants.A_APP_MESSAGES, 'r') as messages_file:
        messages: dict = messages_file.read()
    start = StartHandler(messages)
    help_handler = HelpHandler(messages)
    dev = DeveloperHandler(messages)
    video = VideoIDHandler(messages)
    url = URLHandler(messages)
    text = TextHandler(messages)
    unexpected = UnexpectedHandler(messages)
    
    handlers.append(CommandHandler("start", start.start))
    handlers.append(CommandHandler("help", help_handler.help))
    handlers.append(CommandHandler("develop", dev.develop))
    handlers.append(MessageHandler(Filters.command, video.video_handler))
    handlers.append(MessageHandler(Filters.text & (Filters.entity(MessageEntity.URL) |
                                                   Filters.entity(MessageEntity.TEXT_LINK)), url.url_handler))
    handlers.append(MessageHandler(Filters.text, text.message_handler))
    handlers.append(MessageHandler(Filters.all, unexpected.unexpected))

    return handlers


def main(arguments: Namespace):
    global updater, db_manager
    try:
        import pickle
        import logging
        import secrets
        import string

        from os import path
        from telegram.ext import Updater
    except (ImportError, ModuleNotFoundError) as import_error:
        cPrint("Modules needed not found" + str(import_error), Colors.FAIL)
        exit(-1)
    else:
        try:
            token = arguments.token
            youtube_api_key = arguments.youtube
            creator_id = arguments.creator
            database_user = arguments.db_user
            database_password = arguments.db_password
            must_show_version = arguments.version
            if must_show_version:
                cPrint("Version: " + Constants.A_APP_VERSION + "-" + Constants.A_APP_TAG_R +
                       " (" + Constants.A_APP_TAG + ")", Colors.BOLD)
                exit(0)
            if not path.exists(Constants.A_APP_DATA_FILE):
                if not token:
                    raise ValueError("You must add token at least the first time you execute this app")
                elif not youtube_api_key:
                    raise ValueError("You must include the YouTubeAPI Key at least the first time you execute this app")
                elif not creator_id:
                    raise ValueError("You must include the creator ID (Telegram) at least the first time you execute "
                                     "this app")
                else:
                    if not database_user:
                        database_user = "youtube_md_bot"
                    if not database_password:
                        alphabet = string.ascii_letters + string.digits
                        database_password = ''.join(secrets.choice(alphabet) for i in range(32))
                    with open(Constants.A_APP_DATA_FILE, "wb") as app_data_file:
                        app_data = {"TOKEN": token,
                                    "YT_API": youtube_api_key,
                                    "CREATOR_ID": creator_id,
                                    "DB_USER": database_user,
                                    "DB_PASSWORD:": database_password}
                        pickle.dump(app_data, app_data_file, pickle.HIGHEST_PROTOCOL)
                    main(arguments)
            else:
                cPrint("Initializing bot...", Colors.GREEN)
                cPrint("Looking for packages updates...", Colors.GREEN)

                upgrader = PiPUpgrader(Constants.A_APP_REQ_FILE)
                upgrader.upgradePackages()

                cPrint("Obtaining values...", Colors.GREEN)
                with open(Constants.A_APP_DATA_FILE, "rb") as app_data_file:
                    app_data = pickle.load(app_data_file)

                cPrint("Starting database system...", Colors.GREEN)
                db_manager = DatabaseOperationsBase(username=database_user, password=database_password)

                cPrint("Defining handlers...", Colors.GREEN)
                handlers = handler_definer()
                updater = Updater(token=app_data["TOKEN"], workers=50)
                dispatcher = updater.dispatcher
                for handler in handlers:
                    dispatcher.add_handler(handler)

                cPrint("Defining log...", Colors.GREEN)
                logger.setup_logging(Constants.L_PRIMARY_LOGGER_NAME, Constants.L_PRIMARY_LOGGER_FILENAME,
                                     Constants.L_PRIMARY_LOGGER_MODE)
                logger.setup_logging(Constants.L_SECONDARY_LOGGER_NAME, Constants.L_SECONDARY_LOGGER_MODE)
            try:
                updater.start_polling(poll_interval=1, timeout=90)
            except KeyboardInterrupt:
                cPrint("Exiting program... Wait while closing threads and pending petitions...", Colors.FAIL)
                updater.idle()
                db_manager.finishConnection()
                exit(0)
        except Exception as program_execution_exception:
            cPrint(str(program_execution_exception), Colors.FAIL)
            exit(-1)


if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument("-t",
                      "--token",
                      help="Telegram token obtained via BotFather",
                      type=str)
    args.add_argument("-y",
                      "--youtube",
                      help="YouTube API Key",
                      type=str)
    args.add_argument("-c",
                      "--creator",
                      help="Telegram ID of the creator",
                      type=int)
    args.add_argument("-dbu",
                      "--db_user",
                      help="Database user (can be empty)",
                      type=str)
    args.add_argument("-dbp",
                      "--db_password",
                      help="Database password (can be empty)",
                      type=str)
    args.add_argument("-v",
                      "--version",
                      help="Application version",
                      action="store_true")
    main(args.parse_args())
