import logging


def setup_logging(logger_name: str, log_file: str=None, level: logging=logging.DEBUG, logging_format: str=None):
    if logging_format is None:
        logging_format = "%(asctime)s | %(name)s | [%(levelname)s]: %(message)s"
    if log_file is None:
        __setup_logging_no_file(logger_name, level, logging_format)
    else:
        new_logging = logging.getLogger(logger_name)
        logging_formatter = logging.Formatter(logging_format)
        logging_file_handler = logging.FileHandler(log_file, mode='w')

        logging_file_handler.setFormatter(logging_formatter)

        new_logging.setLevel(level)
        new_logging.addHandler(logging_file_handler)
        __cleanup_old_logs(new_logging, log_file)


def __setup_logging_no_file(logger_name: str, level: logging=logging.DEBUG, logging_format: str=None):
    if logging_format is None:
        raise ValueError("The first time a logger is created, the logging format cannot be None")
    new_logging = logging.getLogger(logger_name)
    logging_formatter = logging.Formatter(logging_format)
    logging_console_handler = logging.StreamHandler()

    logging_console_handler.setFormatter(logging_formatter)

    new_logging.setLevel(level)
    new_logging.addHandler(logging_console_handler)


def __cleanup_old_logs(logger: logging.Logger, filename: str):
    from logging import handlers
    rotating_handler = handlers.RotatingFileHandler(filename, maxBytes=2048, backupCount=5)
    logger.addHandler(rotating_handler)
