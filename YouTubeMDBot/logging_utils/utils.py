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
import os
import logging

from logging.handlers import RotatingFileHandler
from typing import Optional
from .. import (
    LOG_FILE,
    LOG_DEFAULT_FORMAT,
    DEV_CONSOLE_LOG_LEVEL,
    DEV_FILE_LOG_LEVEL
)


def init_logging(logger_name: Optional[str] = None,
                 log_file: Optional[str] = LOG_FILE,
                 console_level: int = DEV_CONSOLE_LOG_LEVEL,
                 file_level: int = DEV_FILE_LOG_LEVEL,
                 log_format: str = LOG_DEFAULT_FORMAT) -> logging:
    """
    Creates a custom logging that outputs to both console and file, if
    filename provided. Automatically cleans-up old logs during runtime and
    allows customization of both console and file levels in addition to the
    formatter.

    :param logger_name: the logger name for later obtaining it.
    :param log_file: a filename for saving the logs during execution - can be
                    `None`
    :param console_level: the logging level for console.
    :param file_level: the logging level for the file.
    :param log_format: the logging format.

    :return: the created logging instance
    """
    formatter = logging.Formatter(log_format)
    logger = logging.getLogger(logger_name)
    if logger.created:
        return logger
    logger.created = True
    for handler in logger.handlers:
        if type(handler) is logging.StreamHandler:
            handler.setLevel(console_level)
            handler.formatter = formatter

    def file_rotator(source: str, dest: str):
        """
        Custom file rotator for creating compressed logging files.

        :param source: source filename.
        :param dest: destination filename.
        """
        import gzip
        import shutil

        with open(source, "rb") as in_file:
            with gzip.open(dest, "wb") as out_file:
                shutil.copyfileobj(in_file, out_file)

    def namer(name: str) -> str:
        """
        Custom namer implementation as we are gzipping files.

        :param name: the name to append .gz
        :return: the name with .gz extension
        """
        return f"{name}.gz"

    if log_file:
        old_log = os.path.exists(log_file)
        file_handler = RotatingFileHandler(log_file,
                                           mode='a',
                                           maxBytes=2 << 20,
                                           backupCount=5)
        file_handler.rotator = file_rotator
        file_handler.namer = namer
        file_handler.setLevel(file_level)
        file_handler.formatter = formatter
        if old_log:
            file_handler.doRollover()
        logger.addHandler(file_handler)

    return logger
