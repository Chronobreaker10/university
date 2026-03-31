import logging
import os
from logging.handlers import RotatingFileHandler
from core.config import LOG_DEFAULT_FORMAT


def setup_logger(file_name, level=logging.INFO, log_format=None):
    if not os.path.exists('logs'):
        os.mkdir('logs')

    handler = RotatingFileHandler(
        f'logs/{file_name}.log',
        maxBytes=10485760, backupCount=20
    )
    if log_format:
        handler.setFormatter(logging.Formatter(LOG_DEFAULT_FORMAT))
    handler.setLevel(level)
    logger = logging.getLogger(file_name)
    logger.addHandler(handler)
    return logger


app_errors_logger = setup_logger('app_errors', logging.WARNING, LOG_DEFAULT_FORMAT)
access_logger = setup_logger("access", logging.DEBUG)
