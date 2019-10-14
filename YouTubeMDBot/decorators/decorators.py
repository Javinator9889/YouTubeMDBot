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
from functools import wraps

from ..constants import PROGRAM_ARGS


# logging = LoggingHandler()


def send_action(action):
    """
    Sends an action while processing a command.
    :param action: the action to be performed.
    :return: itself.
    """

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)
        return command_func

    return decorator


def restricted(func):
    """
    Restricts a specific function to be accessed from non-authorized users.
    :param func: function to be wrapped.
    :return: itself.
    """
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in PROGRAM_ARGS["admin"]:
            return
        return func(update, context, *args, **kwargs)
    return wrapped
