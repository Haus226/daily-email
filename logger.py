import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and logging level.
    
    Args:
        name (str): The name of the logger.
        level (int): The logging level (default is logging.INFO).
    
    Returns:
        logging.Logger: Configured logger instance.
    """

    log_path = os.path.join(f"logs/{name}", ".log")
    handler = TimedRotatingFileHandler(
        log_path, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    handler.suffix = "%Y-%m-%d"
    formatter = logging.Formatter(
        "%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # prevent duplicate logs from root logger
    logger.propagate = False  
    return logger