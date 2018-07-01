import logging


class Constants:
    P_USERS_PATH = "user_data/"
    P_USERS_FILE = "user_info.json"

    D_USER_DICT = {"state": 0,
                   "is_downloading_video": False,
                   "pending_videos": 0}

    A_APP_VERSION = "0.2"
    A_APP_TAG = "development"
    A_APP_TAG_R = "d"
    A_APP_DATA_FILE = "app_data.dict"
    A_APP_REQ_FILE = "requirements.txt"
    A_APP_MESSAGES = "messages/messages.json"

    L_PRIMARY_LOGGER_NAME = "pLog"
    L_PRIMARY_LOGGER_MODE = logging.DEBUG
    L_PRIMARY_LOGGER_FILENAME = "youtube-debug-log.log"
    L_SECONDARY_LOGGER_NAME = "sLog"
    L_SECONDARY_LOGGER_MODE = logging.WARNING
