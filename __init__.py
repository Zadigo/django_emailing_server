import logging
import pathlib

from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).parent.absolute()

ENV_DIR = BASE_DIR / '.env'

load_dotenv(ENV_DIR)


class Logger:
    instance = None

    def __init__(self, name='Emailing server'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        logger.addHandler(handler)

        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M'
        )
        handler.setFormatter(log_format)

        file_handler = logging.FileHandler('access.log')
        logger.addHandler(file_handler)
        file_handler.setFormatter(log_format)

        self.instance = logger

    @classmethod
    def create(cls, name):
        instance = cls(name=name)
        return instance

    def warning(self, message, *args, **kwargs):
        self.instance.warning(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.instance.info(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.instance.error(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self.instance.debug(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.instance.critical(message, *args, **kwargs)


logger = Logger()
