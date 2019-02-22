from logging import getLogger, StreamHandler, INFO, Logger


def create_logger() -> Logger:
    logger = getLogger()
    logger.addHandler(StreamHandler())
    logger.setLevel(INFO)
    return logger
